from rich.console import Console
from rich.table import Column, Table

from license_tracker.models import Dependency

console = Console(record=True)


class AsTable:
    # @staticmethod
    # def export(dependencies: list[Dependency]) -> None:
    #     if not dependencies:
    #         console.print("No dependencies to export")
    #         return None
    #     headers: list[str] = [
    #         key for key in asdict(dependencies[0]).keys() if not key.startswith("_")
    #     ]
    #     table = Table(*headers)
    #     for dependency in dependencies:
    #         items = []
    #         for key in headers:
    #             items.append(getattr(dependency, key))
    #         table.add_row(*items)
    #     console.print(table)
    #     return None

    @staticmethod
    def export_single(dependencies: list[Dependency]) -> None:
        if not dependencies:
            console.print("No dependencies to export")
            return None

        for dependency in dependencies:
            table = Table(
                Column(header="Key", width=30),
                Column(header="Value", width=120),
                show_header=False,
                width=150,
            )
            for key, value in dependency.as_dict().items():
                table.add_row(key, str(value))
            console.print(table)
        return None
