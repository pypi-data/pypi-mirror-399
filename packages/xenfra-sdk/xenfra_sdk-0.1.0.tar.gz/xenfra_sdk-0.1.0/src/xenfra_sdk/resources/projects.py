import logging

from ..exceptions import XenfraAPIError, XenfraError  # Add XenfraError
from ..models import ProjectRead
from .base import BaseManager

logger = logging.getLogger(__name__)


class ProjectsManager(BaseManager):
    def list(self) -> list[ProjectRead]:
        """Retrieves a list of all projects."""
        try:
            response = self._client._request("GET", "/projects/")  # Added trailing slash

            logger.debug(
                f"ProjectsManager.list response: status={response.status_code}, "
                f"body={response.text[:200]}..."  # Truncate long responses
            )

            response.raise_for_status()
            return [ProjectRead(**p) for p in response.json()["projects"]]
        except XenfraAPIError:
            raise  # Re-raise API errors
        except Exception as e:
            # Handle other exceptions like JSON parsing errors
            raise XenfraError(f"Failed to list projects: {e}")

    def show(self, project_id: int) -> ProjectRead:
        """Get details for a specific project.

        Args:
            project_id: The unique identifier for the project.

        Returns:
            ProjectRead: The project details.

        Raises:
            XenfraAPIError: If the API returns an error (e.g., 404 not found).
            XenfraError: If there's a network or parsing error.
        """
        try:
            response = self._client._request("GET", f"/projects/{project_id}")
            logger.debug(f"ProjectsManager.show({project_id}) response: {response.status_code}")
            response.raise_for_status()
            return ProjectRead(**response.json())
        except XenfraAPIError:
            raise  # Re-raise API errors
        except Exception as e:
            raise XenfraError(f"Failed to get project {project_id}: {e}")

    def create(
        self,
        name: str,
        region: str = "nyc3",
        size_slug: str = "s-1vcpu-1gb"
    ) -> ProjectRead:
        """Create a new project.

        Args:
            name: The name for the new project.
            region: The DigitalOcean region (default: nyc3).
            size_slug: The droplet size slug (default: s-1vcpu-1gb).

        Returns:
            ProjectRead: The newly created project details.

        Raises:
            XenfraAPIError: If the API returns an error.
            XenfraError: If there's a network or parsing error.
        """
        try:
            payload = {
                "name": name,
                "region": region,
                "size_slug": size_slug
            }
            logger.debug(f"ProjectsManager.create payload: {payload}")
            response = self._client._request("POST", "/projects/", json=payload)
            response.raise_for_status()
            return ProjectRead(**response.json())
        except XenfraAPIError:
            raise
        except Exception as e:
            raise XenfraError(f"Failed to create project '{name}': {e}")

    def delete(self, project_id: str) -> None:
        """Deletes a project."""
        try:
            response = self._client._request("DELETE", f"/projects/{project_id}")
            response.raise_for_status()
        except XenfraAPIError:
            raise
        except Exception as e:
            raise XenfraError(f"Failed to delete project {project_id}: {e}")
