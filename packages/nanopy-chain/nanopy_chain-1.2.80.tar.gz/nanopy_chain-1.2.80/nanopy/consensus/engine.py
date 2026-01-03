"""
NanoPy Consensus Engine - Block validation and finalization
"""

import logging
from typing import List, Optional, Tuple
from dataclasses import dataclass
import time

from eth_utils import keccak, to_hex

logger = logging.getLogger(__name__)

from nanopy.core.block import Block, BlockHeader, compute_transactions_root, compute_logs_bloom
from nanopy.core.transaction import SignedTransaction, TransactionReceipt
from nanopy.core.state import StateDB
from nanopy.vm.evm import NanoPyEVM, ExecutionContext
from nanopy.consensus.pow import ProofOfWork


@dataclass
class BlockValidationResult:
    """Result of block validation"""
    valid: bool
    error: Optional[str] = None


class ConsensusEngine:
    """
    Consensus engine for block validation and state transition

    Handles:
    - Block header validation
    - Transaction execution
    - State root computation
    - Receipt generation
    - Block finalization
    """

    # Chain parameters
    BLOCK_REWARD = 2 * 10 ** 18  # 2 NPY
    UNCLE_REWARD_FACTOR = 8  # Uncle gets 7/8 of block reward
    MAX_UNCLE_DEPTH = 6
    GAS_LIMIT_BOUND_DIVISOR = 1024
    MIN_GAS_LIMIT = 5000

    def __init__(self, chain_id: int = 1337):
        self.chain_id = chain_id
        self.pow = ProofOfWork()

    def validate_header(
        self,
        header: BlockHeader,
        parent: Optional[BlockHeader] = None,
    ) -> BlockValidationResult:
        """
        Validate a block header

        Args:
            header: Header to validate
            parent: Parent block header (None for genesis)

        Returns:
            BlockValidationResult
        """
        # Genesis block
        if parent is None:
            if header.number != 0:
                return BlockValidationResult(False, "Genesis must be block 0")
            return BlockValidationResult(True)

        # Block number
        if header.number != parent.number + 1:
            return BlockValidationResult(False, f"Invalid block number: expected {parent.number + 1}")

        # Parent hash
        if header.parent_hash != parent.hash:
            return BlockValidationResult(False, "Invalid parent hash")

        # Timestamp
        if header.timestamp <= parent.timestamp:
            return BlockValidationResult(False, "Timestamp must be greater than parent")

        if header.timestamp > int(time.time()) + 15:
            return BlockValidationResult(False, "Block is from the future")

        # Gas limit bounds
        parent_gas_limit = parent.gas_limit
        diff = abs(header.gas_limit - parent_gas_limit)
        max_diff = parent_gas_limit // self.GAS_LIMIT_BOUND_DIVISOR

        if diff > max_diff:
            return BlockValidationResult(False, "Gas limit change too large")

        if header.gas_limit < self.MIN_GAS_LIMIT:
            return BlockValidationResult(False, "Gas limit too low")

        # Gas used
        if header.gas_used > header.gas_limit:
            return BlockValidationResult(False, "Gas used exceeds gas limit")

        # Difficulty
        expected_difficulty = self.pow.adjust_difficulty(parent, header.timestamp)
        if header.difficulty != expected_difficulty:
            # Allow some tolerance
            if abs(header.difficulty - expected_difficulty) > expected_difficulty // 10:
                return BlockValidationResult(False, "Invalid difficulty")

        # Extra data
        if len(header.extra_data) > 32:
            return BlockValidationResult(False, "Extra data too long")

        # Verify PoW
        if not self.pow.verify(header):
            return BlockValidationResult(False, "Invalid proof of work")

        return BlockValidationResult(True)

    def validate_block(
        self,
        block: Block,
        parent: Optional[Block] = None,
        state: Optional[StateDB] = None,
    ) -> BlockValidationResult:
        """
        Validate a complete block including transactions

        Args:
            block: Block to validate
            parent: Parent block
            state: Current state DB

        Returns:
            BlockValidationResult
        """
        # Validate header
        parent_header = parent.header if parent else None
        header_result = self.validate_header(block.header, parent_header)
        if not header_result.valid:
            return header_result

        # Validate transactions root
        tx_root = compute_transactions_root(block.transactions)
        if tx_root != block.header.transactions_root:
            return BlockValidationResult(False, "Invalid transactions root")

        # Validate each transaction
        for tx in block.transactions:
            if tx.transaction.chain_id != self.chain_id:
                return BlockValidationResult(False, f"Invalid chain ID in transaction")

        # If we have state, validate state root
        if state:
            result, _ = self.apply_block(block, state)
            if not result.valid:
                return result

        return BlockValidationResult(True)

    def apply_block(
        self,
        block: Block,
        state: StateDB,
        skip_validation: bool = False,
    ) -> Tuple[BlockValidationResult, List[TransactionReceipt]]:
        """
        Apply block to state (execute all transactions)

        Args:
            block: Block to apply
            state: State DB to modify
            skip_validation: If True, skip state root/gas/bloom verification (for sync)

        Returns:
            Tuple of (BlockValidationResult, list of receipts)
        """
        snapshot = state.snapshot()

        try:
            # Execute transactions
            receipts = []
            cumulative_gas = 0
            logs = []

            for i, tx in enumerate(block.transactions):
                receipt = self.apply_transaction(
                    tx=tx,
                    state=state,
                    block=block,
                    tx_index=i,
                    cumulative_gas=cumulative_gas,
                )
                receipts.append(receipt)
                cumulative_gas = receipt.cumulative_gas_used
                logs.extend(receipt.logs)

            # Apply block reward
            self._apply_rewards(block, state)

            # Skip validation during sync (trust the blocks from peer)
            if skip_validation:
                state.commit(snapshot)
                return BlockValidationResult(True), receipts

            # Verify gas used
            if cumulative_gas != block.header.gas_used:
                state.revert(snapshot)
                return BlockValidationResult(False, f"Gas used mismatch: expected {block.header.gas_used}, got {cumulative_gas}"), []

            # Verify state root
            if state.state_root != block.header.state_root:
                state.revert(snapshot)
                return BlockValidationResult(False, "State root mismatch"), []

            # Verify logs bloom
            expected_bloom = compute_logs_bloom(logs)
            if expected_bloom != block.header.logs_bloom:
                state.revert(snapshot)
                return BlockValidationResult(False, "Logs bloom mismatch"), []

            state.commit(snapshot)
            return BlockValidationResult(True), receipts

        except Exception as e:
            state.revert(snapshot)
            return BlockValidationResult(False, str(e)), []

    def apply_transaction(
        self,
        tx: SignedTransaction,
        state: StateDB,
        block: Block,
        tx_index: int,
        cumulative_gas: int,
    ) -> TransactionReceipt:
        """
        Apply a single transaction to state

        Args:
            tx: Signed transaction to apply
            state: State DB
            block: Current block
            tx_index: Transaction index in block
            cumulative_gas: Cumulative gas used before this tx

        Returns:
            TransactionReceipt
        """
        sender = tx.sender
        t = tx.transaction

        # Validate nonce
        expected_nonce = state.get_nonce(sender)
        if t.nonce != expected_nonce:
            raise ValueError(f"Invalid nonce: expected {expected_nonce}, got {t.nonce}")

        # Validate balance
        max_fee = t.gas * t.effective_gas_price
        total_cost = t.value + max_fee
        balance = state.get_balance(sender)
        if balance < total_cost:
            raise ValueError(f"Insufficient balance: need {total_cost}, have {balance}")

        # Deduct gas upfront
        state.sub_balance(sender, max_fee)
        state.increment_nonce(sender)

        # Create execution context
        evm = NanoPyEVM(state)

        if t.to is None or t.to == "":
            # Contract creation
            from nanopy.core.account import compute_contract_address
            contract_address = compute_contract_address(sender, t.nonce)

            context = ExecutionContext(
                origin=sender,
                gas_price=t.effective_gas_price,
                caller=sender,
                address=contract_address,
                value=t.value,
                data=b"",  # Init code is in transaction data
                gas=t.gas - 21000,  # Subtract intrinsic gas
                code=t.data,  # Transaction data IS the init code
                coinbase=block.coinbase,
                timestamp=block.timestamp,
                number=block.number,
                prevrandao=block.header.difficulty,  # Pre-merge
                gas_limit=block.gas_limit,
                chain_id=self.chain_id,
                base_fee=block.header.base_fee_per_gas or 0,
            )

            result = evm.execute(context)

            if result.success:
                # Store contract code
                state.set_code(contract_address, result.return_data)
                # Transfer value
                if t.value > 0:
                    state.transfer(sender, contract_address, t.value)

        else:
            # Regular transaction or contract call
            code = state.get_code(t.to)

            if len(code) == 0:
                # Simple transfer
                if not state.transfer(sender, t.to, t.value):
                    raise ValueError("Transfer failed")
                gas_used = 21000
                result = type('obj', (object,), {
                    'success': True,
                    'gas_used': gas_used,
                    'return_data': b'',
                    'logs': [],
                })()

            else:
                # Contract call
                context = ExecutionContext(
                    origin=sender,
                    gas_price=t.effective_gas_price,
                    caller=sender,
                    address=t.to,
                    value=t.value,
                    data=t.data,
                    gas=t.gas - 21000,
                    code=code,
                    coinbase=block.coinbase,
                    timestamp=block.timestamp,
                    number=block.number,
                    prevrandao=block.header.difficulty,
                    gas_limit=block.gas_limit,
                    chain_id=self.chain_id,
                    base_fee=block.header.base_fee_per_gas or 0,
                )

                result = evm.execute(context)

                if result.success and t.value > 0:
                    state.transfer(sender, t.to, t.value)

        # Calculate gas used
        intrinsic_gas = 21000 + len(t.data) * 16  # Simplified
        total_gas_used = intrinsic_gas + result.gas_used

        # Refund unused gas
        gas_refund = (t.gas - total_gas_used) * t.effective_gas_price
        state.add_balance(sender, gas_refund)

        # Pay miner
        miner_reward = total_gas_used * t.effective_gas_price
        state.add_balance(block.coinbase, miner_reward)

        # Create receipt
        return TransactionReceipt(
            tx_hash=tx.hash(),
            block_hash=block.hash,
            block_number=block.number,
            tx_index=tx_index,
            sender=sender,
            to=t.to,
            contract_address=context.address if t.to is None else None,
            gas_used=total_gas_used,
            cumulative_gas_used=cumulative_gas + total_gas_used,
            status=1 if result.success else 0,
            logs=[log.to_dict() for log in result.logs] if hasattr(result, 'logs') else [],
            logs_bloom=compute_logs_bloom([log.to_dict() for log in result.logs] if hasattr(result, 'logs') else []),
        )

    def _apply_rewards(self, block: Block, state: StateDB):
        """Apply block rewards to miner"""
        # Block reward
        state.add_balance(block.coinbase, self.BLOCK_REWARD)

        # Uncle rewards (simplified)
        for uncle in block.uncles:
            uncle_reward = self.BLOCK_REWARD * (self.UNCLE_REWARD_FACTOR - (block.number - uncle.number)) // self.UNCLE_REWARD_FACTOR
            state.add_balance(uncle.coinbase, uncle_reward)

            # Include reward for including uncle
            inclusion_reward = self.BLOCK_REWARD // 32
            state.add_balance(block.coinbase, inclusion_reward)

    def create_block(
        self,
        parent: Block,
        transactions: List[SignedTransaction],
        coinbase: str,
        state: StateDB,
        timestamp: int = None,
        extra_data: bytes = b"NanoPy",
    ) -> Tuple[Block, List[TransactionReceipt]]:
        """
        Create a new block

        Args:
            parent: Parent block
            transactions: Transactions to include
            coinbase: Miner address
            state: Current state
            timestamp: Block timestamp (default: now)
            extra_data: Extra data to include

        Returns:
            Tuple of (new_block, receipts)
        """
        if timestamp is None:
            timestamp = int(time.time())

        # Create header skeleton
        new_difficulty = self.pow.adjust_difficulty(parent.header, timestamp)

        header = BlockHeader(
            parent_hash=parent.hash,
            uncle_hash=keccak(b""),
            coinbase=coinbase,
            state_root=bytes(32),  # Placeholder
            transactions_root=compute_transactions_root(transactions),
            receipts_root=bytes(32),  # Placeholder
            logs_bloom=bytes(256),  # Placeholder
            difficulty=new_difficulty,
            number=parent.number + 1,
            gas_limit=parent.gas_limit,  # Keep same for now
            gas_used=0,  # Placeholder
            timestamp=timestamp,
            extra_data=extra_data[:32],
            mix_hash=bytes(32),
            nonce=bytes(8),
            base_fee_per_gas=parent.header.base_fee_per_gas,
        )

        block = Block(header=header, transactions=transactions)

        # Apply transactions
        receipts = []
        cumulative_gas = 0
        all_logs = []
        successful_txs = []  # Track successful transactions

        for i, tx in enumerate(transactions):
            # Take snapshot before each transaction
            tx_snapshot = state.snapshot()
            try:
                receipt = self.apply_transaction(tx, state, block, i, cumulative_gas)
                receipts.append(receipt)
                cumulative_gas = receipt.cumulative_gas_used
                all_logs.extend(receipt.logs)
                successful_txs.append(tx)
            except Exception as e:
                # Restore state on failure
                state.revert(tx_snapshot)
                logger.debug(f"Transaction {i} failed: {e}")
                continue

        # Update block with only successful transactions
        block.transactions = successful_txs

        # Apply rewards
        self._apply_rewards(block, state)

        # Update header with successful transactions
        block.header.transactions_root = compute_transactions_root(successful_txs)
        block.header.gas_used = cumulative_gas
        block.header.state_root = state.state_root
        block.header.logs_bloom = compute_logs_bloom(all_logs)

        # Compute receipts root
        from trie import HexaryTrie
        import rlp
        receipts_trie = HexaryTrie({})
        for i, receipt in enumerate(receipts):
            # Encode logs as RLP: [address, topics, data]
            encoded_logs = []
            for log in receipt.logs:
                encoded_log = [
                    bytes.fromhex(log["address"][2:]),  # address as bytes
                    [bytes.fromhex(t[2:]) for t in log.get("topics", [])],  # topics as list of bytes
                    bytes.fromhex(log.get("data", "0x")[2:]) if log.get("data", "0x") != "0x" else b"",  # data as bytes
                ]
                encoded_logs.append(encoded_log)

            receipts_trie[rlp.encode(i)] = rlp.encode([
                receipt.status,
                receipt.cumulative_gas_used,
                receipt.logs_bloom,
                encoded_logs,
            ])
        block.header.receipts_root = receipts_trie.root_hash

        return block, receipts
