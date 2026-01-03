"""
polydup - Python bindings for duplicate code detection

This package provides Python library bindings for the PolyDup duplicate
code detector. It is NOT a CLI tool.

For CLI usage, install the Rust CLI:
    cargo install polydup

For library usage in Python:
    import polydup
    duplicates = polydup.find_duplicates(['src/'], 50, 0.85)
"""

import sys


def main():
    print("polydup Python package is a library, not a CLI.")
    print()
    print("To use the CLI tool, install it via Cargo:")
    print("    cargo install polydup")
    print()
    print("For Python library usage:")
    print("    import polydup")
    print("    duplicates = polydup.find_duplicates(['src/'], min_block_size=50, similarity=0.85)")
    print()
    print("For more information, see: https://github.com/wiesnerbernard/polydup")
    sys.exit(1)


if __name__ == "__main__":
    main()
