"""
NanoPy Transaction Pool - Pending transaction management
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from collections import defaultdict
import heapq
import threading
import time

from nanopy.core.transaction import Transaction, SignedTransaction


@dataclass(order=True)
class PendingTx:
    """Wrapper for priority queue ordering"""
    priority: int  # Negative gas price for max-heap behavior
    timestamp: float
    tx: SignedTransaction = field(compare=False)

    @classmethod
    def from_signed_tx(cls, tx: SignedTransaction) -> 'PendingTx':
        return cls(
            priority=-tx.transaction.effective_gas_price,
            timestamp=time.time(),
            tx=tx,
        )


class TxPool:
    """
    Transaction pool (mempool) for pending transactions

    Features:
    - Priority ordering by gas price
    - Per-account nonce tracking
    - Replacement by gas price (EIP-1559)
    - Size limits and eviction
    """

    def __init__(
        self,
        max_size: int = 10000,
        max_per_account: int = 100,
        min_gas_price: int = 1,  # Very low for gaming chain
    ):
        self.max_size = max_size
        self.max_per_account = max_per_account
        self.min_gas_price = min_gas_price

        # Storage
        self._pending: List[PendingTx] = []  # Priority queue
        self._by_hash: Dict[str, SignedTransaction] = {}
        self._by_sender: Dict[str, Dict[int, SignedTransaction]] = defaultdict(dict)  # sender -> nonce -> tx

        # Tracking
        self._known_hashes: Set[str] = set()

        # Thread safety
        self._lock = threading.RLock()

    def add(self, tx: SignedTransaction) -> bool:
        """
        Add transaction to pool

        Returns:
            True if added, False if rejected
        """
        with self._lock:
            tx_hash = tx.hash().hex()

            # Already known
            if tx_hash in self._known_hashes:
                return False

            # Check gas price minimum
            if tx.transaction.effective_gas_price < self.min_gas_price:
                return False

            sender = tx.sender.lower()
            nonce = tx.transaction.nonce

            # Check for replacement
            if nonce in self._by_sender[sender]:
                existing = self._by_sender[sender][nonce]
                # Must be at least 10% higher gas price
                if tx.transaction.effective_gas_price < existing.transaction.effective_gas_price * 1.1:
                    return False
                # Remove old tx
                self._remove_tx(existing)

            # Check per-account limit
            if len(self._by_sender[sender]) >= self.max_per_account:
                return False

            # Check pool size
            if len(self._by_hash) >= self.max_size:
                # Evict lowest gas price tx
                self._evict_lowest()

            # Add transaction
            self._by_hash[tx_hash] = tx
            self._by_sender[sender][nonce] = tx
            self._known_hashes.add(tx_hash)

            pending = PendingTx.from_signed_tx(tx)
            heapq.heappush(self._pending, pending)

            return True

    def _remove_tx(self, tx: SignedTransaction):
        """Remove transaction from pool"""
        tx_hash = tx.hash().hex()
        sender = tx.sender.lower()
        nonce = tx.transaction.nonce

        self._by_hash.pop(tx_hash, None)
        if nonce in self._by_sender.get(sender, {}):
            del self._by_sender[sender][nonce]

    def _evict_lowest(self):
        """Evict lowest gas price transaction"""
        # Rebuild heap without removed txs, pop lowest
        new_pending = []
        removed = None

        for p in self._pending:
            if p.tx.hash().hex() in self._by_hash:
                if removed is None:
                    removed = p.tx
                    self._remove_tx(p.tx)
                else:
                    new_pending.append(p)

        heapq.heapify(new_pending)
        self._pending = new_pending

    def get(self, tx_hash: str) -> Optional[SignedTransaction]:
        """Get transaction by hash"""
        with self._lock:
            if tx_hash.startswith("0x"):
                tx_hash = tx_hash[2:]
            return self._by_hash.get(tx_hash)

    def remove(self, tx_hash: str) -> bool:
        """Remove transaction by hash"""
        with self._lock:
            if tx_hash.startswith("0x"):
                tx_hash = tx_hash[2:]
            tx = self._by_hash.get(tx_hash)
            if tx:
                self._remove_tx(tx)
                return True
            return False

    def get_pending_for_block(self, gas_limit: int) -> List[SignedTransaction]:
        """
        Get transactions for block creation, ordered by gas price

        Args:
            gas_limit: Maximum gas for the block

        Returns:
            List of transactions that fit in the block
        """
        with self._lock:
            result = []
            total_gas = 0

            # Get all pending, sorted by gas price
            pending = sorted(
                self._by_hash.values(),
                key=lambda tx: tx.transaction.effective_gas_price,
                reverse=True,
            )

            for tx in pending:
                if total_gas + tx.transaction.gas <= gas_limit:
                    result.append(tx)
                    total_gas += tx.transaction.gas

            return result

    def get_pending_nonce(self, address: str) -> int:
        """Get next nonce for address (including pending txs)"""
        with self._lock:
            address = address.lower()
            if address not in self._by_sender:
                return 0
            nonces = self._by_sender[address].keys()
            if not nonces:
                return 0
            return max(nonces) + 1

    def get_pending_by_sender(self, address: str) -> List[SignedTransaction]:
        """Get all pending transactions for an address"""
        with self._lock:
            address = address.lower()
            if address not in self._by_sender:
                return []
            return list(self._by_sender[address].values())

    def pending_count(self) -> int:
        """Number of pending transactions"""
        with self._lock:
            return len(self._by_hash)

    def content(self) -> Dict[str, Dict[str, List[dict]]]:
        """Get pool content (like txpool_content)"""
        with self._lock:
            pending = defaultdict(dict)

            for sender, nonces in self._by_sender.items():
                for nonce, tx in nonces.items():
                    pending[sender][str(nonce)] = tx.to_dict()

            return {
                "pending": dict(pending),
                "queued": {},  # We don't have queued txs in this simple impl
            }

    def status(self) -> Dict[str, int]:
        """Get pool status"""
        with self._lock:
            return {
                "pending": len(self._by_hash),
                "queued": 0,
            }

    def clear(self):
        """Clear the entire pool"""
        with self._lock:
            self._pending.clear()
            self._by_hash.clear()
            self._by_sender.clear()
            self._known_hashes.clear()

    def remove_mined(self, transactions: List[SignedTransaction]):
        """Remove mined transactions from pool"""
        with self._lock:
            for tx in transactions:
                self.remove(tx.hash().hex())
