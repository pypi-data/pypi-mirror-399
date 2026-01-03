"""Clone a SQL Server database to a new database on the same server."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from .models import DbConfig
from .sql_execution import db_connection

__all__ = ["clone_database"]


def clone_database(
    config: DbConfig,
    target_db: str,
    backup_path: Path,
    data_path: Path,
    log_path: Path,
    *,
    overwrite: bool = False,
) -> None:
    """Clone a SQL Server database using backup and restore.

    Creates a backup of the source database, then restores it as the target
    database with new file locations.

    Args:
        config: Database configuration for the source database.
        target_db: Name of the new target database.
        backup_path: Directory where the backup file will be created.
        data_path: Directory where the target database data file will be placed.
        log_path: Directory where the target database log file will be placed.
        overwrite: If True, drop the target database if it already exists.

    Raises:
        ValueError: If parameters are invalid.
        RuntimeError: If the database operation fails.
    """
    source_db = config.database

    if not source_db or not target_db:
        msg = "Source and target database names must be non-empty."
        raise ValueError(msg)

    if source_db == target_db:
        msg = "Source and target database names must be different."
        raise ValueError(msg)

    # Use master database for administrative operations
    cfg = replace(config, database="master")

    backup_file = backup_path / f"{source_db}_clone.bak"
    data_file = data_path / f"{target_db}.mdf"
    log_file = log_path / f"{target_db}_log.ldf"

    with db_connection(cfg) as conn:
        cursor = conn.cursor()

        # Step 1: Drop target database if overwrite is True
        if overwrite:
            cursor.execute(
                f"IF EXISTS (SELECT 1 FROM sys.databases WHERE name = ?) "
                f"DROP DATABASE [{target_db}]",
                (target_db,),
            )
            conn.commit()

        # Step 2: Backup source database
        cursor.execute(
            f"BACKUP DATABASE [{source_db}] TO DISK = ? WITH INIT, FORMAT",
            (str(backup_file),),
        )
        conn.commit()

        # Step 3: Restore as target database with new file locations
        restore_sql = f"""
        RESTORE DATABASE [{target_db}]
        FROM DISK = ?
        WITH
            MOVE ? TO ?,
            MOVE ? TO ?,
            REPLACE
        """

        # Get logical file names from source database
        cursor.execute(
            "SELECT name FROM sys.master_files WHERE database_id = DB_ID(?)",
            (source_db,),
        )
        logical_files = [row[0] for row in cursor.fetchall()]

        if len(logical_files) < 2:
            msg = f"Could not find data and log files for database '{source_db}'."
            raise RuntimeError(msg)

        data_logical = logical_files[0]
        log_logical = logical_files[1]

        cursor.execute(
            restore_sql,
            (
                str(backup_file),
                data_logical,
                str(data_file),
                log_logical,
                str(log_file),
            ),
        )
        conn.commit()
