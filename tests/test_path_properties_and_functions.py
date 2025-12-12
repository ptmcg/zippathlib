from pathlib import PurePath
import stat

import pytest

from zippathlib import ZipPath
from .util import _make_zip_archive


@pytest.mark.parametrize(
    "test_path, properties",
    [
        ("", {"is_root": True, "is_dir": True, "is_file": False, "exists": True}),
        ("source", {"is_root": False, "is_dir": True, "is_file": False, "exists": True}),
        ("source/subfolder", {"is_root": False, "is_dir": True, "is_file": False, "exists": True}),
        ("source/File1.txt", {"is_root": False, "is_dir": False, "is_file": True, "exists": True}),
        ("source/subfolder/File4.txt", {"is_root": False, "is_dir": False, "is_file": True, "exists": True}),
        ("source/subfolder/File999.txt", {"is_root": False, "is_dir": False, "is_file": False, "exists": False}),
    ]
)
def test_basic_path_properties(test_path: str, properties:dict[str, bool], tmp_path):
    """Testing basic properties of a path"""
    zp = _make_zip_archive(tmp_path)

    # Test basic properties of a path
    # - name
    # - parent
    # - stem
    # - suffix
    # - parts
    # - is_dir()
    # - is_file()
    if test_path:
        zp = zp / test_path
    zp_expected = PurePath(test_path)

    assert zp.name == zp_expected.name
    assert zp.stem == zp_expected.stem
    assert zp.suffix == zp_expected.suffix
    assert list(zp.parts) == list(zp_expected.parts)

    for prop, expected in properties.items():
        assert getattr(zp, prop)() == expected, f"failed to get {prop}() property of {test_path!r}"

    if test_path:
        assert zp.parent == ZipPath(zp.zip_file, str(PurePath(test_path).parent))

    if test_path and properties["exists"]:
        file_stat = zp.stat()
        if properties["is_file"]:
            assert file_stat.st_size > 0
            assert stat.S_ISREG(file_stat.st_mode), f"{test_path} is not a regular file"
            assert not stat.S_ISDIR(file_stat.st_mode), f"{test_path} is a directory"
        if properties["is_dir"]:
            assert file_stat.st_size == 0
            assert not stat.S_ISREG(file_stat.st_mode), f"{test_path} is not a regular file"
            assert stat.S_ISDIR(file_stat.st_mode), f"{test_path} is a directory"

    if not properties["exists"]:
        with pytest.raises(FileNotFoundError):
            zp.stat()
