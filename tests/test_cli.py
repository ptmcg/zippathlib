import pytest

from zippathlib import ZipPath, ZipPathDuplicateFileWarning
from .util import _make_zip_archive


def _run_cli_command(cmd: str):
    # cmd = f"zippathlib {zp.zip_filename} source/File1.txt --extract -".split()

    import sys
    import zippathlib.__main__ as zip_pathlib_main

    sys.argv[:] = cmd.split()
    zip_pathlib_main.main()


def test_file_extraction(tmp_path):
    import pathlib

    zp = _make_zip_archive(tmp_path)
    assert zp.exists()

    # make directory to extract files to
    output_path = (tmp_path / "output")
    output_path.mkdir()

    _run_cli_command(f"zippathlib {zp.zip_filename} source/File1.txt --extract {output_path}")

    extracted_path = output_path / pathlib.Path(zp.zip_filename).stem / "source" / "File1.txt"

    assert extracted_path.exists()
    assert extracted_path.read_text() == "This is file 1."


def test_file_extraction_to_stdout(tmp_path, capsys):

    zp = _make_zip_archive(tmp_path)
    assert zp.exists()

    _run_cli_command(f"zippathlib {zp.zip_filename} source/File1.txt -x -")

    assert capsys.readouterr().out == "This is file 1.\n"


def test_file_extraction_limit(tmp_path, capsys):
    import itertools

    zp = _make_zip_archive(tmp_path)
    assert zp.exists()

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

    _run_cli_command(f"zippathlib {zp.zip_filename} {this_zp._path} --check l --limit 100")
    assert capsys.readouterr().out == (
        "Large files found\nscratch/sub1/file_2.txt - 200 bytes\n"
    )

    outdir = tmp_path / "out"
    outdir.mkdir()
    _run_cli_command(f"zippathlib {zp.zip_filename} {this_zp._path} -x {outdir} --limit 100")

    assert capsys.readouterr().out == (
        "Error: ValueError: Total file size 500 bytes exceeds extract limit 100 bytes\n"
    )

def test_check_for_duplicate_files_and_purge(tmp_path, capsys):
    zp = _make_zip_archive(tmp_path)

    scratch = zp / "scratch" / "scratch.txt"
    scratch.write_text("A" * 100)
    assert scratch.size() == 100
    with pytest.warns(ZipPathDuplicateFileWarning):
        scratch.write_text("A" * 50)
    assert scratch.size() == 50
    with pytest.warns(ZipPathDuplicateFileWarning):
        scratch.write_text("A" * 10)
    assert scratch.size() == 10

    assert zp.scan_for_duplicates() == [
        ("scratch/scratch.txt", 3)
    ], "expected duplicates not found"

    _run_cli_command(f"zippathlib {zp.zip_filename} --check d --limit 100")
    assert capsys.readouterr().out == (
        "Duplicate files found\nscratch/scratch.txt (3)\n"
    )

    # now purge the duplicates
    _run_cli_command(f"zippathlib {zp.zip_filename} --purge")
    assert zp.scan_for_duplicates() == []
    assert scratch.size() == 10
