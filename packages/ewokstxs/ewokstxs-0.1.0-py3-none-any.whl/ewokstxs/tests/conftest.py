try:
    from ewoksxrpd.tests.conftest import pytest_addoption  # noqa: F401
except ImportError:
    pass  # only required since ewoksxrpd 1.2.1
from ewoksxrpd.tests.conftest import aiSetup1  # noqa: F401
from ewoksxrpd.tests.conftest import bliss_lab6_scan  # noqa: F401
from ewoksxrpd.tests.conftest import bliss_task_inputs  # noqa: F401
from ewoksxrpd.tests.conftest import imageSetup1Calibrant1  # noqa: F401
from ewoksxrpd.tests.conftest import pyfai_integration_version  # noqa: F401
from ewoksxrpd.tests.conftest import setup1  # noqa: F401
