from typing import Protocol
from typing import get_type_hints

import inspect


def inspect_protocol(proto):
    attrs = get_type_hints(proto)
    methods = {}

    for name, obj in proto.__dict__.items():
        if callable(obj) and not name.startswith("_"):
            methods[name] = obj

    return {
        "attributes": attrs,
        "methods": methods,
    }


def extract_names_of(inspected: dict) -> tuple[str, ...]:
    if not isinstance(inspected, dict):
        raise TypeError("inspect_protocol() result must be a dict")

    attrs = inspected.get("attributes") or {}
    methods = inspected.get("methods") or {}

    if not isinstance(attrs, dict) or not isinstance(methods, dict):
        raise ValueError("Invalid inspect_protocol() structure")

    return tuple(attrs.keys()) + tuple(methods.keys())


def get_members_of(proto: Protocol):
    return extract_names_of(inspect_protocol(proto))


def conforms_to_protocol(cls_, proto: Protocol):
    if not inspect.isclass(cls_):
        return False

    for attr in get_members_of(proto):
        if not hasattr(cls_, attr):
            return False

    return True
