"""Generate the code reference pages."""

from pathlib import Path

import mkdocs_gen_files

import os

print(os.getcwd())

for path in sorted(Path(f"license_tracker").rglob("*.py")):
    print(f"found path {path}")
    module_path = path.relative_to(".").with_suffix("")
    parts = list(module_path.parts)
    full_doc_path = Path("license_tracker/ref", "/".join(parts[:])).with_suffix(".md")

    if parts[-1] == "__init__":
        continue
    elif parts[-1] == "__main__":
        continue

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        identifier = ".".join(parts)
        print("::: " + identifier, file=fd)

    mkdocs_gen_files.set_edit_path(full_doc_path, path)
