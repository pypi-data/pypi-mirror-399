import logging

# Import Deployment model when it's defined in models.py
# from ..models import Deployment
from ..exceptions import XenfraAPIError, XenfraError  # Add XenfraError
from .base import BaseManager

logger = logging.getLogger(__name__)


class DeploymentsManager(BaseManager):
    def create(self, project_name: str, git_repo: str, branch: str, framework: str) -> dict:
        """Creates a new deployment."""
        try:
            payload = {
                "project_name": project_name,
                "git_repo": git_repo,
                "branch": branch,
                "framework": framework,
            }
            response = self._client._request("POST", "/deployments", json=payload)
            response.raise_for_status()
            # Assuming the API returns a dict, which will be parsed into a Deployment model
            return response.json()
        except XenfraAPIError:
            raise
        except Exception as e:
            raise XenfraError(f"Failed to create deployment: {e}")

    def get_status(self, deployment_id: str) -> dict:
        """Get status for a specific deployment.

        Args:
            deployment_id: The unique identifier for the deployment.

        Returns:
            dict: Deployment status information including state, progress, etc.

        Raises:
            XenfraAPIError: If the API returns an error (e.g., 404 not found).
            XenfraError: If there's a network or parsing error.
        """
        try:
            response = self._client._request("GET", f"/deployments/{deployment_id}/status")
            logger.debug(f"DeploymentsManager.get_status({deployment_id}) response: {response.status_code}")
            response.raise_for_status()
            return response.json()
        except XenfraAPIError:
            raise  # Re-raise API errors
        except Exception as e:
            raise XenfraError(f"Failed to get status for deployment {deployment_id}: {e}")

    def get_logs(self, deployment_id: str) -> str:
        """Get logs for a specific deployment.

        Args:
            deployment_id: The unique identifier for the deployment.

        Returns:
            str: The deployment logs as plain text.

        Raises:
            XenfraAPIError: If the API returns an error (e.g., 404 not found).
            XenfraError: If there's a network or parsing error.
        """
        try:
            response = self._client._request("GET", f"/deployments/{deployment_id}/logs")
            logger.debug(f"DeploymentsManager.get_logs({deployment_id}) response: {response.status_code}")
            response.raise_for_status()

            # Parse response - API should return {"logs": "log content"}
            data = response.json()
            logs = data.get("logs", "")

            if not logs:
                logger.warning(f"No logs found for deployment {deployment_id}")

            return logs

        except XenfraAPIError:
            raise  # Re-raise API errors
        except Exception as e:
            raise XenfraError(f"Failed to get logs for deployment {deployment_id}: {e}")
