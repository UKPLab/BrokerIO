import logging
import random
import string
import time

import socketio

from broker import init_logging


def get_random_string(length):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))
