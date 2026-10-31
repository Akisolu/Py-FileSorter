"""Smoke tests proving the extracted ``main`` entry point is testable."""

import sorter


def test_main_sorts_files_from_argv(tmp_path):
    (tmp_path / "a.txt").write_text("1", encoding="utf-8")
    (tmp_path / "b.jpg").write_text("2", encoding="utf-8")

    sorter.main([str(tmp_path)])

    assert sorted(p.name for p in (tmp_path / "txt").iterdir()) == ["a.txt"]
    assert sorted(p.name for p in (tmp_path / "jpg").iterdir()) == ["b.jpg"]


def test_main_prompts_for_path_when_no_args(tmp_path, monkeypatch, capsys):
    (tmp_path / "a.txt").write_text("1", encoding="utf-8")
    prompts = []

    def fake_input(prompt=None):
        prompts.append(prompt)
        return str(tmp_path)

    monkeypatch.setattr("builtins.input", fake_input)

    sorter.main([])

    assert prompts == ["Enter the path to the directory: "]
    assert (tmp_path / "txt" / "a.txt").is_file()
    assert "Files have been sorted by extension." in capsys.readouterr().out


def test_sort_skips_subdirectories(tmp_path):
    (tmp_path / "a.txt").write_text("1", encoding="utf-8")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "b.txt").write_text("2", encoding="utf-8")

    sorter.main([str(tmp_path)])

    assert (tmp_path / "txt" / "a.txt").is_file()
    assert (sub / "b.txt").is_file()  # untouched: directories are skipped


def test_main_defaults_to_sys_argv(tmp_path, monkeypatch):
    (tmp_path / "a.txt").write_text("1", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["sorter.py", str(tmp_path)])

    rc = sorter.main()

    assert rc is None  # legacy main prints and returns nothing
    assert (tmp_path / "txt" / "a.txt").is_file()


def test_packaging_shim_reexports():
    import py_filesorter

    assert py_filesorter.main == sorter.main
    assert py_filesorter.sort_files_by_extension == sorter.sort_files_by_extension
