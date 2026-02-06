
import pytest
import sys

print("Running tests via script...")
sys.exit(pytest.main(["tests/", "-v"]))
