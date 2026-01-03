import pyFAI
from pyFAI.io import integration_config
from txs.azav import integrate1d

from .utils import PROCESS_KEYS


class TxsWorker:
    def __init__(self, options) -> None:
        self.ai = pyFAI.load(integration_config.normalize(options))
        self.process_options = {k: v for k, v in options.items() if k in PROCESS_KEYS}

    def process(self, data, variance=None, normalization_factor=1.0, metadata=None):
        return integrate1d(
            img=data,
            ai=self.ai,
            normalization_factor=normalization_factor,
            variance=variance,
            metadata=metadata,
            **self.process_options,
        )
