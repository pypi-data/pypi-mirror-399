# Xenfra Python SDK

The official, open-source Python SDK for interacting with the Xenfra API.

This SDK provides a simple and Pythonic interface for developers and AI Agents to programmatically manage infrastructure, deployments, and other platform resources.

## Installation

```bash
pip install xenfra-sdk
```

## Basic Usage

Initialize the client with your API token (or ensure the `XENFRA_TOKEN` environment variable is set).

```python
import os
from xenfra_sdk import XenfraClient
from xenfra_sdk.exceptions import XenfraAPIError

client = XenfraClient(token=os.getenv("XENFRA_TOKEN"))

try:
    projects = client.projects.list()
    for p in projects:
        print(f"Found project: {p.name} (Status: {p.status})")
except XenfraAPIError as e:
    print(f"API Error: {e.detail}")
```

## Usage for Agentic Workflows

The Xenfra SDK is designed to be used as a "tool" by AI Agents (e.g., OpenAI Assistants). The Pydantic models are compatible with function-calling schemas, allowing an agent to easily call these methods.

Here is a conceptual example of how an agent might use the SDK to fulfill a user's request.

```python
# This is a conceptual representation of an agent's internal logic.
# The agent would be configured with functions that call these SDK methods.

def list_all_projects():
    """Lists all available projects in the Xenfra account."""
    return client.projects.list()

def create_new_deployment(project_name: str, git_repo: str, branch: str = "main"):
    """
    Creates a new deployment for a project.
    
    Args:
        project_name: The name for the new deployment.
        git_repo: The URL of the git repository to deploy.
        branch: The branch to deploy (defaults to 'main').
    """
    return client.deployments.create(
        project_name=project_name,
        git_repo=git_repo,
        branch=branch,
        framework="fastapi" # Framework detection would be part of a more complex agent
    )

# --- Agent Execution Flow ---

# User prompt: "Deploy my new app from github.com/user/my-app"

# 1. Agent decides which tool to use: `create_new_deployment`
# 2. Agent extracts parameters:
#    - project_name = "my-app" (inferred)
#    - git_repo = "https://github.com/user/my-app"
# 3. Agent calls the tool:
#    create_new_deployment(
#        project_name="my-app",
#        git_repo="https://github.com/user/my-app"
#    )
```

## Error Handling

The SDK uses custom exceptions for clear error handling. All API-related errors will raise a `XenfraAPIError`, which contains the `status_code` and a `detail` message from the API response.

```python
from xenfra_sdk.exceptions import XenfraAPIError, AuthenticationError

try:
    # Make an API call
    ...
except AuthenticationError as e:
    print("Authentication failed. Please check your token.")
except XenfraAPIError as e:
    print(f"An API error occurred with status {e.status_code}: {e.detail}")
```
