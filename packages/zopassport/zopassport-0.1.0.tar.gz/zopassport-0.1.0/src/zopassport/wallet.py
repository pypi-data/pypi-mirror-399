from typing import Any, TypedDict

import httpx

from .client import ZoApiClient
from .exceptions import ZoNetworkError, ZoWalletError
from .utils import logger


class NetworkConfig(TypedDict):
    rpc: str
    contractAddress: str
    decimals: int


ZO_TOKEN_CONFIG: dict[str, NetworkConfig] = {
    "base": {
        "rpc": "https://mainnet.base.org",
        "contractAddress": "0x111142c7ecaf39797b7865b82034269962142069",
        "decimals": 18,
    },
    "avalanche": {
        "rpc": "https://api.avax.network/ext/bc/C/rpc",
        "contractAddress": "0x111142c7ecaf39797b7865b82034269962142069",
        "decimals": 18,
    },
}

ERC20_BALANCE_ABI = "0x70a08231"  # balanceOf(address)


class ZoWallet:
    """Wallet module for ZoPassport SDK."""

    def __init__(self, client: ZoApiClient) -> None:
        """
        Initialize wallet module.

        Args:
            client: ZoApiClient instance for making API requests
        """
        self.client = client
        self.cached_balance: float = 0.0
        self.user_wallet_address: str | None = None
        self.network: str = "base"

    def set_wallet_address(self, address: str, network: str = "base") -> None:
        """
        Set the user's wallet address.

        Args:
            address: Ethereum wallet address
            network: Network name ("base" or "avalanche", default: "base")
        """
        self.user_wallet_address = address
        self.network = network if network in ZO_TOKEN_CONFIG else "base"
        logger.debug(f"Wallet address set: {address} on {network}")

    async def get_balance(self) -> float:
        """
        Get wallet balance, trying on-chain first then API fallback.

        Returns:
            Balance in $Zo tokens

        Raises:
            ZoWalletError: If both on-chain and API balance fetching fails
        """
        # Try on-chain first
        if self.user_wallet_address:
            on_chain_balance = await self._get_on_chain_balance()
            if on_chain_balance is not None:
                self.cached_balance = on_chain_balance
                return on_chain_balance

        # Fallback to API
        api_balance = await self._get_balance_from_api()
        if api_balance is not None:
            return api_balance

        # Return cached balance if all else fails
        if self.cached_balance > 0:
            logger.warning("Using cached balance, live fetch failed")
            return self.cached_balance

        raise ZoWalletError(
            "Failed to fetch wallet balance from all sources",
            details={"wallet_address": self.user_wallet_address, "network": self.network},
        )

    async def _get_on_chain_balance(self) -> float | None:
        """
        Fetch balance directly from blockchain RPC.

        Returns:
            Balance in tokens or None if fetch fails
        """
        if not self.user_wallet_address:
            return None

        config = ZO_TOKEN_CONFIG.get(self.network)
        if not config:
            logger.warning(f"Unknown network: {self.network}")
            return None

        try:
            padded_address = self.user_wallet_address.lower().replace("0x", "").rjust(64, "0")
            data = ERC20_BALANCE_ABI + padded_address

            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "eth_call",
                "params": [{"to": config["contractAddress"], "data": data}, "latest"],
            }

            async with httpx.AsyncClient() as client:
                rpc_url = str(config["rpc"])
                response = await client.post(rpc_url, json=payload, timeout=5.0)
                result = response.json()

                if "error" in result:
                    logger.warning(f"RPC error: {result['error']}")
                    return None

                raw_balance = int(result.get("result", "0x0"), 16)
                balance = float(raw_balance / (10 ** int(config["decimals"])))
                logger.debug(f"On-chain balance: {balance}")
                return balance

        except httpx.HTTPError as e:
            logger.warning(f"HTTP error fetching on-chain balance: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.warning(f"Error parsing on-chain balance: {e}")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error fetching on-chain balance: {e}")
            return None

    async def _get_balance_from_api(self) -> float | None:
        """
        Fetch balance from ZoPassport API endpoints.

        Returns:
            Balance in tokens or None if fetch fails
        """
        endpoints = [
            "/api/v1/web3/token/airdrops/summary",
            "/api/v1/wallet/balance",
            "/api/v1/profile/wallet",
        ]

        for endpoint in endpoints:
            try:
                response = await self.client.request("GET", endpoint)
                data = response.json()

                # Try to extract balance from various structures
                balance = None
                if isinstance(data, dict):
                    if "data" in data and isinstance(data["data"], dict):
                        balance = data["data"].get("total_amount")
                    if balance is None:
                        balance = data.get("balance") or data.get("total_amount")

                if balance is not None:
                    try:
                        val = float(balance)
                        self.cached_balance = val
                        logger.debug(f"API balance from {endpoint}: {val}")
                        return val
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Failed to convert balance to float: {e}")
                        continue
            except ZoNetworkError as e:
                logger.debug(f"Network error fetching balance from {endpoint}: {e}")
                continue
            except Exception as e:
                logger.debug(f"Error fetching balance from {endpoint}: {e}")
                continue

        return None

    async def get_transactions(self, page: int | None = None) -> dict[str, Any]:
        """
        Get transaction history.

        Args:
            page: Page number for pagination (optional)

        Returns:
            Dictionary containing transactions and pagination info

        Raises:
            ZoWalletError: If all transaction endpoints fail
        """
        endpoints = [
            (
                f"/api/v1/profile/completion-grants/claims?page={page}"
                if page
                else "/api/v1/profile/completion-grants/claims"
            ),
            f"/api/v1/wallet/transactions?page={page}" if page else "/api/v1/wallet/transactions",
        ]

        for endpoint in endpoints:
            try:
                response = await self.client.request("GET", endpoint)
                data = response.json()

                # Handle varying structures
                inner_data = data.get("data", data)

                if isinstance(inner_data, list):
                    return {"transactions": inner_data, "count": len(inner_data)}

                return {
                    "transactions": (
                        inner_data.get("results") or inner_data.get("transactions") or []
                    ),
                    "next": inner_data.get("next"),
                    "previous": inner_data.get("previous"),
                    "count": inner_data.get("count", 0),
                }
            except ZoNetworkError as e:
                logger.debug(f"Network error fetching transactions from {endpoint}: {e}")
                continue
            except Exception as e:
                logger.debug(f"Error fetching transactions from {endpoint}: {e}")
                continue

        raise ZoWalletError(
            "Failed to fetch transactions from all endpoints",
            details={"page": page},
        )
