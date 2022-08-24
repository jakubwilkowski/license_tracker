import typer
from rich.progress import track

from license_tracker import exporters, models, services

app = typer.Typer()


@app.command()
def check(
    dependencies: list[str],
    show: bool = typer.Option(False, help=""),
) -> None:
    """
    Check licenses of one or more packages
    """
    processed_items = []
    for item in track(dependencies, description="Processing..."):
        name, version = models.Dependency.parse_string(item)
        analyzer = services.DependencyAnalyzer(name, version)
        dependency = analyzer()
        if dependency:
            processed_items.append(dependency)
    if show:
        exporters.AsTable.export_single(processed_items)


if __name__ == "__main__":
    app()
