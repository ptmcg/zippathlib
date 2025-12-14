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
    NOBODY = 65534
    NOGROUP = 65534

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
    assert zp.suffixes == zp_expected.suffixes
    assert list(zp.parts) == list(zp_expected.parts)

    for prop, expected in properties.items():
        assert getattr(zp, prop)() == expected, f"failed to get {prop}() property of {test_path!r}"

    if test_path:
        assert zp.parent == ZipPath(zp.zip_file, str(PurePath(test_path).parent))

    if test_path and properties["exists"]:
        file_stat = zp.stat()
        assert file_stat.st_uid == NOBODY
        assert file_stat.st_gid == NOGROUP
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


def test_file_size_overwrite(tmp_path):
    zp = _make_zip_archive(tmp_path)

    scratch = zp / "scratch.txt"
    scratch.write_text("A" * 100)
    assert scratch.size() == 100
    scratch.write_text("A" * 50)
    assert scratch.size() == 50


def test_file_sizes(tmp_path):
    import itertools

    zp = _make_zip_archive(tmp_path)

    this_zp = zp / "scratch"
    file_count = itertools.count(1)

    def make_file(path: str, size: int) -> ZipPath:
        new_zp = this_zp / path / f"file_{next(file_count)}.txt"
        new_zp.write_text("A" * size)
        return new_zp

    # build subdirs with known file sizes
    make_file("sub1", 100)
    make_file("sub1", 200)
    make_file("sub1/sub2", 100)
    make_file("sub1/sub2/sub3", 100)

    assert this_zp.total_size() == 500
    assert (this_zp / "sub1/file_1.txt").size() == 100
    assert (this_zp / "sub1/file_1.txt").total_size() == 100
    assert (this_zp / "sub1/sub2").size() == 0
    assert (this_zp / "sub1/sub2").total_size() == 200

    make_file("sub1/sub2/sub3", 100)
    assert this_zp.total_size() == 600
    assert (this_zp / "sub1/sub2").total_size() == 300
