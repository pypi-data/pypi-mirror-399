"""
NanoPy StateDB - Persistent state storage
Stores account balances, nonces, code, and storage
"""

import json
import os
from typing import Dict, Optional
from eth_utils import to_hex, to_checksum_address


class PersistentStateDB:
    """
    Persistent storage for blockchain state
    Stores accounts and their data on disk

    Structure:
        state_dir/
            accounts/
                0xabc...json  (account data)
            code/
                0xabc...bin   (contract bytecode)
            storage/
                0xabc/
                    key.json  (storage slots)
    """

    def __init__(self, state_dir: str = "./chaindata/state"):
        self.state_dir = state_dir
        self._init_dirs()
        self._cache: Dict[str, dict] = {}

    def _init_dirs(self):
        """Create directory structure"""
        dirs = [
            self.state_dir,
            os.path.join(self.state_dir, "accounts"),
            os.path.join(self.state_dir, "code"),
            os.path.join(self.state_dir, "storage"),
        ]
        for d in dirs:
            os.makedirs(d, exist_ok=True)

    def _normalize_address(self, address: str) -> str:
        """Normalize address to checksum format"""
        if not address.startswith("0x"):
            address = "0x" + address
        return to_checksum_address(address)

    # Account operations

    def get_account(self, address: str) -> dict:
        """Get account data"""
        address = self._normalize_address(address)

        # Check cache first
        if address in self._cache:
            return self._cache[address]

        # Load from disk
        account_path = os.path.join(self.state_dir, "accounts", f"{address}.json")
        if os.path.exists(account_path):
            with open(account_path, "r") as f:
                account = json.load(f)
                self._cache[address] = account
                return account

        # Return empty account
        return {
            "balance": 0,
            "nonce": 0,
            "code_hash": None,
            "storage_root": None,
        }

    def set_account(self, address: str, account_data: dict):
        """Set account data"""
        address = self._normalize_address(address)

        # Update cache
        self._cache[address] = account_data

        # Save to disk
        account_path = os.path.join(self.state_dir, "accounts", f"{address}.json")
        with open(account_path, "w") as f:
            json.dump(account_data, f, indent=2)

    def get_balance(self, address: str) -> int:
        """Get account balance"""
        return self.get_account(address).get("balance", 0)

    def set_balance(self, address: str, balance: int):
        """Set account balance"""
        account = self.get_account(address)
        account["balance"] = balance
        self.set_account(address, account)

    def get_nonce(self, address: str) -> int:
        """Get account nonce"""
        return self.get_account(address).get("nonce", 0)

    def set_nonce(self, address: str, nonce: int):
        """Set account nonce"""
        account = self.get_account(address)
        account["nonce"] = nonce
        self.set_account(address, account)

    def increment_nonce(self, address: str) -> int:
        """Increment and return new nonce"""
        nonce = self.get_nonce(address)
        self.set_nonce(address, nonce + 1)
        return nonce + 1

    # Code operations

    def get_code(self, address: str) -> bytes:
        """Get contract code"""
        address = self._normalize_address(address)
        code_path = os.path.join(self.state_dir, "code", f"{address}.bin")
        if os.path.exists(code_path):
            with open(code_path, "rb") as f:
                return f.read()
        return b""

    def set_code(self, address: str, code: bytes):
        """Set contract code"""
        address = self._normalize_address(address)
        code_path = os.path.join(self.state_dir, "code", f"{address}.bin")
        with open(code_path, "wb") as f:
            f.write(code)

        # Update account code hash
        from eth_utils import keccak
        account = self.get_account(address)
        account["code_hash"] = to_hex(keccak(code))
        self.set_account(address, account)

    def has_code(self, address: str) -> bool:
        """Check if address has contract code"""
        return len(self.get_code(address)) > 0

    # Storage operations

    def get_storage(self, address: str, key: str) -> int:
        """Get storage value at key"""
        address = self._normalize_address(address)
        storage_dir = os.path.join(self.state_dir, "storage", address)

        if not os.path.exists(storage_dir):
            return 0

        # Normalize key
        if isinstance(key, int):
            key = hex(key)

        key_path = os.path.join(storage_dir, f"{key}.json")
        if os.path.exists(key_path):
            with open(key_path, "r") as f:
                data = json.load(f)
                return data.get("value", 0)
        return 0

    def set_storage(self, address: str, key: str, value: int):
        """Set storage value at key"""
        address = self._normalize_address(address)
        storage_dir = os.path.join(self.state_dir, "storage", address)
        os.makedirs(storage_dir, exist_ok=True)

        # Normalize key
        if isinstance(key, int):
            key = hex(key)

        key_path = os.path.join(storage_dir, f"{key}.json")
        with open(key_path, "w") as f:
            json.dump({"value": value}, f)

    def get_all_storage(self, address: str) -> dict:
        """Get all storage slots and values for an address"""
        address = self._normalize_address(address)
        storage_dir = os.path.join(self.state_dir, "storage", address)
        result = {}

        if not os.path.exists(storage_dir):
            return result

        for filename in os.listdir(storage_dir):
            if filename.endswith(".json"):
                slot_hex = filename[:-5]  # Remove .json
                slot = int(slot_hex, 16)
                filepath = os.path.join(storage_dir, filename)
                with open(filepath, "r") as f:
                    data = json.load(f)
                    result[slot] = data.get("value", 0)

        return result

    def persist_storage(self, address: str, storage_trie):
        """Persist all storage from a StorageTrie to disk"""
        address = self._normalize_address(address)
        storage_dir = os.path.join(self.state_dir, "storage", address)
        os.makedirs(storage_dir, exist_ok=True)

        # Use get_all_storage() to get tracked slot->value pairs
        if hasattr(storage_trie, 'get_all_storage'):
            storage_data = storage_trie.get_all_storage()
            for slot, value in storage_data.items():
                slot_hex = hex(slot)
                slot_path = os.path.join(storage_dir, f"{slot_hex}.json")
                with open(slot_path, "w") as f:
                    json.dump({"value": value}, f)

    # Utility methods

    def account_exists(self, address: str) -> bool:
        """Check if account exists (has balance, nonce, or code)"""
        account = self.get_account(address)
        return (
            account.get("balance", 0) > 0 or
            account.get("nonce", 0) > 0 or
            account.get("code_hash") is not None
        )

    def list_accounts(self) -> list:
        """List all accounts with data"""
        accounts_dir = os.path.join(self.state_dir, "accounts")
        accounts = []
        if os.path.exists(accounts_dir):
            for filename in os.listdir(accounts_dir):
                if filename.endswith(".json"):
                    address = filename[:-5]  # Remove .json
                    accounts.append(address)
        return accounts

    def get_all_balances(self) -> Dict[str, int]:
        """Get all account balances"""
        balances = {}
        for address in self.list_accounts():
            balances[address] = self.get_balance(address)
        return balances

    def clear_cache(self):
        """Clear in-memory cache"""
        self._cache.clear()

    def flush(self):
        """Flush all cached data to disk"""
        for address, account in self._cache.items():
            account_path = os.path.join(self.state_dir, "accounts", f"{address}.json")
            with open(account_path, "w") as f:
                json.dump(account, f, indent=2)

    def export_state(self) -> dict:
        """Export full state as dictionary"""
        state = {"accounts": {}}
        for address in self.list_accounts():
            state["accounts"][address] = {
                "balance": self.get_balance(address),
                "nonce": self.get_nonce(address),
                "code": to_hex(self.get_code(address)) if self.has_code(address) else None,
            }
        return state

    def import_state(self, state: dict):
        """Import state from dictionary"""
        for address, data in state.get("accounts", {}).items():
            self.set_balance(address, data.get("balance", 0))
            self.set_nonce(address, data.get("nonce", 0))
            if data.get("code"):
                code = bytes.fromhex(data["code"][2:]) if data["code"].startswith("0x") else bytes.fromhex(data["code"])
                self.set_code(address, code)
