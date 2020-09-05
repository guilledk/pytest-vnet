#!/usr/bin/env python3
import sys
import subprocess

from pytest_vnet import as_script

def test_echo_script():

    @as_script
    def echo():
        import sys
        print(sys.argv[1])

    message = "Hello World!"

    assert subprocess.check_output(
        [sys.executable, echo.path, message]
    ).decode('utf-8').rstrip() == message