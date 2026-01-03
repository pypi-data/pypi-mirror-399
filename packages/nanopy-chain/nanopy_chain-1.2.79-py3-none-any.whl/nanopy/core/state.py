"""
NanoPy State - World State Management
Uses Merkle Patricia Trie for Ethereum compatibility
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import rlp

from eth_utils import keccak, to_hex, to_bytes, to_checksum_address
from trie import HexaryTrie

from nanopy.core.account import Account, AccountDB, EMPTY_CODE_HASH, EMPTY_STORAGE_ROOT


class StorageTrie:
    """
    Storage trie for a single contract
    Maps 32-byte keys to 32-byte values
    """

    def __init__(self, root: bytes = None):
        if root is None:
            self._trie = HexaryTrie({})
        else:
            self._trie = HexaryTrie({}, root_hash=root)
        # Track all storage slots that have been set (slot -> value)
        self._storage_cache: Dict[int, int] = {}

    @property
    def root_hash(self) -> bytes:
        return self._trie.root_hash

    def get(self, key: bytes) -> bytes:
        """Get storage value (32 bytes)"""
        key_hash = keccak(key.rjust(32, b'\x00'))
        try:
            value = self._trie[key_hash]
            if value:
                return rlp.decode(value).rjust(32, b'\x00')
        except KeyError:
            pass
        return bytes(32)

    def set(self, key: bytes, value: bytes):
        """Set storage value"""
        key_hash = keccak(key.rjust(32, b'\x00'))
        # Track the slot and value in cache for persistence
        slot = int.from_bytes(key.rjust(32, b'\x00'), 'big')
        val_int = int.from_bytes(value, 'big')
        self._storage_cache[slot] = val_int

        if value == bytes(32) or val_int == 0:
            # Delete zero values
            try:
                del self._trie[key_hash]
            except KeyError:
                pass
        else:
            # RLP encode and store
            self._trie[key_hash] = rlp.encode(value.lstrip(b'\x00') or b'\x00')

    def get_all_storage(self) -> Dict[int, int]:
        """Get all storage slots and values for persistence"""
        return self._storage_cache.copy()

    def copy(self) -> 'StorageTrie':
        """Create a copy of this trie"""
        new_trie = StorageTrie()
        # Copy the underlying db dict properly - HexaryTrie stores in .db
        new_trie._trie = HexaryTrie(dict(self._trie.db), root_hash=self.root_hash)
        # Copy the storage cache too
        new_trie._storage_cache = self._storage_cache.copy()
        return new_trie


class StateDB:
    """
    State Database - manages world state with Merkle Patricia Trie

    This is the main interface for reading/writing account state.
    Supports snapshots and reverts for transaction execution.
    """

    def __init__(self, state_root: bytes = None):
        self._account_db = AccountDB()
        self._storage_tries: Dict[str, StorageTrie] = {}
        if state_root is None:
            self._account_trie = HexaryTrie({})
        else:
            self._account_trie = HexaryTrie({}, root_hash=state_root)
        self._snapshots: List[Tuple[AccountDB, Dict[str, StorageTrie], bytes]] = []

    @property
    def state_root(self) -> bytes:
        """Get current state root"""
        return self._account_trie.root_hash

    def _get_storage_trie(self, address: str) -> StorageTrie:
        """Get or create storage trie for address"""
        address = address.lower()
        if address not in self._storage_tries:
            account = self._account_db.get_account(address)
            if account.storage_root == EMPTY_STORAGE_ROOT:
                self._storage_tries[address] = StorageTrie()
            else:
                self._storage_tries[address] = StorageTrie(account.storage_root)
        return self._storage_tries[address]

    def _update_account_trie(self, address: str):
        """Update account in trie"""
        address = address.lower()
        account = self._account_db.get_account(address)

        # Update storage root
        if address in self._storage_tries:
            account.storage_root = self._storage_tries[address].root_hash

        # Encode and store in trie
        key = keccak(to_bytes(hexstr=address))
        if account.is_empty:
            try:
                del self._account_trie[key]
            except KeyError:
                pass
        else:
            self._account_trie[key] = account.rlp_encode()

    # Account operations

    def get_account(self, address: str) -> Account:
        return self._account_db.get_account(address)

    def account_exists(self, address: str) -> bool:
        return self._account_db.account_exists(address)

    # Balance operations

    def get_balance(self, address: str) -> int:
        return self._account_db.get_balance(address)

    def set_balance(self, address: str, balance: int):
        self._account_db.set_balance(address, balance)
        self._update_account_trie(address)

    def add_balance(self, address: str, amount: int):
        self._account_db.add_balance(address, amount)
        self._update_account_trie(address)

    def sub_balance(self, address: str, amount: int) -> bool:
        result = self._account_db.sub_balance(address, amount)
        if result:
            self._update_account_trie(address)
        return result

    def transfer(self, sender: str, recipient: str, amount: int) -> bool:
        """Transfer balance from sender to recipient"""
        if self.sub_balance(sender, amount):
            self.add_balance(recipient, amount)
            return True
        return False

    # Nonce operations

    def get_nonce(self, address: str) -> int:
        return self._account_db.get_nonce(address)

    def set_nonce(self, address: str, nonce: int):
        self._account_db.set_nonce(address, nonce)
        self._update_account_trie(address)

    def increment_nonce(self, address: str):
        self._account_db.increment_nonce(address)
        self._update_account_trie(address)

    # Code operations

    def get_code(self, address: str) -> bytes:
        return self._account_db.get_code(address)

    def get_code_hash(self, address: str) -> bytes:
        return self._account_db.get_account(address).code_hash

    def set_code(self, address: str, code: bytes):
        self._account_db.set_code(address, code)
        self._update_account_trie(address)

    # Storage operations

    def get_storage(self, address: str, key: bytes) -> bytes:
        """Get 32-byte storage value"""
        trie = self._get_storage_trie(address)
        return trie.get(key)

    def set_storage(self, address: str, key: bytes, value: bytes):
        """Set 32-byte storage value"""
        trie = self._get_storage_trie(address)
        trie.set(key, value)
        self._update_account_trie(address)

    def get_storage_int(self, address: str, slot: int) -> int:
        """Get storage as integer"""
        key = slot.to_bytes(32, 'big')
        value = self.get_storage(address, key)
        return int.from_bytes(value, 'big')

    def set_storage_int(self, address: str, slot: int, value: int):
        """Set storage as integer"""
        key = slot.to_bytes(32, 'big')
        val = value.to_bytes(32, 'big')
        self.set_storage(address, key, val)

    def get_storage_trie(self, address: str) -> 'StorageTrie':
        """Get storage trie for address (or None if not exists)"""
        address = address.lower()
        return self._storage_tries.get(address)

    def get_all_storage_addresses(self) -> list:
        """Get all addresses that have storage tries (for persistence)"""
        return list(self._storage_tries.keys())

    # Account lifecycle

    def create_account(self, address: str, balance: int = 0, code: bytes = b""):
        """Create new account"""
        account = Account(
            address=address,
            balance=balance,
        )
        self._account_db.set_account(address, account)
        if code:
            self.set_code(address, code)
        self._update_account_trie(address)

    def delete_account(self, address: str):
        """Delete account (SELFDESTRUCT)"""
        self._account_db.delete_account(address)
        self._storage_tries.pop(address.lower(), None)
        self._update_account_trie(address)

    # Snapshots for transaction execution

    def snapshot(self) -> int:
        """Create snapshot, returns snapshot ID"""
        # Copy the trie database to allow proper revert
        trie_db_copy = dict(self._account_trie.db)
        snap = (
            self._account_db.snapshot(),
            {k: v.copy() for k, v in self._storage_tries.items()},
            self._account_trie.root_hash,
            trie_db_copy,
        )
        self._snapshots.append(snap)
        return len(self._snapshots) - 1

    def revert(self, snapshot_id: int):
        """Revert to snapshot"""
        if snapshot_id < len(self._snapshots):
            acc_snap, storage_snap, root, trie_db = self._snapshots[snapshot_id]
            self._account_db.revert(acc_snap)
            self._storage_tries = storage_snap
            # Restore trie with the saved database
            self._account_trie = HexaryTrie(trie_db, root_hash=root)
            self._snapshots = self._snapshots[:snapshot_id]

    def commit(self, snapshot_id: int):
        """Commit changes (discard snapshot)"""
        if snapshot_id < len(self._snapshots):
            self._snapshots = self._snapshots[:snapshot_id]

    def copy(self) -> 'StateDB':
        """Create a copy of the state"""
        new_state = StateDB()
        new_state._account_db = self._account_db.snapshot()
        new_state._storage_tries = {k: v.copy() for k, v in self._storage_tries.items()}
        # Create trie with same root hash - this shares underlying data but is fine for read-only copies
        new_state._account_trie = HexaryTrie({}, root_hash=self.state_root)
        return new_state


class WorldState:
    """
    High-level world state manager
    Wraps StateDB with additional functionality
    """

    def __init__(self, genesis_alloc: Dict[str, int] = None):
        self.db = StateDB()
        self.block_number = 0
        self.block_hash = bytes(32)
        self.coinbase = "0x" + "0" * 40
        self.timestamp = 0
        self.difficulty = 1
        self.gas_limit = 30_000_000

        # Apply genesis allocations
        if genesis_alloc:
            for address, balance in genesis_alloc.items():
                self.db.set_balance(address, balance)

    @property
    def state_root(self) -> bytes:
        return self.db.state_root

    def set_block_context(
        self,
        block_number: int,
        block_hash: bytes,
        coinbase: str,
        timestamp: int,
        difficulty: int,
        gas_limit: int,
    ):
        """Set block context for EVM execution"""
        self.block_number = block_number
        self.block_hash = block_hash
        self.coinbase = coinbase
        self.timestamp = timestamp
        self.difficulty = difficulty
        self.gas_limit = gas_limit

    def to_dict(self) -> dict:
        """Export state as dict"""
        result = {}
        for addr, account in self.db._account_db._accounts.items():
            result[addr] = account.to_dict()
        return result
