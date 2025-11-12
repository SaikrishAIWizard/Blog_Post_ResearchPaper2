import threading
from typing import List

_lock = threading.Lock()
_messages: List[str] = []
_result = None

def clear():
    with _lock:
        _messages.clear()
        global _result
        _result = None

def append(msg: str):
    with _lock:
        _messages.append(msg)
        # Keep list limited to recent 200 messages
        if len(_messages) > 200:
            del _messages[: len(_messages) - 200]

def get_messages():
    with _lock:
        return list(_messages)

def set_result(result):
    global _result
    with _lock:
        _result = result

def get_result():
    with _lock:
        return _result

def append_progress(msg: str):
    """Convenience alias used by other modules."""
    append(msg)
