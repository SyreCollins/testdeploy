from dataclasses import dataclass, field


@dataclass
class PromptTemplate:
    path: str
    name: str
    version: str = "0.0.0"
    owner: str = "AI Team"
    status: str = "draft"
    reviewed: str = ""
    supported_models: list[str] = field(default_factory=list)
    content: str = ""
