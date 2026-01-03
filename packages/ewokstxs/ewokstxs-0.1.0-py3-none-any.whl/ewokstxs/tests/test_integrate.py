import h5py

from ewokstxs.tasks.integrate import TxsIntegrateBlissScan


def test_TxsIntegrateBlissScan_task(bliss_task_inputs, tmpdir):
    npt = 700

    inputs = dict(bliss_task_inputs)
    output_filename = str(tmpdir / "result.h5")
    inputs["output_filename"] = output_filename
    inputs["integration_options"] = {
        "error_model": "azimuthal",
        "method": "nosplit_csr",
        "npt": npt,
    }
    inputs["sample_thickness"] = 0.5

    task = TxsIntegrateBlissScan(inputs=inputs)
    task.execute()
    outputs = task.get_output_values()
    assert outputs["nxdata_url"] == f"{output_filename}::/2.1/p3_integrate/integrated"

    with h5py.File(output_filename) as root:
        axes = ["points", "2th"]
        assert root["2.1/p3_integrate/integrated"].attrs["axes"].tolist() == axes
        assert root["2.1/measurement/p3_integrated"].shape == (31, npt)
