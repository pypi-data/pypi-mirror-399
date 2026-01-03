# fastreactpy/__init__.py
import threading
from functools import wraps

# =========================
# SIGNAL (Thread-safe)
# =========================
class Signal:
    def __init__(self, value):
        self._value = value
        self._effects = set()  # effects that depend on this signal
        self._lock = threading.RLock()  # recursive lock for thread safety

    def __call__(self, new_value=None):
        with self._lock:
            if new_value is not None:
                self._value = new_value
                # Notify all dependent effects
                for effect_func in list(self._effects):
                    effect_func()
            return self._value

    def _subscribe(self, effect_func):
        with self._lock:
            self._effects.add(effect_func)

    def _unsubscribe(self, effect_func):
        with self._lock:
            self._effects.discard(effect_func)

def signal(value):
    return Signal(value)

# =========================
# EFFECT (Thread-safe, tracks dependencies)
# =========================
_effect_stack = threading.local()

def effect(fn):
    """Decorator to make a function reactive."""
    @wraps(fn)
    def wrapped_effect(*args, **kwargs):
        # Clear previous dependencies
        if not hasattr(wrapped_effect, "_dependencies"):
            wrapped_effect._dependencies = set()
        else:
            for s in wrapped_effect._dependencies:
                s._unsubscribe(wrapped_effect)
            wrapped_effect._dependencies.clear()

        # Push effect to stack (for dependency tracking)
        if not hasattr(_effect_stack, "stack"):
            _effect_stack.stack = []
        _effect_stack.stack.append(wrapped_effect)

        try:
            result = fn(*args, **kwargs)
        finally:
            _effect_stack.stack.pop()
        return result

    # Run once immediately to register dependencies
    wrapped_effect()

    return wrapped_effect

# =========================
# Signal access hook for tracking
# =========================
_original_call = Signal.__call__

def _signal_call_hook(self, new_value=None):
    if hasattr(_effect_stack, "stack") and _effect_stack.stack:
        current_effect = _effect_stack.stack[-1]
        self._subscribe(current_effect)
        if not hasattr(current_effect, "_dependencies"):
            current_effect._dependencies = set()
        current_effect._dependencies.add(self)
    return _original_call(self, new_value)

Signal.__call__ = _signal_call_hook

# =========================
# Clean API
# =========================
__all__ = ["signal", "effect"]
