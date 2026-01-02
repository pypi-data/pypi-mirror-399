from typing import Any, Dict, List, Optional, Tuple

import json
import time

# Try to import requests for better Digest auth support
try:
    import requests
    from requests.auth import HTTPDigestAuth

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class MoneroClient:
    """
    Minimal JSON-RPC client for monero-wallet-rpc.
    Uses stdlib only to avoid new dependencies.
    """

    def __init__(
        self,
        rpc_url: str,
        rpc_user: Optional[str] = None,
        rpc_pass: Optional[str] = None,
        timeout: int = 15,
    ):
        self.rpc_url = rpc_url.rstrip("/")
        self.rpc_user = rpc_user
        self.rpc_pass = rpc_pass
        self.timeout = timeout

    def _call(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        payload = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000),
            "method": method,
        }
        if params is not None:
            payload["params"] = params

        # Use requests library for all HTTP calls - much better Digest auth support
        if not HAS_REQUESTS:
            raise RuntimeError(
                "requests library required for Monero RPC. Install with: pip install requests"
            )

        auth = (
            HTTPDigestAuth(self.rpc_user, self.rpc_pass)
            if self.rpc_user and self.rpc_pass
            else None
        )

        try:
            response = requests.post(
                self.rpc_url, json=payload, auth=auth, timeout=self.timeout
            )
            response.raise_for_status()

            obj = response.json()
            if "error" in obj and obj["error"]:
                raise RuntimeError(obj["error"])  # bubble up rpc error
            return obj.get("result")

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Monero RPC connection error: {e}")

    # High-level helpers

    def create_subaddress(
        self, account_index: int = 0, label: Optional[str] = None
    ) -> Tuple[str, int]:
        params: Dict[str, Any] = {"account_index": account_index}
        if label:
            params["label"] = label
        res = self._call("create_address", params)
        return res["address"], res["address_index"]

    def get_transfers_for_subaddr(
        self, account_index: int, subaddr_indices: List[int]
    ) -> Dict[str, Any]:
        params = {
            "in": True,
            "out": False,
            "pending": True,
            "failed": False,
            "pool": True,
            "filter_by_height": False,
            "subaddr_indices": subaddr_indices,
            "account_index": account_index,
        }
        return self._call("get_transfers", params) or {}

    def get_height(self) -> int:
        res = self._call("get_height")
        return int(res.get("height", 0))

    def is_synced(self) -> bool:
        """
        Check if the Monero wallet is ready for payment processing.
        For remote nodes, checks if wallet RPC is responsive and can get height.
        """
        try:
            # For wallet-rpc with remote nodes, if we can get height > 0,
            # the wallet is connected to a synced daemon and ready
            wallet_height = self.get_height()
            return wallet_height > 0
        except Exception:
            # If RPC call fails, wallet is not ready
            return False

    def get_sync_status(self) -> dict:
        """
        Get detailed sync status information.
        For remote nodes, returns wallet readiness status.
        """
        try:
            wallet_height = self.get_height()
            synced = wallet_height > 0

            return {
                "wallet_height": wallet_height,
                "synced": synced,
                "sync_percentage": 100.0 if synced else 0.0,
                "remote_node": True,
                "ready": synced,
            }
        except Exception as e:
            return {
                "wallet_height": 0,
                "synced": False,
                "sync_percentage": 0.0,
                "remote_node": True,
                "ready": False,
                "error": str(e),
            }


class MockMoneroClient:
    """
    Minimal mock client for development. Reads a JSON file mapping subaddress_index
    to a list of inbound transfers for testing the watcher without a live RPC.
    settings:
      - monero.mock_transfers_file: path to JSON file
    JSON format example:
      {
        "height": 100000,
        "transfers": {
          "0": [{"amount": 123000000000, "confirmations": 12, "txid": "tx1"}],
          "5": [{"amount": 999, "confirmations": 0, "txid": "tx2"}]
        }
      }
    """

    def __init__(self, path: str):
        self.path = path
        self._data = None
        self._load()

    def _load(self) -> None:
        try:
            with open(self.path, "r") as f:
                self._data = json.load(f)
        except FileNotFoundError:
            self._data = {"height": 0, "transfers": {}}

    def create_subaddress(
        self, account_index: int = 0, label: Optional[str] = None
    ) -> Tuple[str, int]:
        # Not used by watcher; provided for completeness
        raise RuntimeError(
            "MockMoneroClient does not support create_subaddress in this context"
        )

    def get_transfers_for_subaddr(
        self, account_index: int, subaddr_indices: List[int]
    ) -> Dict[str, Any]:
        transfers: Dict[str, List[Dict[str, Any]]] = {}
        for idx in subaddr_indices:
            key = str(idx)
            arr = self._data.get("transfers", {}).get(key, [])
            if arr:
                transfers.setdefault("in", []).extend(arr)
        return transfers

    def get_height(self) -> int:
        return int(self._data.get("height", 0))

    def is_synced(self) -> bool:
        """Mock client is always considered synced for testing."""
        return True

    def get_sync_status(self) -> dict:
        """Mock client returns synced status for testing."""
        height = self.get_height()
        return {
            "wallet_height": height,
            "daemon_height": height,
            "synced": True,
            "sync_percentage": 100.0,
            "blocks_behind": 0,
        }


class DogecoinClient:
    """
    Minimal JSON-RPC client for dogecoind.
    Uses stdlib only to avoid new dependencies.

    Do Only Good Everyday 🐕
    """

    def __init__(
        self,
        rpc_url: str,
        rpc_user: Optional[str] = None,
        rpc_pass: Optional[str] = None,
        timeout: int = 15,
    ):
        self.rpc_url = rpc_url.rstrip("/")
        self.rpc_user = rpc_user
        self.rpc_pass = rpc_pass
        self.timeout = timeout

    def _call(self, method: str, params: Optional[List[Any]] = None) -> Any:
        """Note: Dogecoin RPC expects params as array, not dict"""
        payload = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000),
            "method": method,
        }
        if params is not None:
            payload["params"] = params

        # Use requests library for all HTTP calls - consistent with MoneroClient
        if not HAS_REQUESTS:
            raise RuntimeError(
                "requests library required for Dogecoin RPC. Install with: pip install requests"
            )

        auth = (
            (self.rpc_user, self.rpc_pass) if self.rpc_user and self.rpc_pass else None
        )

        try:
            response = requests.post(
                self.rpc_url,
                json=payload,
                auth=auth,  # Basic auth for Dogecoin
                timeout=self.timeout,
            )
            response.raise_for_status()

            obj = response.json()
            if "error" in obj and obj["error"]:
                raise RuntimeError(f"RPC error: {obj['error']}")
            return obj.get("result")

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Dogecoin RPC connection error: {e}")

    # Wallet Management

    def getnewaddress(self, label: str = "") -> str:
        """Generate a new Dogecoin address with optional label."""
        return self._call("getnewaddress", [label])

    def getaddressesbylabel(self, label: str) -> Dict[str, Any]:
        """Get all addresses with a specific label."""
        return self._call("getaddressesbylabel", [label])

    def validateaddress(self, address: str) -> Dict[str, Any]:
        """Validate a Dogecoin address."""
        return self._call("validateaddress", [address])

    # Balance and Transaction Info

    def getbalance(self) -> float:
        """Get total wallet balance."""
        return self._call("getbalance")

    def getreceivedbyaddress(self, address: str, minconf: int = 1) -> float:
        """Get total received by specific address."""
        return self._call("getreceivedbyaddress", [address, minconf])

    def listtransactions(
        self, label: str = "*", count: int = 10, skip: int = 0
    ) -> List[Dict[str, Any]]:
        """List transactions for a label or all (*)."""
        return self._call("listtransactions", [label, count, skip])

    def gettransaction(self, txid: str) -> Dict[str, Any]:
        """Get detailed information about a specific transaction."""
        return self._call("gettransaction", [txid])

    # Sending Funds

    def sendtoaddress(self, address: str, amount: float, comment: str = "") -> str:
        """Send Dogecoin to an address. Returns transaction ID."""
        return self._call("sendtoaddress", [address, amount, comment])

    def sendmany(
        self,
        from_label: str,
        addresses_amounts: Dict[str, float],
        minconf: int = 1,
        comment: str = "",
    ) -> str:
        """Send to multiple addresses at once. More efficient for sweeping.

        Args:
            from_label: Account label (use "" for default account)
            addresses_amounts: Dict mapping addresses to amounts
            minconf: Minimum confirmations (default: 1)
            comment: Transaction comment (optional)
        """
        # Build params list - Dogecoin expects specific parameter order
        params = [from_label, addresses_amounts]
        if minconf != 1 or comment:
            params.append(minconf)
        if comment:
            params.append(comment)
        return self._call("sendmany", params)

    # Blockchain Info

    def getblockcount(self) -> int:
        """Get current block height."""
        return self._call("getblockcount")

    def getblockhash(self, block_height: int) -> str:
        """Get block hash for a specific block height."""
        return self._call("getblockhash", [block_height])

    def listsinceblock(self, block_hash: str = None) -> Dict[str, Any]:
        """List transactions since a specific block hash."""
        params = [block_hash] if block_hash else []
        return self._call("listsinceblock", params)

    def getnetworkinfo(self) -> Dict[str, Any]:
        """Get network status information."""
        return self._call("getnetworkinfo")

    def getblockchaininfo(self) -> Dict[str, Any]:
        """Get blockchain synchronization status."""
        return self._call("getblockchaininfo")

    def is_synced(self) -> bool:
        """
        Check if the Dogecoin node is fully synced.
        Returns True if verification progress is near 100%.
        """
        try:
            info = self.getblockchaininfo()
            progress = float(info.get("verificationprogress", 0))
            # Consider synced if >99.9% to handle small timing issues
            return progress >= 0.999
        except Exception:
            # If RPC call fails, consider not synced
            return False

    def get_sync_status(self) -> dict:
        """
        Get detailed sync status information.
        Returns dict with blocks, headers, sync progress, etc.
        """
        try:
            blockchain_info = self.getblockchaininfo()

            blocks = int(blockchain_info.get("blocks", 0))
            headers = int(blockchain_info.get("headers", 0))
            progress = float(blockchain_info.get("verificationprogress", 0))

            synced = progress >= 0.999
            sync_percentage = progress * 100
            blocks_behind = max(0, headers - blocks)

            return {
                "blocks": blocks,
                "headers": headers,
                "synced": synced,
                "sync_percentage": sync_percentage,
                "blocks_behind": blocks_behind,
                "verification_progress": progress,
                "pruned": blockchain_info.get("pruned", False),
                "size_on_disk": blockchain_info.get("size_on_disk", 0),
            }
        except Exception as e:
            return {
                "blocks": 0,
                "headers": 0,
                "synced": False,
                "sync_percentage": 0.0,
                "blocks_behind": 0,
                "verification_progress": 0.0,
                "pruned": False,
                "size_on_disk": 0,
                "error": str(e),
            }


class MockDogecoinClient:
    """Mock client for testing without a real Dogecoin node."""

    def __init__(self, *args, **kwargs):
        self.addresses = {}
        self.next_address_num = 1
        self.balance = 100.0  # Start with 100 DOGE for testing

    def getnewaddress(self, label: str = "") -> str:
        address = f"DTest{self.next_address_num:04d}Address{label[:8]}"
        self.addresses[address] = {"label": label, "balance": 0.0}
        self.next_address_num += 1
        return address

    def getaddressesbylabel(self, label: str) -> Dict[str, Any]:
        return {
            addr: {"purpose": "receive"}
            for addr, info in self.addresses.items()
            if info["label"] == label
        }

    def validateaddress(self, address: str) -> Dict[str, Any]:
        is_valid = address.startswith("D") and len(address) == 34
        return {
            "isvalid": is_valid,
            "address": address if is_valid else "",
            "ismine": address in self.addresses,
        }

    def getbalance(self) -> float:
        return self.balance

    def getreceivedbyaddress(self, address: str, minconf: int = 1) -> float:
        return self.addresses.get(address, {}).get("balance", 0.0)

    def listtransactions(
        self, label: str = "*", count: int = 10, skip: int = 0
    ) -> List[Dict[str, Any]]:
        # Return mock transactions
        return (
            [
                {
                    "address": next(iter(self.addresses)),
                    "category": "receive",
                    "amount": 10.0,
                    "confirmations": 6,
                    "txid": "mocktxid123",
                    "time": int(time.time()),
                }
            ]
            if self.addresses
            else []
        )

    def sendtoaddress(self, address: str, amount: float, comment: str = "") -> str:
        if self.balance >= amount:
            self.balance -= amount
            return f"mocktxid{int(time.time())}"
        raise RuntimeError("Insufficient funds")

    def getblockcount(self) -> int:
        return 5500000  # Mock block height

    def getblockhash(self, block_height: int) -> str:
        """Mock block hash for testing."""
        return f"mock_block_hash_{block_height}"

    def listsinceblock(self, block_hash: str = None) -> Dict[str, Any]:
        """Mock listsinceblock for testing."""
        return {
            "transactions": [
                {
                    "address": (
                        next(iter(self.addresses)) if self.addresses else "DTestAddress"
                    ),
                    "category": "receive",
                    "amount": 5.0,
                    "confirmations": 6,
                    "txid": f"mock_since_txid_{int(time.time())}",
                    "time": int(time.time()),
                    "blockhash": f"mock_block_hash_{5500000}",
                }
            ],
            "lastblock": f"mock_block_hash_{5500000}",
        }

    def getnetworkinfo(self) -> Dict[str, Any]:
        return {
            "version": 1140200,
            "subversion": "/Shibetoshi:1.14.2/",
            "protocolversion": 70015,
            "connections": 8,
        }

    def getblockchaininfo(self) -> Dict[str, Any]:
        """Mock blockchain info - always synced for testing."""
        return {
            "chain": "main",
            "blocks": 5500000,
            "headers": 5500000,
            "verificationprogress": 1.0,
            "pruned": False,
            "size_on_disk": 2000000000,  # 2GB
        }

    def is_synced(self) -> bool:
        """Mock client is always considered synced for testing."""
        return True

    def get_sync_status(self) -> dict:
        """Mock client returns synced status for testing."""
        return {
            "blocks": 5500000,
            "headers": 5500000,
            "synced": True,
            "sync_percentage": 100.0,
            "blocks_behind": 0,
            "verification_progress": 1.0,
            "pruned": False,
            "size_on_disk": 2000000000,
        }


def get_client_from_settings(settings) -> MoneroClient:
    """
    Helper to construct a client from Pyramid settings.
    Expects keys:
      monero.rpc_url, monero.rpc_user, monero.rpc_pass
    """
    if str(settings.get("monero.mock", "false")).lower() in ("1", "true", "yes"):
        path = settings.get("monero.mock_transfers_file") or "mock_transfers.json"
        return MockMoneroClient(path)
    rpc_url = settings.get("monero.rpc_url")
    if not rpc_url:
        raise RuntimeError("monero.rpc_url not configured")
    return MoneroClient(
        rpc_url=rpc_url,
        rpc_user=settings.get("monero.rpc_user"),
        rpc_pass=settings.get("monero.rpc_pass"),
    )


def get_dogecoin_client_from_settings(settings):
    """
    Helper to construct a Dogecoin client from Pyramid settings.

    Uses standard Dogecoin Core RPC - works with both full and pruned nodes.
    Pruned mode recommended: only ~2GB storage vs 50GB for full node.

    Settings:
      dogecoin.rpc_url, dogecoin.rpc_user, dogecoin.rpc_pass
    """
    if str(settings.get("dogecoin.mock", "false")).lower() in ("1", "true", "yes"):
        return MockDogecoinClient()

    rpc_url = settings.get("dogecoin.rpc_url")
    if not rpc_url:
        raise RuntimeError("dogecoin.rpc_url not configured")

    return DogecoinClient(
        rpc_url=rpc_url,
        rpc_user=settings.get("dogecoin.rpc_user"),
        rpc_pass=settings.get("dogecoin.rpc_pass"),
    )
