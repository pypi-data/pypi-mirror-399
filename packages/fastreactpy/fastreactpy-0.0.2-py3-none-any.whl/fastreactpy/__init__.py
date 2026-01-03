from functools import wraps

_current_effect = None

class Signal:
    def __init__(self, value):
        self._value = value
        self._effects = set()

    def __call__(self, *args):
        if not args:
            # getter
            if _current_effect:
                self._effects.add(_current_effect)
            return self._value
        else:
            # setter
            self._value = args[0]
            for eff in list(self._effects):
                eff()

def signal(value):
    return Signal(value)

def effect(fn):
    @wraps(fn)
    def wrapper():
        global _current_effect
        _current_effect = wrapper
        try:
            fn()
        finally:
            _current_effect = None
    wrapper()
    return wrapper
