###############################################################################
# main.py Test Suite
###############################################################################
import runpy
from unittest.mock import patch


def test_main_prints_hello_from_artpack_when_run_as_script():
    with patch("builtins.print") as mock_print:
        runpy.run_path("main.py", run_name="__main__")
        mock_print.assert_called_once_with("Hello from artpack!")
