# tests/test_dumpster.py
from dumpster.api import dump, load_config
from dumpster.models import DumpsterConfig
from pathlib import Path

REPO_PATH = Path(__file__).parent.parent
TEST_CONFIG_PATH = REPO_PATH / "dump.yaml"
TEST_OUTPUT_PATH = REPO_PATH / "sources.txt"


def test_load_config():
    """Test loading configuration from dump.yaml"""
    config = load_config(TEST_CONFIG_PATH)
    assert isinstance(config, DumpsterConfig)
    assert config.output in str(TEST_OUTPUT_PATH)
    assert ".py" in (config.extensions or [])


def test_dump_creates_output_file():
    """Test that dump creates the output file"""
    dump(root_path=REPO_PATH, config_file=TEST_CONFIG_PATH)
    assert TEST_OUTPUT_PATH.exists()
    content = TEST_OUTPUT_PATH.read_text()
    assert "# file: test.py" in content
    assert "# file: README.md" in content
    # avoid to find this exact line in the dump
    assert ".venv" + "/lib" not in content


def test_git_metadata_included():
    """Test that Git metadata is included in the output"""
    dump(root_path=REPO_PATH, config_file=TEST_CONFIG_PATH)
    content = TEST_OUTPUT_PATH.read_text()
    assert "# repository_root:" in content
    assert "# branch:" in content
    assert "# commit:" in content
