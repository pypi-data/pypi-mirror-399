# direct_formatting_pandas_ods_reader/__main__.py
import sys
import argparse
import csv
import pandas as pd
from . import read_ods, __version__

def main():
    parser = argparse.ArgumentParser(
        description="Convert an ODS sheet to CSV with direct formatting preserved."
    )
    parser.add_argument(
        "input",
        help="Path to the .ods file"
    )
    parser.add_argument(
        "-s", "--sheet",
        type=int,
        default=0,
        help="Index of sheet to read (0-based, default: 0)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output CSV file (if omitted, writes to stdout)"
    )
    parser.add_argument(
        "-t", "--type",
        choices=["asciidoc", "markdown", "html", "none"],
        default="asciidoc",
        help="Output text format for formatting marks (default: asciidoc)"
    )
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()

    # Read ODS file
    try:
        df = read_ods(args.input, sheet_index=args.sheet, format=args.type)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Output to CSV or stdout
    if args.output:
        df.to_csv(
            args.output,
            index=False,
            quoting=csv.QUOTE_ALL,  # put all fields in quotes
            lineterminator="\n"
        )
    else:
        df.to_csv(
            sys.stdout,
            index=False,
            quoting=csv.QUOTE_ALL,
            lineterminator="\n"
        )

if __name__ == "__main__":
    main()
