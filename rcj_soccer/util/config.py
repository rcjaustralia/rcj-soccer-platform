import os

ENVIRON_PREFIX = "RCJ_"


def get(base, name, default=None):
    full_name = ENVIRON_PREFIX + base.upper() + "_" + name.upper()
    val = os.environ.get(full_name, default)
    return val
