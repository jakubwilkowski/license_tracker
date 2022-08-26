from unittest.mock import MagicMock, patch

from rich.table import Table

from license_tracker.exporters import ConsoleExporter, FileExporter
from license_tracker.models import Dependency


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
        assert len(table.rows) == len(dependency.as_dict().keys())


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
            dependency.as_dict().keys()
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
            == len(dependency.as_dict().keys()) - 1
        )
        assert mock_open.return_value.__enter__.return_value.writelines.call_count == 1
