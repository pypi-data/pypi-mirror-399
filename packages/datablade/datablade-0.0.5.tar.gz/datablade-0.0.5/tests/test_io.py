"""Tests for datablade.io module."""

import zipfile
from unittest.mock import Mock, patch

import pytest

from datablade.io import get_json, get_zip


class TestGetJson:
    """Tests for get_json function."""

    @patch("datablade.io.json.requests.get")
    def test_successful_json_fetch(self, mock_get):
        """Test successful JSON data retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {"key": "value"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_json("https://api.example.com/data.json")

        assert result == {"key": "value"}
        mock_get.assert_called_once()

    @patch("datablade.io.json.requests.get")
    def test_http_error_raises_exception(self, mock_get):
        """Test that HTTP errors raise RequestException."""
        mock_get.side_effect = Exception("HTTP 404")

        with pytest.raises(Exception):
            get_json("https://api.example.com/notfound.json")

    def test_empty_url_raises_error(self):
        """Test that empty URL raises ValueError."""
        with pytest.raises(ValueError, match="url must be a non-empty string"):
            get_json("")

    def test_non_string_url_raises_error(self):
        """Test that non-string URL raises ValueError."""
        with pytest.raises(ValueError, match="url must be a non-empty string"):
            get_json(123)

    @patch("datablade.io.json.requests.get")
    def test_passes_kwargs_to_requests(self, mock_get):
        """Test that kwargs are passed to requests.get."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        get_json("https://api.example.com/data.json", headers={"Auth": "token"})

        mock_get.assert_called_with(
            "https://api.example.com/data.json", headers={"Auth": "token"}
        )


class TestGetZip:
    """Tests for get_zip function."""

    @patch("datablade.io.zip.requests.get")
    def test_download_zip_to_bytesio(self, mock_get):
        """Test downloading ZIP file to BytesIO."""
        # Create a mock ZIP file
        mock_response = Mock()
        mock_response.content = b"fake zip content"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_zip("https://example.com/data.zip", path=None)

        assert result is not None
        assert hasattr(result, "read")  # Should be BytesIO-like

    @patch("datablade.io.zip.requests.get")
    @patch("datablade.io.zip.zipfile.ZipFile")
    def test_extract_zip_to_path(self, mock_zipfile, mock_get, temp_dir):
        """Test extracting ZIP file to a path."""
        # Mock the response
        mock_response = Mock()
        mock_response.content = b"fake zip content"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Mock ZipFile
        mock_zip = Mock()
        mock_zip.infolist.return_value = []
        mock_zipfile.return_value.__enter__.return_value = mock_zip

        result = get_zip("https://example.com/data.zip", path=str(temp_dir))

        assert result is None  # Should return None when extracting to path

    def test_empty_url_raises_error(self):
        """Test that empty URL raises ValueError."""
        with pytest.raises(ValueError, match="url must be a non-empty string"):
            get_zip("")

    @patch("datablade.io.zip.requests.get")
    def test_http_error_raises_exception(self, mock_get):
        """Test that HTTP errors are raised."""
        mock_get.side_effect = Exception("HTTP 404")

        with pytest.raises(Exception):
            get_zip("https://example.com/notfound.zip")

    @patch("datablade.io.zip.requests.get")
    @patch("datablade.io.zip.zipfile.ZipFile")
    def test_bad_zip_raises_badzipfile(self, mock_zipfile, mock_get, temp_dir):
        """Test that invalid zip content raises BadZipFile."""
        mock_response = Mock()
        mock_response.content = b"not a real zip"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        mock_zipfile.side_effect = zipfile.BadZipFile("bad zip")

        with pytest.raises(zipfile.BadZipFile):
            get_zip("https://example.com/bad.zip", path=str(temp_dir))
