"""Tests for the ``app_cli`` command line interface."""

import pytest

import app_cli


def test_no_args_prints_mini_guide(capsys):
    rc = app_cli.main([])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Quick guide" in out
    assert "-d" in out
    assert "--version, -v" in out
    assert "--help, -h" in out


@pytest.mark.parametrize("flag", ["--version", "-v"])
def test_version_flag(flag, capsys):
    with pytest.raises(SystemExit) as exc:
        app_cli.main([flag])
    assert exc.value.code == 0
    assert app_cli.PROG in capsys.readouterr().out


def test_dir_flag_sorts_files(tmp_path, capsys):
    (tmp_path / "a.txt").write_text("1", encoding="utf-8")
    (tmp_path / "b.jpg").write_text("2", encoding="utf-8")

    rc = app_cli.main(["--dir", str(tmp_path)])

    assert rc == 0
    assert sorted(p.name for p in (tmp_path / "txt").iterdir()) == ["a.txt"]
    assert sorted(p.name for p in (tmp_path / "jpg").iterdir()) == ["b.jpg"]
    assert "Files have been sorted by extension." in capsys.readouterr().out


def test_short_d_flag_is_alias(tmp_path):
    (tmp_path / "a.txt").write_text("1", encoding="utf-8")

    rc = app_cli.main(["-d", str(tmp_path)])

    assert rc == 0
    assert (tmp_path / "txt" / "a.txt").is_file()


def test_dir_missing_returns_error(tmp_path, capsys):
    missing = tmp_path / "does-not-exist"

    rc = app_cli.main(["-d", str(missing)])

    assert rc == 2
    assert "is not a directory" in capsys.readouterr().err


def test_dir_pointing_at_a_file_returns_error(tmp_path, capsys):
    file_path = tmp_path / "file.txt"
    file_path.write_text("x", encoding="utf-8")

    rc = app_cli.main(["-d", str(file_path)])

    assert rc == 2
    assert "is not a directory" in capsys.readouterr().err


def test_argv_defaults_to_sys_argv(tmp_path, monkeypatch):
    (tmp_path / "a.txt").write_text("1", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["py-filesorter", "-d", str(tmp_path)])

    rc = app_cli.main()

    assert rc == 0
    assert (tmp_path / "txt" / "a.txt").is_file()


def test_version_falls_back_when_distribution_not_installed(monkeypatch, capsys):
    from importlib import metadata

    def broken(*args, **kwargs):
        raise metadata.PackageNotFoundError

    monkeypatch.setattr(metadata, "version", broken)

    with pytest.raises(SystemExit):
        app_cli.main(["--version"])

    assert "v0.1.0" in capsys.readouterr().out
