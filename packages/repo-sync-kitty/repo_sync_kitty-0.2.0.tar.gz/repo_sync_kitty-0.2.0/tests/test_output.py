"""Tests for output display utilities."""

from repo_sync_kitty.output.display import create_status_table


def test_create_status_table() -> None:
    """Test creating a status table."""
    table = create_status_table()
    assert table.title == "Repository Status"
    # Table should have 4 columns
    assert len(table.columns) == 4
