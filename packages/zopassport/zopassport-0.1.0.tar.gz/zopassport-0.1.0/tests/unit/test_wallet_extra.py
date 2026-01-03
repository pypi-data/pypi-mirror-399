"""Extra tests for wallet module coverage."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from zopassport.wallet import ZoWallet


class TestZoWalletExtra:
    """Extra tests for ZoWallet."""

    @pytest.fixture
    def wallet(self):
        client = AsyncMock()
        client.request = AsyncMock()
        return ZoWallet(client)

    @pytest.mark.asyncio
    async def test_get_balance_from_api_format_1(self, wallet):
        """Test balance format: data -> total_amount."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"total_amount": "123.45"}}
        wallet.client.request.return_value = mock_response

        balance = await wallet._get_balance_from_api()
        assert balance == 123.45

    @pytest.mark.asyncio
    async def test_get_balance_from_api_format_2(self, wallet):
        """Test balance format: balance field."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"balance": "67.89"}
        wallet.client.request.return_value = mock_response

        balance = await wallet._get_balance_from_api()
        assert balance == 67.89

    @pytest.mark.asyncio
    async def test_get_balance_from_api_format_3(self, wallet):
        """Test balance format: total_amount field."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"total_amount": 100}
        wallet.client.request.return_value = mock_response

        balance = await wallet._get_balance_from_api()
        assert balance == 100.0

    @pytest.mark.asyncio
    async def test_get_balance_from_api_invalid_value(self, wallet):
        """Test handling invalid float value."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"balance": "invalid"}
        wallet.client.request.return_value = mock_response

        balance = await wallet._get_balance_from_api()
        assert balance is None

    @pytest.mark.asyncio
    async def test_get_balance_from_api_network_error(self, wallet):
        """Test handling network error during balance fetch."""
        from zopassport.exceptions import ZoNetworkError

        wallet.client.request.side_effect = ZoNetworkError("Net fail")

        balance = await wallet._get_balance_from_api()
        assert balance is None

    @pytest.mark.asyncio
    async def test_get_transactions_list_format(self, wallet):
        """Test transactions response as direct list."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": [{"id": 1}]}
        wallet.client.request.return_value = mock_response

        result = await wallet.get_transactions()
        assert len(result["transactions"]) == 1

    @pytest.mark.asyncio
    async def test_get_transactions_results_format(self, wallet):
        """Test transactions response with results field."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"results": [{"id": 1}]}}
        wallet.client.request.return_value = mock_response

        result = await wallet.get_transactions()
        assert len(result["transactions"]) == 1

    @pytest.mark.asyncio
    async def test_get_transactions_transactions_field(self, wallet):
        """Test transactions response with transactions field."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"transactions": [{"id": 1}]}}
        wallet.client.request.return_value = mock_response

        result = await wallet.get_transactions()
        assert len(result["transactions"]) == 1
