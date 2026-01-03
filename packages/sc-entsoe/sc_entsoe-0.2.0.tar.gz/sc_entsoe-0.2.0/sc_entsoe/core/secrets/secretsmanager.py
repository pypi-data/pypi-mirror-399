"""AWS Secrets Manager-based secret getter."""

import json

import boto3
from botocore.exceptions import ClientError

from .secrets import SecretGetter


class SecretsManagerSecret(SecretGetter):
    """Secret getter that reads from AWS Secrets Manager."""

    def __init__(self, region_name: str | None = None):
        """
        Initialize Secrets Manager client.

        Args:
            region_name: AWS region name (defaults to AWS_REGION env var or default region)
        """
        self.client = boto3.client("secretsmanager", region_name=region_name)

    async def get_secrets(self, secret_ref: str | None = None) -> dict[str, str]:
        """
        Get secrets from AWS Secrets Manager.

        Args:
            secret_ref: Name or ARN of the secret in Secrets Manager

        Returns:
            Dictionary of secret key-value pairs

        Raises:
            ValueError: If secret_ref is None or empty, or if secret doesn't contain a string value
            ClientError: If AWS API call fails
        """
        if not secret_ref:
            return {}

        try:
            response = self.client.get_secret_value(SecretId=secret_ref)
        except ClientError as e:
            raise ValueError(f"failed to get secret from Secrets Manager: {e}") from e

        if "SecretString" not in response or not response["SecretString"]:
            raise ValueError("secret does not contain a string value")

        try:
            secrets = json.loads(response["SecretString"])
            if not isinstance(secrets, dict):
                raise ValueError("secret JSON is not a dictionary")
            return {str(k): str(v) for k, v in secrets.items()}
        except json.JSONDecodeError as e:
            raise ValueError(f"failed to parse secret JSON: {e}") from e
