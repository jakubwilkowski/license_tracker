from typing import Optional

import rich

from license_tracker import exceptions, models, providers


class DependencyAnalyzer:
    def __init__(self, name: str, version: Optional[str]):
        self.name = name
        self.version = version

    def __call__(self) -> Optional[models.Dependency]:
        try:
            dependency = providers.PypiClient().fetch_dependency_data(
                self.name, self.version
            )
        except exceptions.NoLicenseFound as e:
            rich.print(
                f"{self.name} ({e.dependency_version}) [red]:heavy_exclamation_mark: No licenses found"
            )
            return None
        rich.print(
            f"{dependency} [green]:heavy_check_mark:{ ' [/green][yellow]Found multiple license files' if len(dependency.licenses) > 1 else ''}"
        )

        return dependency
