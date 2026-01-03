"""
NanoPy - Ethereum-compatible blockchain fork
"""

__version__ = "1.2.78"
__chain_id__ = 1337

from nanopy.core import Block, Transaction, Account, WorldState
from nanopy.crypto import generate_keypair, Wallet

__all__ = [
    "Block",
    "Transaction",
    "Account",
    "WorldState",
    "generate_keypair",
    "Wallet",
    "__version__",
    "__chain_id__",
]
