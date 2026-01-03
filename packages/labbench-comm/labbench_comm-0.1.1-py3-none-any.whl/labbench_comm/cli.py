import argparse

from labbench_comm import __version__


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="labbench-comm",
        description="LabBench device communication toolkit",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.parse_args()
