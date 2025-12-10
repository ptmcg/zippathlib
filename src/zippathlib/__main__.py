
import argparse
import sys

from zippathlib import ZipPath

def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("zip_file", help="Zip file to explore")
    parser.add_argument("path_within_zip", nargs='?', default="",
            help="Path within the zip file (optional)")

    # options
    parser.add_argument("--tree" , action="store_true", help="List all files in a tree-like format.")
    parser.add_argument("--extract", "-x",  action="store_true", help="Extract files from zip file.")
    parser.add_argument("--outputdir", "-o", help="Output directory for extraction.")

    return parser


def main():
    args =  make_parser().parse_args()

    zip_file = args.zip_file
    path_within_zip = args.path_within_zip
    NL = "\n"

    try:
        zip_path = ZipPath(zip_file)

        if "*" in path_within_zip:
            # Handle * wildcard for path_within_zip
            files = [item for item in zip_path.glob(path_within_zip)]
            print("Files:", *map(str, files), sep=NL)
        else:

            if path_within_zip:
                zip_path = zip_path / path_within_zip

            if args.tree:
                # list all files  in a tree-like format
                for item in zip_path.rglob("*"):
                        print(f"{'  '*(item.depth-1)}|-- {item}")

            else:
                if zip_path.is_file():
                    print(f"File: {zip_path}")
                    print(f"Content:{NL}{zip_path.read_text()[:100]}...")

                elif zip_path.is_dir():
                    print(f"Directory: {zip_path}")
                    print("Contents:")
                    for item in zip_path.iterdir():
                        type_indicator = "FD"[item.is_dir()]
                        print(f"  [{type_indicator}] {item.name()}")
                else:
                    print(f"Path does not exist: {zip_path}")

    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")


if __name__ == '__main__':
    raise SystemExit(main())