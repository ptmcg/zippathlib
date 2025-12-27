import zipfile
import pytest
from pathlib import Path
from zippathlib import ZipPath
from .util import _make_source_directory

def test_at_path_with_dest(tmp_path):
    source = tmp_path / "source"
    _make_source_directory(tmp_path)
    
    zip_file = tmp_path / "test_at_path.zip"
    zp = ZipPath.at_path(source, zip_file)
    
    assert zip_file.exists()
    assert zipfile.is_zipfile(zip_file)
    assert zp.zip_filename == zip_file
    
    # Check if files from source are in the zip
    # Note: at_path uses file.relative_to(source_path.parent)
    # So if source is tmp_path/source, files will be under "source/" in zip
    with zipfile.ZipFile(zip_file, 'r') as zf:
        namelist = zf.namelist()
        assert "source/File1.txt" in namelist
        assert "source/subfolder/File4.txt" in namelist

def test_at_path_no_dest(tmp_path):
    source = tmp_path / "source"
    _make_source_directory(tmp_path)
    
    # Expected zip path is source.parent / f"{source.stem}.zip"
    expected_zip = tmp_path / "source.zip"
    
    zp = ZipPath.at_path(source)
    
    assert expected_zip.exists()
    assert zipfile.is_zipfile(expected_zip)
    assert zp.zip_filename == expected_zip

def test_at_path_already_exists(tmp_path):
    source = tmp_path / "source"
    _make_source_directory(tmp_path)
    
    zip_file = tmp_path / "existing.zip"
    # Create an empty zip first
    with zipfile.ZipFile(zip_file, 'w') as zf:
        pass
        
    # at_path should return ZipPath for existing zip without changing it
    zp = ZipPath.at_path(source, zip_file)
    
    assert zp.zip_filename == zip_file
    with zipfile.ZipFile(zip_file, 'r') as zf:
        assert len(zf.namelist()) == 0

def test_create_new_empty_zip(tmp_path):
    zip_file = tmp_path / "new_empty.zip"
    zp = ZipPath.create(zip_file)
    
    assert zip_file.exists()
    assert zipfile.is_zipfile(zip_file)
    assert zp.zip_filename == zip_file
    
    with zipfile.ZipFile(zip_file, 'r') as zf:
        assert len(zf.namelist()) == 0

def test_create_already_exists(tmp_path):
    zip_file = tmp_path / "already_exists.zip"
    # Create a zip with one file
    with zipfile.ZipFile(zip_file, 'w') as zf:
        zf.writestr("dummy.txt", "content")
        
    zp = ZipPath.create(zip_file)
    
    assert zp.zip_filename == zip_file
    with zipfile.ZipFile(zip_file, 'r') as zf:
        assert "dummy.txt" in zf.namelist()
        assert len(zf.namelist()) == 1
