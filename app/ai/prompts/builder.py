import logging

from jinja2 import Environment

from app.ai.prompts.registry import PromptRegistry

logger = logging.getLogger("zam-ai-core-api.prompt-builder")

SECTION_SEPARATOR = "\n\n---\n\n"


class PromptBuilder:
    def __init__(self, registry: PromptRegistry) -> None:
        self._registry = registry
        self._sections: list[str] = []

    def add(self, template_key: str, **kwargs) -> "PromptBuilder":
        template = self._registry.get(template_key)
        rendered = self._render(template.content, **kwargs)
        self._sections.append(rendered)
        return self

    def add_raw(self, text: str) -> "PromptBuilder":
        if text:
            self._sections.append(text)
        return self

    def build(self) -> str:
        return SECTION_SEPARATOR.join(self._sections)

    @staticmethod
    def _render(template_content: str, **kwargs) -> str:
        try:
            env = Environment(autoescape=False)
            tpl = env.from_string(template_content)
            return tpl.render(**kwargs)
        except Exception as e:
            logger.error(f"Prompt rendering failed: {e}")
            return template_content
