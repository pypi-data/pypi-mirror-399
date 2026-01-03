"""
Tabular model deployment via Tabular Editor CLI.

This module provides functionality to deploy Tabular Editor 'Save to Folder'
models to SSAS, AAS, or Power BI Premium/Fabric using Tabular Editor CLI.
"""

from __future__ import annotations

import re
import subprocess
from collections.abc import Sequence
from pathlib import Path

from .connection import Connection, redact_secrets


class TabularDeploymentError(RuntimeError):
    """Raised when Tabular Editor deployment fails."""


def _ensure_te_folder_model(model_folder: Path) -> None:
    """Validate that model folder contains required database.json file."""
    if not (model_folder / "database.json").exists():
        raise FileNotFoundError(
            f"Model folder must contain database.json (Tabular Editor 'Save to Folder' format): {model_folder}"
        )


def _te_version(te_exe: Path) -> tuple[int, int, int]:
    """
    Extract Tabular Editor version from `TabularEditor.exe /?` output.

    Args:
        te_exe: Path to TabularEditor.exe

    Returns:
        Version tuple (major, minor, patch)
    """
    r = subprocess.run([str(te_exe), "/?"], text=True, capture_output=True)
    txt = (r.stdout or "") + "\n" + (r.stderr or "")
    m = re.search(r"Tabular Editor\s+(\d+)\.(\d+)\.(\d+)", txt)
    if not m:
        return (0, 0, 0)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def deploy_tabular_model(
    *,
    tabular_editor_exe: str | Path,
    model_folder: str | Path,
    connection: Connection | str,
    database: str,
    overwrite: bool = True,
    # Selective deploy controls:
    deploy_connections: bool = False,  # -C
    deploy_partitions: bool = True,  # -P
    deploy_shared_expressions: bool = False,  # -S (deploy flag, TE >= 2.27.0)
    deploy_roles: bool = False,  # -R
    deploy_role_members: bool = False,  # -M (only meaningful with -R)
    # Other flags:
    skip_incremental_policy_partitions: bool = False,  # -P -Y
    warn_unprocessed: bool = False,  # -W
    fail_on_dax_errors: bool = False,  # -E
    extra_flags: Sequence[str] | None = None,
) -> None:
    """
    Deploy a Tabular Editor folder model using TE2 CLI.

    Args:
        tabular_editor_exe: Path to TabularEditor.exe
        model_folder: Path to Tabular Editor 'Save to Folder' model
        connection: Connection object or connection string
        database: Target database name
        overwrite: Allow overwriting existing database
        deploy_connections: Deploy data source connections (-C)
        deploy_partitions: Deploy partitions (-P)
        deploy_shared_expressions: Deploy shared expressions (-S, TE >= 2.27.0)
        deploy_roles: Deploy roles (-R)
        deploy_role_members: Deploy role members (-M, requires deploy_roles)
        skip_incremental_policy_partitions: Skip incremental policy partitions (-Y)
        warn_unprocessed: Warn on unprocessed objects (-W)
        fail_on_dax_errors: Fail on DAX errors (-E)
        extra_flags: Additional CLI flags

    Raises:
        FileNotFoundError: If TabularEditor.exe or model folder not found
        TabularDeploymentError: If deployment fails

    Note:
        Defaults align with common CI/CD practices:
        - Do NOT deploy connections/data sources
        - Do NOT deploy roles or role members
        - DO deploy partitions
    """
    te = Path(tabular_editor_exe)
    if not te.exists():
        raise FileNotFoundError(f"TabularEditor.exe not found: {te}")

    folder = Path(model_folder)
    _ensure_te_folder_model(folder)

    te_ver = _te_version(te)

    data_source = (
        connection.to_deploy_connection_string()
        if isinstance(connection, Connection)
        else str(connection).strip()
    )

    cmd: list[str] = [str(te), str(folder), "-D", data_source, database]

    if overwrite:
        cmd.append("-O")

    # Deploy connections/data sources (optional)
    if deploy_connections:
        cmd.append("-C")

    # Deploy partitions (optional)
    if deploy_partitions:
        cmd.append("-P")
        if skip_incremental_policy_partitions:
            cmd.append("-Y")

    # Deploy shared expressions (TE >= 2.27.0 deploy flag)
    if deploy_shared_expressions:
        if te_ver >= (2, 27, 0):
            cmd.append("-S")
        else:
            # TE < 2.27.0 does not have deploy -S; ignoring is safer than breaking the CLI.
            pass

    # Deploy roles / members (optional)
    if deploy_roles:
        cmd.append("-R")
        if deploy_role_members:
            cmd.append("-M")
    # If deploy_roles is False, we intentionally do nothing even if deploy_role_members is True.

    if warn_unprocessed:
        cmd.append("-W")
    if fail_on_dax_errors:
        cmd.append("-E")
    if extra_flags:
        cmd.extend(extra_flags)

    result = subprocess.run(cmd, text=True, capture_output=True)

    if result.returncode != 0:
        # Get secrets for redaction
        secrets = connection.get_secrets() if isinstance(connection, Connection) else []
        safe_cmd = " ".join(redact_secrets(p, secrets) for p in cmd)
        raise TabularDeploymentError(
            "Tabular deployment failed\n"
            f"Return code: {result.returncode}\n"
            f"Command: {safe_cmd}\n"
            f"STDOUT:\n{redact_secrets(result.stdout, secrets)}\n"
            f"STDERR:\n{redact_secrets(result.stderr, secrets)}"
        )
