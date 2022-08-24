import pytest

from license_tracker.models import Dependency


class TestDependency:
    def test_dependecy_str(self):
        dep = Dependency(
            "dep_name",
            "1.2.3",
            "mit",
            "interesting project",
            "http://example.org",
        )

        assert str(dep) == "dep_name (1.2.3)"

    @pytest.mark.parametrize(
        "value, expected_result",
        (
            ("packaging==21.3", ("packaging", "21.3")),
            (" packaging==21.3 ", ("packaging", "21.3")),
            ("packaging  ==21.3", ("packaging", "21.3")),
            ("packaging==   21.3", ("packaging", "21.3")),
            ("packaging", ("packaging", None)),
        ),
    )
    def test_parse_string_splits_name_and_version(self, value, expected_result):
        assert expected_result == Dependency.parse_string(value)

    def test_as_dict_returns_right_keys(self, dependency):
        assert "Name" in dependency.as_dict()
        assert "Version" in dependency.as_dict()
        assert "Summary" in dependency.as_dict()
        assert "Project URL" in dependency.as_dict()
        assert "License Name" in dependency.as_dict()
        assert "License filename (1)" in dependency.as_dict()
        assert "License download URLs (1)" in dependency.as_dict()
        assert "License raw contents (1)" in dependency.as_dict()
        assert "License sha (1)" in dependency.as_dict()
