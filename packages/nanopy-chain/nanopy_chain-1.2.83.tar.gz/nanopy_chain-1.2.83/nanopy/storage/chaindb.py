"""
NanoPy ChainDB - Persistent block storage
Stores blocks, transactions, and receipts on disk
"""

import json
import os
from typing import Dict, List, Optional
from dataclasses import asdict

from eth_utils import to_hex, keccak


class ChainDB:
    """
    Persistent storage for blockchain data
    Uses simple JSON files for portability (can upgrade to LevelDB later)

    Structure:
        data_dir/
            blocks/
                0.json, 1.json, ...  (by block number)
            block_hashes/
                0xabc...json  (hash -> block number mapping)
            transactions/
                0xabc...json  (tx hash -> tx data)
            receipts/
                0xabc...json  (tx hash -> receipt)
            state/
                latest.json  (current state snapshot)
            meta.json  (chain metadata)
    """

    def __init__(self, data_dir: str = "./chaindata"):
        self.data_dir = data_dir
        self._init_dirs()
        self._load_meta()

    def _init_dirs(self):
        """Create directory structure"""
        dirs = [
            self.data_dir,
            os.path.join(self.data_dir, "blocks"),
            os.path.join(self.data_dir, "block_hashes"),
            os.path.join(self.data_dir, "transactions"),
            os.path.join(self.data_dir, "receipts"),
            os.path.join(self.data_dir, "state"),
        ]
        for d in dirs:
            os.makedirs(d, exist_ok=True)

    def _load_meta(self):
        """Load chain metadata"""
        meta_path = os.path.join(self.data_dir, "meta.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                self._meta = json.load(f)
        else:
            self._meta = {
                "chain_id": 1337,
                "latest_block": -1,
                "genesis_hash": None,
                "total_difficulty": 0,
            }
            self._save_meta()

    def _save_meta(self):
        """Save chain metadata"""
        meta_path = os.path.join(self.data_dir, "meta.json")
        with open(meta_path, "w") as f:
            json.dump(self._meta, f, indent=2)

    @property
    def latest_block_number(self) -> int:
        return self._meta["latest_block"]

    @property
    def genesis_hash(self) -> Optional[str]:
        return self._meta.get("genesis_hash")

    @property
    def total_difficulty(self) -> int:
        return self._meta.get("total_difficulty", 0)

    # Block operations

    def put_block(self, block_data: dict) -> str:
        """
        Store a block
        Returns block hash
        """
        block_number = block_data["number"]
        # Handle hex string from to_dict()
        if isinstance(block_number, str):
            block_number = int(block_number, 16)
        block_hash = block_data.get("hash")

        if not block_hash:
            # Calculate hash if not provided
            block_hash = to_hex(keccak(json.dumps(block_data, sort_keys=True).encode()))
            block_data["hash"] = block_hash

        # Save block by number
        block_path = os.path.join(self.data_dir, "blocks", f"{block_number}.json")
        with open(block_path, "w") as f:
            json.dump(block_data, f, indent=2)

        # Save hash -> number mapping
        hash_path = os.path.join(self.data_dir, "block_hashes", f"{block_hash}.json")
        with open(hash_path, "w") as f:
            json.dump({"number": block_number}, f)

        # Update metadata
        if block_number > self._meta["latest_block"]:
            self._meta["latest_block"] = block_number
            difficulty = block_data.get("difficulty", 1)
            if isinstance(difficulty, str):
                difficulty = int(difficulty, 16)
            self._meta["total_difficulty"] += difficulty

        if block_number == 0:
            self._meta["genesis_hash"] = block_hash

        self._save_meta()

        # Save transactions (skip if they're just hashes, not full tx data)
        for tx in block_data.get("transactions", []):
            if isinstance(tx, dict):
                self.put_transaction(tx)

        return block_hash

    def get_block_by_number(self, number: int) -> Optional[dict]:
        """Get block by number"""
        block_path = os.path.join(self.data_dir, "blocks", f"{number}.json")
        if os.path.exists(block_path):
            with open(block_path, "r") as f:
                return json.load(f)
        return None

    def get_block_by_hash(self, block_hash: str) -> Optional[dict]:
        """Get block by hash"""
        hash_path = os.path.join(self.data_dir, "block_hashes", f"{block_hash}.json")
        if os.path.exists(hash_path):
            with open(hash_path, "r") as f:
                data = json.load(f)
                return self.get_block_by_number(data["number"])
        return None

    def get_latest_block(self) -> Optional[dict]:
        """Get the latest block"""
        if self._meta["latest_block"] >= 0:
            return self.get_block_by_number(self._meta["latest_block"])
        return None

    def has_block(self, number: int) -> bool:
        """Check if block exists"""
        block_path = os.path.join(self.data_dir, "blocks", f"{number}.json")
        return os.path.exists(block_path)

    # Transaction operations

    def put_transaction(self, tx_data: dict) -> str:
        """Store a transaction"""
        tx_hash = tx_data.get("hash")
        if not tx_hash:
            tx_hash = to_hex(keccak(json.dumps(tx_data, sort_keys=True).encode()))
            tx_data["hash"] = tx_hash

        tx_path = os.path.join(self.data_dir, "transactions", f"{tx_hash}.json")
        with open(tx_path, "w") as f:
            json.dump(tx_data, f, indent=2)

        return tx_hash

    def get_transaction(self, tx_hash: str) -> Optional[dict]:
        """Get transaction by hash"""
        tx_path = os.path.join(self.data_dir, "transactions", f"{tx_hash}.json")
        if os.path.exists(tx_path):
            with open(tx_path, "r") as f:
                return json.load(f)
        return None

    # Receipt operations

    def put_receipt(self, tx_hash: str, receipt: dict):
        """Store a transaction receipt"""
        receipt_path = os.path.join(self.data_dir, "receipts", f"{tx_hash}.json")
        with open(receipt_path, "w") as f:
            json.dump(receipt, f, indent=2)

    def get_receipt(self, tx_hash: str) -> Optional[dict]:
        """Get transaction receipt"""
        receipt_path = os.path.join(self.data_dir, "receipts", f"{tx_hash}.json")
        if os.path.exists(receipt_path):
            with open(receipt_path, "r") as f:
                return json.load(f)
        return None

    # State operations

    def save_state(self, state_data: dict):
        """Save current state snapshot"""
        state_path = os.path.join(self.data_dir, "state", "latest.json")
        with open(state_path, "w") as f:
            json.dump(state_data, f, indent=2)

    def load_state(self) -> Optional[dict]:
        """Load state snapshot"""
        state_path = os.path.join(self.data_dir, "state", "latest.json")
        if os.path.exists(state_path):
            with open(state_path, "r") as f:
                return json.load(f)
        return None

    # Iteration

    def iter_blocks(self, start: int = 0, end: int = None) -> List[dict]:
        """Iterate over blocks"""
        if end is None:
            end = self._meta["latest_block"] + 1

        blocks = []
        for i in range(start, end):
            block = self.get_block_by_number(i)
            if block:
                blocks.append(block)
        return blocks

    def get_block_count(self) -> int:
        """Get total number of blocks"""
        return self._meta["latest_block"] + 1

    # Reset

    def reset(self):
        """Reset the chain (delete all data)"""
        import shutil
        if os.path.exists(self.data_dir):
            shutil.rmtree(self.data_dir)
        self._init_dirs()
        self._meta = {
            "chain_id": 1337,
            "latest_block": -1,
            "genesis_hash": None,
            "total_difficulty": 0,
        }
        self._save_meta()
