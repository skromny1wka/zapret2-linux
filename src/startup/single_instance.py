# single_instance.py

import atexit
import os
import sys

if sys.platform == "win32":
    import ctypes

    ERROR_ALREADY_EXISTS = 183
    _kernel32 = ctypes.windll.kernel32


def create_mutex(name: str):
    """
    Пытаемся создать именованный mutex.
    Возвращает (handle, already_running: bool)
    """
    _kernel32.SetLastError(0)
    handle = _kernel32.CreateMutexW(None, False, name)
    last_error = _kernel32.GetLastError()
    already_running = last_error == ERROR_ALREADY_EXISTS

    if not handle:
        return None, False

    return handle, already_running


def release_mutex(handle):
    if handle:
        _kernel32.ReleaseMutex(handle)
        _kernel32.CloseHandle(handle)

else:
    import fcntl

    _LOCK_HANDLE = None
    _LOCK_PATH = os.path.join(
        os.environ.get("XDG_RUNTIME_DIR") or "/tmp",
        "zapret-gui.lock",
    )

    def create_mutex(name: str):
        global _LOCK_HANDLE
        del name
        try:
            fd = os.open(_LOCK_PATH, os.O_CREAT | os.O_RDWR, 0o600)
        except OSError:
            return None, False
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            os.close(fd)
            return None, True
        _LOCK_HANDLE = fd
        atexit.register(release_mutex, fd)
        return fd, False

    def release_mutex(handle):
        global _LOCK_HANDLE
        if handle is None:
            return
        try:
            import fcntl

            fcntl.flock(handle, fcntl.LOCK_UN)
        except Exception:
            pass
        try:
            os.close(handle)
        except Exception:
            pass
        if _LOCK_HANDLE == handle:
            _LOCK_HANDLE = None
        try:
            os.remove(_LOCK_PATH)
        except OSError:
            pass
