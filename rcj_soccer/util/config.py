import os

ENVIRON_PREFIX = "RCJ_"


def get(base, name):
    full_name = ENVIRON_PREFIX + base.upper() + "_" + name.upper()
    val = os.environ.get(full_name, None)
    return val
