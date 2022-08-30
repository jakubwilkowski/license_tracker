from unittest.mock import MagicMock, patch

from rich.table import Table

from license_tracker.exporters import ConsoleExporter, FileExporter, as_dict
from license_tracker.models import Dependency


class TestAsDict:
    def test_as_dict_returns_right_default_keys(self, dependency: Dependency) -> None:
        target_representation = as_dict(dependency)
        assert "Name" in target_representation
        assert "Version" in target_representation
        assert "Summary" in target_representation
        assert "Project URL" in target_representation
        assert "License Name" in target_representation
        assert "License filename (1)" in target_representation
        assert "License download URLs (1)" in target_representation
        assert "License raw contents (1)" in target_representation
        assert "License sha (1)" in target_representation

    def test_as_dict_returns_empty_strings_for_extra_rows(
        self, dependency: Dependency
    ) -> None:
        extra_rows = ["Lorem", "Ipsum", "dolor"]
        target_representation = as_dict(dependency, extra_rows=extra_rows)
        for extra_row in extra_rows:
            assert extra_row in target_representation
            assert target_representation[extra_row] == ""


class TestConsoleExporter:
    @patch("license_tracker.exporters.console.print")
    def test_returns_early_when_no_dependencies(
        self, mocked_console: MagicMock
    ) -> None:
        ConsoleExporter().single(list())
        mocked_console.assert_called_once_with("No dependencies to export")

    @patch("license_tracker.exporters.console.print")
    def test_a_table_is_generated_for_dependency(
        self, mocked_console: MagicMock, dependency: Dependency
    ) -> None:
        ConsoleExporter().single([dependency])
        assert isinstance(mocked_console.call_args[0][0], Table)

    @patch("license_tracker.exporters.console.print")
    def test_dependecy_table_has_needed_properties(
        self, mocked_console: MagicMock, dependency: Dependency
    ) -> None:
        ConsoleExporter().single([dependency])
        table: Table = mocked_console.call_args[0][0]
        assert table.width == 150
        assert table.columns[0].header == "Key"
        assert table.columns[1].header == "Value"
        # expect that we'll add one row per key
        assert len(table.rows) == len(as_dict(dependency).keys())


class TestFileExporter:
    @patch("license_tracker.exporters.console.print")
    def test_returns_early_when_no_dependencies(
        self, mocked_console: MagicMock
    ) -> None:
        FileExporter().single(list())
        mocked_console.assert_called_once_with("No dependencies to export")

    @patch("license_tracker.exporters.os.makedirs")
    @patch("license_tracker.exporters.open")
    def test_single_tries_to_create_output_directory(
        self, _mock_open: MagicMock, mock_makedirs: MagicMock, dependency: Dependency
    ) -> None:
        FileExporter().single([dependency])
        mock_makedirs.assert_called_once_with("output", exist_ok=True)

    @patch("license_tracker.exporters.os.makedirs")
    @patch("license_tracker.exporters.open")
    def test_single_exports_dependency_to_a_file(
        self, mock_open: MagicMock, _mock_makedirs: MagicMock, dependency: Dependency
    ) -> None:
        FileExporter().single([dependency])

        # expect that we'll write one line per key
        assert mock_open.return_value.__enter__.return_value.write.call_count == len(
            as_dict(dependency).keys()
        )
        mock_open.return_value.__enter__.return_value.writelines.assert_not_called()

    @patch("license_tracker.exporters.os.makedirs")
    @patch("license_tracker.exporters.open")
    def test_single_multiline_license_breaks_on_newlines(
        self, mock_open: MagicMock, _mock_makedirs: MagicMock, dependency: Dependency
    ) -> None:
        dependency.licenses[0].raw_content = "\n".join(
            ["Lorem", "Ipsum", "dolor", "sit"]
        )
        FileExporter().single([dependency])

        # expect that we'll write one line per key, minus license key, which uses writelines
        assert (
            mock_open.return_value.__enter__.return_value.write.call_count
            == len(as_dict(dependency).keys()) - 1
        )
        assert mock_open.return_value.__enter__.return_value.writelines.call_count == 1
