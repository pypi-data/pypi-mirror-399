import inspect

ATTRIBUTE_STARTUP = "__zayt_startup__"
ATTRIBUTE_BACKGROUND = "__zayt_background__"


def startup(target):
    assert inspect.isfunction(target)
    setattr(target, ATTRIBUTE_STARTUP, True)
    return target


def background(target):
    assert inspect.iscoroutinefunction(target)
    setattr(target, ATTRIBUTE_BACKGROUND, True)
    return target
