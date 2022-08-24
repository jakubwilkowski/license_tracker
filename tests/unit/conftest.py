import pytest

from license_tracker.models import Dependency, License


@pytest.fixture
def version() -> str:
    return "1.2.3"


@pytest.fixture
def package_name() -> str:
    return "project"


@pytest.fixture
def license_(package_name: str, version: str) -> License:
    return License(
        "LICENSE.APACHE",
        "Lorem ipsum",
        f"https://raw.githubusercontent.com/org/{package_name}/{version}/LICENSE.APACHE",
        "a25ce5cf7b97b76a64a64e4af0ca43cb7f061aff",
    )


@pytest.fixture
def dependency(package_name: str, version: str, license_: License) -> Dependency:
    return Dependency(
        name=package_name,
        version=version,
        summary="Very cool project",
        project_url="https://github.com/org/project/tree/1.2.3",
        license_name="MIT",
        licenses=[license_],
    )
