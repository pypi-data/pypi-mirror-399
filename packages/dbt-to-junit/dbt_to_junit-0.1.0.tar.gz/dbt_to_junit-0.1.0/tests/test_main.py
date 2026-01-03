"""Tests for main module."""

import pytest

from src.main import main


def test_main(capsys):
    """Test main function."""
    main()
    captured = capsys.readouterr()
    assert "Hello from dbt-junit-xml!" in captured.out
