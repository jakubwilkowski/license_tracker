import re
from typing import Final, Optional, Union

import httpx
from httpx import URL, HTTPStatusError, Response
from httpx._types import URLTypes

from license_tracker import exceptions, models


class GithubClient:
    def get_licenses(self, project_url: URLTypes, version: str) -> list[models.License]:
        try:
            license_files = self._fetch_license_files(project_url, version)
        except HTTPStatusError:
            raise exceptions.NoLicenseFound(
                "Could not fetch license files", name=None, version=version
            )

        results = []
        for license_file in license_files:
            download_url = license_file["download_url"]
            raw_content = self._fetch_license_content(download_url)
            results.append(
                models.License(
                    str(license_file["name"]),
                    str(raw_content),
                    URL(download_url),
                    str(license_file["sha"]),
                )
            )
        if not results:
            raise exceptions.NoLicenseFound(
                "No licenses found in repo", name=None, version=version
            )
        return results

    @staticmethod
    def _fetch_license_content(url: URLTypes) -> str:
        response = httpx.get(url)
        response.raise_for_status()
        return response.text

    @staticmethod
    def _fetch_license_files(
        project_url: URLTypes, version: str, _failed: bool = False
    ) -> list[dict[str, Union[str, URL]]]:
        url = str(project_url).replace("github.com", "api.github.com/repos")
        response = httpx.get(url + f"contents?ref={version}")
        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            if response.status_code != 404 or _failed:
                raise e
            # Versioning might follow different naming than tags - try to fetch tags in
            # hope of finding something that would resemble version - blame django-guardian
            # TODO: add workaround for psycopg2 which uses 2_9_3 for version 2.9.3...
            res = httpx.get(url + "tags")
            res.raise_for_status()
            for tag_object in res.json():
                if version in tag_object["name"]:
                    return GithubClient._fetch_license_files(
                        project_url, tag_object["name"], _failed=True
                    )
        licenses = [
            file for file in response.json() if "license" in file["name"].lower()
        ]
        return licenses

    def get_versioned_project_url(self, project_url: URLTypes, version: str) -> URL:
        return URL(str(project_url) + f"tree/{version}")


class PypiClient:
    HOST: str = "https://pypi.org/pypi/"
    VALID_PROJECT_URL_KEYS: Final[list[str]] = ["Source", "Homepage"]

    def fetch_dependency_data(
        self, name: str, version: Optional[str] = None
    ) -> models.Dependency:
        url = self._build_url(name, version)
        response = self._call(url)
        content = response.json()["info"]
        if version:
            assert version == content["version"]

        project_url = self._get_project_url(content["project_urls"])
        return models.Dependency(
            name=name,
            version=content["version"],
            summary=content["summary"],
            project_url=GithubClient().get_versioned_project_url(
                project_url, content["version"]
            ),
            license_name=content["license"],
            licenses=GithubClient().get_licenses(project_url, content["version"]),
        )

    @classmethod
    def _build_url(cls, name: str, version: Optional[str] = None) -> str:
        if version:
            return cls.HOST + f"{name}/{version}/json"
        return cls.HOST + f"{name}/json"

    @staticmethod
    def _call(url: str) -> Response:
        response: Response = httpx.get(url)
        response.raise_for_status()
        return response

    @classmethod
    def _get_project_url(cls, project_urls: dict[str, URLTypes]) -> URL:
        pattern = r"(?P<url>http[s]?://github\.com/[-_\w]+/[-_\w]+).*"
        # TODO: add test for django-filter
        for url in project_urls.values():
            if url and (m := re.match(pattern, str(url))):
                return URL(m.groupdict()["url"] + "/")
        raise Exception("Could not find project url")
