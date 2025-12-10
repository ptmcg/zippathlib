# zippathlib - Provides a pathlib.Path subclass for accessing files in ZIP archives

`zippathlib` is a Python library that provides a standalone `ZipPath` class for working with files 
inside ZIP archives using a familiar pathlib-like interface. This allows you to navigate and 
access files within a ZIP archive without first extracting them. From your Python code, you can access
the contents using the familar `pathlib.Path` API, instead of the standard library's `zipfile` module, and
perform operations like reading, writing, checking existence of files and directories, etc.

<!-- TOC -->
* [zippathlib - Provides a pathlib.Path subclass for accessing files in ZIP archives](#zippathlib---provides-a-pathlibpath-subclass-for-accessing-files-in-zip-archives)
  * [Features](#features)
  * [Usage - Command line](#usage---command-line)
    * [List the root directory of a ZIP archive](#list-the-root-directory-of-a-zip-archive)
    * [List the files in a directory](#list-the-files-in-a-directory)
    * [List the first few lines of a file](#list-the-first-few-lines-of-a-file)
    * [Extract a file from a ZIP archive to the local filesystem](#extract-a-file-from-a-zip-archive-to-the-local-filesystem)
  * [Usage - `zippathlib.ZipPath` API](#usage---zippathlibzippath-api)
    * [Open a file from a ZIP archive for reading](#open-a-file-from-a-zip-archive-for-reading)
    * [Store a file into a ZIP archive, and use the '/' operator to navigate or create directories](#store-a-file-into-a-zip-archive-and-use-the--operator-to-navigate-or-create-directories)
    * [List all files in a directory within the ZIP](#list-all-files-in-a-directory-within-the-zip)
    * [Check if a file exists in the ZIP](#check-if-a-file-exists-in-the-zip)
  * [Installation](#installation)
  * [Testing](#testing)
  * [Contributing](#contributing)
  * [License](#license)
<!-- TOC -->

## Features
- `ZipPath` class provides a pathlib-like interface to ZIP archive files and directories.
- Supports path composition using the '/' operator.
- Supports basic read/write operations on files within a ZIP archive, including opening files for reading, writing data, etc.
- Allows navigating the directory structure within a ZIP archive using familiar `pathlib` methods like `iterdir()`, `joinpath()`, etc.
- Command-line interface for browsing a ZIP archive's contents, or for extracting files to the local filesystem.


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

    $ python -m zippathlib files/frmeshfull154.zip frmeshfull154/gen02.dat
    File: files\frmeshfull154.zip::frmeshfull154/gen02.dat
    Content:
    [
    [
    Q([(-1618,12647),(-629,8485),(3130,8887),(3048,11037)],[11606295,14889819,13131311,9905975]),
    Q(...

### Extract a file from a ZIP archive to the local filesystem

    # if outputdir is omitted, file is extracted to the current directory
    $ python -m zippathlib files/frmeshfull154.zip frmeshfull154/gen02.dat --extract --outputdir /tmp


## Usage - `zippathlib.ZipPath` API

Here are some examples on how to use `ZipPath` in your Python code:

### Open a file from a ZIP archive for reading

```python
from zippathlib import ZipPath

zip_path = ZipPath('archive.zip', 'path/to/file.txt')
with zip_path.open() as f:
    content = f.read()
```

### Store a file into a ZIP archive, and use the '/' operator to navigate or create directories

```python
from zippathlib import ZipPath

zp = ZipPath('archive.zip')
content_file = zp / 'some/directory' / 'file.txt'
content_file.write_text("This is too easy!")
```


### List all files in a directory within the ZIP

```python
from zippathlib import ZipPath

zip_path = ZipPath('archive.zip')
for file in (zip_path / 'some' / 'directory').iterdir():
    print(file)
```

### Check if a file exists in the ZIP

```python
from zippathlib import ZipPath

if ZipPath('archive.zip', 'path/to/file.txt').exists():
    print("File exists")
```

## Installation
You can install `ZipPath` using pip:

```bash
pip install zippathlib
```

## Testing
Tests are located in the tests directory and can be run using pytest:

```bash
pytest tests
```

## Contributing
Contributions are welcome. Please open an issue or submit a pull request on GitHub.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
