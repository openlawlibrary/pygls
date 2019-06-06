import json


def _is_namedtuple_instance(x):
    _type = type(x)
    bases = _type.__bases__
    if len(bases) != 1 or bases[0] != tuple:
        return False
    fields = getattr(_type, '_fields', None)
    if not isinstance(fields, tuple):
        return False
    return all(type(i) == str for i in fields)


def namedtuple_to_dict(obj):
    # https://stackoverflow.com/a/39235373/9669050
    if isinstance(obj, dict):
        return {key: namedtuple_to_dict(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [namedtuple_to_dict(value) for value in obj]
    elif _is_namedtuple_instance(obj):
        return {key: namedtuple_to_dict(value) for key, value in obj._asdict().items()}
    elif isinstance(obj, tuple):
        return tuple(namedtuple_to_dict(value) for value in obj)
    else:
        return obj


def obj_to_json(obj):
    return json.dumps(obj, default=lambda o: o.__dict__, indent=2)
