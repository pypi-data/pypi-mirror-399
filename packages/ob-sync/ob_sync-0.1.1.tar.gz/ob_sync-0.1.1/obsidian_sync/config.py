import os
from pathlib import Path
from dataclasses import dataclass
from typing import List

import yaml


@dataclass
class GitHubConfig:
    username: str
    repo: str
    branch: str = "main"
    
    @property
    def raw_url_base(self) -> str:
        return f"https://raw.githubusercontent.com/{self.username}/{self.repo}/{self.branch}"


@dataclass
class Config:
    vault_path: Path
    github: GitHubConfig
    attachments_folder: str
    output_path_resources: str
    output_path: Path
    include: List[str]
    exclude: List[str]
    
    @classmethod
    def from_file(cls, config_path: Path) -> "Config":
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
        
        vault_path = Path(os.path.expanduser(data["vault_path"]))
        output_path = Path(os.path.expanduser(data["output_path"]))
        output_path_resources = Path(os.path.expanduser(data["output_path_resources"]))
        
        github = GitHubConfig(
            username=data["github"]["username"],
            repo=data["github"]["repo"],
            branch=data["github"].get("branch", "main"),
        )
        
        return cls(
            vault_path=vault_path,
            github=github,
            attachments_folder=data.get("attachments_folder", "assets"),
            output_path=output_path,
            output_path_resources=output_path_resources,
            include=data.get("include", ["**/*.md"]),
            exclude=data.get("exclude", []),
        )