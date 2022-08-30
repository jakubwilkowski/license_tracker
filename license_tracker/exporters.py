import os
from typing import Final, MutableMapping, Optional

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
    FIRST_COL_LEN: Final[int] = 30

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
                        f.writelines(self._format_line(key, str(value)))
                    else:
                        f.writelines(self._format_multiline(str(key), str(value)))
        return None

    def _format_line(self, key: str, value: str) -> list[str]:
        lines = []
        if len(key) < self.FIRST_COL_LEN - 1:
            lines.append(f"{key:<{self.FIRST_COL_LEN}} | {value}\n")
            return lines
        # for keys that are longer than 29 characters we need to split them
        # so they can nicely fit in the file.
        split_lines = self._split_key(key, self.FIRST_COL_LEN - 1)
        for line in split_lines:
            lines.append(f"{line:<{self.FIRST_COL_LEN}} | {value}\n")
        return lines

    @staticmethod
    def _split_key(key: str, max_col_len: int) -> list[str]:
        remainder = key.strip()
        results = []
        while len(remainder) > max_col_len:
            # if there are no spaces where we can cut split column name, just take
            # as much and possible and repeat
            if remainder.find(" ") == -1:
                fitting = remainder[:max_col_len]
            else:
                words = remainder.split(" ")
                counter = len(words)
                # take the largest number of words we can fit in 30 characters
                # and leave the rest for next lines
                while len(" ".join(word for word in words[:counter])) > max_col_len:
                    counter -= 1
                fitting = " ".join(word for word in words[:counter])
            results.append(fitting)
            remainder = remainder[len(fitting) :].strip()

        if remainder:
            results.append(remainder)
        return results

    def _format_multiline(self, key: str, value: str) -> list[str]:
        results = []
        first_line, *others = str(value).split("\n")
        results.extend(self._format_line(key, str(first_line)))
        for next_line in others:
            results.extend(self._format_line("", str(next_line)))
        return results
