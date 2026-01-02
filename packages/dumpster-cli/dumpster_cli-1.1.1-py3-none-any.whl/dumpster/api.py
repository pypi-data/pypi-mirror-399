#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import yaml
from pathlib import Path
from typing import Iterable, List, Dict
from functools import lru_cache

from dumpster.git_utils import is_git_ignored, get_git_metadata, render_git_metadata
from dumpster.logs import getLogger
from dumpster.models import DumpsterConfig

logger = getLogger(__name__)

ROOT = Path(os.getenv("DUMPSTER_CONFIG", Path.cwd().resolve()))
CONFIG_FILE = Path(os.getenv("DUMPSTER_CONFIG", ROOT / "dump.yaml"))

# ---------------------------------------------------------------------------
# File handling
# ---------------------------------------------------------------------------

TEXT_EXTENSIONS = {
    ".py",
    ".pyi",
    ".md",
    ".yaml",
    ".yml",
    ".toml",
    ".json",
    ".txt",
    ".rst",
    ".ini",
}


# Load configuration from dump.yaml
@lru_cache(maxsize=1)
def load_config(config_file: Path | str | None = None) -> DumpsterConfig:
    config_file = Path(config_file or CONFIG_FILE)
    if not config_file.exists():
        raise FileNotFoundError(f"{CONFIG_FILE} not found")

    return DumpsterConfig.model_validate(yaml.safe_load(open(config_file)))


# Get text extensions from config or use defaults
def get_text_extensions() -> set[str]:
    config = load_config()
    extensions = config.extensions

    if extensions is not None:
        return set(extensions)

    return TEXT_EXTENSIONS


def is_text_file(path: Path) -> bool:
    extensions = get_text_extensions()
    return path.suffix.lower() in extensions


def should_skip(path: Path) -> bool:
    if path.is_dir():
        return True

    if not is_text_file(path):
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
    path = (root_path / entry).resolve()

    # Explicit glob pattern
    if any(ch in entry for ch in ["*", "?", "["]):
        return sorted(root_path.glob(entry))

    # Directory → recursive include
    if path.is_dir():
        return sorted(path.rglob("*"))

    # Single file
    if path.is_file():
        return [path]

    return []


def iter_content_files(entries: Iterable[str], root_path: Path) -> List[Path]:
    seen = set()
    result: List[Path] = []

    for entry in entries:
        for path in expand_content_entry(entry, root_path):
            if should_skip(path):
                continue
            if path in seen:
                continue
            seen.add(path)
            result.append(path)

    return sorted(result)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def dump(
    root_path: Path | str | None = None,
    config_file: Path | str | None = None,
) -> None:

    if root_path and not config_file:
        config_file = Path(root_path) / "dump.yaml"

    root_path = Path(root_path or ROOT)
    if not root_path.exists():
        logger.error(f"{root_path} does not exists")
        raise FileNotFoundError()

    config_file = Path(config_file or CONFIG_FILE)
    if not CONFIG_FILE.exists():
        logger.error(f"{CONFIG_FILE} does not exists")
        raise FileNotFoundError()

    config = load_config(config_file)

    contents: List[str] = config.contents

    files = iter_content_files(contents, root_path)
    git_meta = get_git_metadata(root_path)

    output_path = config.output
    OUTFILE = (root_path / output_path).resolve()

    with open(OUTFILE, "w", encoding="utf-8") as out:
        if config.prompt:
            out.write(config.prompt.strip() + "\n\n")

        out.write(render_git_metadata(git_meta) + "\n\n")

        if config.header:
            out.write(config.header.strip() + "\n\n")

        for file in files:
            rel = file.relative_to(root_path)
            out.write(f"\n# file: {rel}\n")
            out.write(file.read_text(encoding="utf-8", errors="ignore"))
            out.write("\n")

        if config.footer:
            out.write("\n" + config.footer.strip() + "\n")

    logger.info(f"Wrote {len(files)} files to {OUTFILE}")
