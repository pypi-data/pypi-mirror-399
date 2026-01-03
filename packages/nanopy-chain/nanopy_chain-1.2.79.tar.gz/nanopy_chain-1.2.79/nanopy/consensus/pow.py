"""
NanoPy Proof of Work - Ethash-like consensus
"""

import time
import struct
from typing import Tuple, Optional
from dataclasses import dataclass
import hashlib
import threading

from eth_utils import keccak

from nanopy.core.block import Block, BlockHeader


@dataclass
class MiningResult:
    """Result of mining attempt"""
    success: bool
    nonce: bytes
    mix_hash: bytes
    hash_rate: float  # Hashes per second


class ProofOfWork:
    """
    Proof of Work implementation

    Simplified Ethash-like algorithm:
    - Uses Keccak-256 for hashing
    - Difficulty adjustment based on block time
    - Target block time: 12 seconds
    """

    TARGET_BLOCK_TIME = 12  # seconds
    DIFFICULTY_ADJUSTMENT_INTERVAL = 100  # blocks
    MIN_DIFFICULTY = 1
    MAX_DIFFICULTY = 2 ** 256 - 1

    def __init__(self, difficulty: int = 1000):
        self.difficulty = difficulty
        self._mining = False
        self._hashrate = 0

    @property
    def target(self) -> int:
        """Calculate target from difficulty"""
        return 2 ** 256 // max(self.difficulty, 1)

    @property
    def hashrate(self) -> float:
        return self._hashrate

    def verify(self, header: BlockHeader) -> bool:
        """
        Verify proof of work for a block header

        Args:
            header: Block header to verify

        Returns:
            True if valid PoW
        """
        # Compute hash
        block_hash = self._compute_pow_hash(header)
        hash_int = int.from_bytes(block_hash, 'big')

        # Check against target
        target = 2 ** 256 // max(header.difficulty, 1)
        return hash_int < target

    def _compute_pow_hash(self, header: BlockHeader) -> bytes:
        """Compute PoW hash for header"""
        # Serialize header without nonce and mix_hash for initial hash
        header_bytes = self._serialize_header(header)
        seed_hash = keccak(header_bytes)

        # Mix with nonce
        nonce_bytes = header.nonce if isinstance(header.nonce, bytes) else header.nonce.to_bytes(8, 'big')
        mix = seed_hash + nonce_bytes

        # Multiple rounds of hashing (simplified Ethash)
        for _ in range(64):
            mix = keccak(mix)

        return mix

    def _serialize_header(self, header: BlockHeader) -> bytes:
        """Serialize header for hashing (without nonce/mix_hash)"""
        parts = [
            header.parent_hash,
            header.uncle_hash,
            bytes.fromhex(header.coinbase[2:]) if header.coinbase.startswith("0x") else bytes.fromhex(header.coinbase),
            header.state_root,
            header.transactions_root,
            header.receipts_root,
            header.logs_bloom,
            header.difficulty.to_bytes(32, 'big'),
            header.number.to_bytes(8, 'big'),
            header.gas_limit.to_bytes(8, 'big'),
            header.gas_used.to_bytes(8, 'big'),
            header.timestamp.to_bytes(8, 'big'),
            header.extra_data,
        ]
        return b''.join(parts)

    def mine(
        self,
        header: BlockHeader,
        timeout: float = None,
        start_nonce: int = 0
    ) -> Optional[MiningResult]:
        """
        Mine a block (find valid nonce)

        Args:
            header: Block header to mine
            timeout: Maximum time to mine (None for no limit)
            start_nonce: Starting nonce value

        Returns:
            MiningResult if successful, None if stopped/timeout
        """
        self._mining = True
        target = 2 ** 256 // max(header.difficulty, 1)

        start_time = time.time()
        nonce = start_nonce
        attempts = 0

        while self._mining:
            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                self._mining = False
                return None

            # Try this nonce
            header.nonce = nonce.to_bytes(8, 'big')
            pow_hash = self._compute_pow_hash(header)
            hash_int = int.from_bytes(pow_hash, 'big')

            attempts += 1

            if hash_int < target:
                # Found valid nonce!
                elapsed = time.time() - start_time
                self._hashrate = attempts / elapsed if elapsed > 0 else 0

                return MiningResult(
                    success=True,
                    nonce=header.nonce,
                    mix_hash=pow_hash[:32],
                    hash_rate=self._hashrate,
                )

            nonce += 1

            # Update hashrate periodically
            if attempts % 10000 == 0:
                elapsed = time.time() - start_time
                self._hashrate = attempts / elapsed if elapsed > 0 else 0

        return None

    def stop_mining(self):
        """Stop current mining operation"""
        self._mining = False

    def adjust_difficulty(self, parent: BlockHeader, current_time: int) -> int:
        """
        Adjust difficulty based on block time

        Args:
            parent: Parent block header
            current_time: Current timestamp

        Returns:
            New difficulty value
        """
        time_diff = current_time - parent.timestamp

        if time_diff < self.TARGET_BLOCK_TIME:
            # Blocks too fast, increase difficulty
            adjustment = parent.difficulty // 2048 + 1
            new_difficulty = parent.difficulty + adjustment
        elif time_diff > self.TARGET_BLOCK_TIME * 2:
            # Blocks too slow, decrease difficulty
            adjustment = parent.difficulty // 2048 + 1
            new_difficulty = parent.difficulty - adjustment
        else:
            new_difficulty = parent.difficulty

        # Clamp to valid range
        return max(self.MIN_DIFFICULTY, min(new_difficulty, self.MAX_DIFFICULTY))


def mine_block(
    block: Block,
    pow: ProofOfWork = None,
    timeout: float = None
) -> Optional[Block]:
    """
    Mine a block with PoW

    Args:
        block: Block to mine
        pow: ProofOfWork instance (creates default if None)
        timeout: Mining timeout in seconds

    Returns:
        Mined block with valid nonce, or None if failed
    """
    if pow is None:
        pow = ProofOfWork(block.header.difficulty)

    result = pow.mine(block.header, timeout=timeout)

    if result and result.success:
        block.header.nonce = result.nonce
        block.header.mix_hash = result.mix_hash
        block.header._hash = None  # Invalidate cached hash
        return block

    return None


class Miner:
    """
    Background miner thread
    """

    def __init__(self, pow: ProofOfWork, coinbase: str):
        self.pow = pow
        self.coinbase = coinbase
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._current_block: Optional[Block] = None

    def start(self, get_block_fn, submit_block_fn):
        """
        Start mining in background

        Args:
            get_block_fn: Function that returns next block to mine
            submit_block_fn: Function to submit mined block
        """
        self._running = True

        def mine_loop():
            while self._running:
                # Get next block to mine
                block = get_block_fn()
                if block is None:
                    time.sleep(1)
                    continue

                self._current_block = block

                # Mine it
                result = self.pow.mine(block.header, timeout=30)

                if result and result.success:
                    block.header.nonce = result.nonce
                    block.header.mix_hash = result.mix_hash
                    submit_block_fn(block)

        self._thread = threading.Thread(target=mine_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop mining"""
        self._running = False
        self.pow.stop_mining()
        if self._thread:
            self._thread.join(timeout=5)

    @property
    def is_mining(self) -> bool:
        return self._running

    @property
    def hashrate(self) -> float:
        return self.pow.hashrate
