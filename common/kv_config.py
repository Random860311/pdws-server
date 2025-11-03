import configparser
import os
import tempfile
import threading
from pathlib import Path

from filelock import FileLock, Timeout  # pip install filelock

class KVConfig:
    """
    Thread-safe and process-safe key/value config backed by an INI file.

    - Namespaces via INI sections (default: "app").
    - Atomic writes to avoid corruption.
    - File-level lock to coordinate across processes.
    """
    def __init__(self, section: str, path: str | os.PathLike = "settings.ini", lock_timeout: float = 5.0):
        self.path = Path(path)
        self.section = section
        self._mem = configparser.ConfigParser()
        self._lock = threading.RLock()
        self._filelock = FileLock(str(self.path) + ".lock")
        self._lock_timeout = lock_timeout

        # Ensure file exists with the section
        if not self.path.exists():
            self._mem[self.section] = {}
            self._atomic_write()
        else:
            self._load()

    # ---------- public API ----------

    def get(self, key: str, fallback: str | None = None) -> str | None:
        with self._lock, self._acquire_filelock():
            self._load()
            sect = self._mem[self.section] if self._mem.has_section(self.section) else {}
            return sect.get(key, fallback)

    def get_int(self, key: str, fallback: int | None = None) -> int | None:
        val = self.get(key, None)
        if val is None:
            return fallback
        try:
            return int(val)
        except ValueError:
            return fallback

    def get_float(self, key: str, fallback: float | None = None) -> float | None:
        val = self.get(key, None)
        if val is None:
            return fallback
        try:
            return float(val)
        except ValueError:
            return fallback

    def get_bool(self, key: str, fallback: bool | None = None) -> bool | None:
        with self._lock, self._acquire_filelock():
            self._load()
            try:
                return self._mem.getboolean(self.section, key, fallback=fallback)
            except (ValueError, configparser.NoOptionError, configparser.NoSectionError):
                return fallback

    def set(self, key: str, value: str | int | float | bool | None) -> None:
        """
        Sets a value and persists immediately (atomic write).
        """
        if value is None:
            self.delete(key)
        with self._lock, self._acquire_filelock():
            self._load()
            if self.section not in self._mem:
                self._mem[self.section] = {}
            self._mem[self.section][key] = str(value)
            self._atomic_write()

    def delete(self, key: str) -> bool:
        """
        Removes a key. Returns True if it existed.
        """
        with self._lock, self._acquire_filelock():
            self._load()
            if self.section in self._mem and key in self._mem[self.section]:
                del self._mem[self.section][key]
                self._atomic_write()
                return True
            return False

    def items(self) -> dict[str, str]:
        """
        Snapshot of all key/values in the section.
        """
        with self._lock, self._acquire_filelock():
            self._load()
            return dict(self._mem[self.section]) if self.section in self._mem else {}

    # ---------- internals ----------

    def _load(self) -> None:
        self._mem.clear()
        # configparser can read empty file gracefully
        self._mem.read(self.path, encoding="utf-8")
        if self.section not in self._mem:
            self._mem[self.section] = {}

    def _atomic_write(self) -> None:
        tmp_dir = self.path.parent
        tmp_fd, tmp_name = tempfile.mkstemp(prefix=self.path.name + ".", dir=tmp_dir)
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                self._mem.write(f)
                f.flush()
                os.fsync(f.fileno())  # ensure bytes hit disk
            # Atomic replace on all major OSes (Windows 10+, Linux, macOS)
            os.replace(tmp_name, self.path)
        finally:
            # If os.replace raised, try to clean up tmp file
            try:
                if os.path.exists(tmp_name):
                    os.remove(tmp_name)
            except OSError:
                pass

    from contextlib import contextmanager
    @contextmanager
    def _acquire_filelock(self):
        try:
            self._filelock.acquire(timeout=self._lock_timeout)
            yield
        except Timeout:
            raise TimeoutError(f"Could not acquire config file lock within {self._lock_timeout}s")
        finally:
            if self._filelock.is_locked:
                self._filelock.release()
