import pytest

from .util import _make_zip_archive


def _run_cli_command(cmd: str):
    # cmd = f"zippathlib {zp.zip_file} source/File1.txt --extract -o -".split()

    import sys
    import zippathlib.__main__ as zip_pathlib_main

    sys.argv[:] = cmd.split()
    zip_pathlib_main.main()


def test_file_extraction(tmp_path):

    zp = _make_zip_archive(tmp_path)
    assert zp.exists()

    # make directory to extract files to
    output_path = (tmp_path / "output")
    output_path.mkdir()

    _run_cli_command(f"zippathlib {zp.zip_file} source/File1.txt --extract --outputdir  {output_path}")

    extracted_path = output_path / "source" / "File1.txt"

    assert extracted_path.exists()
    assert extracted_path.read_text() == "This is file 1."


def test_file_extraction_to_stdout(tmp_path, capsys):

    zp = _make_zip_archive(tmp_path)
    assert zp.exists()

    _run_cli_command(f"zippathlib {zp.zip_file} source/File1.txt --extract -o -")

    assert capsys.readouterr().out == "This is file 1.\n"
