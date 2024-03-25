""" Command line interface for BrokerIO

Author: Dennis Zyska
"""
import argparse
import logging
import pkgutil

import brokerio.cli.interfaces
from brokerio.cli.interfaces.BrokerCLI import BrokerCLI
from .CLI import CLI
from .CLI import register_client_module
from .. import init_logging


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def main():
    logger = init_logging("BrokerIO", logging.DEBUG)

    # Argument parser
    parser = argparse.ArgumentParser(description="BrokerIO command line", add_help=False)

    parser.add_argument('--env', help="Environment file to load", type=str, default="")

    subparser = parser.add_subparsers(title="BrokerIO Manager", dest='command')

    # Add cli modules
    cliInterfaces = []
    package = brokerio.cli.interfaces
    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__, prefix=''):
        if not ispkg:
            cliInterfaces.append({
                "module": getattr(importer.find_module(modname).load_module(modname), modname)
            })

    for interf in cliInterfaces:
        _parser = subparser.add_parser(interf["module"].name, help=interf["module"].help, add_help=False)
        interf["module"].arg_parser(_parser)
        interf["parser"] = _parser

    # parse arguments
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
    else:
        for interf in cliInterfaces:
            if interf["module"].name == args.command:
                interf["module"](interf["parser"]).parse(args)
