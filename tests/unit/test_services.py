from unittest.mock import patch

from license_tracker import exceptions
from license_tracker.providers import PypiClient
from license_tracker.services import DependencyAnalyzer


class TestDependencyAnalyzer:
    @patch.object(PypiClient, "fetch_dependency_data")
    def test_dependency_without_a_license_returns_none(
        self, mock_fetch_dependency, package_name, version
    ):
        mock_fetch_dependency.side_effect = exceptions.NoLicenseFound(
            "Error message", name=package_name, version=version
        )
        assert not DependencyAnalyzer(package_name, version)()

    @patch.object(PypiClient, "fetch_dependency_data")
    def test_processed_dependency_gets_returned(
        self,
        mock_fetch_dependency,
        dependency,
    ):
        mock_fetch_dependency.return_value = dependency
        assert DependencyAnalyzer(dependency.name, dependency.version)() == dependency
