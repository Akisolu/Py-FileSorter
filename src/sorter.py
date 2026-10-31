import pathlib


def sort_files_by_extension(path):
    path = pathlib.Path(path)

    for f in path.iterdir():
        if f.is_dir():
            continue

        ext = f.suffix[1:]  # Get the extension without the leading dot
        ext_dir = path / ext  # Build the path for the extension directory

        ext_dir.mkdir(exist_ok=True)

        dst = ext_dir / f.name  # Build the destination path
        f.rename(dst)


if __name__ == "__main__":
    input_path = input("Enter the path to the directory: ")
    sort_files_by_extension(input_path)
    print("Files have been sorted by extension.")
