# zippathlib - Provides a pathlib.Path subclass for accessing files in ZIP archives

`zippathlib` is a Python library that provides a standalone `ZipPath` class for working with files 
inside ZIP archives using a familiar pathlib-like interface. This allows you to navigate and 
access files within a ZIP archive without first extracting them. From your Python code, you can access
the contents using the familar `pathlib.Path` API, instead of the standard library's `zipfile` module, and
perform operations like reading, writing, checking existence of files and directories, etc.

## Usage - Command line
The `zippathlib` module can be run from the command line with `zippathlib [options] ZIP_FILE [PATH]`.

### List the root directory of a ZIP archive

    $ python -m zippathlib files/frmeshfull154.zip
    Directory: files\frmeshfull154.zip::
    Contents:
      [D] frmeshfull154

### List the files in a directory

    $ python -m zippathlib files/frmeshfull154.zip frmeshfull154
    Directory: files/frmeshfull154.zip::frmeshfull154
    Contents:
      [F] gen00.dat
      [F] gen01.dat
      [F] gen02.dat
      [F] gen03.dat
      [F] gen04.dat

### List the first few lines of a file
