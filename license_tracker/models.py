from dataclasses import dataclass, field
from typing import Optional

from httpx._types import URLTypes


@dataclass
class License:
    filename: str
    raw_content: str
    url: URLTypes
    sha: str


@dataclass
class Dependency:
    name: str
    version: str
    license_name: str
    summary: str
    project_url: URLTypes
    licenses: list[License] = field(default_factory=list)

    def __str__(self) -> str:
        return f"{self.name} ({self.version})"

    @staticmethod
    def parse_string(value: str) -> tuple[str, Optional[str]]:
        try:
            name, version = value.strip().split("==")
        except ValueError:
            # keep it simple, if version is not pinned, then let's assume it's not specified
            name, version = value.strip(), None
        return name.strip(), version.strip() if version else None
