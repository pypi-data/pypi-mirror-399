"""Extra tests for auth module coverage."""

from unittest.mock import MagicMock

import pytest

from zopassport.auth import ZoAuth


class TestZoAuthExtra:
    """Extra tests for ZoAuth."""

    @pytest.fixture
    def auth(self):
        return ZoAuth(MagicMock())

    def test_extract_error_message_errors_list(self, auth):
        """Test extracting error from 'errors' list."""
        response = MagicMock()
        response.json.return_value = {"errors": ["Error 1", "Error 2"]}
        msg = auth._extract_error_message(response)
        assert msg == "Error 1"

    def test_extract_error_message_detail(self, auth):
        """Test extracting error from 'detail' field."""
        response = MagicMock()
        response.json.return_value = {"detail": "Detail error"}
        msg = auth._extract_error_message(response)
        assert msg == "Detail error"

    def test_extract_error_message_message(self, auth):
        """Test extracting error from 'message' field."""
        response = MagicMock()
        response.json.return_value = {"message": "Message error"}
        msg = auth._extract_error_message(response)
        assert msg == "Message error"

    def test_extract_error_message_error(self, auth):
        """Test extracting error from 'error' field."""
        response = MagicMock()
        response.json.return_value = {"error": "Simple error"}
        msg = auth._extract_error_message(response)
        assert msg == "Simple error"

    def test_extract_error_message_default(self, auth):
        """Test default error message."""
        response = MagicMock()
        response.json.return_value = {}
        msg = auth._extract_error_message(response)
        assert msg == "Authentication failed"

    def test_extract_error_message_json_error(self, auth):
        """Test handling JSON decode error."""
        response = MagicMock()
        response.json.side_effect = ValueError
        msg = auth._extract_error_message(response)
        assert msg == "Authentication failed"
