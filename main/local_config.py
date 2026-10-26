"""Nạp .env.local, ưu tiên biến môi trường đã đặt trong terminal."""
import os
import re
import shlex
from pathlib import Path


def load_local_environment(path=None):
    path = Path(path) if path is not None else Path(__file__).resolve().parents[1] / ".env.local"
    if not path.is_file():
        return
    values = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            parts = shlex.split(line, comments=True)
            if parts and parts[0] == "export":
                parts = parts[1:]
            if not parts:
                continue
            if len(parts) != 1 or "=" not in parts[0]:
                raise ValueError
            key, value = parts[0].split("=", 1)
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
                raise ValueError
            values[key] = value
        except ValueError:
            raise ValueError(f"Cấu hình {path.name}, dòng {number} không hợp lệ.") from None
    for key, value in values.items():
        os.environ.setdefault(key, value)
