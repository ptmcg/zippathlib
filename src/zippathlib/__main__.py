import argparse
import zipfile
from pathlib import Path

from rich import print as rprint
from rich.tree import Tree as RichTree

from zippathlib import ZipPath

DEFAULT_SIZE_LIMIT = 2 * 1024**3

def get_version() -> str:
    from . import __version__
    return __version__

def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.prog = 'zippathlib'
    parser.add_argument("zip_file", help="Zip file to explore")
    parser.add_argument("path_within_zip", nargs='?', default="",
            help="Path within the zip file (optional)")

    # options
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {get_version()}"
    )
    parser.add_argument("--tree" , action="store_true", help="list all files in a tree-like format")
    parser.add_argument(
        "-x", "--extract",
        nargs="?", const=".", default=None,
        dest="outputdir",
        help="extract files from zip file to a directory or '-' for stdout, default is '.'"
    )
    parser.add_argument(
        "--limit", default=2*1024**3,
        type = _h2i,
        help="guard value against malicious ZIP files that uncompress"
             " to excessive sizes; specify as an integer or float value"
             " optionally followed by a multiplier suffix K,M,G,T,P,E, or Z;"
             f" default is {_i2h(DEFAULT_SIZE_LIMIT).rstrip('B')}"
    )

    return parser

def _i2h(n: int) -> str:
    if n < 1024:
        return f"{n:,} bytes"
    for prefix in "KMGTPEZ":
        n /= 1024
        if n < 1024:
            break
    return f"{n:.2f}{prefix}B"

def _h2i(s: str) -> int:
    if not s:
        return 0

    s = s.rstrip("B").replace(",", "").removesuffix(" bytes")

    if s.isdigit():
        return int(s)

    n = 1
    for prefix in "KMGTPEZ":
        n *= 1024
        if prefix == s[-1]:
            break
    return int(n * float(s[:-1]))

def _extract_file(zippath:ZipPath, outputdir: Path | None = None):
    """Extract a file from the zip archive."""
    if not zippath.exists():
        raise FileNotFoundError(f"File {str(zippath)!r} not found in zip archive.")

    data = zippath.read_bytes()
    path, _, name = zippath._path.rpartition("/")
    (outputdir / path).mkdir(parents=True, exist_ok=True)
    outputpath = outputdir / path / name
    outputpath.write_bytes(data)


def _construct_tree(zippath:ZipPath) -> RichTree:
    """Construct a rich Tree for the given zip path."""

    ret = RichTree("")
    parent_stack: list[tuple[RichTree, int]] = [(ret, zippath._depth - 1)]

    for node in zippath.riterdir():
        if not node.name:
            continue

        # unwind stack until depth < node's depth (which will be the new node's parent)
        while node._depth <= parent_stack[-1][-1]:
            parent_stack.pop()

        parent = parent_stack[-1][0]
        node_branch = parent.add(node.name)

        parent_stack.append((node_branch, node._depth))

    return ret


def main():
    args =  make_parser().parse_args()

    zip_file = args.zip_file
    path_within_zip = args.path_within_zip
    NL = "\n"

    try:
        # See if zip_file is actually a ZIP file
        zipfile.ZipFile(zip_file)

        zip_path = ZipPath(zip_file)

        if "*" in path_within_zip:
            # Handle * wildcard for path_within_zip
            files = [item for item in zip_path.glob(path_within_zip)]
            print("Files:", *map(str, files), sep=NL)
        else:

            if path_within_zip:
                zip_path = zip_path / path_within_zip

            if not zip_path.exists():
                raise ValueError(f"{path_within_zip!r} does not exist in {zip_file}")

            if args.tree:
                # print pretty tree of ZIP contents
                rprint(_construct_tree(zip_path))

            elif args.outputdir:
                # extracting one or more files/directories
                if args.outputdir == "-":
                    if zip_path.is_file():
                        # dump to stdout
                        print(zip_path.read_text())
                    else:
                        raise ValueError("Cannot dump directory to stdout")
                else:
                    # extract files to given directory
                    zip_file_path = Path(zip_file)
                    outputdir = Path(args.outputdir) / zip_file_path.stem
                    total_size = zip_path.total_size()
                    if total_size > args.limit:
                        raise ValueError(f"Total file size {_i2h(total_size)} exceeds extract limit {_i2h(args.limit)}")

                    for file in zip_path.riterdir():
                        if file.is_file():
                            print(f"extracting {file}")
                            _extract_file(file, outputdir)
                        else:
                            # make directory, in case it is an empty dir
                            (outputdir / file._path).mkdir(parents=True, exist_ok=True)

            else:
                # just browsing
                if zip_path.is_file():
                    print(f"File: {zip_path} ({_i2h(zip_path.size())})")
                    content = zip_path.read_text()
                    print(
                        f"Content:{NL}{content[:100]}"
                        f"{'...' if  len(content) > 100 else ''}"
                    )

                elif zip_path.is_dir():
                    print(f"Directory: {zip_path} (total size {_i2h(zip_path.total_size())})")
                    print("Contents:")
                    for item in zip_path.iterdir():
                        type_indicator = "FD"[item.is_dir()]
                        print(f"  [{type_indicator}] {item.name} {_i2h(item.size()) if item.is_file() else _i2h(item.total_size())}")
                else:
                    print(f"Path does not exist: {zip_path}")

    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        # raise


if __name__ == '__main__':
    raise SystemExit(main())