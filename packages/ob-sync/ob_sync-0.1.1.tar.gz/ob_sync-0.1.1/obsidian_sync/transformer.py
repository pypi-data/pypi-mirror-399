import re
from pathlib import Path
from typing import Set, Tuple

from .config import Config


# Regex patterns for Obsidian wiki-links
# Matches ![[image.png]] or ![[image.png|300]] (with optional size)
IMAGE_WIKI_LINK = re.compile(r'!\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')

# Matches [[Note Name]] or [[Note Name|Display Text]]
NOTE_WIKI_LINK = re.compile(r'(?<!!)\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')


def transform_image_links(content: str, config: Config) -> Tuple[str, Set[str]]:
    images_found: Set[str] = set()
    
    def replace_image(match: re.Match) -> str:
        image_name = match.group(1).strip()
        images_found.add(image_name)
        safe_image_name = image_name.replace(" ", "_")

        raw_url = (
            f"{config.github.raw_url_base}/"
            f"{config.output_path_resources}/{safe_image_name}"
        )
        
        alt_text = Path(safe_image_name).stem
        
        return f"![{alt_text}]({raw_url})"
    
    transformed = IMAGE_WIKI_LINK.sub(replace_image, content)
    return transformed, images_found


def transform_note_links(content: str) -> str:
    def replace_note(match: re.Match) -> str:
        note_name = match.group(1).strip()
        display_text = match.group(2) or note_name
        
        safe_name = note_name.replace(" ", "_")
        
        return f"[{display_text}](./{safe_name}.md)"
    
    return NOTE_WIKI_LINK.sub(replace_note, content)


def transform_file(file_path: Path, config: Config) -> Tuple[str, Set[str]]:
    content = file_path.read_text(encoding="utf-8")
    content, images = transform_image_links(content, config)
    content = transform_note_links(content)
    
    return content, images
