#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import yaml
from pathlib import Path
from typing import Iterable, List, Optional, Any, Dict, Callable
from functools import lru_cache

from dumpster.git_utils import is_git_ignored, get_git_metadata, render_git_metadata
from dumpster.logs import getLogger
from dumpster.models import DumpsterConfig
from dumpster.const import DEFAULT_TEXT_EXTENSIONS, FILE_SEPARATOR

logger = getLogger(__name__)

ROOT = Path(os.getenv("DUMPSTER_ROOT", Path.cwd().resolve()))
CONFIG_FILE = Path(os.getenv("DUMPSTER_CONFIG", ROOT / "dump.yaml"))


def _slugify(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_-]+", "-", value)
    value = re.sub(r"^-+|-+$", "", value)
    return value or "dump"


def _load_yaml_dict(config_file: Path) -> Dict[str, Any]:
    if not config_file.exists():
        raise FileNotFoundError(f"{config_file} not found")

    with open(config_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if not isinstance(data, dict):
        raise ValueError("dump.yaml must be a YAML mapping/object at the top level")

    return data


def _compile_name_matcher(pattern: str) -> Callable[[str], bool]:
    """
    Matches dump item name using:
      1) regex fullmatch (case-insensitive) if pattern compiles
      2) else exact case-insensitive match
      3) plus a substring fallback (case-insensitive) for convenience
    """
    pattern = (pattern or "").strip()
    if not pattern:
        return lambda _: True

    try:
        rx = re.compile(pattern, re.IGNORECASE)

        def _match(name: str) -> bool:
            n = name or ""
            return bool(rx.fullmatch(n) or rx.search(n))

        return _match
    except re.error:
        lower = pattern.lower()

        def _match(name: str) -> bool:
            n = (name or "").lower()
            return n == lower or lower in n

        return _match


@lru_cache(maxsize=1)
def load_config(config_file: Path | str | None = None) -> DumpsterConfig:
    """
    Single-config loader (ignores `dumps:` if present).
    Kept for backwards compatibility and existing tests.
    """
    config_file = Path(config_file or CONFIG_FILE)
    data = _load_yaml_dict(config_file)
    if "dumps" in data:
        data = {k: v for k, v in data.items() if k != "dumps"}
    return DumpsterConfig.model_validate(data)


def _extensions_from_config(config: DumpsterConfig) -> set[str]:
    if config.extensions is not None:
        return {e.lower() for e in config.extensions}
    return DEFAULT_TEXT_EXTENSIONS


def is_text_file(path: Path, extensions: set[str]) -> bool:
    return path.suffix.lower() in extensions


def should_skip(path: Path, extensions: set[str]) -> bool:
    if path.is_dir():
        return True
    if not is_text_file(path, extensions):
        return True
    if is_git_ignored(path):
        return True
    return False


def expand_content_entry(entry: str, root_path: Path) -> List[Path]:
    """
    Expansion rules:
      - directory → recursive include (dir/**)
      - glob pattern → glob expansion
      - file → include file
    """
    entry = entry.strip()
    path = (root_path / entry).resolve()

    # Explicit glob pattern
    if any(ch in entry for ch in ["*", "?", "["]):
        return sorted(root_path.glob(entry))

    if path.is_dir():
        return sorted(path.rglob("*"))

    if path.is_file():
        return [path]

    return []


def iter_content_files(
    entries: Iterable[str],
    root_path: Path,
    extensions: set[str],
) -> List[Path]:
    seen: set[Path] = set()
    result: List[Path] = []

    for entry in entries:
        expanded = expand_content_entry(entry, root_path)

        for path in expanded:
            # If the entry points to a concrete file, trust it (ignore ext filter + gitignore)
            is_explicit_file = (root_path / entry).resolve() == path and path.is_file()

            if not is_explicit_file and should_skip(path, extensions):
                continue

            if path in seen:
                continue

            seen.add(path)
            result.append(path)

    return sorted(result)


def _write_dump(
    *,
    root_path: Path,
    config: DumpsterConfig,
    contents_override: Optional[List[str]] = None,
) -> Path:
    effective_contents = (
        contents_override if contents_override is not None else config.contents
    )
    extensions = _extensions_from_config(config)
    files = iter_content_files(effective_contents, root_path, extensions)

    git_meta = get_git_metadata(root_path)

    outfile = (root_path / config.output).resolve()
    outfile.parent.mkdir(parents=True, exist_ok=True)

    with open(outfile, "w", encoding="utf-8") as out:

        if config.prompt:
            out.write(config.prompt.strip() + "\n\n")

        if config.header:
            out.write(config.header.strip() + "\n\n")

        out.write(render_git_metadata(git_meta) + "\n\n")

        for file in files:
            rel = file.relative_to(root_path)
            out.write(f"\n{FILE_SEPARATOR} {rel}\n")
            out.write(file.read_text(encoding="utf-8", errors="ignore"))
            out.write("\n")

        if config.footer:
            out.write("\n" + config.footer.strip() + "\n")

    logger.info(f"Wrote {len(files)} files to {outfile}")
    return outfile


def dump(
    root_path: Path | str | None = None,
    config_file: Path | str | None = None,
    contents: Optional[List[str]] = None,
    name: Optional[str] = None,
) -> List[Path]:
    """
    - If `dumps:` exists: process each item (optionally filtered by --name pattern).
      Root-level options act as defaults for items if not specified, EXCEPT `output`.
      If an item has no output, it becomes: <slug(name)>.txt
    - If no `dumps:`: process top-level options as a single item.
    Returns list of output paths written.
    """
    root_path = Path(root_path or ROOT)

    if not config_file:
        config_file = root_path / "dump.yaml"
    config_file = Path(config_file)

    raw = _load_yaml_dict(config_file)
    outputs: List[Path] = []

    dumps = raw.get("dumps")
    if isinstance(dumps, list) and dumps:
        # Root-level defaults for all dump items, excluding output (explicitly not a default).
        # If "only dumps exists", this dict is empty (good).
        defaults = {k: v for k, v in raw.items() if k not in ("dumps", "output")}

        matcher = _compile_name_matcher(name) if name else (lambda _: True)

        selected: List[Dict[str, Any]] = []
        for i, item in enumerate(dumps):
            if not isinstance(item, dict):
                logger.warning(
                    f"Skipping dumps[{i}] because it is not a mapping/object"
                )
                continue
            item_name = item.get("name")
            if not isinstance(item_name, str) or not item_name.strip():
                raise ValueError(f"dumps[{i}] is missing a valid 'name' field")
            if matcher(item_name):
                selected.append(item)

        if name and not selected:
            raise ValueError(f"No dump profiles matched --name {name!r}")

        for item in selected:
            item_name = item["name"].strip()
            merged = dict(defaults)
            merged.update(item)

            # output is NOT inherited from root; compose if missing
            if "output" not in item or not str(item.get("output") or "").strip():
                merged["output"] = f".dumpster/{_slugify(item_name)}.txt"

            # Ensure the config has its name
            merged["name"] = item_name

            config = DumpsterConfig.model_validate(merged)
            outputs.append(
                _write_dump(
                    root_path=root_path, config=config, contents_override=contents
                )
            )

        return outputs

    # Single-config mode: process top-level options as a single item
    config = DumpsterConfig.model_validate(raw)
    outputs.append(
        _write_dump(root_path=root_path, config=config, contents_override=contents)
    )
    return outputs
