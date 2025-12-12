import argparse
import zipfile
from pathlib import Path

from rich import print as rprint
from rich.tree import Tree as RichTree

from zippathlib import ZipPath

def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.prog = 'zippathlib'
    parser.add_argument("zip_file", help="Zip file to explore")
    parser.add_argument("path_within_zip", nargs='?', default="",
            help="Path within the zip file (optional)")

    # options
    parser.add_argument("--tree" , action="store_true", help="list all files in a tree-like format")
    parser.add_argument("--extract", "-x",  action="store_true", help="extract files from zip file")
    parser.add_argument(
        "--outputdir", "-o",
        help=(
            "output directory for extraction; must be a directory or '-' for stdout;"
            " must be used with --extract; default is '.'"
        )
    )

    return parser


def _extract_file(zippath:ZipPath, outputdir: Path | None = None):
    """Extract a file from the zip archive."""
    if outputdir is None:
        outputdir = Path()

    if not zippath.exists():
        raise FileNotFoundError(f"File {str(zippath)!r} not found in zip archive.")

    if  zippath.is_file():
        data = zippath.read_bytes()
        path, _, name = zippath._path.rpartition("/")
        (outputdir / path).mkdir(parents=True, exist_ok=True)
        outputpath = outputdir / path / name
        outputpath.write_bytes(data)

    elif zippath.is_dir():
        for item in zippath.riterdir():
            if item is not zippath:
                _extract_file(item, outputdir)

    else:
        raise TypeError("Unsupported ZipPath type.")


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
                rprint(_construct_tree(zip_path))

            elif args.extract:
                if not args.outputdir:
                    _extract_file(zip_path)
                elif args.outputdir == "-":
                    print(zip_path.read_text())
                else:
                    outputdir = Path(args.outputdir)
                    _extract_file(zip_path, outputdir)

            elif args.outputdir:
                raise ValueError("--outputdir must be used with --extract.")

            else:
                if zip_path.is_file():
                    print(f"File: {zip_path}")
                    content = zip_path.read_text()
                    print(
                        f"Content:{NL}{content[:100]}"
                        f"{'...' if  len(content) > 100 else ''}"
                    )

                elif zip_path.is_dir():
                    print(f"Directory: {zip_path}")
                    print("Contents:")
                    for item in zip_path.iterdir():
                        type_indicator = "FD"[item.is_dir()]
                        print(f"  [{type_indicator}] {item.name}")
                else:
                    print(f"Path does not exist: {zip_path}")

    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        # raise


if __name__ == '__main__':
    raise SystemExit(main())