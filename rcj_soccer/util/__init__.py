from . import config


def obj_to_dict(obj):
    return {
        name: getattr(obj, name) for name in dir(obj)
        if not callable(getattr(obj, name)) and not name.startswith("__")
    }
