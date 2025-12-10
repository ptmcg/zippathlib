import pytest
from zippathlib import ZipPath

from .util import _make_zip_archive


def test_navigate_through_zip(tmp_path):

    zp = _make_zip_archive(tmp_path)

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


def test_file_globbing(tmp_path):

    zp = _make_zip_archive(tmp_path)

    assert len(list(zp.glob("*.txt"))) == 0
    assert len(list((zp / "source").glob("*.txt"))) == 3
    assert len(list(zp.rglob("*.txt"))) == 4
