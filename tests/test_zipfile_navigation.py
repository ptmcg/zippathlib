import os
import zipfile

import pytest
from zippathlib import ZipPath


def test_navigate_through_zip(tmp_path):
    # create a source folder at tmp_path/source, with 3 files and 1 subfolder with a single file
    (tmp_path / "source").mkdir()
    (tmp_path / "source" / "File1.txt").write_text("This is file 1.")
    (tmp_path / "source" / "File2.txt").write_text("This is file 2.")
    (tmp_path / "source" / "File3.txt").write_text("This is file 3 content.")
    (tmp_path / "source" / "subfolder").mkdir()
    (tmp_path / "source" / "subfolder" / "File4.txt").write_text("This is file 4 in the subfolder.")

    (tmp_path / "zip").mkdir()

    with zipfile.ZipFile(tmp_path / "zip" / "test.zip", mode="w") as zf:
        for path in tmp_path.rglob("source/**/*"):
            zf.write(path , arcname=str(path.relative_to(tmp_path)))

    # open zip and check its content. It should be the same as source folder. Be careful not to include the leading path
    # that ZipPath does not want to include, i.e., "source". The zipfile.ZipFile will return it when opened.
    zp = ZipPath(tmp_path / "zip" / "test.zip")
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
