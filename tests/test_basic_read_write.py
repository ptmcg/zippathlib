import os
from zippathlib import ZipPath
import pytest

from .util import _make_zip_archive


def test_write_and_read(tmp_path):
    zp = _make_zip_archive(tmp_path)  # Path to your temporary zip file

    contents = "New content for new file"
    with (zp / "newfile.txt").open('wt') as f:
        written = f.write(contents)
    assert written == len(contents)

    with (zp / "newfile.txt").open(mode='rb') as f:
        contents_read = f.read()

    assert contents_read == contents.encode()
    assert (zp / "newfile.txt").read_bytes() == contents.encode()

def test_write_and_read2(tmp_path):
    zp = _make_zip_archive(tmp_path)  # Path to your temporary zip file

    contents = "New content for new file"
    written = (zp / "newfile.txt").write_text(contents)
    assert written == len(contents)
    contents2 = (zp / "newfile.txt").read_text()

    assert contents2 == contents
