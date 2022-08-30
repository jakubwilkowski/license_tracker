from typing import Optional, Tuple

import pytest

from license_tracker.models import Dependency


class TestDependency:
    def test_dependecy_str(self) -> None:
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
    def test_parse_string_splits_name_and_version(
        self, value: str, expected_result: Tuple[str, Optional[str]]
    ) -> None:
        assert expected_result == Dependency.parse_string(value)
