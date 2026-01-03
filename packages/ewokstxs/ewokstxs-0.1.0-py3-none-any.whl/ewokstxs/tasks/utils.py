from __future__ import annotations

import logging
import os.path
from collections.abc import Generator

import h5py
import numpy as np
import txs
from blissdata.beacon.data import BeaconData
from blissdata.redis_engine.exceptions import ScanNotFoundError, ScanValidationError
from blissdata.redis_engine.store import DataStore
from ewoksdata.data import nexus
from ewoksdata.data.bliss import iter_bliss_scan_data, iter_bliss_scan_data_from_memory
from pyFAI.containers import Integrate1dResult
from silx.io import h5py_utils
from silx.io.dictdump import dicttonx
from silx.io.url import DataUrl

_logger = logging.getLogger(__name__)


RETRY_OPTIONS = {"retry_timeout": 2 * 60, "retry_period": 1}
"""Retry options used both for reading and writing"""


@h5py_utils.retry()
def _open_h5_file(filename: str, mode: str = "r"):
    """Open a HDF5 file and retries if it fails"""
    return h5py.File(filename, mode)


class TxsResultsWriter:
    """Writes txs results to a HDF5 group.

    :param scan_nxentry_url: URL of the HDF5 group of the scan
    :param results_nxentry_url: URL of the HDF5 group where to write the results
    """

    FLUSH_PERIOD = 3.0
    """Period at which to write to the HDF5 file (seconds)"""

    def __init__(
        self,
        scan_nxentry_url: DataUrl,
        results_nxentry_url: DataUrl,
    ):
        self._scan_nxentry_url = scan_nxentry_url
        self._results_nxentry_url = results_nxentry_url

        self._results_buffer: list[Integrate1dResult] = []
        self._results_timestamp: list[float] = []
        self._chunk_length: int | None = None
        self._nxdata_url: DataUrl | None = None

    def __del__(self):
        self.flush(all=True)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush(all=True)

    @property
    def nxdata_url(self) -> DataUrl | None:
        """URL of the HDF5 group storing the NXdata, None if not yet created"""
        return self._nxdata_url

    def add_result(self, result: Integrate1dResult, timestamp: float):
        """Append data from txs result to the HDF5 datasets"""
        self._results_buffer.append(result)
        self._results_timestamp.append(timestamp)

        if timestamp - self._results_timestamp[0] < self.FLUSH_PERIOD:
            return

        if (
            self._chunk_length is None
            or len(self._results_buffer) >= self._chunk_length
        ):
            self.flush()

    def _create_result_nxentry(self, result: Integrate1dResult) -> DataUrl:
        # Create the output result group and create folders and HDF5 file if needed
        nexus.create_url(self._results_nxentry_url, **RETRY_OPTIONS)
        result_filename = self._results_nxentry_url.file_path()

        # Use a relative path for the external links
        scan_filename = os.path.relpath(
            self._scan_nxentry_url.file_path(),
            os.path.dirname(result_filename),
        )
        scan_group_name = self._scan_nxentry_url.data_path()

        radial_name, radial_unit = result.unit.name.split("_")

        with _open_h5_file(result_filename, mode="a", **RETRY_OPTIONS) as h5file:
            dicttonx(
                {
                    # Add links to some of the scan entries
                    "instrument": h5py.ExternalLink(
                        scan_filename, f"{scan_group_name}/instrument"
                    ),
                    "measurement": h5py.ExternalLink(
                        scan_filename, f"{scan_group_name}/measurement"
                    ),
                    "sample": h5py.ExternalLink(
                        scan_filename, f"{scan_group_name}/sample"
                    ),
                    "title": h5py.ExternalLink(
                        scan_filename, f"{scan_group_name}/title"
                    ),
                    # NXProcess group storing txs results
                    "@default": "integrate",
                    "integrate": {
                        "@NX_class": "NXprocess",
                        # NXData group storing integrated patterns
                        "@default": "integrated",
                        "integrated": {
                            "@NX_class": "NXdata",
                            "@signal": "intensity",
                            "@axes": [".", radial_name],
                            "@interpretation": "spectrum",
                            radial_name: result.radial,
                            f"{radial_name}@units": radial_unit,
                        },
                        "program": "txs",
                        "version": txs.__version__,
                    },
                },
                h5file,
                self._results_nxentry_url.data_path(),
                update_mode="modify",
            )

            nxdata_path = (
                f"{self._results_nxentry_url.data_path()}/integrate/integrated"
            )

            # Create intensity and errors datasets
            npt_rad = len(result.radial)

            nxdata_group = h5file[nxdata_path]
            nxdata_group.create_dataset(
                "intensity",
                dtype=result.intensity.dtype,
                shape=(0, npt_rad),
                chunks=(self._chunk_length, npt_rad),
                maxshape=(None, npt_rad),
                compression="gzip",
            )
            if result.sigma is not None:
                nxdata_group.create_dataset(
                    "intensity_errors",
                    dtype=result.sigma.dtype,
                    shape=(0, npt_rad),
                    chunks=(self._chunk_length, npt_rad),
                    maxshape=(None, npt_rad),
                    compression="gzip",
                )

            return DataUrl(file_path=result_filename, data_path=nxdata_path)

    def _guess_chunk_length(self) -> int:
        if len(self._results_timestamp) > 1:
            # expects regular framerate
            average_frame_rate = 1.0 / np.mean(np.diff(self._results_timestamp))
            chunk_length = int(average_frame_rate * self.FLUSH_PERIOD)
        else:
            chunk_length = len(self._results_timestamp)
        return max(min(chunk_length, 32), 1)

    def flush(self, all: bool = False) -> None:
        if len(self._results_buffer) == 0:
            return

        if self._chunk_length is None:
            self._chunk_length = self._guess_chunk_length()

        if all:
            write_length = len(self._results_buffer)
        else:
            write_length = (
                len(self._results_buffer) // self._chunk_length * self._chunk_length
            )
        if write_length == 0:
            return

        if self._nxdata_url is None:
            # Creates hdf5 entry lazily from first received result
            self._nxdata_url = self._create_result_nxentry(self._results_buffer[0])

        with _open_h5_file(
            self._nxdata_url.file_path(), mode="a", **RETRY_OPTIONS
        ) as h5file:
            nxdata_group = h5file[self._nxdata_url.data_path()]
            intensity_group = nxdata_group["intensity"]

            write_offset = len(intensity_group)
            dataset_length = write_offset + write_length

            intensity_group.resize(dataset_length, axis=0)
            intensity_group[write_offset:dataset_length] = [
                result.intensity for result in self._results_buffer[:write_length]
            ]

            intensity_errors_group = nxdata_group.get("intensity_errors")
            if intensity_errors_group is not None:
                intensity_errors_group.resize(dataset_length, axis=0)
                intensity_errors_group[write_offset:dataset_length] = [
                    result.sigma for result in self._results_buffer[:write_length]
                ]

            self._results_buffer = self._results_buffer[write_length:]


def detector_frames(
    scan_key: str | None,
    filename: str | None,
    scan_number: int,
    detector: str,
) -> Generator[tuple[float, np.ndarray]]:
    """Generator of detector frames from a scan retrieved either through redis or from file

    At least one of scan_key and filename must not be None or empty.

    :scan_key: blissdata key of the scan
    :filename: Path of the HDF5 raw data file to read
    :scan_entry_name: HDF5 path in the file of the group containing the scan data
    :detector: name of the detector
    """
    if not scan_key and not filename:
        raise ValueError("At least one of scan_key and filename must not None or empty")

    if scan_key:  # Try using redis first
        # TODO rework
        try:
            data_store = DataStore(BeaconData().get_redis_data_db())
        except Exception:
            _logger.info("Cannot connect to beacon host or redis")
            _logger.debug("Backtrace", exc_info=True)
        else:
            try:
                _ = data_store.load_scan(scan_key)
            except (ScanNotFoundError, ScanValidationError):
                _logger.info(f"Cannot retrieve scan from redis: {scan_key}")
                _logger.debug("Backtrace", exc_info=True)
            else:
                _logger.info("Retrieve frames through redis")
                for data in iter_bliss_scan_data_from_memory(
                    scan_key,
                    lima_names=[detector],
                    counter_names=["elapsed_time"],
                    **RETRY_OPTIONS,
                ):
                    yield data["elapsed_time"], data[detector]
                return

    if not filename:
        raise RuntimeError("Cannot connect to redis or retrieve the scan")

    _logger.info("Read frames from file")
    for data in iter_bliss_scan_data(
        filename,
        scan_number,
        lima_names=[detector],
        # One counter is needed here to make sure to iterate over the right number of frames
        counter_names=["elapsed_time"],
        **RETRY_OPTIONS,
    ):
        _logger.info(f"Read image for {data['elapsed_time']}")
        yield data["elapsed_time"], data[detector]
