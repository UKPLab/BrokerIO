import os

from broker.utils.Guard import Guard
from broker import load_env

if __name__ == '__main__':
    load_env()
    guard = Guard(os.getenv("BROKER_URL"))
    guard.run()
