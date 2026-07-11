#!/usr/bin/env python3

"""Application catalogue loader for HamRadio-Pi Ultimate."""

import json
from pathlib import Path
from typing import Any


class CatalogueError(Exception):
    """Raised when the application catalogue cannot be loaded."""


class ApplicationCatalogue:
    """Loads and provides access to the application catalogue."""

    def __init__(self, catalogue_path: Path | None = None) -> None:
        if catalogue_path is None:
            catalogue_path = (
                Path(__file__).resolve().parent.parent
                / "data"
                / "applications.json"
            )

        self.catalogue_path = catalogue_path
        self.applications: list[dict[str, Any]] = []

    def load(self) -> None:
        """Load applications from the JSON catalogue."""

        if not self.catalogue_path.exists():
            raise CatalogueError(
                f"Catalogue file was not found:\n{self.catalogue_path}"
            )

        try:
            with self.catalogue_path.open(
                "r",
                encoding="utf-8",
            ) as catalogue_file:
                data = json.load(catalogue_file)

        except json.JSONDecodeError as error:
            raise CatalogueError(
                f"The catalogue contains invalid JSON:\n{error}"
            ) from error

        except OSError as error:
            raise CatalogueError(
                f"The catalogue could not be opened:\n{error}"
            ) from error

        applications = data.get("applications")

        if not isinstance(applications, list):
            raise CatalogueError(
                "The catalogue must contain an 'applications' list."
            )

        self.applications = applications

    def application_count(self) -> int:
        """Return the number of applications in the catalogue."""

        return len(self.applications)

    def categories(self) -> list[str]:
        """Return a sorted list of application categories."""

        return sorted(
            {
                str(application.get("category", "Other"))
                for application in self.applications
            }
        )

    def applications_in_category(
        self,
        category: str,
    ) -> list[dict[str, Any]]:
        """Return applications belonging to a category."""

        return sorted(
            [
                application
                for application in self.applications
                if application.get("category") == category
            ],
            key=lambda application: str(
                application.get("name", "")
            ).lower(),
        )