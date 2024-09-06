""" Guard to connect to the broker to monitor public messages

Author: Dennis Zyska
"""
import os

from .Guard import Guard


def start_guard(args):
    guard = Guard(args.broker_url)
    guard.run()
    guard.join()
