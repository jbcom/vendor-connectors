"""Cloud Connectors - Universal cloud provider clients with transparent secret management."""

__version__ = "0.1.0"

from .aws import AWSConnector
from .github import GithubConnector
from .google import GoogleConnector
from .slack import SlackConnector
from .vault import VaultConnector
from .zoom import ZoomConnector

__all__ = [
    "AWSConnector",
    "GithubConnector", 
    "GoogleConnector",
    "SlackConnector",
    "VaultConnector",
    "ZoomConnector",
]
