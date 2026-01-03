"""
RPC Client for Validator - Connects to NanoPy nodes
"""

import json
import time
import logging
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

logger = logging.getLogger(__name__)


class RPCError(Exception):
    """JSON-RPC error"""
    def __init__(self, code: int, message: str, data: Optional[str] = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(f"RPC Error {code}: {message}")


class NodeRPCClient:
    """
    RPC client with failover support for connecting to NanoPy nodes.

    Features:
    - Automatic failover between multiple nodes
    - Retry logic with exponential backoff
    - Health checking
    - Connection pooling (future)
    """

    def __init__(
        self,
        nodes: List[str],
        timeout: int = 10,
        max_retries: int = 3,
        failover_timeout: int = 5,
    ):
        self.nodes = nodes
        self.timeout = timeout
        self.max_retries = max_retries
        self.failover_timeout = failover_timeout

        # Track node health
        self._current_node_index = 0
        self._node_failures: Dict[str, int] = {node: 0 for node in nodes}
        self._node_last_success: Dict[str, float] = {}

        self._request_id = 0

    @property
    def current_node(self) -> str:
        """Get the current active node URL."""
        return self.nodes[self._current_node_index]

    def _next_request_id(self) -> int:
        """Get next request ID."""
        self._request_id += 1
        return self._request_id

    def _switch_node(self):
        """Switch to the next available node."""
        old_node = self.current_node
        self._current_node_index = (self._current_node_index + 1) % len(self.nodes)
        logger.warning(f"Switching from {old_node} to {self.current_node}")

    def _call_node(self, node: str, method: str, params: List[Any]) -> Any:
        """Make a single RPC call to a specific node."""
        request_data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self._next_request_id(),
        }

        request = Request(
            node,
            data=json.dumps(request_data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))

            if "error" in result:
                error = result["error"]
                raise RPCError(
                    error.get("code", -1),
                    error.get("message", "Unknown error"),
                    error.get("data"),
                )

            # Mark node as healthy
            self._node_failures[node] = 0
            self._node_last_success[node] = time.time()

            return result.get("result")

        except (URLError, HTTPError, TimeoutError) as e:
            self._node_failures[node] = self._node_failures.get(node, 0) + 1
            raise ConnectionError(f"Failed to connect to {node}: {e}")

    def call(self, method: str, *params) -> Any:
        """
        Make an RPC call with automatic failover.

        Args:
            method: RPC method name
            *params: Method parameters

        Returns:
            RPC result

        Raises:
            RPCError: If RPC returns an error
            ConnectionError: If all nodes are unavailable
        """
        last_error = None
        tried_nodes = set()

        while len(tried_nodes) < len(self.nodes):
            node = self.current_node
            tried_nodes.add(node)

            for retry in range(self.max_retries):
                try:
                    return self._call_node(node, method, list(params))
                except ConnectionError as e:
                    last_error = e
                    logger.debug(f"Retry {retry + 1}/{self.max_retries} for {node}: {e}")
                    if retry < self.max_retries - 1:
                        time.sleep(0.5 * (retry + 1))  # Exponential backoff
                except RPCError:
                    # RPC errors should be propagated, not retried
                    raise

            # All retries failed, switch to next node
            self._switch_node()

        raise ConnectionError(f"All nodes unavailable. Last error: {last_error}")

    # Convenience methods for validator operations

    def get_block_template(self, coinbase: str) -> dict:
        """Get block template for building a new block."""
        return self.call("validator_getBlockTemplate", coinbase)

    def submit_block(self, block_data: dict) -> dict:
        """Submit a built block to the node."""
        return self.call("validator_submitBlock", block_data)

    def is_selected(self, address: str) -> dict:
        """Check if address is selected as next validator."""
        return self.call("validator_isSelected", address)

    def get_pending_transactions(self, gas_limit: Optional[str] = None) -> list:
        """Get pending transactions for block building."""
        if gas_limit:
            return self.call("validator_getPendingTransactions", gas_limit)
        return self.call("validator_getPendingTransactions")

    def get_sync_status(self) -> dict:
        """Get node sync status."""
        return self.call("validator_getSyncStatus")

    def get_block_number(self) -> int:
        """Get current block number."""
        result = self.call("eth_blockNumber")
        return int(result, 16)

    def get_chain_id(self) -> int:
        """Get chain ID."""
        result = self.call("eth_chainId")
        return int(result, 16)

    def register_validator(self, address: str, stake: int) -> bool:
        """Register as a validator with stake."""
        return self.call("nno_registerValidator", address, hex(stake))

    def get_validators(self) -> list:
        """Get list of active validators."""
        return self.call("nno_getValidators")

    def get_stake(self, address: str) -> int:
        """Get stake amount for an address."""
        result = self.call("nno_getStake", address)
        return int(result, 16)

    def health_check(self) -> bool:
        """Check if current node is healthy."""
        try:
            self.get_block_number()
            return True
        except Exception:
            return False

    def get_healthy_node(self) -> Optional[str]:
        """Find a healthy node from the list."""
        for i, node in enumerate(self.nodes):
            try:
                self._current_node_index = i
                if self.health_check():
                    return node
            except Exception:
                continue
        return None

