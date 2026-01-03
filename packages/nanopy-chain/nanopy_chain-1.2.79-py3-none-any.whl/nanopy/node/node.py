"""
NanoPy Node - Main blockchain node implementation
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import time
import threading
import secrets

from eth_utils import to_hex, to_bytes, keccak

logger = logging.getLogger(__name__)
from eth_account import Account as EthAccount

from nanopy.core.block import Block
from nanopy.core.transaction import Transaction, SignedTransaction, TransactionReceipt
from nanopy.core.state import StateDB, WorldState
from nanopy.crypto.wallet import Wallet, KeyStore
from nanopy.vm.evm import NanoPyEVM, ExecutionContext
from nanopy.network.txpool import TxPool
from nanopy.network.rpc import RPC, start_rpc
from nanopy.consensus.pow import ProofOfWork
from nanopy.consensus.pos import ProofOfStake
from nanopy.consensus.engine import ConsensusEngine
from nanopy.storage.chaindb import ChainDB
from nanopy.storage.statedb import PersistentStateDB

# libp2p P2P networking (required)
LIBP2P_AVAILABLE = False
try:
    from nanopy.network.libp2p_network import (
        LibP2PNetwork, LibP2PConfig, run_libp2p_network, LIBP2P_AVAILABLE
    )
except ImportError:
    pass


@dataclass
class NodeConfig:
    """Node configuration"""
    chain_id: int = 1337
    network_id: int = 1337
    gas_limit: int = 30_000_000
    gas_price: int = 1000  # 1000 wei (very cheap gas for gaming)
    coinbase: str = ""
    rpc_host: str = "0.0.0.0"
    rpc_port: int = 8545
    p2p_host: str = "0.0.0.0"
    p2p_port: int = 30303
    bootnodes: list = None
    max_peers: int = 25
    block_time: int = 12  # seconds
    data_dir: str = "./chaindata"  # Persistent storage directory
    persist: bool = True  # Enable persistence
    genesis_file: str = ""  # Path to genesis.json
    consensus: str = "pow"  # pow or pos
    validator_key: str = ""  # Private key for validator
    staking_contract: str = ""  # Address of staking contract for PoS
    use_libp2p: bool = True  # Use libp2p instead of legacy TCP P2P
    p2p_private_key: str = ""  # Private key for P2P identity (optional)


class NanoPyNode:
    """
    NanoPy Blockchain Node

    A full Ethereum-compatible blockchain node supporting:
    - EVM execution
    - Proof of Stake validation
    - JSON-RPC API (HTTP + WebSocket)
    - Transaction pool
    - P2P networking (libp2p)
    - Account management
    """

    def __init__(self, config: NodeConfig = None):
        self.config = config or NodeConfig()

        # Core components
        self.chain_id = self.config.chain_id
        self.state = StateDB()
        self.world = WorldState()
        self.txpool = TxPool()
        self.consensus = ConsensusEngine(self.chain_id)

        # Persistent storage
        self.chaindb = ChainDB(self.config.data_dir) if self.config.persist else None
        self.statedb = PersistentStateDB(f"{self.config.data_dir}/state") if self.config.persist else None

        # Blockchain storage (in-memory cache)
        self.blocks: List[Block] = []
        self.blocks_by_hash: Dict[bytes, Block] = {}
        self.receipts: Dict[str, TransactionReceipt] = {}
        self.transactions: Dict[str, SignedTransaction] = {}

        # Account management
        self.keystore = KeyStore()
        self.coinbase = self.config.coinbase

        # Consensus
        self.pow = ProofOfWork()
        self.pos = ProofOfStake(
            state=self.state,
            staking_contract=self.config.staking_contract or None,
            node=self
        )
        self._validating = False
        self._validator_thread: Optional[threading.Thread] = None

        # Filters (for eth_newFilter, etc.)
        self._filters: Dict[str, dict] = {}
        self._filter_counter = 0

        # Dev mode state
        self._snapshots: List[tuple] = []
        self._next_block_timestamp: Optional[int] = None
        self._time_offset = 0

        # P2P Network
        self.p2p: Optional[P2PNetwork] = None

        # RPC Server (HTTP + WebSocket on same port)
        self.rpc_server: Optional[RPC] = None
        self._rpc_loop: Optional[asyncio.AbstractEventLoop] = None

        # Initialize or load chain
        self._init_chain()

    def _init_chain(self):
        """Initialize chain - load from disk or create genesis"""
        if self.chaindb and self.chaindb.latest_block_number >= 0:
            # Load existing chain
            self._load_chain()
        else:
            # Create new chain with genesis
            self._init_genesis()

    def _load_chain(self):
        """Load chain from persistent storage"""
        for i in range(self.chaindb.latest_block_number + 1):
            block_data = self.chaindb.get_block_by_number(i)
            if block_data:
                block = Block.from_dict(block_data)
                self.blocks.append(block)
                self.blocks_by_hash[block.hash] = block

        if self.statedb:
            for address in self.statedb.list_accounts():
                balance = self.statedb.get_balance(address)
                nonce = self.statedb.get_nonce(address)
                self.state.set_balance(address, balance)
                self.state.set_nonce(address, nonce)
                code = self.statedb.get_code(address)
                if code:
                    self.state.set_code(address, code)
                # Load storage for contracts
                storage = self.statedb.get_all_storage(address)
                for slot, value in storage.items():
                    self.state.set_storage_int(address, slot, value)

    def _init_genesis(self):
        """Initialize genesis block and state"""
        import json
        import os

        genesis_data = None

        # NanoPy Mainnet Genesis (chain_id 7770) - load from embedded JSON file
        # Pyralis Testnet Genesis (chain_id 77777)
        genesis_file = None
        if self.chain_id == 7770:
            genesis_file = os.path.join(os.path.dirname(__file__), "..", "genesis", "mainnet.json")
        elif self.chain_id == 77777:
            genesis_file = os.path.join(os.path.dirname(__file__), "..", "genesis", "testnet.json")

        if genesis_file and os.path.exists(genesis_file):
            with open(genesis_file, 'r') as f:
                genesis_data = json.load(f)
        # Load from file if provided (for custom networks)
        elif self.config.genesis_file and os.path.exists(self.config.genesis_file):
            with open(self.config.genesis_file, 'r') as f:
                genesis_data = json.load(f)

        if genesis_data:
            # Parse genesis
            alloc = genesis_data.get("alloc", {})
            for address, data in alloc.items():
                if not address.startswith("0x"):
                    address = "0x" + address
                balance = int(data.get("balance", "0"), 16) if isinstance(data.get("balance"), str) else data.get("balance", 0)
                self.state.set_balance(address, balance)
                if self.statedb:
                    self.statedb.set_balance(address, balance)

            # Create genesis block
            difficulty = int(genesis_data.get("difficulty", "0x1"), 16)
            gas_limit = int(genesis_data.get("gasLimit", hex(self.config.gas_limit)), 16)
            timestamp = int(genesis_data.get("timestamp", "0x0"), 16)
            extra_data = to_bytes(hexstr=genesis_data.get("extraData", "0x4e616e6f5079"))
            nonce = int(genesis_data.get("nonce", "0x0"), 16)

            genesis = Block.genesis(
                chain_id=self.chain_id,
                gas_limit=gas_limit,
                extra_data=extra_data,
                difficulty=difficulty,
                timestamp=timestamp,
                nonce=nonce,
            )
        else:
            # Default genesis for custom chains
            genesis_alloc = {
                "0x0000000000000000000000000000000000000001": 10000 * 10**18,
                "0x0000000000000000000000000000000000000002": 10000 * 10**18,
                "0x0000000000000000000000000000000000000003": 10000 * 10**18,
            }
            for address, balance in genesis_alloc.items():
                self.state.set_balance(address, balance)
                if self.statedb:
                    self.statedb.set_balance(address, balance)

            genesis = Block.genesis(
                chain_id=self.chain_id,
                gas_limit=self.config.gas_limit,
                extra_data=b"NanoPy Genesis",
            )

        genesis.header.state_root = self.state.state_root

        self.blocks.append(genesis)
        self.blocks_by_hash[genesis.hash] = genesis

        if self.chaindb:
            self.chaindb.put_block(genesis.to_dict(full_transactions=True))


    # Properties
    @property
    def block_number(self) -> int:
        return len(self.blocks) - 1

    @property
    def latest_block(self) -> Block:
        return self.blocks[-1]

    @property
    def is_mining(self) -> bool:
        """Always False - mining deprecated in favor of PoS validation"""
        return False

    @property
    def hashrate(self) -> float:
        """Always 0 - mining deprecated in favor of PoS validation"""
        return 0

    @property
    def gas_price(self) -> int:
        return self.config.gas_price

    @property
    def max_priority_fee(self) -> int:
        return 1000  # Same as gas price

    @property
    def accounts(self) -> List[str]:
        return self.keystore.list_addresses()

    @property
    def peers(self) -> List:
        return []  # No P2P yet

    # Account management
    def create_account(self) -> str:
        """Create a new account"""
        wallet = self.keystore.create_wallet()
        return wallet.address

    def import_account(self, private_key: str) -> str:
        """Import account from private key"""
        wallet = Wallet(private_key)
        self.keystore.add_wallet(wallet)
        return wallet.address

    def fund_account(self, address: str, amount: int):
        """Fund an account (dev mode)"""
        self.state.add_balance(address, amount)
        # Persist
        if self.statedb:
            current = self.statedb.get_balance(address)
            self.statedb.set_balance(address, current + amount)

    # State queries
    def get_balance(self, address: str, block: str = "latest") -> int:
        return self.state.get_balance(address)

    def get_storage_at(self, address: str, slot: int, block: str = "latest") -> int:
        return self.state.get_storage_int(address, slot)

    def get_transaction_count(self, address: str, block: str = "latest") -> int:
        # Include pending transactions
        pending_nonce = self.txpool.get_pending_nonce(address)
        state_nonce = self.state.get_nonce(address)
        return max(pending_nonce, state_nonce)

    def get_code(self, address: str, block: str = "latest") -> bytes:
        return self.state.get_code(address)

    # Block queries
    def get_block_by_number(self, block_number: str) -> Optional[Block]:
        if block_number == "latest":
            return self.latest_block
        elif block_number == "pending":
            return self.latest_block  # No pending blocks yet
        elif block_number == "earliest":
            return self.blocks[0]
        else:
            num = int(block_number, 16)
            if 0 <= num < len(self.blocks):
                return self.blocks[num]
        return None

    def get_block_by_hash(self, block_hash: str) -> Optional[Block]:
        if block_hash.startswith("0x"):
            block_hash = bytes.fromhex(block_hash[2:])
        return self.blocks_by_hash.get(block_hash)

    # Transaction queries
    def get_transaction_by_hash(self, tx_hash: str) -> Optional[SignedTransaction]:
        if tx_hash.startswith("0x"):
            tx_hash = tx_hash[2:]
        return self.transactions.get(tx_hash)

    def get_transaction_receipt(self, tx_hash: str) -> Optional[TransactionReceipt]:
        if tx_hash.startswith("0x"):
            tx_hash = tx_hash[2:]
        return self.receipts.get(tx_hash)

    # Transaction submission
    def send_transaction(self, tx_data: dict) -> str:
        """Send transaction (must have unlocked account)"""
        sender = tx_data["from"]
        wallet = self.keystore.get_wallet(sender)
        if not wallet:
            raise ValueError(f"Account {sender} not found in keystore")

        # Build transaction
        nonce = self.get_transaction_count(sender)
        tx = Transaction(
            nonce=nonce,
            to=tx_data.get("to"),
            value=int(tx_data.get("value", "0x0"), 16),
            data=to_bytes(hexstr=tx_data.get("data", "0x")),
            gas=int(tx_data.get("gas", "0x5208"), 16),
            gas_price=int(tx_data.get("gasPrice", hex(self.gas_price)), 16),
            chain_id=self.chain_id,
        )

        # Sign and submit
        signed = wallet.sign_transaction(tx)
        return self._submit_transaction(signed)

    def send_raw_transaction(self, raw_tx: str) -> str:
        """Send raw signed transaction"""
        import rlp

        if raw_tx.startswith("0x"):
            raw_tx = raw_tx[2:]

        tx_bytes = bytes.fromhex(raw_tx)

        # Decode RLP
        decoded = rlp.decode(tx_bytes)

        # Legacy transaction: [nonce, gasPrice, gasLimit, to, value, data, v, r, s]
        if len(decoded) == 9:
            nonce = int.from_bytes(decoded[0], 'big') if decoded[0] else 0
            gas_price = int.from_bytes(decoded[1], 'big') if decoded[1] else 0
            gas_limit = int.from_bytes(decoded[2], 'big') if decoded[2] else 21000
            to = "0x" + decoded[3].hex() if decoded[3] else None
            value = int.from_bytes(decoded[4], 'big') if decoded[4] else 0
            data = decoded[5] if decoded[5] else b''
            v = int.from_bytes(decoded[6], 'big') if decoded[6] else 0
            r = int.from_bytes(decoded[7], 'big') if decoded[7] else 0
            s = int.from_bytes(decoded[8], 'big') if decoded[8] else 0

            # Extract chain_id from v (EIP-155)
            if v >= 35:
                chain_id = (v - 35) // 2
            else:
                chain_id = self.chain_id

            # Create transaction object
            tx = Transaction(
                nonce=nonce,
                gas_price=gas_price,
                gas=gas_limit,
                to=to,
                value=value,
                data=data,
                chain_id=chain_id,
            )

            # Create signed transaction
            signed_tx = SignedTransaction(
                transaction=tx,
                v=v,
                r=r,
                s=s,
            )

            return self._submit_transaction(signed_tx)
        else:
            raise ValueError(f"Unsupported transaction format: {len(decoded)} fields")

    def _submit_transaction(self, signed_tx: SignedTransaction) -> str:
        """Submit signed transaction to pool"""
        tx_hash = to_hex(signed_tx.hash())

        # Validate
        sender = signed_tx.sender
        t = signed_tx.transaction

        # Check nonce
        expected_nonce = self.state.get_nonce(sender)
        pending_nonce = self.txpool.get_pending_nonce(sender)
        if t.nonce < expected_nonce:
            raise ValueError(f"Nonce too low: expected >= {expected_nonce}")

        # Check balance
        max_cost = t.value + t.gas * t.effective_gas_price
        balance = self.state.get_balance(sender)
        if balance < max_cost:
            raise ValueError(f"Insufficient balance: have {balance}, need {max_cost}")

        # Add to pool
        if not self.txpool.add(signed_tx):
            raise ValueError("Failed to add transaction to pool")

        self.transactions[tx_hash[2:]] = signed_tx

        # Notify WebSocket subscribers of new pending transaction
        self._notify_pending_transaction(signed_tx.hash())

        return tx_hash

    # Contract calls
    def call(self, tx_data: dict, block: str = "latest") -> str:
        """Execute contract call (no state change)"""
        sender = tx_data.get("from", "0x" + "0" * 40)
        to = tx_data.get("to", "")
        value = int(tx_data.get("value", "0x0"), 16)
        data = to_bytes(hexstr=tx_data.get("data", "0x"))
        gas = int(tx_data.get("gas", "0x1000000"), 16)

        if not to:
            raise ValueError("Contract creation not supported in eth_call")

        code = self.state.get_code(to)

        # Create temporary state copy
        temp_state = self.state.copy()
        evm = NanoPyEVM(temp_state)

        context = ExecutionContext(
            origin=sender,
            gas_price=self.gas_price,
            caller=sender,
            address=to,
            value=value,
            data=data,
            gas=gas,
            code=code,
            is_static=True,
            coinbase=self.coinbase,
            timestamp=self.latest_block.timestamp,
            number=self.block_number,
            prevrandao=self.latest_block.header.difficulty,
            gas_limit=self.config.gas_limit,
            chain_id=self.chain_id,
            base_fee=self.latest_block.header.base_fee_per_gas or 0,
        )

        result = evm.execute(context)

        if not result.success:
            raise ValueError(f"Execution failed: {result.error}")

        return to_hex(result.return_data)

    def estimate_gas(self, tx_data: dict, block: str = "latest") -> int:
        """Estimate gas for transaction"""
        # Simple estimation
        base_gas = 21000

        data = tx_data.get("data", "0x")
        if data.startswith("0x"):
            data = data[2:]
        data_gas = len(bytes.fromhex(data)) * 16

        to = tx_data.get("to")
        if not to:
            # Contract creation
            return base_gas + data_gas + 32000

        code = self.state.get_code(to)
        if len(code) == 0:
            # Simple transfer
            return base_gas + data_gas

        # Contract call - simulate with high gas limit and measure actual usage
        value = tx_data.get("value", "0x0")
        if isinstance(value, str):
            value = int(value, 16) if value.startswith("0x") else int(value)

        from_addr = tx_data.get("from", "0x" + "0" * 40)

        # Take snapshot to revert after simulation
        snapshot = self.state.snapshot()

        from nanopy.vm.evm import NanoPyEVM, ExecutionContext
        evm = NanoPyEVM(self.state)

        # Use very high gas for simulation
        sim_gas = 30_000_000

        context = ExecutionContext(
            origin=from_addr,
            gas_price=1,
            caller=from_addr,
            address=to,
            value=value,
            data=bytes.fromhex(data) if data else b"",
            gas=sim_gas,
            code=code,
            coinbase="0x" + "0" * 40,
            timestamp=int(__import__('time').time()),
            number=self.block_number,
            prevrandao=0,
            gas_limit=sim_gas,
            chain_id=self.config.chain_id,
            base_fee=0,
        )

        try:
            result = evm.execute(context)
            # Revert simulation changes
            self.state.revert(snapshot)

            if result.success:
                # Add intrinsic gas + 10% safety margin
                estimated = int((result.gas_used + base_gas + data_gas) * 1.1)
                return estimated
            else:
                # Execution failed even with high gas - return high estimate
                return base_gas + data_gas + 500000
        except Exception as e:
            # Revert on error
            self.state.revert(snapshot)
            # Fallback to safe estimate
            return base_gas + data_gas + 500000

    def sign_message(self, address: str, message: str) -> str:
        """Sign message with account"""
        wallet = self.keystore.get_wallet(address)
        if not wallet:
            raise ValueError(f"Account {address} not found")
        return wallet.sign_message(message)

    def _persist_state_changes(self, transactions: list):
        """Persist state changes after block processing"""
        if not self.statedb:
            return

        logger.debug(f"Persisting state changes for {len(transactions)} transactions")
        # Get all affected addresses and persist their state
        addresses = set()
        contract_addresses = set()  # Track created contracts

        for tx in transactions:
            addresses.add(tx.sender)
            if tx.transaction.to:
                addresses.add(tx.transaction.to)
            else:
                # Contract creation - compute contract address
                from eth_utils import keccak
                import rlp
                sender_bytes = bytes.fromhex(tx.sender[2:] if tx.sender.startswith("0x") else tx.sender)
                nonce = tx.transaction.nonce
                contract_addr = "0x" + keccak(rlp.encode([sender_bytes, nonce]))[-20:].hex()
                addresses.add(contract_addr)
                contract_addresses.add(contract_addr)

        # Also persist coinbase
        if self.coinbase:
            addresses.add(self.coinbase)

        for address in addresses:
            balance = self.state.get_balance(address)
            nonce = self.state.get_nonce(address)
            self.statedb.set_balance(address, balance)
            self.statedb.set_nonce(address, nonce)

            # Persist code for contracts
            code = self.state.get_code(address)
            if code:
                self.statedb.set_code(address, code)

        # Persist ALL storage tries (not just tx addresses)
        # This catches contracts called internally (e.g., DEX receiving tokens)
        storage_addresses = self.state.get_all_storage_addresses()
        logger.debug(f"Persisting storage for {len(storage_addresses)} addresses")
        for address in storage_addresses:
            storage_trie = self.state.get_storage_trie(address)
            if storage_trie:
                self.statedb.persist_storage(address, storage_trie)

    # PoS Staking
    def register_validator(self, address: str, stake: int) -> bool:
        """Register as validator with stake"""
        if self.state.get_balance(address) < stake:
            return False

        if not self.pos.register_validator(address, stake, self.block_number):
            return False

        self.state.sub_balance(address, stake)
        if self.statedb:
            self.statedb.set_balance(address, self.state.get_balance(address))

        return True

    def add_stake(self, address: str, amount: int) -> bool:
        """Add stake to existing validator"""
        if self.state.get_balance(address) < amount:
            return False

        if not self.pos.add_stake(address, amount, self.block_number):
            return False

        self.state.sub_balance(address, amount)
        if self.statedb:
            self.statedb.set_balance(address, self.state.get_balance(address))

        return True

    def withdraw_stake(self, address: str) -> int:
        """Withdraw stake from validator"""
        success, amount = self.pos.withdraw_stake(address, self.block_number)

        if success and amount > 0:
            self.state.add_balance(address, amount)
            if self.statedb:
                self.statedb.set_balance(address, self.state.get_balance(address))

        return amount if success else 0

    def get_validators(self) -> list:
        """Get list of validators"""
        return self.pos.get_validator_set()

    def get_stake(self, address: str) -> int:
        """Get stake for address"""
        return self.pos.get_stake(address)

    def _setup_validator(self):
        """Setup validator from config key"""
        try:
            # Get address from private key
            key = self.config.validator_key
            if key.startswith("0x"):
                key = key[2:]
            account = EthAccount.from_key(bytes.fromhex(key))
            address = account.address

            # Set as coinbase
            self.coinbase = address

            # Get balance for stake
            balance = self.state.get_balance(address)
            min_stake = self.pos.MIN_STAKE

            if balance >= min_stake:
                # Register as validator with minimum stake
                stake_amount = min_stake
                self.pos.register_validator(address, stake_amount, self.block_number)
                logger.info(f"Validator registered: {address} with stake {stake_amount / 10**18} NPY")

                # Start validating
                self.start_validating()
            else:
                logger.warning(f"Insufficient balance to stake: {balance / 10**18} NPY (need {min_stake / 10**18} NPY)")
        except Exception as e:
            logger.error(f"Failed to setup validator: {e}")

    def start_validating(self):
        """Start block validation (PoS)"""
        logger.debug(f"start_validating called, coinbase={self.coinbase}")
        if self._validating:
            return

        if not self.coinbase:
            logger.warning("No coinbase set, cannot validate")
            return

        is_val = self.pos.is_validator(self.coinbase)
        if not is_val:
            logger.warning("Not a validator, cannot start validation")
            return

        self._validating = True
        self._validator_thread = threading.Thread(target=self._validation_loop, daemon=True)
        self._validator_thread.start()
        logger.info("Validation started")

    def stop_validating(self):
        """Stop validation"""
        self._validating = False

    def _validation_loop(self):
        """Background validation loop"""
        logger.debug(f"Validation loop started for {self.coinbase}")
        while self._validating:
            try:
                selected = self.pos.select_validator(
                    self.block_number,
                    self.latest_block.hash
                )

                if selected and selected.lower() == self.coinbase.lower():
                    block = self.validate_and_create_block()
                    if block:
                        logger.info(f"Block {block.number} created. Hash: {block.hash.hex()[:16]}...")

                time.sleep(self.config.block_time)
            except Exception as e:
                logger.error(f"Validation error: {e}")
                time.sleep(1)

    def validate_and_create_block(self) -> Optional[Block]:
        """Create and validate a block (PoS)"""
        parent = self.latest_block
        transactions = self.txpool.get_pending_for_block(self.config.gas_limit)

        timestamp = int(time.time()) + self._time_offset

        block, receipts = self.consensus.create_block(
            parent=parent,
            transactions=transactions,
            coinbase=self.coinbase,
            state=self.state,
            timestamp=timestamp,
        )

        block.header.difficulty = 1
        block.header.nonce = b'\x00' * 8  # 8 bytes for PoS

        self.blocks.append(block)
        self.blocks_by_hash[block.hash] = block

        if self.chaindb:
            self.chaindb.put_block(block.to_dict(full_transactions=True))

        for receipt in receipts:
            self.receipts[to_hex(receipt.tx_hash)[2:]] = receipt
            if self.chaindb:
                self.chaindb.put_receipt(to_hex(receipt.tx_hash), receipt.to_dict())

        self.pos.apply_reward(self.coinbase, self.block_number)
        self.state.add_balance(self.coinbase, self.pos.BLOCK_REWARD)

        if self.statedb:
            self._persist_state_changes(transactions)
            self.statedb.set_balance(self.coinbase, self.state.get_balance(self.coinbase))

        self.txpool.remove_mined(transactions)

        if self.p2p and hasattr(self.p2p, '_loop') and self.p2p._loop:
            import asyncio
            try:
                asyncio.run_coroutine_threadsafe(
                    self.p2p.broadcast_block(block.to_dict()),
                    self.p2p._loop
                )
            except Exception:
                pass

        # Notify WebSocket subscribers of new block
        self._notify_new_block(block, receipts)

        return block

    def _notify_new_block(self, block: Block, receipts: list = None):
        """Notify WebSocket subscribers of new block"""
        if not self.rpc_server:
            logger.debug("No RPC server, skipping WebSocket notification")
            return
        if not self._rpc_loop:
            logger.debug("No RPC loop, skipping WebSocket notification")
            return

        import asyncio
        try:
            # Notify newHeads subscribers
            logger.info(f"Broadcasting block {block.number} to WebSocket subscribers")
            future = asyncio.run_coroutine_threadsafe(
                self.rpc_server.broadcast_new_head(block),
                self._rpc_loop
            )
            # Wait for result with timeout to catch errors
            try:
                future.result(timeout=2.0)
            except Exception as e:
                logger.warning(f"broadcast_new_head error: {e}")

            # Notify logs subscribers if there are logs in receipts
            if receipts:
                all_logs = []
                for receipt in receipts:
                    if hasattr(receipt, 'logs') and receipt.logs:
                        all_logs.extend(receipt.logs)
                if all_logs:
                    asyncio.run_coroutine_threadsafe(
                        self.rpc_server.broadcast_logs(all_logs, block.hash, block.number),
                        self._rpc_loop
                    )
        except Exception as e:
            logger.warning(f"WebSocket notification error: {e}")

    def _notify_pending_transaction(self, tx_hash: bytes):
        """Notify WebSocket subscribers of new pending transaction"""
        if not self.rpc_server or not self._rpc_loop:
            return

        import asyncio
        try:
            asyncio.run_coroutine_threadsafe(
                self.rpc_server.broadcast_pending_tx(tx_hash),
                self._rpc_loop
            )
        except Exception as e:
            logger.debug(f"WebSocket pendingTx notification error: {e}")

    # Filters
    def new_filter(self, params: dict) -> str:
        """Create new log filter"""
        self._filter_counter += 1
        filter_id = hex(self._filter_counter)
        self._filters[filter_id] = {
            "type": "log",
            "params": params,
            "last_block": self.block_number,
            "logs": [],
        }
        return filter_id

    def new_block_filter(self) -> str:
        """Create new block filter"""
        self._filter_counter += 1
        filter_id = hex(self._filter_counter)
        self._filters[filter_id] = {
            "type": "block",
            "last_block": self.block_number,
            "hashes": [],
        }
        return filter_id

    def new_pending_transaction_filter(self) -> str:
        """Create pending transaction filter"""
        self._filter_counter += 1
        filter_id = hex(self._filter_counter)
        self._filters[filter_id] = {
            "type": "pending",
            "hashes": [],
        }
        return filter_id

    def uninstall_filter(self, filter_id: str) -> bool:
        """Remove filter"""
        return self._filters.pop(filter_id, None) is not None

    def get_filter_changes(self, filter_id: str) -> List:
        """Get filter changes since last poll"""
        f = self._filters.get(filter_id)
        if not f:
            return []

        if f["type"] == "block":
            # Return new block hashes
            new_hashes = []
            for i in range(f["last_block"] + 1, self.block_number + 1):
                new_hashes.append(to_hex(self.blocks[i].hash))
            f["last_block"] = self.block_number
            return new_hashes

        return []

    def get_filter_logs(self, filter_id: str) -> List:
        """Get all logs for filter"""
        return []  # Simplified

    def get_logs(self, params: dict) -> List[dict]:
        """Get logs matching filter"""
        return []  # Simplified

    def fee_history(self, block_count: int, newest_block: str, percentiles: List[float]) -> dict:
        """Get fee history"""
        return {
            "baseFeePerGas": [hex(self.gas_price)] * (block_count + 1),
            "gasUsedRatio": [0.5] * block_count,
            "oldestBlock": hex(max(0, self.block_number - block_count + 1)),
            "reward": [[hex(self.max_priority_fee)] * len(percentiles)] * block_count,
        }

    # Dev mode (Hardhat/Ganache compatibility)
    def increase_time(self, seconds: int):
        """Increase time offset"""
        self._time_offset += seconds

    def set_next_block_timestamp(self, timestamp: int):
        """Set next block timestamp"""
        self._next_block_timestamp = timestamp

    def snapshot(self) -> int:
        """Create state snapshot"""
        snap_id = len(self._snapshots)
        self._snapshots.append((
            self.state.snapshot(),
            len(self.blocks),
            self._time_offset,
        ))
        return snap_id

    def revert(self, snapshot_id: int) -> bool:
        """Revert to snapshot"""
        if snapshot_id >= len(self._snapshots):
            return False

        state_snap, block_count, time_offset = self._snapshots[snapshot_id]
        self.state.revert(state_snap)
        self.blocks = self.blocks[:block_count]
        self._time_offset = time_offset
        self._snapshots = self._snapshots[:snapshot_id]
        return True

    # Server
    def start(self):
        """Start the node (RPC server with HTTP+WS, P2P)"""
        # Start RPC server (HTTP + WebSocket on same port)
        self._start_rpc()

        # Start P2P network
        self._start_p2p()

        # Start validating if PoS with validator key
        if self.config.consensus == "pos" and self.config.validator_key:
            self._setup_validator()

    def _start_rpc(self):
        """Start HTTP + WebSocket RPC server on single port"""
        import asyncio
        import threading

        rpc_ready = threading.Event()

        def run_rpc_server():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._rpc_loop = loop

            async def start_and_run():
                self.rpc_server = await start_rpc(
                    self,
                    self.config.rpc_host,
                    self.config.rpc_port
                )
                logger.info(f"RPC server ready for WebSocket subscriptions")
                rpc_ready.set()  # Signal that RPC is ready
                # Keep server running
                while True:
                    await asyncio.sleep(1)

            try:
                loop.run_until_complete(start_and_run())
            except Exception as e:
                logger.error(f"RPC server error: {e}")
                rpc_ready.set()  # Unblock even on error

        rpc_thread = threading.Thread(target=run_rpc_server, daemon=True)
        rpc_thread.start()
        logger.info(f"RPC server (HTTP+WS) starting on {self.config.rpc_host}:{self.config.rpc_port}")

        # Wait for RPC server to be ready (max 5 seconds)
        if rpc_ready.wait(timeout=5):
            logger.info("RPC server initialized successfully")
        else:
            logger.warning("RPC server initialization timeout - WebSocket notifications may not work")

    def _start_p2p(self):
        """Start P2P network - libp2p only"""
        if not LIBP2P_AVAILABLE:
            raise RuntimeError("libp2p not available! Install with: pip install libp2p trio")

        libp2p_config = LibP2PConfig(
            listen_addrs=[f"/ip4/{self.config.p2p_host}/tcp/{self.config.p2p_port}"],
            bootstrap_peers=self._convert_bootnodes_to_multiaddr(self.config.bootnodes or []),
            chain_id=self.chain_id,
            network_id=self.config.network_id,
            max_peers=self.config.max_peers,
            private_key=bytes.fromhex(self.config.p2p_private_key[2:]) if self.config.p2p_private_key.startswith("0x") else bytes.fromhex(self.config.p2p_private_key) if self.config.p2p_private_key else None,
            data_dir=self.config.data_dir,
        )

        # Pass callbacks directly to avoid race condition
        # (callbacks must be set BEFORE the trio thread starts syncing)
        self.p2p = run_libp2p_network(
            libp2p_config,
            self,
            on_new_block=self._handle_p2p_block,
            on_new_tx=self._handle_p2p_transaction
        )
        logger.info("P2P network started with callbacks")

    def _convert_bootnodes_to_multiaddr(self, bootnodes: list) -> list:
        """Convert bootnode addresses to libp2p multiaddr format"""
        multiaddrs = []
        for bootnode in bootnodes:
            if bootnode.startswith("/ip4") or bootnode.startswith("/dns"):
                # Already a multiaddr
                multiaddrs.append(bootnode)
            else:
                # Convert host:port to multiaddr
                try:
                    host, port = bootnode.split(":")
                    multiaddrs.append(f"/ip4/{host}/tcp/{port}")
                except ValueError:
                    pass
        return multiaddrs

    def _handle_p2p_block(self, block_data: dict, peer):
        """Handle new block from P2P network - execute transactions to rebuild state"""
        try:
            block_num = block_data.get("number", "0x0")
            print(f"[P2P BLOCK] Received block {block_num} from peer", flush=True)
            logger.info(f"P2P received block {block_num} from peer")
            block = Block.from_dict(block_data)

            expected_number = self.block_number + 1
            if block.number != expected_number:
                logger.info(f"Skip block {block.number}, expected {expected_number}")
                return

            if block.parent_hash != self.latest_block.hash:
                logger.info(f"Block {block.number} parent mismatch, expected {self.latest_block.hash.hex()[:16]}")
                return

            # Execute transactions to rebuild state (block replay)
            # Use skip_validation=True during sync to trust blocks from peer
            block_receipts = None
            if block.transactions:
                result, block_receipts = self.consensus.apply_block(block, self.state, skip_validation=True)
                if not result.valid:
                    logger.warning(f"Block {block.number} replay failed: {result.error}")
                else:
                    logger.debug(f"Block {block.number}: {len(block.transactions)} txs executed")
                    # Persist state changes
                    if self.statedb:
                        self._persist_state_changes(block.transactions)
                    # Store receipts
                    for receipt in block_receipts:
                        self.receipts[to_hex(receipt.tx_hash)[2:]] = receipt
                        if self.chaindb:
                            self.chaindb.put_receipt(to_hex(receipt.tx_hash), receipt.to_dict())

            self.blocks.append(block)
            self.blocks_by_hash[block.hash] = block
            print(f"[P2P BLOCK] Block {block.number} added, notifying WebSocket", flush=True)
            logger.info(f"Block {block.number} added from peer, notifying WebSocket")

            if self.chaindb:
                self.chaindb.put_block(block_data)

            # Notify WebSocket subscribers of new block
            self._notify_new_block(block, block_receipts)

        except Exception as e:
            logger.warning(f"P2P block error: {e}")

    def _handle_p2p_transaction(self, tx_data: dict, peer):
        """Handle new transaction from P2P network"""
        try:
            # Add to mempool
            pass
        except Exception:
            pass

    async def broadcast_block(self, block: Block):
        """Broadcast mined block to peers"""
        if self.p2p:
            import asyncio
            asyncio.create_task(self.p2p.broadcast_block(block.to_dict()))

    def run(self):
        """Run node (blocking)"""
        self.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[Node] Shutting down gracefully...")
            if self.p2p:
                # Signal P2P to stop - don't use asyncio.run with trio
                try:
                    self.p2p._running = False
                    # Give P2P thread time to cleanup
                    import time as t
                    t.sleep(0.5)
                except Exception:
                    pass
            print("[Node] Stopped.")

