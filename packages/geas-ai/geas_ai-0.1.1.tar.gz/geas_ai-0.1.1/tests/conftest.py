import pytest
import os
from typer.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def setup_geas_environment(tmp_path):
    """
    Sets up a temporary GEAS environment with a global agents.yaml.
    """
    # Create .geas/config structure in the tmp_path
    geas_dir = tmp_path / ".geas"
    geas_dir.mkdir()
    config_dir = geas_dir / "config"
    config_dir.mkdir()

    # Create a dummy agents.yaml
    agents_yaml = config_dir / "agents.yaml"
    agents_yaml.write_text(
        """
agents:
  test_agent:
    role: "Test Role"
    goal: "Test Goal"
    backstory: "Test Backstory"
""",
        encoding="utf-8",
    )

    # Change CWD to tmp_path so geas commands run against this env
    cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(cwd)
