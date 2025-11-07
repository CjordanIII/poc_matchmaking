
import json
from pathlib import Path
import tempfile
from typing import Any, Optional


def parse_json_file(file_path: str) -> Optional[Any]:
    """Read JSON from a path and return the parsed object.

    Returns None on file-not-found or JSON decode errors (prints an error).
    """
    p = Path(file_path)
    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {file_path}")
        return None


def atomic_write_json(obj: Any, path: str | Path, *, indent: int = 2, sort_keys: bool = False) -> None:
    """Write JSON to `path` atomically (write temp file then replace).

    Ensures partial/truncated writes don't leave a broken file if the process is interrupted.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=str(p.parent)) as tf:
        json.dump(obj, tf, ensure_ascii=False, indent=indent, sort_keys=sort_keys)
        tmp = Path(tf.name)
    tmp.replace(p)


def to_json_string(data: Any, location: str) -> Optional[str]:
    """Compatibility wrapper that writes JSON to `location` with pretty formatting.

    Returns a success message or None on failure.
    """
    try:
        atomic_write_json(data, location, indent=2, sort_keys=True)
        return "Data successfully written to JSON file"
    except (TypeError, ValueError) as e:
        print(f"Error converting to JSON string: {e}")
        return None


