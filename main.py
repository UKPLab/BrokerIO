import os

from broker.utils.Guard import Guard

if __name__ == '__main__':
    guard = Guard(os.getenv("BROKER_URL"))
    guard.run()
