from typing import Optional


class NoLicenseFound(Exception):
    def __init__(
        self, message: str, *, name: Optional[str] = None, version: str
    ) -> None:
        super().__init__(message)
        self.dependency_name = name
        self.dependency_version = version
