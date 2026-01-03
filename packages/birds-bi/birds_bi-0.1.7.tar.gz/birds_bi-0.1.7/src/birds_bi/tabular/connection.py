"""
Tabular connection configuration and utilities.

This module provides a unified connection abstraction for both deployment
and processing of tabular models (SSAS, AAS, Power BI).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AuthMethod(Enum):
    """Authentication methods for tabular connections."""

    WINDOWS = "windows"
    INTERACTIVE = "interactive"
    SERVICE_PRINCIPAL = "service_principal"


@dataclass(frozen=True, slots=True)
class Connection:
    """
    Unified connection configuration for tabular models.

    Supports multiple authentication methods:
    - Windows Integrated (SSAS on-prem)
    - Interactive AAD (local development)
    - Service Principal (CI/CD automation)

    Attributes:
        endpoint: Server endpoint URL or connection string
        auth: Authentication method to use
        tenant_id: Azure AD tenant ID (required for service principal)
        client_id: Application/client ID (required for service principal)
        client_secret: Application secret (required for service principal)
        provider: MSOLAP provider version
    """

    endpoint: str
    auth: AuthMethod = AuthMethod.INTERACTIVE

    # Service principal credentials
    tenant_id: str | None = None
    client_id: str | None = None
    client_secret: str | None = None

    # Connection settings
    provider: str = "MSOLAP.8"

    def to_deploy_connection_string(self) -> str:
        """
        Build connection string for Tabular Editor deployment.

        Returns:
            Connection string suitable for Tabular Editor CLI

        Raises:
            ValueError: If required credentials are missing
        """
        endpoint = self.endpoint.strip()

        match self.auth:
            case AuthMethod.WINDOWS | AuthMethod.INTERACTIVE:
                return endpoint

            case AuthMethod.SERVICE_PRINCIPAL:
                self._validate_service_principal()
                return (
                    f"Provider={self.provider};"
                    f"Data Source={endpoint};"
                    f"User ID=app:{self.client_id}@{self.tenant_id};"
                    f"Password={self.client_secret};"
                )

        raise ValueError(f"Unsupported auth method: {self.auth}")

    def to_process_connection_string(self) -> str:
        """
        Build connection string for ADOMD.NET processing.

        Returns:
            Connection string suitable for ADOMD.NET

        Raises:
            ValueError: If required credentials are missing
        """
        match self.auth:
            case AuthMethod.WINDOWS:
                return (
                    f"Provider={self.provider};"
                    f"Data Source={self.endpoint};"
                    "Integrated Security=SSPI;"
                )

            case AuthMethod.INTERACTIVE:
                # MSOLAP may prompt for sign-in
                return f"Provider={self.provider};" f"Data Source={self.endpoint};"

            case AuthMethod.SERVICE_PRINCIPAL:
                self._validate_service_principal()
                return (
                    f"Provider={self.provider};"
                    f"Data Source={self.endpoint};"
                    f"User ID=app:{self.client_id}@{self.tenant_id};"
                    f"Password={self.client_secret};"
                    "Persist Security Info=True;"
                )

        raise ValueError(f"Unsupported auth method: {self.auth}")

    def _validate_service_principal(self) -> None:
        """Validate service principal credentials are present."""
        if not self.tenant_id:
            raise ValueError("tenant_id is required for service principal auth")
        if not self.client_id:
            raise ValueError("client_id is required for service principal auth")
        if not self.client_secret:
            raise ValueError("client_secret is required for service principal auth")

    def get_secrets(self) -> list[str]:
        """
        Get list of secret values for redaction.

        Returns:
            List of secret strings that should be redacted from logs
        """
        secrets = []
        if self.client_secret:
            secrets.append(self.client_secret)
        return secrets


# Convenience factory functions
def ssas_windows(endpoint: str) -> Connection:
    """
    Create connection for on-premises SSAS with Windows authentication.

    Args:
        endpoint: SSAS server endpoint

    Returns:
        Connection configured for Windows auth
    """
    return Connection(endpoint=endpoint, auth=AuthMethod.WINDOWS)


def aas_interactive(endpoint: str) -> Connection:
    """
    Create connection for Azure Analysis Services with interactive auth.

    Args:
        endpoint: AAS server endpoint

    Returns:
        Connection configured for interactive auth
    """
    return Connection(endpoint=endpoint, auth=AuthMethod.INTERACTIVE)


def pbi_interactive(endpoint: str) -> Connection:
    """
    Create connection for Power BI XMLA with interactive auth.

    Args:
        endpoint: Power BI XMLA endpoint

    Returns:
        Connection configured for interactive auth
    """
    return Connection(endpoint=endpoint, auth=AuthMethod.INTERACTIVE)


def aas_service_principal(
    endpoint: str,
    *,
    tenant_id: str,
    client_id: str,
    client_secret: str,
) -> Connection:
    """
    Create connection for Azure Analysis Services with service principal.

    Args:
        endpoint: AAS server endpoint
        tenant_id: Azure AD tenant ID
        client_id: Application/client ID
        client_secret: Application secret

    Returns:
        Connection configured for service principal auth
    """
    return Connection(
        endpoint=endpoint,
        auth=AuthMethod.SERVICE_PRINCIPAL,
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
    )


def pbi_service_principal(
    endpoint: str,
    *,
    tenant_id: str,
    client_id: str,
    client_secret: str,
) -> Connection:
    """
    Create connection for Power BI XMLA with service principal.

    Args:
        endpoint: Power BI XMLA endpoint
        tenant_id: Azure AD tenant ID
        client_id: Application/client ID
        client_secret: Application secret

    Returns:
        Connection configured for service principal auth
    """
    return Connection(
        endpoint=endpoint,
        auth=AuthMethod.SERVICE_PRINCIPAL,
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
    )


def redact_secrets(text: str, secrets: list[str] | None = None) -> str:
    """
    Redact secrets from text for safe logging.

    Args:
        text: Text that may contain secrets
        secrets: List of secret values to redact

    Returns:
        Text with secrets replaced by '***REDACTED***'
    """
    import re

    if not text:
        return text

    redacted = text

    # Redact specific secrets
    if secrets:
        for secret in secrets:
            if secret:
                redacted = redacted.replace(secret, "***REDACTED***")

    # Redact password fields
    redacted = re.sub(
        r"(?i)(Password\s*=\s*)[^;]+",
        r"\1***REDACTED***",
        redacted,
    )

    return redacted
