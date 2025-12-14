# zippathlib - Provides a pathlib.Path-like class for accessing files in ZIP archives

`zippathlib` is a Python library that provides a standalone `ZipPath` class for working with files 
inside ZIP archives using a familiar pathlib.Path-like interface. This allows you to navigate and 
access files within a ZIP archive without first extracting them. From your Python code, you can access
the contents using the familar `pathlib.Path` API, instead of the standard library's `zipfile` module, and
perform operations like reading, writing, checking existence of files and directories, etc.

`zippathlib` is also accessible from the command line, allowing you to list contents of ZIP archives,
extract individual files or directories, and view the contents of the ZIP archive as a tree.

<!-- TOC -->
* [zippathlib - Provides a pathlib.Path-like class for accessing files in ZIP archives](#zippathlib---provides-a-pathlibpath-like-class-for-accessing-files-in-zip-archives)
  * [Features](#features)
  * [Usage - Command line](#usage---command-line)
    * [List the root directory of a ZIP archive](#list-the-root-directory-of-a-zip-archive)
    * [List the files in a directory](#list-the-files-in-a-directory)
    * [List the first few lines of a file](#list-the-first-few-lines-of-a-file)
    * [Extract a file from a ZIP archive to the local filesystem](#extract-a-file-from-a-zip-archive-to-the-local-filesystem)
    * [Extract a file from a ZIP archive to stdout](#extract-a-file-from-a-zip-archive-to-stdout)
    * [View the contents of a ZIP archive (or a subdirectory within the ZIP archive) as a tree](#view-the-contents-of-a-zip-archive-or-a-subdirectory-within-the-zip-archive-as-a-tree)
  * [Usage - `zippathlib.ZipPath` API](#usage---zippathlibzippath-api)
    * [Open a file from a ZIP archive for reading](#open-a-file-from-a-zip-archive-for-reading)
    * [Store a file into a ZIP archive, and use the '/' operator to navigate or create directories](#store-a-file-into-a-zip-archive-and-use-the--operator-to-navigate-or-create-directories)
    * [List all files in a directory within the ZIP](#list-all-files-in-a-directory-within-the-zip)
    * [Recursively list all directories and files in the ZIP](#recursively-list-all-directories-and-files-in-the-zip)
    * [Check if a file exists in the ZIP](#check-if-a-file-exists-in-the-zip)
  * [Installation](#installation)
  * [Testing](#testing)
  * [Contributing](#contributing)
  * [License](#license)
<!-- TOC -->

## Features
- `ZipPath` class provides a pathlib-like API to access ZIP archive files and directories.
- Supports path composition using the '/' operator.
- Supports basic read/write operations on files within a ZIP archive, including opening files for reading, writing data, etc.
- Allows navigating the directory structure within a ZIP archive using familiar `pathlib` methods like `iterdir()`, `joinpath()`, etc.
 `riterdir()` provides a recursive listing of the directories and files in the archive.
- Command-line interface for browsing a ZIP archive's contents, or for extracting files to the local filesystem.


## Usage - Command line
The `zippathlib` module can be run from the command line with `zippathlib [options] ZIP_FILE [PATH]`.

    $ zippathlib -h
    usage: zippathlib [-h] [--tree] [--extract [OUTPUTDIR]] [--limit LIMIT]
                      zip_file [path_within_zip]
    
    positional arguments:
      zip_file              Zip file to explore
      path_within_zip       Path within the zip file (optional)
    
    options:
      -h, --help            show this help message and exit
      --tree                list all files in a tree-like format
      --extract, -x [OUTPUTDIR]
                            extract files from zip file to a directory or '-' for
                            stdout, default is '.'
      --limit LIMIT         guard value against malicious ZIP files that uncompress
                            to excessive sizes; specify as an integer or float value
                            optionally followed by a multiplier suffix K,M,G,T,P,E,
                            or Z; default is 2.00G

### List the root directory of a ZIP archive

    $ zippathlib .\dist\zippathlib-0.1.0-py3-none-any.whl
    Directory: dist\zippathlib-0.1.0-py3-none-any.whl::
    Contents:
      [D] zippathlib
      [D] zippathlib-0.1.0.dist-info

### List the files in a directory

    $ zippathlib .\dist\zippathlib-0.1.0-py3-none-any.whl zippathlib-0.1.0.dist-info
    Directory: dist\zippathlib-0.1.0-py3-none-any.whl::zippathlib-0.1.0.dist-info
    Contents:
      [D] licenses
      [F] METADATA
      [F] WHEEL
      [F] entry_points.txt
      [F] top_level.txt
      [F] RECORD

### List the first few lines of a file

    $ zippathlib .\dist\zippathlib-0.1.0-py3-none-any.whl zippathlib-0.1.0.dist-info/licenses/LICENSE
    File: dist\zippathlib-0.1.0-py3-none-any.whl::zippathlib-0.1.0.dist-info/licenses/LICENSE
    Content:
    MIT License
    
    Copyright (c) 2025 Paul McGuire
    
    Permission is hereby granted, free of charge, to a...

### Extract a file from a ZIP archive to the local filesystem

    # if outputdir is omitted, file is extracted to the current directory
    $ zippathlib .\dist\zippathlib-0.1.0-py3-none-any.whl zippathlib-0.1.0.dist-info/licenses/LICENSE --extract /tmp

### Extract a file from a ZIP archive to stdout

    # if outputdir is "-", file is extracted and printed to stdout
    $ zippathlib .\dist\zippathlib-0.1.0-py3-none-any.whl zippathlib-0.1.0.dist-info/licenses/LICENSE --extract -
    MIT License
    
    Copyright (c) 2025 Paul McGuire
    
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    ...

### View the contents of a ZIP archive (or a subdirectory within the ZIP archive) as a tree

    $ python -m zippathlib ./dist/zippathlib-0.1.0-py3-none-any.whl --tree

    ├── zippathlib-0.1.0.dist-info
    │   ├── RECORD
    │   ├── top_level.txt
    │   ├── entry_points.txt
    │   ├── WHEEL
    │   ├── METADATA
    │   └── licenses
    │       └── LICENSE
    └── zippathlib
        ├── zip_pathlib.py
        ├── __main__.py
        └── __init__.py 

(Thanks to Will McGugan's `rich` library for making the tree output so easy.)

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

### Recursively list all directories and files in the ZIP

```python
from zippathlib import ZipPath

zip_path = ZipPath('archive.zip')

# list all contents, in depth first search
for file in zip_path.riterdir():
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
Contributions are welcome. Please open an issue or submit a pull request on [GitHub](https://github.com/ptmcg/zippathlib).

If you have ideas or suggestions, feel free to drop a note in the GitHub repo [Discussions](https://github.com/ptmcg/zippathlib/discussions).

## License
This project is licensed under the MIT License - see the LICENSE file for details.
