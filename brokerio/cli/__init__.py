""" Command line interface for BrokerIO

Author: Dennis Zyska
"""
import argparse
import logging
import pkgutil
import sys
import importlib.util

import brokerio.cli.interfaces
from brokerio.cli.interfaces.BrokerCLI import BrokerCLI
from .CLI import CLI
from .CLI import register_client_module
from .. import init_logging
import os

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


def parse_args(args):
    parser = argparse.ArgumentParser(description="BrokerIO command line", add_help=True)
    subparser = parser.add_subparsers(title="BrokerIO Manager", dest='command')

    # Add cli modules
    cli_interfaces = []
    package = brokerio.cli.interfaces
    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__, prefix=''):
        if not ispkg:
            module_path = os.path.join(importer.path, modname)
            spec = importlib.util.spec_from_file_location(modname, module_path + ".py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            model_class = getattr(module, modname)

            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                cli_interfaces.append({
                    "module": model_class
                })

    for interface in cli_interfaces:
        _parser = subparser.add_parser(interface["module"].name, help=interface["module"].help, add_help=False)
        interface["module"].arg_parser(_parser)
        interface["parser"] = _parser

    return parser.parse_args(args), parser, cli_interfaces


def main():
    logger = init_logging("BrokerIO", logging.DEBUG)

    args, parser, cli_interfaces = parse_args(sys.argv[1:])
    if args.command is None:
        parser.print_help()
    else:
        for interface in cli_interfaces:
            if interface["module"].name == args.command:
                interface["module"](interface["parser"]).parse(args)
