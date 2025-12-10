import os
import zipfile

import pytest
from zippathlib import ZipPath


def _make_source_directory(path):
    # create a source folder at tmp_path/source, with 3 files and 1 subfolder with a single file
    (path / "source").mkdir()
    (path / "source" / "File1.txt").write_text("This is file 1.")
    (path / "source" / "File2.txt").write_text("This is file 2.")
    (path / "source" / "File3.txt").write_text("This is file 3 content.")
    (path / "source" / "subfolder").mkdir()
    (path / "source" / "subfolder" / "File4.txt").write_text("This is file 4 in the subfolder.")


def test_navigate_through_zip(tmp_path):

    _make_source_directory(tmp_path)

    # make directory for ZIP archive
    (tmp_path / "zip").mkdir()

    zp = ZipPath.at_path(tmp_path / "source", tmp_path / "zip" / "test.zip")

    # open zip and check its content. It should be the same as source folder. Be careful not to include the leading path
    # that ZipPath does not want to include, i.e., "source". The zipfile.ZipFile will return it when opened.
    assert zp.is_valid()
    all_files = list(zp.riterdir())
    assert len(all_files) == 7

    zpss = ZipPath(tmp_path / "zip" / "test.zip", "source/subfolder")
    assert zpss.is_valid()
    all_zpss_files = list(zpss.riterdir())
    print(all_zpss_files)
    assert len(all_zpss_files) == 2

    assert (zp / "source" / "File1.txt").read_text()==  "This is file 1."
    assert (zp / "source" / "subfolder" / "File4.txt").read_text() == "This is file 4 in the subfolder."
    assert (zpss / "File4.txt").read_text() == "This is file 4 in the subfolder."


def test_file_extraction (tmp_path):
    import os

    _make_source_directory(tmp_path)

    # make directory for ZIP archive
    (tmp_path / "zip").mkdir()

    zp = ZipPath.at_path(tmp_path / "source", tmp_path / "zip" / "test.zip")
    assert zp.exists()

    # make directory to extract files to
    output_path = (tmp_path / "output")
    output_path.mkdir()

    cmd = f"python -m zippathlib {zp.zip_file} source/File1.txt --extract --outputdir  {output_path}"
    os.system(cmd)

    extracted_path = output_path / "source" / "File1.txt"

    assert extracted_path.exists()
    assert extracted_path.read_text() == "This is file 1."
