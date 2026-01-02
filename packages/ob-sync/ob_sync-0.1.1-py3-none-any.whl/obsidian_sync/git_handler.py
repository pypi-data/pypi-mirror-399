from pathlib import Path
from datetime import datetime

from git import Repo, InvalidGitRepositoryError


class GitHandler:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self._repo = None
    
    @property
    def repo(self) -> Repo:
        if self._repo is None:
            try:
                self._repo = Repo(self.repo_path)
            except InvalidGitRepositoryError:
                raise ValueError(
                    f"{self.repo_path} is not a git repository. "
                    "Please clone your GitHub repo there first."
                )
        return self._repo
    
    def has_changes(self) -> bool:
        return bool(self.repo.untracked_files or self.repo.is_dirty())
    
    def commit_and_push(self, message: str = None) -> bool:
        if not self.has_changes():
            return False
        
        if message is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            message = f"Sync from Obsidian - {timestamp}"
        
        self.repo.git.add(A=True)
        self.repo.index.commit(message)
        self.repo.remote("origin").push()
        
        return True
    
    def status(self) -> dict:
        return {
            "branch": self.repo.active_branch.name,
            "dirty": self.repo.is_dirty(),
            "untracked": len(self.repo.untracked_files),
        }
