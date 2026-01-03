from __future__ import annotations

import os.path
from collections.abc import Generator
from typing import Any

import numpy as np
import txs
from ewokscore import Task
from pyFAI.containers import Integrate1dResult
from silx.io.url import DataUrl

from .utils import TxsResultsWriter, detector_frames


def txs_integration_results(
    scan_key: str | None,
    filename: str | None,
    scan_number: int,
    energy: float,
    distance: float,
    center: tuple[float, float],
    detector: str,
    binning: int | tuple[int, int] | None,
    pixel: float | tuple[float, float] | None = None,
    integrate1d_options: dict[str, Any] | None = None,
) -> Generator[tuple[float, Integrate1dResult]]:
    """Generator of txs's azimuthal integration results

    At least one of scan_key and filename must not be None or an empty string

    :param scan_key: blissdata scan unique identifier
    :param filename: Path of the HDF5 file where the scan is saved
    :param scan_number: Scan number
    :param energy: X-ray photon energy (eV)
    :param distance: Sample-to-detector distance (m)
    :param center: Coordinates of the image center (hor, ver) (pixel)
    :param detector: Detector name
    :param binning: Detector binning (hor, ver). Giving one value will set both hor and ver.
    :param pixel: Pixel size (hor, ver) (m)
    :param integrate1d_options: Extra arguments to pass to integrate1d
    """
    if not scan_key and not filename:
        raise ValueError(
            "Both scan_key and filename are None or an empty string. At least one must be defined"
        )

    if pixel:
        ai = txs.get_ai(energy, distance, center, binning=binning, pixel=pixel)
    else:
        ai = txs.get_ai(energy, distance, center, binning=binning, detector=detector)

    if integrate1d_options is None:
        integrate1d_options = {}
    for timestamp, image in detector_frames(scan_key, filename, scan_number, detector):
        yield timestamp, txs.azav.integrate1d(image, ai, **integrate1d_options)


class TxsTask(  # type: ignore[call-arg]
    Task,
    input_names=[
        "scan_key",
        "filename",
        "scan",
        "energy",
        "distance",
        "center",
        "detector",
        "binning",
        "output_filename",
    ],
    optional_input_names=["pixel", "integrate1d_options"],
    output_names=["nxdata_url"],
):
    """txs integration task which saves the results to a HDF5 file"""

    def run(self):
        scan_group_name = f"{self.inputs.scan}.1"

        with TxsResultsWriter(
            scan_nxentry_url=DataUrl(
                file_path=os.path.abspath(self.inputs.filename),
                data_path=scan_group_name,
            ),
            results_nxentry_url=DataUrl(
                file_path=os.path.abspath(self.inputs.output_filename),
                data_path=scan_group_name,
            ),
        ) as writer:
            for timestamp, result in txs_integration_results(
                self.inputs.scan_key,
                self.inputs.filename,
                self.inputs.scan,
                self.inputs.energy,
                self.inputs.distance,
                self.inputs.center,
                self.inputs.detector,
                self.inputs.binning,
                self.get_input_value("pixel", None),
                self.get_input_value("integrate1d_options", None),
            ):
                writer.add_result(result, timestamp)

        nxdata_url = writer.nxdata_url
        self.outputs.nxdata_url = nxdata_url.path() if nxdata_url else None


class TxsTaskWithoutSaving(  # type: ignore[call-arg]
    Task,
    input_names=[
        "scan_key",
        "filename",
        "scan",
        "energy",
        "distance",
        "center",
        "detector",
        "binning",
    ],
    optional_input_names=["pixel", "integrate1d_options"],
    output_names=[
        "radial",
        "radial_units",
        "intensity",
        "intensity_error",
    ],
):
    """txs integration task which returns the results"""

    def run(self):
        results = []
        for _, result in txs_integration_results(
            self.inputs.scan_key,
            self.inputs.filename,
            self.inputs.scan,
            self.inputs.energy,
            self.inputs.distance,
            self.inputs.center,
            self.inputs.detector,
            self.inputs.binning,
            self.get_input_value("pixel", None),
            self.get_input_value("integrate1d_options", None),
        ):
            results.append(result)

        if not results:
            raise RuntimeError("No data was processed")

        self.outputs.radial = results[0].radial
        self.outputs.radial_units = results[0].unit.name
        self.outputs.intensity = np.array([res.intensity for res in results])
        self.outputs.intensity_error = np.array([res.sigma for res in results])
