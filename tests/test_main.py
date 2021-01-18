"""
test_main.py -- smoke test
"""

import os
import pytest

from click.testing import CliRunner

from builder import main


@pytest.fixture(scope='module')
def runner():
    return CliRunner()

def test_main(runner):
    result = runner.invoke(main.cli, ['--help'])
    assert result.exit_code == 0

    testoutput = result.output
    expectedoutput = open('tests/expectedoutput', 'r').read()
    assert expectedoutput == testoutput
