from dataclasses import dataclass, field
from typing import Optional, Union

from httpx import URL
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
            # keep it simple, if versions is not pinned, then let's assume it's not specified
            name, version = value.strip(), None
        return name.strip(), version.strip() if version else None

    def as_dict(self) -> dict[str, Union[str, URL]]:
        result = {
            "Name": self.name,
            "Version": self.version,
            "Summary": self.summary,
            "Project URL": self.project_url,
            "License Name": self.license_name,
        }
        for idx, license_ in enumerate(self.licenses, start=1):
            result.update(
                {
                    f"License filename ({idx})": license_.filename,
                    f"License download URLs ({idx})": license_.url,
                    f"License raw contents ({idx})": license_.raw_content,
                    f"License sha ({idx})": license_.sha,
                }
            )
        return result
