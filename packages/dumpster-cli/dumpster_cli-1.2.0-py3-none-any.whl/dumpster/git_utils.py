from pathlib import Path
from git import Repo
from pathlib import Path
from typing import Dict

from dumpster.logs import getLogger

logger = getLogger(__name__)


def git_repo(root: Path):
    try:
        return Repo(root, search_parent_directories=True)
    except Exception as e:
        logger.warning(f"Failed to find git repo from {root}: {e}")
        return None


def is_git_repo(path: Path) -> bool:
    return git_repo(path) is not None


def is_git_ignored(path: Path) -> bool:
    repo = git_repo(path)
    if not repo:
        logger.info(f"{path} is not in the git repo")
        return False

    try:
        # Get relative path to repository root
        rel_path = path.relative_to(repo.working_dir)
        ignored = repo.ignored(str(rel_path))
        is_ignored = str(rel_path) in ignored
        return is_ignored
    except Exception as e:
        logger.warning(f"Failed to check ignored file for {path}: {e}")
        return False


def get_git_metadata(path: Path) -> Dict[str, str] | None:
    try:
        working_dir = str(path)

        git_dir_exists = Path(path / ".git").exists()
        if not git_dir_exists:
            return None

        repo = Repo(path, search_parent_directories=True)
        head = repo.head
        commit = head.commit
        remote = repo.remote()

        return {
            "working_dir": working_dir,
            "remote_url": str(remote.url),
            "remote_name": str(remote.name),
            "branch": head.ref.name if head.is_detached else "detached",
            "commit": str(commit.hexsha),
            "commit_time": commit.committed_datetime.isoformat(),
            "author": f"{commit.author.name} <{commit.author.email}>",
            "message": str(commit.message).strip() if commit.message else "",
            "dirty": "yes" if repo.is_dirty() else "no",
        }
    except Exception as e:
        logger.warning(f"Failed to get repo metadata from {path}: {e}")
        return None


def render_git_metadata(meta: Dict[str, str] | None) -> str:
    if meta is None:
        return ""
    lines = ["# Git metadata"]
    for k, v in meta.items():
        lines.append(f"# {k}: {v}")
    return "\n".join(lines)
