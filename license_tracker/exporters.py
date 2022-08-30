import os
from typing import MutableMapping, Optional

from httpx._types import URLTypes
from rich.console import Console
from rich.table import Column, Table

from license_tracker.models import Dependency

console = Console(record=True)


def as_dict(
    dependency: Dependency, extra_rows: Optional[list[str]] = None
) -> MutableMapping[str, Optional[URLTypes]]:
    result: MutableMapping[str, Optional[URLTypes]] = {
        "Name": dependency.name,
        "Version": dependency.version,
        "Summary": dependency.summary,
        "Project URL": dependency.project_url,
        "License Name": dependency.license_name,
    }
    for idx, license_ in enumerate(dependency.licenses, start=1):
        result.update(
            {
                f"License filename ({idx})": license_.filename,
                f"License download URLs ({idx})": license_.url,
                f"License raw contents ({idx})": license_.raw_content,
                f"License sha ({idx})": license_.sha,
            }
        )
    if extra_rows:
        result.update({extra_row: "" for extra_row in extra_rows})
    return result


class ConsoleExporter:
    def single(
        self, dependencies: list[Dependency], extra_rows: Optional[list[str]] = None
    ) -> None:
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
            for key, value in as_dict(dependency, extra_rows=extra_rows).items():
                table.add_row(key, str(value))
            console.print(table)
        return None


class FileExporter:
    @staticmethod
    def _format_line(key: str, value: str) -> str:
        return f"{key:<30} | {value}\n"

    def single(
        self, dependencies: list[Dependency], extra_rows: Optional[list[str]] = None
    ) -> None:
        if not dependencies:
            console.print("No dependencies to export")
            return None

        os.makedirs("output", exist_ok=True)

        for dependency in dependencies:
            filename = (
                "_".join([dependency.name, *dependency.version.split(".")]) + ".txt"
            )
            with open(f"output/{filename}", "w") as f:
                for key, value in as_dict(dependency, extra_rows=extra_rows).items():
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
