"""
NanoPy Keys - Ethereum-compatible key management
Uses eth-keys and eth-account for real Ethereum compatibility
"""

from typing import Tuple, Union
import secrets

from eth_keys import keys
from eth_keys.datatypes import PrivateKey, PublicKey, Signature
from eth_account import Account
from eth_account.messages import encode_defunct, SignableMessage
from eth_utils import keccak, to_bytes, to_hex, to_checksum_address


def generate_keypair() -> Tuple[str, str, str]:
    """
    Generate a new Ethereum keypair

    Returns:
        Tuple of (private_key, public_key, address)
        All as hex strings with 0x prefix
    """
    # Generate 32 random bytes for private key
    private_key_bytes = secrets.token_bytes(32)
    private_key = keys.PrivateKey(private_key_bytes)

    public_key = private_key.public_key
    address = public_key.to_checksum_address()

    return (
        to_hex(private_key.to_bytes()),
        to_hex(public_key.to_bytes()),
        address,
    )


def private_key_to_public_key(private_key: Union[str, bytes]) -> str:
    """
    Derive public key from private key

    Args:
        private_key: 32-byte private key as hex string or bytes

    Returns:
        Public key as hex string with 0x prefix
    """
    if isinstance(private_key, str):
        if private_key.startswith("0x"):
            private_key = private_key[2:]
        private_key = bytes.fromhex(private_key)

    pk = keys.PrivateKey(private_key)
    return to_hex(pk.public_key.to_bytes())


def public_key_to_address(public_key: Union[str, bytes]) -> str:
    """
    Derive address from public key

    Args:
        public_key: 64-byte public key as hex string or bytes

    Returns:
        Checksum address with 0x prefix
    """
    if isinstance(public_key, str):
        if public_key.startswith("0x"):
            public_key = public_key[2:]
        public_key = bytes.fromhex(public_key)

    pk = keys.PublicKey(public_key)
    return pk.to_checksum_address()


def sign_message(private_key: Union[str, bytes], message: Union[str, bytes]) -> str:
    """
    Sign a message with EIP-191 personal_sign

    Args:
        private_key: Private key as hex string or bytes
        message: Message to sign (string or bytes)

    Returns:
        Signature as hex string with 0x prefix
    """
    if isinstance(private_key, str):
        if private_key.startswith("0x"):
            private_key = private_key[2:]
        private_key = bytes.fromhex(private_key)

    if isinstance(message, str):
        message = message.encode()

    # EIP-191 encoding
    signable = encode_defunct(primitive=message)
    signed = Account.sign_message(signable, private_key)

    return to_hex(signed.signature)


def sign_message_hash(private_key: Union[str, bytes], message_hash: Union[str, bytes]) -> Tuple[int, int, int]:
    """
    Sign a message hash directly (no EIP-191 encoding)

    Args:
        private_key: Private key as hex string or bytes
        message_hash: 32-byte hash to sign

    Returns:
        Tuple of (v, r, s) signature components
    """
    if isinstance(private_key, str):
        if private_key.startswith("0x"):
            private_key = private_key[2:]
        private_key = bytes.fromhex(private_key)

    if isinstance(message_hash, str):
        if message_hash.startswith("0x"):
            message_hash = message_hash[2:]
        message_hash = bytes.fromhex(message_hash)

    pk = keys.PrivateKey(private_key)
    signature = pk.sign_msg_hash(message_hash)

    return signature.v, signature.r, signature.s


def recover_signer(message: Union[str, bytes], signature: Union[str, bytes]) -> str:
    """
    Recover signer address from EIP-191 signed message

    Args:
        message: Original message (string or bytes)
        signature: Signature as hex string or bytes

    Returns:
        Recovered address with 0x prefix
    """
    if isinstance(message, str):
        message = message.encode()

    if isinstance(signature, str):
        if signature.startswith("0x"):
            signature = signature[2:]
        signature = bytes.fromhex(signature)

    signable = encode_defunct(primitive=message)
    address = Account.recover_message(signable, signature=signature)

    return to_checksum_address(address)


def recover_signer_from_hash(message_hash: Union[str, bytes], v: int, r: int, s: int) -> str:
    """
    Recover signer address from message hash and signature components

    Args:
        message_hash: 32-byte hash that was signed
        v, r, s: Signature components

    Returns:
        Recovered address with 0x prefix
    """
    if isinstance(message_hash, str):
        if message_hash.startswith("0x"):
            message_hash = message_hash[2:]
        message_hash = bytes.fromhex(message_hash)

    signature = keys.Signature(vrs=(v, r, s))
    public_key = signature.recover_public_key_from_msg_hash(message_hash)

    return public_key.to_checksum_address()


def verify_signature(
    message: Union[str, bytes],
    signature: Union[str, bytes],
    address: str
) -> bool:
    """
    Verify an EIP-191 signed message

    Args:
        message: Original message (string or bytes)
        signature: Signature to verify
        address: Expected signer address

    Returns:
        True if signature is valid and from the given address
    """
    try:
        recovered = recover_signer(message, signature)
        return recovered.lower() == address.lower()
    except Exception:
        return False


def is_valid_private_key(private_key: Union[str, bytes]) -> bool:
    """Check if private key is valid"""
    try:
        if isinstance(private_key, str):
            if private_key.startswith("0x"):
                private_key = private_key[2:]
            private_key = bytes.fromhex(private_key)

        if len(private_key) != 32:
            return False

        keys.PrivateKey(private_key)
        return True
    except Exception:
        return False


def is_valid_address(address: str) -> bool:
    """Check if address is valid (checksum or not)"""
    try:
        if not address.startswith("0x"):
            return False
        if len(address) != 42:
            return False
        # Try to convert to checksum
        to_checksum_address(address)
        return True
    except Exception:
        return False


def checksum_address(address: str) -> str:
    """Convert address to checksum format"""
    return to_checksum_address(address)
