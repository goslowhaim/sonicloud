from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

from .validation import asdict_shallow, parse_dataclass

T = TypeVar("T")


def load_jsonl(path: Path, cls: type[T]) -> list[T]:
    records: list[T] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            try:
                records.append(parse_dataclass(cls, payload))
            except Exception as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc
    return records


def dump_jsonl(path: Path, records: list[object]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(asdict_shallow(record), ensure_ascii=False, sort_keys=True))
            handle.write("\n")
