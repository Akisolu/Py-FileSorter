"""Tests for the ``app_cli`` command line interface."""

import json
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
    assert "--json" in out


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


def test_json_result_reports_moves_and_extensionless_files(tmp_path, capsys):
    (tmp_path / "photo.jpg").write_text("1", encoding="utf-8")
    (tmp_path / "README").write_text("2", encoding="utf-8")

    rc = app_cli.main(["--dir", str(tmp_path), "--json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert rc == 0
    assert captured.err == ""
    assert "\x1b[" not in captured.out
    assert payload == {
        "status": "completed",
        "directory": str(tmp_path),
        "summary": {"moved": 1, "skipped": 1},
        "moved": [
            {
                "source": str(tmp_path / "photo.jpg"),
                "destination": str(tmp_path / "jpg" / "photo.jpg"),
            }
        ],
        "skipped": [{"path": str(tmp_path / "README"), "reason": "no_extension"}],
    }


def test_json_result_reports_collisions_as_warnings(tmp_path, capsys):
    (tmp_path / "photo.jpg").write_text("new", encoding="utf-8")
    (tmp_path / "jpg").mkdir()
    (tmp_path / "jpg" / "photo.jpg").write_text("old", encoding="utf-8")

    rc = app_cli.main(["--dir", str(tmp_path), "--json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert rc == 0
    assert captured.err == ""
    assert payload["status"] == "completed_with_warnings"
    assert payload["summary"] == {"moved": 0, "skipped": 1}
    assert payload["skipped"] == [
        {
            "path": str(tmp_path / "photo.jpg"),
            "reason": "destination_exists",
            "destination": str(tmp_path / "jpg" / "photo.jpg"),
        }
    ]


def test_json_missing_directory_returns_structured_error(capsys):
    rc = app_cli.main(["--json"])

    captured = capsys.readouterr()
    assert rc == 2
    assert captured.err == ""
    assert json.loads(captured.out) == {
        "status": "error",
        "error": {
            "code": "missing_directory",
            "message": "A directory is required. Use --dir DIR to choose one.",
        },
    }


def test_json_invalid_directory_returns_structured_error(tmp_path, capsys):
    missing = tmp_path / "missing-dir"

    rc = app_cli.main(["--dir", str(missing), "--json"])

    captured = capsys.readouterr()
    assert rc == 2
    assert captured.err == ""
    assert json.loads(captured.out) == {
        "status": "error",
        "error": {
            "code": "not_a_directory",
            "message": f"'{missing}' is not a directory",
            "path": str(missing),
        },
    }


def test_json_filesystem_error_returns_failure_status(tmp_path, monkeypatch, capsys):
    def fail(_path):
        raise PermissionError("permission denied")

    monkeypatch.setattr(app_cli.sorter, "sort_files_by_extension", fail)

    rc = app_cli.main(["--dir", str(tmp_path), "--json"])

    captured = capsys.readouterr()
    assert rc == 1
    assert captured.err == ""
    assert json.loads(captured.out) == {
        "status": "error",
        "error": {
            "code": "filesystem_error",
            "message": "permission denied",
            "partial_changes_possible": True,
        },
    }


def test_human_summary_reports_moved_and_skipped_files(tmp_path, capsys):
    (tmp_path / "photo.jpg").write_text("1", encoding="utf-8")
    (tmp_path / "README").write_text("2", encoding="utf-8")

    rc = app_cli.main(["--dir", str(tmp_path)])

    captured = capsys.readouterr()
    assert rc == 0
    assert "Moved 1 file(s)." in captured.out
    assert "Left 1 file(s) without an extension unchanged." in captured.out


def test_human_summary_warns_on_collision(tmp_path, capsys):
    (tmp_path / "photo.jpg").write_text("new", encoding="utf-8")
    (tmp_path / "jpg").mkdir()
    (tmp_path / "jpg" / "photo.jpg").write_text("old", encoding="utf-8")

    rc = app_cli.main(["--dir", str(tmp_path)])

    captured = capsys.readouterr()
    assert rc == 0
    assert "No files were moved" in captured.out
    assert "warning:" in captured.err
    assert "already exists" in captured.err


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

    assert "v1.1.1" in capsys.readouterr().out


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
