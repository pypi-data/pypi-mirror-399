import argparse
import logging
from pprint import pprint

from ewoks import execute_graph
from ewoksutils.task_utils import task_inputs


def main():
    """Run TxsTask with the provided arguments"""
    parser = argparse.ArgumentParser(
        description="Run TxsTask with the given arguments",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "filename",
        type=str,
        help="Path of the HDF5 file where the scan is saved",
    )
    parser.add_argument(
        "scan",
        type=int,
        help="Scan number",
    )
    parser.add_argument(
        "output_filename",
        type=str,
        help="Path of the HDF5 file where to save the integrated results",
    )
    parser.add_argument(
        "-e",
        "--energy",
        required=True,
        type=float,
        help="X-ray photon energy (eV)",
    )
    parser.add_argument(
        "-d",
        "--distance",
        required=True,
        type=float,
        help="Sample-to-detector distance (m)",
    )

    # optional

    parser.add_argument(
        "-c",
        "--center",
        nargs=2,
        type=float,
        default=(960.0, 960.0),
        help="Coordinates of the image center (hor, ver) (pixel)",
    )
    parser.add_argument(
        "--detector",
        type=str,
        default="rayonix",
        help="Detector name",
    )
    parser.add_argument(
        "-b",
        "--binning",
        nargs=2,
        type=int,
        default=(2, 2),
        help="Detector binning (hor, ver)",
    )
    parser.add_argument(
        "-p",
        "--pixel",
        nargs=2,
        type=float,
        default=None,
        help="Pixel size (hor, ver) (m)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity level (-v: INFO, -vv:DEBUG)",
    )

    inputs = {k: v for k, v in vars(parser.parse_args()).items() if k != "verbose"}
    inputs["scan_key"] = None

    print("Inputs:")
    pprint(inputs)
    result = execute_graph(
        {
            "graph": {"id": "txs"},
            "nodes": [
                {
                    "id": "txs_task",
                    "task_type": "class",
                    "task_identifier": "ewokstxs.tasks.txs.TxsTask",
                },
            ],
        },
        inputs=task_inputs(id="txs_task", inputs=inputs),
    )
    print("Result:")
    pprint(result)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    main()
