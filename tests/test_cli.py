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
