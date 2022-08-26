import os

from rich.console import Console
from rich.table import Column, Table

from license_tracker.models import Dependency

console = Console(record=True)


class ConsoleExporter:
    def single(self, dependencies: list[Dependency]) -> None:
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


class FileExporter:
    @staticmethod
    def _format_line(key: str, value: str) -> str:
        return f"{key:<30} | {value}\n"

    def single(self, dependencies: list[Dependency]) -> None:
        if not dependencies:
            console.print("No dependencies to export")
            return None

        os.makedirs("output", exist_ok=True)

        for dependency in dependencies:
            filename = (
                "_".join([dependency.name, *dependency.version.split(".")]) + ".txt"
            )
            with open(f"output/{filename}", "w") as f:
                for key, value in dependency.as_dict().items():
                    if len(str(value).split("\n")) == 1:
                        f.write(self._format_line(key, str(value)))
                    else:
                        f.writelines(self._format_multiline(str(key), str(value)))
        return None

    def _format_multiline(self, key: str, value: str) -> list[str]:
        results = []
        first_line, *others = str(value).split("\n")
        results.append(self._format_line(key, str(first_line)))
        for next_line in others:
            results.append(self._format_line("", str(next_line)))
        return results
