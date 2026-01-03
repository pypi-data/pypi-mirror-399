from geas_ai.main import app


def test_agents_command_global(runner, setup_geas_environment):
    """
    Test that 'geas agents' correctly reads and displays the global configuration.
    """
    result = runner.invoke(app, ["agents"])
    assert result.exit_code == 0
    assert "GEAS Agents Roster (Global)" in result.stdout
    assert "test_agent" in result.stdout
    assert "Test Role" in result.stdout
    assert "Test Goal" in result.stdout


def test_agents_command_no_geas(runner, tmp_path):
    """
    Test that 'geas agents' fails properly if not in a geas environment.
    """
    # Ensure we are in an empty temp dir and GEAS is not initialized
    import os

    current_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        result = runner.invoke(app, ["agents"])
        assert result.exit_code == 1
        assert "GEAS is not initialized" in result.stdout
    finally:
        os.chdir(current_cwd)
