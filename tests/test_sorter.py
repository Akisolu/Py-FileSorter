"""Behavior contract for ``sorter.sort_files_by_extension`` (see its docstring)."""

import pytest

import sorter


def test_files_with_different_extensions_go_to_their_folders(tmp_path):
    (tmp_path / "photo.jpg").write_text("1", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("2", encoding="utf-8")

    sorter.sort_files_by_extension(tmp_path)

    assert (tmp_path / "jpg" / "photo.jpg").is_file()
    assert (tmp_path / "txt" / "notes.txt").is_file()


def test_files_sharing_one_extension_share_the_folder(tmp_path):
    (tmp_path / "uno.jpg").write_text("1", encoding="utf-8")
    (tmp_path / "dos.jpg").write_text("2", encoding="utf-8")

    sorter.sort_files_by_extension(tmp_path)

    sorted_names = sorted(p.name for p in (tmp_path / "jpg").iterdir())
    assert sorted_names == ["dos.jpg", "uno.jpg"]


def test_multi_dot_names_use_the_last_extension(tmp_path):
    (tmp_path / "backup.tar.gz").write_text("1", encoding="utf-8")

    sorter.sort_files_by_extension(tmp_path)

    assert (tmp_path / "gz" / "backup.tar.gz").is_file()


def test_existing_subfolders_are_left_untouched(tmp_path):
    sub = tmp_path / "folder"
    sub.mkdir()
    inner = sub / "a.txt"
    inner.write_text("1", encoding="utf-8")

    sorter.sort_files_by_extension(tmp_path)

    assert sub.is_dir()  # untouched, not treated as an extension folder
    assert inner.is_file()
    assert inner.read_text(encoding="utf-8") == "1"


def test_extensionless_files_and_dotfiles_stay_in_place(tmp_path):
    (tmp_path / "README").write_text("1", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("2", encoding="utf-8")

    sorter.sort_files_by_extension(tmp_path)

    assert (tmp_path / "README").is_file()  # still at the top level
    assert (tmp_path / ".gitignore").is_file()  # dotfile: same stay-put policy
    assert not (tmp_path / "jpg").exists() and not (tmp_path / "empty").exists()


def test_collision_keeps_both_files_and_continues(tmp_path, capsys):
    (tmp_path / "photo.jpg").write_text("new", encoding="utf-8")
    (tmp_path / "jpg").mkdir()
    (tmp_path / "jpg" / "photo.jpg").write_text("old", encoding="utf-8")
    (tmp_path / "a.txt").write_text("x", encoding="utf-8")

    result = sorter.sort_files_by_extension(tmp_path)

    assert (tmp_path / "photo.jpg").is_file()  # source kept in place
    destination = tmp_path / "jpg" / "photo.jpg"
    assert destination.read_text(encoding="utf-8") == "old"  # untouched
    assert (tmp_path / "txt" / "a.txt").is_file()  # the rest of the batch carries on
    assert result.skipped[0].reason == "destination_exists"
    assert result.skipped[0].destination == destination
    assert capsys.readouterr().err == ""


def test_missing_route_raises_an_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        sorter.sort_files_by_extension(tmp_path / "missing-dir")


def test_file_route_raises_an_error(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("x", encoding="utf-8")

    with pytest.raises(NotADirectoryError):
        sorter.sort_files_by_extension(file_path)
