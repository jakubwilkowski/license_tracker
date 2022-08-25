from typing import Union
from unittest.mock import MagicMock, patch

import pytest
from httpx import HTTPStatusError, Response
from httpx._types import URLTypes

from license_tracker import exceptions
from license_tracker.models import Dependency, License
from license_tracker.providers import GithubClient, PypiClient, httpx


@pytest.fixture
def pypi_real_project_urls() -> dict[str, URLTypes]:
    """
    Example project urls of Django from pypi
    """

    return {
        "Documentation": "https://docs.djangoproject.com/",
        "Funding": "https://www.djangoproject.com/fundraising/",
        "Homepage": "https://www.djangoproject.com/",
        "Release notes": "https://docs.djangoproject.com/en/stable/releases/",
        "Source": "https://github.com/django/django/",
        "Tracker": "https://code.djangoproject.com/",
    }


@pytest.fixture
def pypi_real_response(
    pypi_real_project_urls: dict[str, URLTypes]
) -> dict[str, dict[str, dict[str, URLTypes]]]:
    return {"info": {"project_urls": pypi_real_project_urls}}


@pytest.fixture
def github_repo_url() -> str:
    return "https://github.com/org/project/"


PypiResponseType = dict[str, dict[str, Union[str, dict[str, URLTypes]]]]


@pytest.fixture
def pypi_response() -> PypiResponseType:
    return {"info": {"project_urls": {"Source": "https://github.com/org/project/"}}}


class TestGithubClient:
    @patch.object(httpx, "get")
    def test__fetch_license_content_returns_text_of_the_license(
        self, patched_get: MagicMock
    ) -> None:
        mock_response = Response(
            status_code=200, text="Lorem ipsum", request=MagicMock()
        )
        patched_get.return_value = mock_response

        response = GithubClient._fetch_license_content(
            "https://raw.githubusercontent.com/org/project/main/LICENSE.BSD"
        )

        assert response == "Lorem ipsum"

    @patch.object(httpx, "get")
    def test__fetch_license_files_returns_license_files(
        self, patched_get: MagicMock, github_repo_url: str, version: str
    ) -> None:
        """
        Good examples of multiple license files can be found in django and packaging repo:
        https://github.com/django/django or https://github.com/pypa/packaging/
        """

        unexpected_filenames = [
            ".gitignore",
            "setup.py",
            ".editorconfig",
        ]
        expected_filenames = [
            "LICENSE",
            "LICENSE.python",
            "LICENSE.APACHE",
            "LICENSE.BSD",
        ]
        fake_contents = [
            {"name": filename} for filename in unexpected_filenames + expected_filenames
        ]
        mock_response = Response(
            status_code=200, request=MagicMock(), json=fake_contents
        )
        patched_get.return_value = mock_response

        response = GithubClient._fetch_license_files(github_repo_url, version=version)

        patched_get.assert_called_once_with(
            "https://api.github.com/repos/org/project/contents?ref=1.2.3"
        )
        for file in response:
            assert file["name"] in expected_filenames
            assert file["name"] not in unexpected_filenames

    @patch.object(httpx, "get")
    def test__fetch_license_files_raises_on_second_404(
        self, patched_get: MagicMock, github_repo_url: str, version: str
    ) -> None:
        mock_response = Response(status_code=404, request=MagicMock(), json={})
        patched_get.return_value = mock_response

        with pytest.raises(HTTPStatusError):
            GithubClient._fetch_license_files(
                github_repo_url, version=version, _failed=True
            )

    @pytest.mark.parametrize("status_code", [400, 401, 429, 500, 502])
    @patch.object(httpx, "get")
    def test__fetch_license_files_raises_on_most_4xx_5xx(
        self,
        patched_get: MagicMock,
        status_code: int,
        github_repo_url: str,
        version: str,
    ) -> None:
        mock_response = Response(status_code=status_code, request=MagicMock(), json={})
        patched_get.return_value = mock_response

        with pytest.raises(HTTPStatusError):
            GithubClient._fetch_license_files(github_repo_url, version=version)

    @patch.object(GithubClient, "_fetch_license_files")
    @patch.object(GithubClient, "_fetch_license_content")
    def test_get_licenses_returns_expected_license_files(
        self,
        mock_fetch_content: MagicMock,
        mock_fetch_files: MagicMock,
        github_repo_url: str,
        version: str,
        license_: License,
    ) -> None:
        mock_fetch_files.return_value = [
            {
                "name": filename,
                "download_url": f"https://raw.githubusercontent.com/org/project/{version}/{filename}",
                "sha": sha,
            }
            for filename, sha in zip(
                [
                    license_.filename,
                    "LICENSE.BSD",
                ],
                [
                    license_.sha,
                    "5f4f225dd282aa7e4361ec3c2750bbbaaed8ab1f",
                ],
            )
        ]
        mock_fetch_content.side_effect = ["Lorem ipsum", "dolor sit amet"]

        result = GithubClient().get_licenses(github_repo_url, version)

        expected_result = [
            license_,
            License(
                "LICENSE.BSD",
                "dolor sit amet",
                f"https://raw.githubusercontent.com/org/project/1.2.3/LICENSE.BSD",
                "5f4f225dd282aa7e4361ec3c2750bbbaaed8ab1f",
            ),
        ]
        assert sorted(result, key=lambda x: x.sha) == sorted(
            expected_result, key=lambda x: x.sha
        )

    @patch.object(GithubClient, "_fetch_license_files")
    def test_get_licenses_raises_when_there_are_no_licenses(
        self, mock_fetch_files: MagicMock, github_repo_url: str, version: str
    ) -> None:
        mock_fetch_files.return_value = []
        with pytest.raises(exceptions.NoLicenseFound):
            GithubClient().get_licenses(project_url=github_repo_url, version=version)

    @patch.object(GithubClient, "_fetch_license_files")
    def test_get_licenses_raises_when_there_github_is_not_available(
        self, mock_fetch_files: MagicMock, github_repo_url: str, version: str
    ) -> None:
        mock_fetch_files.side_effect = HTTPStatusError(
            "error", request=MagicMock(), response=MagicMock()
        )
        with pytest.raises(exceptions.NoLicenseFound):
            GithubClient().get_licenses(project_url=github_repo_url, version=version)

    def test_get_versioned_project_url(
        self, github_repo_url: str, version: str
    ) -> None:
        assert (
            GithubClient().get_versioned_project_url(github_repo_url, version)
            == "https://github.com/org/project/tree/1.2.3"
        )


class TestPypiClient:
    def test__build_url_calls_versioned_api_if_possible(self, version: str) -> None:
        assert f"{PypiClient.HOST}test/json" == PypiClient._build_url("test", None)
        assert f"{PypiClient.HOST}test/{version}/json" == PypiClient._build_url(
            "test", version
        )

    @patch.object(httpx, "get")
    def test__call_calls_given_url(self, patched_get: MagicMock) -> None:
        mock_response = Response(status_code=200, request=MagicMock())
        patched_get.return_value = mock_response

        result = PypiClient._call("https://example.org")

        assert result == mock_response
        patched_get.assert_called_once_with("https://example.org")

    def test__get_project_url_finds_github_urls(
        self, pypi_real_project_urls: dict[str, URLTypes]
    ) -> None:
        assert (
            PypiClient._get_project_url(pypi_real_project_urls)
            == "https://github.com/django/django/"
        )

    def test__get_project_raises_if_github_url_not_in_desired_keys(
        self, pypi_real_project_urls: dict[str, URLTypes]
    ) -> None:
        pypi_real_project_urls.pop("Source")

        with pytest.raises(Exception) as excinfo:
            PypiClient._get_project_url(pypi_real_project_urls)
        assert str(excinfo.value) == "Could not find project url"

    @patch.object(PypiClient, "_call")
    @patch.object(GithubClient, "get_licenses")
    def test_fetch_dependency_data_returns_expected_versioned_dependency(
        self,
        mock_github_licenses: MagicMock,
        mock_call: MagicMock,
        pypi_response: PypiResponseType,
        license_: License,
        version: str,
    ) -> None:
        pypi_response["info"]["version"] = version
        pypi_response["info"]["summary"] = "Very cool project"
        pypi_response["info"]["license"] = "MIT"
        mock_call.return_value = Response(status_code=200, json=pypi_response)
        mock_github_licenses.return_value = [license_]
        expected = Dependency(
            name="project",
            version=str(version),
            summary="Very cool project",
            project_url="https://github.com/org/project/tree/1.2.3",
            license_name="MIT",
            licenses=[license_],
        )

        assert expected == PypiClient().fetch_dependency_data("project", "1.2.3")
