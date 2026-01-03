"""
NanoPy Block - Ethereum-compatible blocks
"""

from dataclasses import dataclass, field
from typing import List, Optional
import time
import rlp

from eth_typing import Hash32, Address
from eth_utils import keccak, to_hex, to_bytes
from eth_bloom import BloomFilter

from nanopy.core.transaction import SignedTransaction


@dataclass
class BlockHeader:
    """
    Ethereum-compatible block header
    Contains all metadata for a block
    """
    parent_hash: bytes  # 32 bytes
    uncle_hash: bytes  # 32 bytes (ommers hash)
    coinbase: str  # 20 bytes (miner/validator)
    state_root: bytes  # 32 bytes
    transactions_root: bytes  # 32 bytes
    receipts_root: bytes  # 32 bytes
    logs_bloom: bytes  # 256 bytes
    difficulty: int
    number: int  # Block number
    gas_limit: int
    gas_used: int
    timestamp: int
    extra_data: bytes  # Max 32 bytes
    mix_hash: bytes  # 32 bytes (PoW)
    nonce: bytes  # 8 bytes (PoW)

    # EIP-1559 fields
    base_fee_per_gas: Optional[int] = None

    # EIP-4895 - Withdrawals (post-merge)
    withdrawals_root: Optional[bytes] = None

    # Calculated
    _hash: bytes = field(default=None, repr=False)

    def __post_init__(self):
        """Calculate block hash after initialization"""
        if self._hash is None:
            self._hash = self.compute_hash()

    @property
    def hash(self) -> bytes:
        """Block hash"""
        if self._hash is None:
            self._hash = self.compute_hash()
        return self._hash

    def compute_hash(self) -> bytes:
        """Compute block header hash (RLP encoded then keccak256)"""
        # Ensure nonce is bytes (8 bytes for PoS)
        nonce = self.nonce if isinstance(self.nonce, bytes) else self.nonce.to_bytes(8, 'big')

        items = [
            self.parent_hash,
            self.uncle_hash,
            to_bytes(hexstr=self.coinbase) if isinstance(self.coinbase, str) else self.coinbase,
            self.state_root,
            self.transactions_root,
            self.receipts_root,
            self.logs_bloom,
            self.difficulty,
            self.number,
            self.gas_limit,
            self.gas_used,
            self.timestamp,
            self.extra_data,
            self.mix_hash,
            nonce,
        ]

        # Add EIP-1559 base fee if present
        if self.base_fee_per_gas is not None:
            items.append(self.base_fee_per_gas)

        # Add withdrawals root if present (post-merge)
        if self.withdrawals_root is not None:
            items.append(self.withdrawals_root)

        return keccak(rlp.encode(items))

    def to_dict(self) -> dict:
        """Convert to JSON-RPC compatible dict"""
        result = {
            "parentHash": to_hex(self.parent_hash),
            "sha3Uncles": to_hex(self.uncle_hash),
            "miner": self.coinbase,
            "stateRoot": to_hex(self.state_root),
            "transactionsRoot": to_hex(self.transactions_root),
            "receiptsRoot": to_hex(self.receipts_root),
            "logsBloom": to_hex(self.logs_bloom),
            "difficulty": hex(self.difficulty),
            "number": hex(self.number),
            "gasLimit": hex(self.gas_limit),
            "gasUsed": hex(self.gas_used),
            "timestamp": hex(self.timestamp),
            "extraData": to_hex(self.extra_data),
            "mixHash": to_hex(self.mix_hash),
            "nonce": to_hex(self.nonce),
            "hash": to_hex(self.hash),
        }

        if self.base_fee_per_gas is not None:
            result["baseFeePerGas"] = hex(self.base_fee_per_gas)

        if self.withdrawals_root is not None:
            result["withdrawalsRoot"] = to_hex(self.withdrawals_root)

        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'BlockHeader':
        """Create BlockHeader from JSON-RPC dict"""
        return cls(
            parent_hash=to_bytes(hexstr=data["parentHash"]),
            uncle_hash=to_bytes(hexstr=data["sha3Uncles"]),
            coinbase=data["miner"],
            state_root=to_bytes(hexstr=data["stateRoot"]),
            transactions_root=to_bytes(hexstr=data["transactionsRoot"]),
            receipts_root=to_bytes(hexstr=data["receiptsRoot"]),
            logs_bloom=to_bytes(hexstr=data["logsBloom"]),
            difficulty=int(data["difficulty"], 16),
            number=int(data["number"], 16),
            gas_limit=int(data["gasLimit"], 16),
            gas_used=int(data["gasUsed"], 16),
            timestamp=int(data["timestamp"], 16),
            extra_data=to_bytes(hexstr=data["extraData"]),
            mix_hash=to_bytes(hexstr=data["mixHash"]),
            nonce=to_bytes(hexstr=data["nonce"]),
            base_fee_per_gas=int(data["baseFeePerGas"], 16) if data.get("baseFeePerGas") else None,
            withdrawals_root=to_bytes(hexstr=data["withdrawalsRoot"]) if data.get("withdrawalsRoot") else None,
            _hash=to_bytes(hexstr=data["hash"]) if data.get("hash") else None,
        )


@dataclass
class Block:
    """
    Complete Ethereum-compatible block
    """
    header: BlockHeader
    transactions: List[SignedTransaction] = field(default_factory=list)
    uncles: List[BlockHeader] = field(default_factory=list)
    withdrawals: List[dict] = field(default_factory=list)

    @property
    def hash(self) -> bytes:
        return self.header.hash

    @property
    def number(self) -> int:
        return self.header.number

    @property
    def parent_hash(self) -> bytes:
        return self.header.parent_hash

    @property
    def gas_used(self) -> int:
        return self.header.gas_used

    @property
    def gas_limit(self) -> int:
        return self.header.gas_limit

    @property
    def timestamp(self) -> int:
        return self.header.timestamp

    @property
    def coinbase(self) -> str:
        return self.header.coinbase

    @classmethod
    def genesis(
        cls,
        chain_id: int = 1337,
        difficulty: int = 1,
        gas_limit: int = 30_000_000,
        coinbase: str = "0x0000000000000000000000000000000000000000",
        timestamp: int = 0,
        extra_data: bytes = b"NanoPy Genesis",
        nonce: int = 0,
    ) -> 'Block':
        """Create genesis block"""
        header = BlockHeader(
            parent_hash=bytes(32),  # All zeros
            uncle_hash=keccak(rlp.encode([])),  # Empty uncle list hash
            coinbase=coinbase,
            state_root=keccak(b""),  # Empty state root initially
            transactions_root=keccak(rlp.encode([])),
            receipts_root=keccak(rlp.encode([])),
            logs_bloom=bytes(256),
            difficulty=difficulty,
            number=0,
            gas_limit=gas_limit,
            gas_used=0,
            timestamp=timestamp,
            extra_data=extra_data[:32],  # Max 32 bytes
            mix_hash=bytes(32),
            nonce=nonce.to_bytes(8, 'big'),
            base_fee_per_gas=1_000_000_000,  # 1 Gwei initial base fee (EIP-1559)
        )

        return cls(header=header)

    def to_dict(self, full_transactions: bool = False) -> dict:
        """Convert to JSON-RPC compatible dict"""
        result = self.header.to_dict()

        if full_transactions:
            result["transactions"] = [tx.to_dict() for tx in self.transactions]
        else:
            result["transactions"] = [to_hex(tx.hash()) for tx in self.transactions]

        result["uncles"] = [to_hex(uncle.hash) for uncle in self.uncles]

        if self.withdrawals:
            result["withdrawals"] = self.withdrawals

        result["size"] = hex(self._calculate_size())

        return result

    def _calculate_size(self) -> int:
        """Calculate approximate block size in bytes"""
        # Header + transactions
        size = 500  # Base header size
        for tx in self.transactions:
            size += len(tx.raw())
        return size

    @classmethod
    def from_dict(cls, data: dict) -> 'Block':
        """Create Block from JSON-RPC dict"""
        header = BlockHeader.from_dict(data)

        # Parse full transactions if available (not just hashes)
        transactions = []
        for tx_data in data.get("transactions", []):
            if isinstance(tx_data, dict):
                # Full transaction object
                transactions.append(SignedTransaction.from_dict(tx_data))
            # else: just a hash string, skip

        return cls(
            header=header,
            transactions=transactions,
            uncles=[],
            withdrawals=data.get("withdrawals", []),
        )


def compute_transactions_root(transactions: List[SignedTransaction]) -> bytes:
    """Compute Merkle Patricia Trie root of transactions"""
    from trie import HexaryTrie

    trie = HexaryTrie({})
    for i, tx in enumerate(transactions):
        key = rlp.encode(i)
        trie[key] = tx.raw()

    return trie.root_hash


def compute_logs_bloom(logs: List[dict]) -> bytes:
    """Compute bloom filter for logs"""
    bloom = BloomFilter()

    for log in logs:
        # Add address
        address = to_bytes(hexstr=log["address"])
        bloom.add(address)

        # Add topics
        for topic in log.get("topics", []):
            bloom.add(to_bytes(hexstr=topic))

    # Convert bloom filter to 256 bytes
    return int(bloom).to_bytes(256, 'big')
