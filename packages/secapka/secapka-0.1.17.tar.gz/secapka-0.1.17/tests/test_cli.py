from click.testing import CliRunner

from secapka.cli import cli


def test_version_flag():
    r = CliRunner().invoke(cli, ["-V"])
    assert r.exit_code == 0
    assert "secapka" in r.output.lower()


def test_help():
    r = CliRunner().invoke(cli, ["--help"])
    assert r.exit_code == 0
    assert "scan" in r.output
    assert "show" in r.output
    assert "export" in r.output
