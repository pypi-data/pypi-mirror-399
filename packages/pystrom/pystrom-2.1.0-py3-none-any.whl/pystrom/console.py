import argparse
import logging
import sys

from pystrom.finder import MyStromDeviceFinder

logger = logging.getLogger(__name__)


class MyStromCommandParser:
    """MyStrom command line utility"""

    COMMANDS = ["find"]

    def __get_usage__(self) -> str:
        doc = "pystrom <command> [args]\n\nPossible commands:\n"
        for cmd in self.COMMANDS:
            doc += cmd.ljust(12) + getattr(self, cmd).__doc__ + "\n"
        return doc + "\n"

    def __init__(self) -> None:
        parser = argparse.ArgumentParser(
            description="Control MyStrom devices", usage=self.__get_usage__()
        )
        parser.add_argument("command", help="Subcommand to run")
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            logger.error("Unrecognized command")
            parser.print_help()
            exit(1)
        getattr(self, args.command)()

    # Commands

    def find(self) -> None:
        """Search MyStrom devices in your local network"""
        parser = argparse.ArgumentParser(description=self.find.__doc__)
        parser.add_argument(
            "--live",
            action="store_true",
            help="Keep connection open until manually stopped.",
        )
        args = parser.parse_args(sys.argv[2:])

        with MyStromDeviceFinder() as finder:
            if args.live:
                finder.find_continuous()
            else:
                finder.find_all()
