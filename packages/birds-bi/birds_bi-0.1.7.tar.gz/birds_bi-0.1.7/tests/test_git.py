"""Tests for birds_bi.git module - Git integration for change detection."""

from pathlib import Path

from birds_bi.git import Change, Changes, get_changes_from_file
from birds_bi.repo import Repository


class TestGitModels:
    """Test Git module data models."""

    def test_change_dataclass_structure(self) -> None:
        """Test Change model structure."""
        # Test that Change dataclass exists and has expected attributes
        from dataclasses import fields

        change_fields = {f.name for f in fields(Change)}
        assert "deploy_action" in change_fields
        assert "component" in change_fields

    def test_changes_dataclass_structure(self) -> None:
        """Test Changes model structure."""
        from dataclasses import fields

        changes_fields = {f.name for f in fields(Changes)}
        assert "deploy_dwh" in changes_fields
        assert "deploy_tabular" in changes_fields
        assert "components" in changes_fields

    def test_changes_empty(self) -> None:
        """Test Changes with no components."""
        changes = Changes(deploy_dwh=False, deploy_tabular=False, components=[])

        assert changes.deploy_dwh is False
        assert changes.deploy_tabular is False
        assert len(changes.components) == 0


class TestGetChangesFromFile:
    """Test get_changes_from_file functionality."""

    def test_get_changes_empty_file(self, temp_repo_path: Path) -> None:
        """Test parsing empty changes file."""
        # Create repository structure
        content_path = temp_repo_path / "content"
        content_path.mkdir(parents=True)

        # Create empty changes file
        changes_file = temp_repo_path / "changed_files.txt"
        changes_file.write_text("")

        repo = Repository(temp_repo_path)
        changes = get_changes_from_file(repo, changes_file)

        assert isinstance(changes, Changes)
        assert changes.deploy_dwh is False
        assert changes.deploy_tabular is False
        assert len(changes.components) == 0

    def test_get_changes_non_content_files(self, temp_repo_path: Path) -> None:
        """Test parsing changes file with non-content changes."""
        # Create repository structure
        content_path = temp_repo_path / "content"
        content_path.mkdir(parents=True)

        # Create changes file with non-content paths
        changes_file = temp_repo_path / "changed_files.txt"
        changes_file.write_text("README.md\\ndocs/guide.md\\n.gitignore\\n")

        repo = Repository(temp_repo_path)
        changes = get_changes_from_file(repo, changes_file)

        assert isinstance(changes, Changes)
        assert changes.deploy_dwh is False
        assert len(changes.components) == 0

    def test_get_changes_tabular_modifications(self, temp_repo_path: Path) -> None:
        """Test parsing changes with tabular directory modifications."""
        # Create repository structure
        tabular_path = temp_repo_path / "tabular"
        tabular_path.mkdir(parents=True)

        # Create changes file with tabular modifications
        changes_file = temp_repo_path / "changed_files.txt"
        changes_file.write_text("tabular/model.bim\\ntabular/database.json\\n")

        repo = Repository(temp_repo_path)
        changes = get_changes_from_file(repo, changes_file)

        assert isinstance(changes, Changes)
        assert changes.deploy_tabular is True

    def test_get_changes_readme_ignored(self, temp_repo_path: Path) -> None:
        """Test that README.md files are ignored in content."""
        # Create repository structure
        content_path = temp_repo_path / "content"
        dim_path = content_path / "dim"
        dim_path.mkdir(parents=True)

        # Create changes file with README modifications
        changes_file = temp_repo_path / "changed_files.txt"
        changes_file.write_text("content/dim/README.md\ncontent/fact/README.md\n")

        repo = Repository(temp_repo_path)
        changes = get_changes_from_file(repo, changes_file)

        # README files should not trigger component deployments
        assert len(changes.components) == 0

    def test_get_changes_from_path_object(self, temp_repo_path: Path) -> None:
        """Test get_changes_from_file accepts Path object."""
        content_path = temp_repo_path / "content"
        content_path.mkdir(parents=True)

        changes_file = temp_repo_path / "changes.txt"
        changes_file.write_text("")

        repo = Repository(temp_repo_path)

        # Should work with Path object
        changes = get_changes_from_file(repo, changes_file)
        assert isinstance(changes, Changes)

        # Should also work with string
        changes = get_changes_from_file(repo, str(changes_file))
        assert isinstance(changes, Changes)
