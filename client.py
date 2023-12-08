import argparse
import logging

from broker import init_logging
from client import register_client_module
from client.Broker import Broker
from client.Models import Models

if __name__ == '__main__':
    logger = init_logging("Broker Manager", logging.DEBUG)

    # Argument parser
    parser = argparse.ArgumentParser(description="Broker Manager")
    subparser = parser.add_subparsers(title="Broker Manager", dest='command')
    modules = {}
    register_client_module(modules, subparser, Models)
    register_client_module(modules, subparser, Broker)

    # parse arguments
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
    else:
        modules[args.command].handle(args)
