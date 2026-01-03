from contextlib import contextmanager

from ewoksxrpd.tasks.integrate import IntegrateBlissScan
from txs import __version__ as txs_version

from ..utils import TXS_INPUTS_KEYS
from ..worker import TxsWorker


class TxsIntegrateBlissScan(IntegrateBlissScan, optional_input_names=TXS_INPUTS_KEYS):  # type: ignore[call-arg]
    def _get_ewoks_pyfai_options(self) -> dict:
        pyfai_options = super()._get_ewoks_pyfai_options()
        txs_options = {
            k: v for k, v in self.get_input_values().items() if k in TXS_INPUTS_KEYS
        }

        return {**pyfai_options, **txs_options}

    @contextmanager
    def _worker(self):
        options = self._get_ewoks_pyfai_options()
        yield TxsWorker(options), options

    def run(self):
        super().run()

        nxdata_url = self.get_output_value("nxdata_url")
        with self.open_h5item(nxdata_url, mode="a", create=True) as nxdata:
            nxprocess = nxdata.parent
            del nxprocess["program"]
            nxprocess["program"] = "txs"
            del nxprocess["version"]
            nxprocess["version"] = txs_version
