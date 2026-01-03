"""Tests for datablade.utils module."""

import logging
import pathlib

import pytest

from datablade.utils import (
    configure_logging,
    flatten,
    get_logger,
    log_debug,
    log_error,
    log_info,
    log_warning,
    pathing,
    print_verbose,
    sql_quotename,
)


class TestStrings:
    """Tests for string utility functions."""

    def test_sql_quotename_with_brackets(self):
        """Test SQL name quoting with brackets."""
        result = sql_quotename("table_name")
        assert result == "[table_name]"

    def test_sql_quotename_with_ticks(self):
        """Test SQL name quoting with single quotes."""
        result = sql_quotename("table_name", brackets=False, ticks=True)
        assert result == "'table_name'"

    def test_sql_quotename_removes_existing_brackets(self):
        """Test that existing brackets are removed."""
        result = sql_quotename("[table_name]")
        assert result == "[table_name]"

    def test_sql_quotename_none_raises_error(self):
        """Test that None raises ValueError."""
        with pytest.raises(ValueError, match="name must be provided"):
            sql_quotename(None)

    def test_sql_quotename_empty_string_raises_error(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError, match="name must be a non-empty string"):
            sql_quotename("   ")

    def test_sql_quotename_non_string_raises_error(self):
        """Test that non-string raises TypeError."""
        with pytest.raises(TypeError, match="name must be a string"):
            sql_quotename(123)

    def test_pathing_with_valid_path(self, temp_dir):
        """Test path standardization with valid path."""
        result = pathing(str(temp_dir))
        assert isinstance(result, pathlib.Path)
        assert result.exists()

    def test_pathing_with_pathlib_path(self, temp_dir):
        """Test path standardization with pathlib.Path."""
        result = pathing(temp_dir)
        assert isinstance(result, pathlib.Path)
        assert result == temp_dir

    def test_pathing_with_invalid_path_raises_error(self):
        """Test that invalid path raises ValueError."""
        with pytest.raises(ValueError, match="Path does not exist"):
            pathing("/this/path/does/not/exist")

    def test_pathing_with_none_raises_error(self):
        """Test that None raises ValueError."""
        with pytest.raises(ValueError, match="path input must be provided"):
            pathing(None)

    def test_pathing_with_non_string_or_path_raises_error(self):
        """Test that non-string/non-Path raises TypeError."""
        with pytest.raises(TypeError, match="input must be a string or pathlib.Path"):
            pathing(123)


class TestLists:
    """Tests for list utility functions."""

    def test_flatten_simple_list(self):
        """Test flattening a simple list."""
        result = flatten([1, 2, 3])
        assert result == [1, 2, 3]

    def test_flatten_nested_list(self):
        """Test flattening a nested list."""
        result = flatten([1, [2, 3], [[4], 5]])
        assert result == [1, 2, 3, 4, 5]

    def test_flatten_deeply_nested(self):
        """Test flattening deeply nested lists."""
        result = flatten([1, [2, [3, [4, [5]]]]])
        assert result == [1, 2, 3, 4, 5]

    def test_flatten_empty_list(self):
        """Test flattening an empty list."""
        result = flatten([])
        assert result == []

    def test_flatten_non_list_raises_error(self):
        """Test that non-list raises TypeError."""
        with pytest.raises(TypeError, match="nest must be a list"):
            flatten("not a list")


class TestLogging:
    """Tests for logging utilities."""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a Logger instance."""
        logger = get_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "datablade"

    def test_configure_logging_sets_level(self):
        """Test that configure_logging sets the logging level."""
        logger = configure_logging(level=logging.DEBUG)
        assert isinstance(logger, logging.Logger)
        # At least one handler should have DEBUG level
        assert any(h.level == logging.DEBUG for h in logger.handlers)

    def test_configure_logging_log_file_writes_output(self, temp_dir):
        log_path = temp_dir / "datablade.log"
        logger = configure_logging(level=logging.INFO, log_file=log_path)
        assert log_path.exists()

        log_info("Hello file", verbose=True)
        # Ensure content is flushed
        for h in logger.handlers:
            try:
                h.flush()
            except Exception:
                pass

        content = log_path.read_text(encoding="utf-8")
        assert "Hello file" in content

    def test_configure_logging_format_alias_conflict_raises(self):
        with pytest.raises(
            ValueError, match="Provide only one of format_string or format"
        ):
            configure_logging(format_string="%(message)s", format="%(message)s")

    def test_log_info_with_verbose_true(self, caplog):
        """Test that log_info logs when verbose=True."""
        with caplog.at_level(logging.INFO, logger="datablade"):
            log_info("Test message", verbose=True)
            assert "Test message" in caplog.text

    def test_log_info_with_verbose_false(self, caplog):
        """Test that log_info doesn't log when verbose=False."""
        with caplog.at_level(logging.INFO, logger="datablade"):
            log_info("Test message", verbose=False)
            assert "Test message" not in caplog.text

    def test_log_warning(self, caplog):
        """Test log_warning function."""
        with caplog.at_level(logging.WARNING, logger="datablade"):
            log_warning("Warning message", verbose=True)
            assert "Warning message" in caplog.text

    def test_log_error(self, caplog):
        """Test log_error function."""
        with caplog.at_level(logging.ERROR, logger="datablade"):
            log_error("Error message", verbose=True)
            assert "Error message" in caplog.text

    def test_log_debug(self, caplog):
        """Test log_debug function."""
        # Configure logger to DEBUG level
        configure_logging(level=logging.DEBUG)
        with caplog.at_level(logging.DEBUG, logger="datablade"):
            log_debug("Debug message", verbose=True)
            assert "Debug message" in caplog.text

    def test_print_verbose_is_alias_for_log_info(self, caplog):
        """Test that print_verbose is an alias for log_info."""
        with caplog.at_level(logging.INFO, logger="datablade"):
            print_verbose("Verbose message", verbose=True)
            assert "Verbose message" in caplog.text
