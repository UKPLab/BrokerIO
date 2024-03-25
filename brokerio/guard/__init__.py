""" Guard to connect to the broker to monitor public messages

Author: Dennis Zyska
"""
import os

from .Guard import Guard
from .. import load_env


def start_guard():
    load_env()
    guard = Guard(os.getenv("BROKER_URL"))
    guard.run()
