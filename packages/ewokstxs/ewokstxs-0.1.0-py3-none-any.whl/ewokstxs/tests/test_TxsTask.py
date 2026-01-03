import logging
from pathlib import Path

import pytest
import txs
from ewoks import execute_graph
from silx.io.url import DataUrl

# This requires txs to be installed in dev mode with pip install -e
_TXS_TEST_FILEPATH = (
    Path(txs.__file__).parent.absolute()
    / "tests/sample_data/bliss/dye1/dye1_0002/dye1_0002.h5"
)


@pytest.mark.skipif(not _TXS_TEST_FILEPATH.is_file(), reason="Missing test file")
def test_task(tmp_path):
    workflow = {
        "graph": {"id": "txs"},
        "nodes": [
            {
                "id": "txs",
                "task_type": "class",
                "task_identifier": "ewokstxs.tasks.txs.TxsTask",
            },
        ],
    }

    output_filename = str(tmp_path.absolute() / "id09_azav.h5")
    scan_number = 12

    parameters = {
        "scan_key": None,
        "filename": str(_TXS_TEST_FILEPATH),
        "scan": scan_number,
        "energy": 18000,
        "distance": 0.3,
        "center": (960.0, 960.0),
        "detector": "rayonix",
        "binning": (2, 2),
        "output_filename": output_filename,
    }

    inputs = [
        {"id": "txs", "name": name, "value": value}
        for name, value in parameters.items()
    ]

    logging.debug(f"worflow parameters: {parameters}")
    result = execute_graph(workflow, inputs=inputs)
    logging.debug(f"workflow result: {result}")
    assert DataUrl(result["nxdata_url"]) == DataUrl(
        file_path=output_filename, data_path=f"/{scan_number}.1/integrate/integrated"
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_task(Path().absolute())
