import contextlib
import logging
log = logging.getLogger(__name__)
registry = {}


class NoSuchService(RuntimeError):
    def __init__(self, name):
        super().__init__("No such service: %s" % name)


def load(name, actor):
    return get(name)(actor)


def get(name):
    if name in registry:
        return registry[name]

    # attempt to load the service as a python module:class
    if ':' not in name:
        raise NoSuchService(name)
    modname, classname = name.split(':')
    modpath = modname.split('.')
    classpath = classname.split('.')
    try:
        c = __import__(modname)
    except ImportError as e:
        log.exception("Could not import 'modname'", e)
        raise NoSuchService(name)

    for n in modpath[1:]:
        c = getattr(c, n, None)
        if c is None:
            log.error("No module '%s'", n)
            raise NoSuchService(name)
    for n in classpath:
        c = getattr(c, n, None)
        if c is None:
            log.error("No '%s'", n)
            raise NoSuchService(name)
    return c


def register(name, factory):
    registry[name] = factory


def unregister(name):
    del registry[name]


@contextlib.contextmanager
def temp_register(name, factory=None):
    if factory is not None:
        register(name, factory)
    yield get(name)
    unregister(name)


# load the demo module so it registers its services
__import__('xbus.demo')
