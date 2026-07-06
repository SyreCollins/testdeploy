import logging
import os
import re
from pathlib import Path

import yaml

from app.ai.prompts.models import PromptTemplate

logger = logging.getLogger("zam-ai-core-api.prompt-registry")

PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "prompts"

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)", re.DOTALL)


class PromptRegistry:
    def __init__(self, prompts_dir: str | Path | None = None) -> None:
        self._prompts_dir = Path(prompts_dir) if prompts_dir else PROMPTS_DIR
        self._templates: dict[str, PromptTemplate] = {}
        self._loaded = False

    def load_all(self) -> None:
        if self._loaded:
            return
        if not self._prompts_dir.is_dir():
            logger.warning(f"Prompts directory not found: {self._prompts_dir}")
            return

        for md_file in self._prompts_dir.rglob("*.md"):
            relative = md_file.relative_to(self._prompts_dir)
            key = str(relative.with_suffix("")).replace(os.sep, ".")
            self._templates[key] = self._load_file(md_file, key)

        self._loaded = True
        logger.info(f"Loaded {len(self._templates)} prompt templates from {self._prompts_dir}")

    def get(self, key: str) -> PromptTemplate:
        if not self._loaded:
            self.load_all()
        template = self._templates.get(key)
        if template is None:
            msg = f"Prompt template not found: {key}"
            raise KeyError(msg)
        return template

    def list_templates(self) -> list[str]:
        if not self._loaded:
            self.load_all()
        return sorted(self._templates.keys())

    def reload(self) -> None:
        self._loaded = False
        self._templates.clear()
        self.load_all()

    @staticmethod
    def _load_file(path: Path, key: str) -> PromptTemplate:
        raw = path.read_text(encoding="utf-8")
        match = FRONTMATTER_RE.match(raw)

        if match:
            frontmatter_raw = match.group(1)
            body = match.group(2).strip()
            frontmatter = yaml.safe_load(frontmatter_raw) or {}
        else:
            frontmatter = {}
            body = raw.strip()

        return PromptTemplate(
            path=key,
            name=frontmatter.get("name", key),
            version=frontmatter.get("version", "0.0.0"),
            owner=frontmatter.get("owner", "AI Team"),
            status=frontmatter.get("status", "draft"),
            reviewed=frontmatter.get("reviewed", ""),
            supported_models=frontmatter.get("supported_models", []),
            content=body,
        )
