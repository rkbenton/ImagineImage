from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parent


@pytest.fixture(autouse=True)
def run_from_tests_dir(monkeypatch):
    """Run every test with tests/ as the working directory.

    The tests use cwd-relative paths (test_themes, image_out, and the
    config_factory.json fixture copy), and the app itself reads
    config_factory.json from the cwd. Without this, the result depends on
    where pytest was launched: from the project root, the real
    config_factory.json and a missing test_themes directory break tests.
    """
    monkeypatch.chdir(TESTS_DIR)
