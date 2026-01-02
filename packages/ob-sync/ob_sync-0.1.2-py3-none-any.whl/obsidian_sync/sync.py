import os

import hashlib
import json
import shutil
from pathlib import Path
from typing import Dict, List, Set

import pathspec

from .config import Config
from .transformer import transform_file


class SyncEngine:
    def __init__(self, config: Config):
        self.config = config
        self.hash_file = config.output_path / ".sync-hashes.json"
        self.hashes: Dict[str, str] = self._load_hashes()
        
    def _load_hashes(self) -> Dict[str, str]:
        if self.hash_file.exists():
            with open(self.hash_file, "r") as f:
                return json.load(f)
        return {}
    
    def _save_hashes(self) -> None:
        self.hash_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.hash_file, "w") as f:
            json.dump(self.hashes, f, indent=2)
    
    def _compute_hash(self, file_path: Path) -> str:
        content = file_path.read_bytes()
        return hashlib.md5(content).hexdigest()
    
    def _get_files_to_sync(self) -> List[Path]:
        vault = self.config.vault_path
        
        include_spec = pathspec.PathSpec.from_lines(
            "gitwildmatch", self.config.include
        )
        exclude_spec = pathspec.PathSpec.from_lines(
            "gitwildmatch", self.config.exclude
        )
        
        files = []
        for md_file in vault.rglob("*.md"):
            relative = md_file.relative_to(vault)
            rel_str = str(relative)
            
            if include_spec.match_file(rel_str) and not exclude_spec.match_file(rel_str):
                files.append(md_file)
        
        return files
    
    def _copy_image(self, image_name: str) -> bool:
        attachments = Path(os.path.expanduser(self.config.attachments_folder))
        source = attachments / image_name
        if not source.exists():
            matches = [f for f in attachments.rglob("*") if f.name == image_name]
            print( image_name ,matches)
            if not matches:
                print(f"Image not found: {image_name}")
                return False
            source = matches[0]
        
        dest_dir = self.config.output_path / self.config.output_path_resources
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / image_name.replace(" ", "_")

        shutil.copy2(source, dest)
        return True
    
    def sync(self) -> Dict[str, int]:
        stats = {"files": 0, "images": 0, "skipped": 0}
        all_images: Set[str] = set()
        
        self.config.output_path.mkdir(parents=True, exist_ok=True)
        
        files = self._get_files_to_sync()
        
        for file_path in files:
            relative = file_path.relative_to(self.config.vault_path)
            rel_key = str(relative)
            
            current_hash = self._compute_hash(file_path)
            if self.hashes.get(rel_key) == current_hash:
                stats["skipped"] += 1
                continue
            
            transformed, images = transform_file(file_path, self.config)
            all_images.update(images)
            
            output_file = self.config.output_path / relative
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(transformed, encoding="utf-8")
            
            self.hashes[rel_key] = current_hash
            stats["files"] += 1
        
        for image_name in all_images:
            if self._copy_image(image_name):
                stats["images"] += 1
        
        self._save_hashes()
        return stats
