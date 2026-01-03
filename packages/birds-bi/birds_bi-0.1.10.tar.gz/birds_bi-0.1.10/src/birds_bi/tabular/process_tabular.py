"""
Tabular model processing via TMSL over XMLA.

This module provides functionality to process (refresh) tabular models
on SSAS, AAS, or Power BI Premium/Fabric using ADOMD.NET.

Targets:
    - SSAS Tabular (on-prem)
    - Azure Analysis Services (AAS)
    - Power BI Premium / Fabric semantic models via XMLA endpoints

Requirements:
    - Windows recommended (MSOLAP/ADOMD.NET dependency)
    - pythonnet (pip install pythonnet)
    - ADOMD.NET available on the host (commonly installed with SSMS)

Notes:
    - Processing is executed via ADOMD.NET by sending a TMSL Refresh command
    - This module does NOT implement OAuth flows
    - It relies on MSOLAP/ADOMD.NET behavior for authentication
"""

from __future__ import annotations

import json
from collections.abc import Sequence

from .connection import Connection, redact_secrets


class TabularProcessError(RuntimeError):
    """Raised when processing (TMSL execution) fails."""


def _tmsl_refresh_full(database: str) -> str:
    """
    Generate TMSL command for full database refresh.

    Args:
        database: Database name to refresh

    Returns:
        JSON-encoded TMSL command
    """
    payload = {
        "refresh": {"type": "full", "objects": [{"database": database}]}
    }  # Process Full
    return json.dumps(payload, separators=(",", ":"))


def _load_adomd_assembly() -> None:
    """
    Load the ADOMD.NET assembly, searching multiple common locations.

    Raises:
        TabularProcessError: If ADOMD.NET cannot be found
    """
    import os
    from pathlib import Path

    import clr

    # Try standard reference first (GAC or already loaded)
    try:
        clr.AddReference("Microsoft.AnalysisServices.AdomdClient")
        return
    except Exception:  # noqa: BLE001, S110
        pass

    # Common installation paths for ADOMD.NET (from SSMS or standalone client)
    search_paths = [
        Path(os.environ.get("ProgramFiles", "C:\\Program Files"))
        / "Microsoft.NET"
        / "ADOMD.NET"
        / "160",
        Path(os.environ.get("ProgramFiles", "C:\\Program Files"))
        / "Microsoft.NET"
        / "ADOMD.NET"
        / "150",
        Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"))
        / "Microsoft.NET"
        / "ADOMD.NET"
        / "160",
        Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"))
        / "Microsoft.NET"
        / "ADOMD.NET"
        / "150",
    ]

    for base_path in search_paths:
        dll_path = base_path / "Microsoft.AnalysisServices.AdomdClient.dll"
        if dll_path.exists():
            try:
                clr.AddReference(str(dll_path))
                return
            except Exception:  # noqa: BLE001, S110
                continue

    raise TabularProcessError(
        "Could not load ADOMD.NET (Microsoft.AnalysisServices.AdomdClient). "
        "Install SSMS or the Microsoft Analysis Services client libraries. "
        f"Searched paths: {[str(p) for p in search_paths]}"
    )


def _execute_tmsl(
    conn_str: str,
    tmsl_json: str,
    *,
    secrets_to_redact: Sequence[str] = (),
) -> None:
    """
    Execute a TMSL JSON command over XMLA using ADOMD.NET via pythonnet.

    Args:
        conn_str: MSOLAP connection string
        tmsl_json: JSON-encoded TMSL command
        secrets_to_redact: List of secret values to redact from errors

    Raises:
        TabularProcessError: If ADOMD.NET is unavailable or execution fails
    """
    _load_adomd_assembly()

    from Microsoft.AnalysisServices.AdomdClient import (
        AdomdCommand,
        AdomdConnection,
    )

    try:
        connection = AdomdConnection(conn_str)
        connection.Open()
        try:
            cmd = AdomdCommand(tmsl_json, connection)
            cmd.CommandTimeout = 0  # infinite; manage timeouts at pipeline level
            cmd.ExecuteNonQuery()
        finally:
            connection.Close()
    except Exception as e:  # noqa: BLE001
        msg = redact_secrets(str(e), list(secrets_to_redact))
        raise TabularProcessError(f"TMSL execution failed: {msg}") from e


def process_tabular(
    *,
    connection: Connection | str,
    database: str,
) -> None:
    """
    Process (refresh) a tabular model using TMSL over XMLA.

    Args:
        connection: Connection object or connection string
        database: Target database name to refresh

    Raises:
        TabularProcessError: If processing fails or ADOMD.NET is unavailable

    Note:
        Executes a full refresh (Process Full) on the entire database.
        For more granular processing, use custom TMSL commands.
    """
    conn_str = (
        connection.to_process_connection_string()
        if isinstance(connection, Connection)
        else f"Provider=MSOLAP;Data Source={connection};"
    )
    tmsl = _tmsl_refresh_full(database)

    secrets = []
    if isinstance(connection, Connection):
        secrets = connection.get_secrets()

    _execute_tmsl(conn_str, tmsl, secrets_to_redact=secrets)
