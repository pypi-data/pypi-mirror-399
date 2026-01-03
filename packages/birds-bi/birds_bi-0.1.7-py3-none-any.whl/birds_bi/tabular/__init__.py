"""
Tabular model deployment and processing.

This module provides tools for deploying and processing tabular models
(SSAS, AAS, Power BI Premium/Fabric) using Tabular Editor CLI and ADOMD.NET.
"""

from .connection import (
    AuthMethod,
    Connection,
    aas_interactive,
    aas_service_principal,
    pbi_interactive,
    pbi_service_principal,
    redact_secrets,
    ssas_windows,
)
from .deploy_tabular import TabularDeploymentError, deploy_tabular_model
from .process_tabular import TabularProcessError, process_tabular

__all__ = [
    # Connection types and helpers
    "AuthMethod",
    "Connection",
    "aas_interactive",
    "aas_service_principal",
    "pbi_interactive",
    "pbi_service_principal",
    "redact_secrets",
    "ssas_windows",
    # Deployment
    "TabularDeploymentError",
    "deploy_tabular_model",
    # Processing
    "TabularProcessError",
    "process_tabular",
]
