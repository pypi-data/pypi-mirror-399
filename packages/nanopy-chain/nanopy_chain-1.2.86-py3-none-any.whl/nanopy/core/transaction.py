"""
NanoPy Transaction - Ethereum-compatible transactions
Uses eth-account and eth-rlp for real Ethereum compatibility
"""

from dataclasses import dataclass, field
from typing import Optional, Union
import rlp
from rlp.sedes import big_endian_int, binary, Binary

from eth_typing import Address, Hash32, HexStr
from eth_utils import keccak, to_bytes, to_hex, to_checksum_address
from eth_keys import keys
from eth_account import Account as EthAccount
from eth_account.datastructures import SignedTransaction as EthSignedTx


class TransactionType:
    """EIP-2718 transaction types"""
    LEGACY = 0x00
    EIP2930 = 0x01  # Access list
    EIP1559 = 0x02  # Dynamic fee


@dataclass
class Transaction:
    """
    Ethereum-compatible transaction
    Supports Legacy, EIP-2930, and EIP-1559 transaction types
    """
    # Common fields
    nonce: int
    to: Optional[str]  # None for contract creation
    value: int  # In Wei
    data: bytes = b""
    chain_id: int = 1337

    # Gas fields
    gas: int = 21000

    # Legacy gas pricing
    gas_price: Optional[int] = None

    # EIP-1559 gas pricing
    max_fee_per_gas: Optional[int] = None
    max_priority_fee_per_gas: Optional[int] = None

    # EIP-2930 access list
    access_list: list = field(default_factory=list)

    # Transaction type (auto-detected)
    type: int = field(default=TransactionType.LEGACY)

    def __post_init__(self):
        """Determine transaction type based on fields"""
        if self.max_fee_per_gas is not None:
            self.type = TransactionType.EIP1559
            if self.gas_price is None:
                self.gas_price = self.max_fee_per_gas
        elif self.access_list:
            self.type = TransactionType.EIP2930
        else:
            self.type = TransactionType.LEGACY
            if self.gas_price is None:
                self.gas_price = 10 ** 9  # 1 Gwei default

    @property
    def effective_gas_price(self) -> int:
        """Get effective gas price for this transaction"""
        if self.type == TransactionType.EIP1559:
            return self.max_fee_per_gas or self.gas_price or 10**9
        return self.gas_price or 10**9

    def hash(self) -> bytes:
        """Calculate transaction hash (without signature)"""
        if self.type == TransactionType.LEGACY:
            # Legacy transaction hash
            items = [
                self.nonce,
                self.gas_price,
                self.gas,
                to_bytes(hexstr=self.to) if self.to else b"",
                self.value,
                self.data,
                self.chain_id,
                0,
                0,
            ]
        elif self.type == TransactionType.EIP1559:
            items = [
                self.chain_id,
                self.nonce,
                self.max_priority_fee_per_gas or 0,
                self.max_fee_per_gas or self.gas_price,
                self.gas,
                to_bytes(hexstr=self.to) if self.to else b"",
                self.value,
                self.data,
                self.access_list,
            ]
        else:
            items = [
                self.chain_id,
                self.nonce,
                self.gas_price,
                self.gas,
                to_bytes(hexstr=self.to) if self.to else b"",
                self.value,
                self.data,
                self.access_list,
            ]

        encoded = rlp.encode(items)
        if self.type != TransactionType.LEGACY:
            encoded = bytes([self.type]) + encoded

        return keccak(encoded)

    def to_dict(self) -> dict:
        """Convert to JSON-RPC compatible dict"""
        result = {
            "nonce": hex(self.nonce),
            "to": self.to,
            "value": hex(self.value),
            "data": to_hex(self.data),
            "gas": hex(self.gas),
            "chainId": hex(self.chain_id),
            "type": hex(self.type),
        }

        if self.type == TransactionType.EIP1559:
            result["maxFeePerGas"] = hex(self.max_fee_per_gas or 0)
            result["maxPriorityFeePerGas"] = hex(self.max_priority_fee_per_gas or 0)
        else:
            result["gasPrice"] = hex(self.gas_price or 0)

        if self.access_list:
            result["accessList"] = self.access_list

        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        """Create Transaction from JSON-RPC dict"""
        tx_type = int(data.get("type", "0x0"), 16)

        return cls(
            nonce=int(data.get("nonce", "0x0"), 16),
            to=data.get("to"),
            value=int(data.get("value", "0x0"), 16),
            data=to_bytes(hexstr=data.get("data", "0x") or data.get("input", "0x")),
            chain_id=int(data.get("chainId", "0x539"), 16),
            gas=int(data.get("gas", "0x5208"), 16),
            gas_price=int(data.get("gasPrice", "0x0"), 16) if data.get("gasPrice") else None,
            max_fee_per_gas=int(data.get("maxFeePerGas", "0x0"), 16) if data.get("maxFeePerGas") else None,
            max_priority_fee_per_gas=int(data.get("maxPriorityFeePerGas", "0x0"), 16) if data.get("maxPriorityFeePerGas") else None,
            access_list=data.get("accessList", []),
        )


@dataclass
class SignedTransaction:
    """
    Signed Ethereum transaction
    """
    transaction: Transaction
    v: int
    r: int
    s: int
    sender: str = ""

    def __post_init__(self):
        """Recover sender from signature if not provided"""
        if not self.sender:
            self.sender = self.recover_sender()

    def hash(self) -> bytes:
        """Transaction hash including signature"""
        tx = self.transaction

        if tx.type == TransactionType.LEGACY:
            items = [
                tx.nonce,
                tx.gas_price,
                tx.gas,
                to_bytes(hexstr=tx.to) if tx.to else b"",
                tx.value,
                tx.data,
                self.v,
                self.r,
                self.s,
            ]
            encoded = rlp.encode(items)
        else:
            if tx.type == TransactionType.EIP1559:
                items = [
                    tx.chain_id,
                    tx.nonce,
                    tx.max_priority_fee_per_gas or 0,
                    tx.max_fee_per_gas or tx.gas_price,
                    tx.gas,
                    to_bytes(hexstr=tx.to) if tx.to else b"",
                    tx.value,
                    tx.data,
                    tx.access_list,
                    self.v,
                    self.r,
                    self.s,
                ]
            else:
                items = [
                    tx.chain_id,
                    tx.nonce,
                    tx.gas_price,
                    tx.gas,
                    to_bytes(hexstr=tx.to) if tx.to else b"",
                    tx.value,
                    tx.data,
                    tx.access_list,
                    self.v,
                    self.r,
                    self.s,
                ]
            encoded = bytes([tx.type]) + rlp.encode(items)

        return keccak(encoded)

    def recover_sender(self) -> str:
        """Recover sender address from signature"""
        tx = self.transaction
        msg_hash = tx.hash()

        # Normalize v to recovery id (0 or 1)
        # v can be: 27/28 (pre-EIP155), 0/1, or chainId*2+35/36 (EIP-155)
        v = self.v
        if v >= 35:
            # EIP-155: v = chainId * 2 + 35 + recid
            v = (v - 35) % 2
        elif v >= 27:
            v = v - 27

        # Build signature with v as 0 or 1
        signature = keys.Signature(
            vrs=(v, self.r, self.s)
        )

        try:
            public_key = signature.recover_public_key_from_msg_hash(msg_hash)
            return to_checksum_address(public_key.to_address())
        except Exception:
            return ""

    @classmethod
    def sign(cls, transaction: Transaction, private_key: Union[str, bytes]) -> 'SignedTransaction':
        """Sign a transaction with a private key"""
        if isinstance(private_key, str):
            if private_key.startswith("0x"):
                private_key = private_key[2:]
            private_key = bytes.fromhex(private_key)

        # Create eth-account compatible tx dict
        tx_dict = {
            "nonce": transaction.nonce,
            "to": transaction.to,
            "value": transaction.value,
            "data": transaction.data,
            "gas": transaction.gas,
            "chainId": transaction.chain_id,
        }

        if transaction.type == TransactionType.EIP1559:
            tx_dict["maxFeePerGas"] = transaction.max_fee_per_gas
            tx_dict["maxPriorityFeePerGas"] = transaction.max_priority_fee_per_gas
            tx_dict["type"] = 2
        else:
            tx_dict["gasPrice"] = transaction.gas_price

        if transaction.access_list:
            tx_dict["accessList"] = transaction.access_list

        # Sign with eth-account
        signed = EthAccount.sign_transaction(tx_dict, private_key)

        return cls(
            transaction=transaction,
            v=signed.v,
            r=int.from_bytes(signed.r, 'big') if isinstance(signed.r, bytes) else signed.r,
            s=int.from_bytes(signed.s, 'big') if isinstance(signed.s, bytes) else signed.s,
            sender=EthAccount.from_key(private_key).address,
        )

    def to_dict(self) -> dict:
        """Convert to JSON-RPC compatible dict"""
        result = self.transaction.to_dict()
        result.update({
            "hash": to_hex(self.hash()),
            "from": self.sender,
            "v": hex(self.v),
            "r": hex(self.r),
            "s": hex(self.s),
        })
        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'SignedTransaction':
        """Create SignedTransaction from JSON-RPC dict"""
        tx = Transaction.from_dict(data)
        return cls(
            transaction=tx,
            v=int(data.get("v", "0x0"), 16),
            r=int(data.get("r", "0x0"), 16),
            s=int(data.get("s", "0x0"), 16),
            sender=data.get("from", ""),
        )

    def raw(self) -> bytes:
        """Get raw transaction bytes for broadcasting"""
        tx = self.transaction

        if tx.type == TransactionType.LEGACY:
            items = [
                tx.nonce,
                tx.gas_price,
                tx.gas,
                to_bytes(hexstr=tx.to) if tx.to else b"",
                tx.value,
                tx.data,
                self.v,
                self.r,
                self.s,
            ]
            return rlp.encode(items)
        else:
            if tx.type == TransactionType.EIP1559:
                items = [
                    tx.chain_id,
                    tx.nonce,
                    tx.max_priority_fee_per_gas or 0,
                    tx.max_fee_per_gas or tx.gas_price,
                    tx.gas,
                    to_bytes(hexstr=tx.to) if tx.to else b"",
                    tx.value,
                    tx.data,
                    tx.access_list,
                    self.v,
                    self.r,
                    self.s,
                ]
            else:
                items = [
                    tx.chain_id,
                    tx.nonce,
                    tx.gas_price,
                    tx.gas,
                    to_bytes(hexstr=tx.to) if tx.to else b"",
                    tx.value,
                    tx.data,
                    tx.access_list,
                    self.v,
                    self.r,
                    self.s,
                ]
            return bytes([tx.type]) + rlp.encode(items)


class TransactionReceipt:
    """Transaction execution receipt"""

    def __init__(
        self,
        tx_hash: bytes,
        block_hash: bytes,
        block_number: int,
        tx_index: int,
        sender: str,
        to: Optional[str],
        contract_address: Optional[str],
        gas_used: int,
        cumulative_gas_used: int,
        status: int,  # 1 = success, 0 = failure
        logs: list = None,
        logs_bloom: bytes = None,
    ):
        self.tx_hash = tx_hash
        self.block_hash = block_hash
        self.block_number = block_number
        self.tx_index = tx_index
        self.sender = sender
        self.to = to
        self.contract_address = contract_address
        self.gas_used = gas_used
        self.cumulative_gas_used = cumulative_gas_used
        self.status = status
        self.logs = logs or []
        self.logs_bloom = logs_bloom or bytes(256)

    def to_dict(self) -> dict:
        return {
            "transactionHash": to_hex(self.tx_hash),
            "blockHash": to_hex(self.block_hash),
            "blockNumber": hex(self.block_number),
            "transactionIndex": hex(self.tx_index),
            "from": self.sender,
            "to": self.to,
            "contractAddress": self.contract_address,
            "gasUsed": hex(self.gas_used),
            "cumulativeGasUsed": hex(self.cumulative_gas_used),
            "status": hex(self.status),
            "logs": self.logs,
            "logsBloom": to_hex(self.logs_bloom),
        }
