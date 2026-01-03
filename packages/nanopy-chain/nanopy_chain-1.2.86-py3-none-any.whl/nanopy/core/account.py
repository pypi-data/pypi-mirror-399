"""
NanoPy Account - Ethereum-compatible accounts
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
import rlp

from eth_utils import keccak, to_hex, to_bytes
from eth_typing import Address


# Empty code hash (keccak256 of empty bytes)
EMPTY_CODE_HASH = keccak(b"")

# Empty storage root (keccak256 of RLP encoded empty trie)
EMPTY_STORAGE_ROOT = keccak(rlp.encode(b""))


@dataclass
class Account:
    """
    Ethereum-compatible account state

    Two types of accounts:
    - EOA (Externally Owned Account): Controlled by private key
    - Contract Account: Contains code, controlled by code execution
    """
    nonce: int = 0
    balance: int = 0
    storage_root: bytes = field(default_factory=lambda: EMPTY_STORAGE_ROOT)
    code_hash: bytes = field(default_factory=lambda: EMPTY_CODE_HASH)

    # Not part of account state, but useful
    address: str = ""
    code: bytes = b""
    storage: Dict[bytes, bytes] = field(default_factory=dict)

    @property
    def is_empty(self) -> bool:
        """Account is empty if nonce=0, balance=0, and no code"""
        return (
            self.nonce == 0 and
            self.balance == 0 and
            self.code_hash == EMPTY_CODE_HASH
        )

    @property
    def is_contract(self) -> bool:
        """Account is a contract if it has code"""
        return self.code_hash != EMPTY_CODE_HASH

    @property
    def is_eoa(self) -> bool:
        """Account is EOA if it has no code"""
        return not self.is_contract

    def rlp_encode(self) -> bytes:
        """Encode account state as RLP (for state trie)"""
        return rlp.encode([
            self.nonce,
            self.balance,
            self.storage_root,
            self.code_hash,
        ])

    @classmethod
    def rlp_decode(cls, data: bytes, address: str = "") -> 'Account':
        """Decode account from RLP"""
        items = rlp.decode(data)
        return cls(
            nonce=int.from_bytes(items[0], 'big') if items[0] else 0,
            balance=int.from_bytes(items[1], 'big') if items[1] else 0,
            storage_root=items[2] if items[2] else EMPTY_STORAGE_ROOT,
            code_hash=items[3] if items[3] else EMPTY_CODE_HASH,
            address=address,
        )

    def to_dict(self) -> dict:
        """Convert to JSON-RPC compatible dict"""
        return {
            "address": self.address,
            "nonce": hex(self.nonce),
            "balance": hex(self.balance),
            "storageRoot": to_hex(self.storage_root),
            "codeHash": to_hex(self.code_hash),
            "isContract": self.is_contract,
        }

    def copy(self) -> 'Account':
        """Create a copy of this account"""
        return Account(
            nonce=self.nonce,
            balance=self.balance,
            storage_root=self.storage_root,
            code_hash=self.code_hash,
            address=self.address,
            code=self.code,
            storage=self.storage.copy(),
        )


def compute_contract_address(sender: str, nonce: int) -> str:
    """
    Compute CREATE contract address
    Address = keccak256(rlp([sender, nonce]))[12:]
    """
    sender_bytes = to_bytes(hexstr=sender)
    encoded = rlp.encode([sender_bytes, nonce])
    return "0x" + keccak(encoded)[12:].hex()


def compute_create2_address(sender: str, salt: bytes, init_code_hash: bytes) -> str:
    """
    Compute CREATE2 contract address (EIP-1014)
    Address = keccak256(0xff ++ sender ++ salt ++ keccak256(init_code))[12:]
    """
    sender_bytes = to_bytes(hexstr=sender)
    data = b"\xff" + sender_bytes + salt + init_code_hash
    return "0x" + keccak(data)[12:].hex()


class AccountDB:
    """
    In-memory account database
    For production, use LevelDB or similar
    """

    def __init__(self):
        self._accounts: Dict[str, Account] = {}
        self._code: Dict[bytes, bytes] = {}  # code_hash -> code

    def get_account(self, address: str) -> Account:
        """Get account, create empty if not exists"""
        address = address.lower()
        if address not in self._accounts:
            self._accounts[address] = Account(address=address)
        return self._accounts[address]

    def set_account(self, address: str, account: Account):
        """Set account state"""
        address = address.lower()
        account.address = address
        self._accounts[address] = account

    def account_exists(self, address: str) -> bool:
        """Check if account exists and is not empty"""
        address = address.lower()
        if address not in self._accounts:
            return False
        return not self._accounts[address].is_empty

    def get_balance(self, address: str) -> int:
        return self.get_account(address).balance

    def set_balance(self, address: str, balance: int):
        account = self.get_account(address)
        account.balance = balance

    def add_balance(self, address: str, amount: int):
        account = self.get_account(address)
        account.balance += amount

    def sub_balance(self, address: str, amount: int) -> bool:
        account = self.get_account(address)
        if account.balance >= amount:
            account.balance -= amount
            return True
        return False

    def get_nonce(self, address: str) -> int:
        return self.get_account(address).nonce

    def set_nonce(self, address: str, nonce: int):
        account = self.get_account(address)
        account.nonce = nonce

    def increment_nonce(self, address: str):
        account = self.get_account(address)
        account.nonce += 1

    def get_code(self, address: str) -> bytes:
        account = self.get_account(address)
        if account.code:
            return account.code
        return self._code.get(account.code_hash, b"")

    def set_code(self, address: str, code: bytes):
        account = self.get_account(address)
        account.code = code
        account.code_hash = keccak(code) if code else EMPTY_CODE_HASH
        if code:
            self._code[account.code_hash] = code

    def get_storage(self, address: str, key: bytes) -> bytes:
        account = self.get_account(address)
        return account.storage.get(key, bytes(32))

    def set_storage(self, address: str, key: bytes, value: bytes):
        account = self.get_account(address)
        if value == bytes(32):
            account.storage.pop(key, None)
        else:
            account.storage[key] = value

    def delete_account(self, address: str):
        """Delete account (SELFDESTRUCT)"""
        address = address.lower()
        self._accounts.pop(address, None)

    def snapshot(self) -> 'AccountDB':
        """Create a snapshot for reverting"""
        snap = AccountDB()
        for addr, acc in self._accounts.items():
            snap._accounts[addr] = acc.copy()
        snap._code = self._code.copy()
        return snap

    def revert(self, snapshot: 'AccountDB'):
        """Revert to snapshot"""
        self._accounts = snapshot._accounts
        self._code = snapshot._code
