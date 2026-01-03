"""Tests for wallet module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from zopassport.exceptions import ZoWalletError
from zopassport.wallet import ZoWallet


class TestZoWallet:
    """Tests for ZoWallet class."""

    @pytest.fixture
    def wallet(self, mock_client):
        # mock_client needs to be defined or passed
        client = AsyncMock()
        client.request = AsyncMock()
        return ZoWallet(client)

    def test_set_wallet_address(self, wallet):
        """Test setting wallet address."""
        wallet.set_wallet_address("0x123", network="avalanche")
        assert wallet.user_wallet_address == "0x123"
        assert wallet.network == "avalanche"

        # Default network
        wallet.set_wallet_address("0x456", network="invalid")
        assert wallet.user_wallet_address == "0x456"
        assert wallet.network == "base"

    @pytest.mark.asyncio
    async def test_get_balance_api_fallback(self, wallet):
        """Test fetching balance from API when on-chain fails/is skipped."""
        wallet.set_wallet_address("0x123")

        # Mock on-chain failure (return None)
        wallet._get_on_chain_balance = AsyncMock(return_value=None)

        # Mock API success
        # Note: Since we mock the method, the side effect of updating cached_balance
        # won't happen unless we define it. For this test, we verify the return value.
        wallet._get_balance_from_api = AsyncMock(return_value=100.5)

        balance = await wallet.get_balance()
        assert balance == 100.5
        # assert wallet.cached_balance == 100.5  # Removed as mock doesn't update cache

    @pytest.mark.asyncio
    async def test_get_balance_cached(self, wallet):
        """Test returning cached balance if all fetch methods fail."""
        wallet.cached_balance = 50.0
        wallet._get_on_chain_balance = AsyncMock(return_value=None)
        wallet._get_balance_from_api = AsyncMock(return_value=None)

        balance = await wallet.get_balance()
        assert balance == 50.0

    @pytest.mark.asyncio
    async def test_get_balance_failure(self, wallet):
        """Test failure when no balance can be retrieved."""
        wallet.cached_balance = 0.0
        wallet._get_on_chain_balance = AsyncMock(return_value=None)
        wallet._get_balance_from_api = AsyncMock(return_value=None)

        with pytest.raises(ZoWalletError):
            await wallet.get_balance()

    @pytest.mark.asyncio
    async def test_get_transactions(self, wallet):
        """Test fetching transactions."""
        # Setup the mock response object with .json() returning the data
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"id": "tx1", "amount": 10}, {"id": "tx2", "amount": 20}]
        }

        # Make request() return the mock_response (since request is async, it returns the value directly)
        wallet.client.request.return_value = mock_response

        result = await wallet.get_transactions()
        assert len(result["transactions"]) == 2
        assert result["count"] == 2

    @pytest.mark.asyncio
    async def test_get_on_chain_balance_success(self, wallet):
        """Test successful on-chain balance fetch."""
        wallet.set_wallet_address("0x123")

        # Mock httpx client response
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "0xde0b6b3a7640000"}  # 1.0 * 10^18

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            balance = await wallet._get_on_chain_balance()
            assert balance == 1.0

    @pytest.mark.asyncio
    async def test_get_on_chain_balance_error(self, wallet):
        """Test on-chain balance fetch with RPC error."""
        wallet.set_wallet_address("0x123")

        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "RPC Error"}

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            balance = await wallet._get_on_chain_balance()
            assert balance is None

    @pytest.mark.asyncio
    async def test_get_transactions_failure(self, wallet):
        """Test transactions fetch failure from all endpoints."""
        # Setup mock to raise exception for all calls
        wallet.client.request = AsyncMock(side_effect=Exception("API Error"))

        with pytest.raises(ZoWalletError):
            await wallet.get_transactions()
