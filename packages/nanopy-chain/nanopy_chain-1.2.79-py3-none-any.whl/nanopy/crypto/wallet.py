"""
NanoPy Wallet - HD Wallet and account management
Compatible with BIP-39, BIP-32, BIP-44
"""

from typing import List, Optional, Tuple, Union
import secrets
import json

from eth_account import Account
from eth_account.hdaccount import generate_mnemonic, Mnemonic, seed_from_mnemonic
from eth_keys import keys
from eth_utils import to_hex, to_checksum_address, keccak

from nanopy.core.transaction import Transaction, SignedTransaction

# Enable HD wallet features
Account.enable_unaudited_hdwallet_features()


# BIP-44 derivation path for Ethereum
ETH_DERIVATION_PATH = "m/44'/60'/0'/0"


class Wallet:
    """
    Simple wallet for a single private key
    """

    def __init__(self, private_key: Union[str, bytes]):
        """
        Initialize wallet with private key

        Args:
            private_key: 32-byte private key as hex string or bytes
        """
        if isinstance(private_key, str):
            if private_key.startswith("0x"):
                private_key = private_key[2:]
            private_key = bytes.fromhex(private_key)

        self._private_key = private_key
        self._account = Account.from_key(private_key)

    @property
    def private_key(self) -> str:
        """Get private key as hex string"""
        return to_hex(self._private_key)

    @property
    def public_key(self) -> str:
        """Get public key as hex string"""
        pk = keys.PrivateKey(self._private_key)
        return to_hex(pk.public_key.to_bytes())

    @property
    def address(self) -> str:
        """Get checksum address"""
        return self._account.address

    @classmethod
    def create(cls) -> 'Wallet':
        """Create new random wallet"""
        private_key = secrets.token_bytes(32)
        return cls(private_key)

    @classmethod
    def from_keyfile(cls, path: str, password: str) -> 'Wallet':
        """Load wallet from encrypted keyfile (Web3 keystore)"""
        with open(path, 'r') as f:
            keyfile = json.load(f)
        private_key = Account.decrypt(keyfile, password)
        return cls(private_key)

    def to_keyfile(self, password: str) -> dict:
        """Export wallet as encrypted keyfile (Web3 keystore)"""
        return Account.encrypt(self._private_key, password)

    def save_keyfile(self, path: str, password: str):
        """Save wallet to encrypted keyfile"""
        keyfile = self.to_keyfile(password)
        with open(path, 'w') as f:
            json.dump(keyfile, f)

    def sign_transaction(self, tx: Transaction) -> SignedTransaction:
        """Sign a transaction"""
        return SignedTransaction.sign(tx, self._private_key)

    def sign_message(self, message: Union[str, bytes]) -> str:
        """Sign a message with EIP-191"""
        from nanopy.crypto.keys import sign_message
        return sign_message(self._private_key, message)

    def sign_typed_data(self, domain: dict, types: dict, message: dict) -> str:
        """Sign typed data with EIP-712"""
        from eth_account.messages import encode_typed_data
        signable = encode_typed_data(domain, types, message)
        signed = self._account.sign_message(signable)
        return to_hex(signed.signature)

    def __repr__(self) -> str:
        return f"Wallet({self.address})"


class HDWallet:
    """
    Hierarchical Deterministic Wallet (BIP-39/BIP-32/BIP-44)
    Generates multiple addresses from a single seed phrase
    """

    def __init__(self, mnemonic: str, passphrase: str = ""):
        """
        Initialize HD wallet with mnemonic phrase

        Args:
            mnemonic: BIP-39 mnemonic phrase (12 or 24 words)
            passphrase: Optional passphrase for additional security
        """
        self._mnemonic = mnemonic
        self._passphrase = passphrase
        self._seed = seed_from_mnemonic(mnemonic, passphrase)
        self._accounts: List[Account] = []

    @property
    def mnemonic(self) -> str:
        """Get mnemonic phrase (KEEP SECRET!)"""
        return self._mnemonic

    @classmethod
    def create(cls, num_words: int = 12, passphrase: str = "") -> 'HDWallet':
        """
        Create new HD wallet with random mnemonic

        Args:
            num_words: Number of words (12 or 24)
            passphrase: Optional passphrase

        Returns:
            New HDWallet instance
        """
        mnemonic = generate_mnemonic(num_words=num_words, lang="english")
        return cls(mnemonic, passphrase)

    @classmethod
    def generate(cls, num_words: int = 12, passphrase: str = "") -> 'HDWallet':
        """Alias for create()"""
        return cls.create(num_words, passphrase)

    @classmethod
    def from_mnemonic(cls, mnemonic: str, passphrase: str = "") -> 'HDWallet':
        """Create HD wallet from existing mnemonic"""
        # Validate mnemonic
        Mnemonic(language="english").check(mnemonic)
        return cls(mnemonic, passphrase)

    def derive_account(self, index: int = 0) -> Wallet:
        """
        Derive account at index using BIP-44 path

        Path: m/44'/60'/0'/0/{index}

        Args:
            index: Account index (0, 1, 2, ...)

        Returns:
            Wallet for derived account
        """
        path = f"{ETH_DERIVATION_PATH}/{index}"
        account = Account.from_mnemonic(self._mnemonic, passphrase=self._passphrase, account_path=path)
        return Wallet(account.key)

    def get_accounts(self, count: int = 10) -> List[Wallet]:
        """
        Get multiple derived accounts

        Args:
            count: Number of accounts to derive

        Returns:
            List of Wallet instances
        """
        return [self.derive_account(i) for i in range(count)]

    def get_addresses(self, count: int = 10) -> List[str]:
        """
        Get multiple derived addresses

        Args:
            count: Number of addresses to derive

        Returns:
            List of checksum addresses
        """
        return [self.derive_account(i).address for i in range(count)]

    def get_address(self, index: int = 0) -> str:
        """Get address at specific index"""
        return self.derive_account(index).address

    def __repr__(self) -> str:
        return f"HDWallet(words={len(self._mnemonic.split())})"


class KeyStore:
    """
    Manages multiple wallets/accounts
    """

    def __init__(self):
        self._wallets: dict[str, Wallet] = {}
        self._default: Optional[str] = None

    def add_wallet(self, wallet: Wallet, name: str = None) -> str:
        """Add wallet to keystore"""
        address = wallet.address
        if name:
            self._wallets[name] = wallet
        self._wallets[address] = wallet

        if self._default is None:
            self._default = address

        return address

    def create_wallet(self, name: str = None) -> Wallet:
        """Create and add new wallet"""
        wallet = Wallet.create()
        self.add_wallet(wallet, name)
        return wallet

    def get_wallet(self, address_or_name: str) -> Optional[Wallet]:
        """Get wallet by address or name"""
        return self._wallets.get(address_or_name)

    def get_default(self) -> Optional[Wallet]:
        """Get default wallet"""
        if self._default:
            return self._wallets.get(self._default)
        return None

    def set_default(self, address: str):
        """Set default wallet"""
        if address in self._wallets:
            self._default = address

    def list_addresses(self) -> List[str]:
        """List all wallet addresses"""
        return [addr for addr in self._wallets.keys() if addr.startswith("0x")]

    def remove_wallet(self, address: str):
        """Remove wallet from keystore"""
        self._wallets.pop(address, None)
        if self._default == address:
            addresses = self.list_addresses()
            self._default = addresses[0] if addresses else None

    def __len__(self) -> int:
        return len(self.list_addresses())

    def __contains__(self, address: str) -> bool:
        return address in self._wallets
