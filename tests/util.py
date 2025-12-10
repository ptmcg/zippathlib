from zippathlib import ZipPath


def _make_source_directory(path):
    # create a source folder at tmp_path/source, with 3 files and 1 subfolder with a single file
    (path / "source").mkdir()
    (path / "source" / "File1.txt").write_text("This is file 1.")
    (path / "source" / "File2.txt").write_text("This is file 2.")
    (path / "source" / "File3.txt").write_text("This is file 3 content.")
    (path / "source" / "subfolder").mkdir()
    (path / "source" / "subfolder" / "File4.txt").write_text("This is file 4 in the subfolder.")


def _make_zip_archive(path) ->  ZipPath:
    _make_source_directory(path)

    # make directory for ZIP archive
    (path / "zip").mkdir()

    zp = ZipPath.at_path(path / "source", path / "zip" / "test.zip")

    return zp

