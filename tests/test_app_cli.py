"""Tests for the ``app_cli`` command line interface."""

import sys

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
    assert "v" in capsys.readouterr().out


def test_version_reads_distribution_metadata(monkeypatch, capsys):
    from importlib import metadata

    monkeypatch.setattr(
        metadata,
        "version",
        lambda name: "2.7.1" if name == "py-filesorter" else "err",
    )

    with pytest.raises(SystemExit):
        app_cli.main(["--version"])

    assert "v2.7.1" in capsys.readouterr().out


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


class FakeTty:
    def isatty(self):
        return True


class FakeNotTty:
    def isatty(self):
        return False


def test_paint_wraps_in_ansi_only_when_enabled():
    assert app_cli.paint("hi", "31", True) == "\x1b[31mhi\x1b[0m"
    assert app_cli.paint("hi", "31", False) == "hi"


def test_use_color_tty_and_no_color(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    assert app_cli.use_color(FakeTty()) is True
    assert app_cli.use_color(FakeNotTty()) is False

    monkeypatch.setenv("NO_COLOR", "1")
    assert app_cli.use_color(FakeTty()) is False


def test_mini_guide_prints_plain_text_without_tty(capsys):
    rc = app_cli.main([])
    out = capsys.readouterr().out
    assert rc == 0
    assert "\x1b[" not in out
    assert "Quick guide:" in out


def test_mini_guide_prints_colors_when_tty(monkeypatch):
    monkeypatch.setattr("colorama.just_fix_windows_console", lambda: None)
    monkeypatch.delenv("NO_COLOR", raising=False)
    chunks = []

    class StreamRecorder:
        def write(self, text):
            chunks.append(text)
            return len(text)

        def flush(self):
            pass

        def isatty(self):
            return True

    monkeypatch.setattr(sys, "stdout", StreamRecorder())

    assert app_cli.main([]) == 0
    assert "\x1b[" in "".join(chunks)
    assert "Quick guide:" in "".join(chunks)
