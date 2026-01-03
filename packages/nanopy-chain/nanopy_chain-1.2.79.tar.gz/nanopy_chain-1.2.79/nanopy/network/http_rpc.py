"""
NanoPy RPC Server - Ethereum JSON-RPC compatible API
"""

import json
import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional, Union
from http.server import HTTPServer, BaseHTTPRequestHandler
from dataclasses import dataclass
import threading
from collections import defaultdict
import time

from eth_utils import to_hex, to_bytes, keccak

# RPC logger for transaction monitoring
rpc_logger = logging.getLogger("nanopy.rpc")

# Track requests per IP for spam detection
request_stats = defaultdict(lambda: {"count": 0, "rejected": 0, "last_seen": 0})

from nanopy.core.block import Block
from nanopy.core.transaction import Transaction, SignedTransaction, TransactionReceipt
from nanopy.core.state import StateDB
from nanopy.network.txpool import TxPool


@dataclass
class RPCError:
    """JSON-RPC error"""
    code: int
    message: str
    data: Optional[str] = None

    def to_dict(self) -> dict:
        result = {"code": self.code, "message": self.message}
        if self.data:
            result["data"] = self.data
        return result


# Standard error codes
PARSE_ERROR = RPCError(-32700, "Parse error")
INVALID_REQUEST = RPCError(-32600, "Invalid Request")
METHOD_NOT_FOUND = RPCError(-32601, "Method not found")
INVALID_PARAMS = RPCError(-32602, "Invalid params")
INTERNAL_ERROR = RPCError(-32603, "Internal error")


class NanoPyRPC:
    """
    Ethereum JSON-RPC API implementation

    Supports:
    - eth_* methods for blockchain interaction
    - net_* methods for network info
    - web3_* methods for client info
    - txpool_* methods for transaction pool
    - debug_* methods for debugging
    """

    def __init__(self, node: 'NanoPyNode'):
        self.node = node
        self._methods: Dict[str, Callable] = {}
        self._register_methods()

    def _register_methods(self):
        """Register all RPC methods"""
        # Web3 methods
        self._methods["web3_clientVersion"] = self.web3_client_version
        self._methods["web3_sha3"] = self.web3_sha3

        # Net methods
        self._methods["net_version"] = self.net_version
        self._methods["net_listening"] = self.net_listening
        self._methods["net_peerCount"] = self.net_peer_count

        # Eth methods
        self._methods["eth_chainId"] = self.eth_chain_id
        self._methods["eth_protocolVersion"] = self.eth_protocol_version
        self._methods["eth_syncing"] = self.eth_syncing
        self._methods["eth_coinbase"] = self.eth_coinbase
        self._methods["eth_mining"] = self.eth_mining
        self._methods["eth_hashrate"] = self.eth_hashrate
        self._methods["eth_gasPrice"] = self.eth_gas_price
        self._methods["eth_accounts"] = self.eth_accounts
        self._methods["eth_blockNumber"] = self.eth_block_number
        self._methods["eth_getBalance"] = self.eth_get_balance
        self._methods["eth_getStorageAt"] = self.eth_get_storage_at
        self._methods["eth_getTransactionCount"] = self.eth_get_transaction_count
        self._methods["eth_getBlockTransactionCountByHash"] = self.eth_get_block_tx_count_by_hash
        self._methods["eth_getBlockTransactionCountByNumber"] = self.eth_get_block_tx_count_by_number
        self._methods["eth_getCode"] = self.eth_get_code
        self._methods["eth_sign"] = self.eth_sign
        self._methods["eth_sendTransaction"] = self.eth_send_transaction
        self._methods["eth_sendRawTransaction"] = self.eth_send_raw_transaction
        self._methods["eth_call"] = self.eth_call
        self._methods["eth_estimateGas"] = self.eth_estimate_gas
        self._methods["eth_getBlockByHash"] = self.eth_get_block_by_hash
        self._methods["eth_getBlockByNumber"] = self.eth_get_block_by_number
        self._methods["eth_getTransactionByHash"] = self.eth_get_transaction_by_hash
        self._methods["eth_getTransactionByBlockHashAndIndex"] = self.eth_get_tx_by_block_hash_and_index
        self._methods["eth_getTransactionByBlockNumberAndIndex"] = self.eth_get_tx_by_block_number_and_index
        self._methods["eth_getTransactionReceipt"] = self.eth_get_transaction_receipt
        self._methods["eth_newFilter"] = self.eth_new_filter
        self._methods["eth_newBlockFilter"] = self.eth_new_block_filter
        self._methods["eth_newPendingTransactionFilter"] = self.eth_new_pending_tx_filter
        self._methods["eth_uninstallFilter"] = self.eth_uninstall_filter
        self._methods["eth_getFilterChanges"] = self.eth_get_filter_changes
        self._methods["eth_getFilterLogs"] = self.eth_get_filter_logs
        self._methods["eth_getLogs"] = self.eth_get_logs
        self._methods["eth_maxPriorityFeePerGas"] = self.eth_max_priority_fee_per_gas
        self._methods["eth_feeHistory"] = self.eth_fee_history

        # TxPool methods
        self._methods["txpool_content"] = self.txpool_content
        self._methods["txpool_status"] = self.txpool_status

        # EVM methods (Hardhat/Ganache compatibility)
        self._methods["evm_mine"] = self.evm_mine
        self._methods["evm_increaseTime"] = self.evm_increase_time
        self._methods["evm_setNextBlockTimestamp"] = self.evm_set_next_block_timestamp
        self._methods["evm_snapshot"] = self.evm_snapshot
        self._methods["evm_revert"] = self.evm_revert

        # NanoNode staking methods (PoS)
        self._methods["nno_getValidators"] = self.nno_get_validators
        self._methods["nno_getStake"] = self.nno_get_stake
        self._methods["nno_registerValidator"] = self.nno_register_validator
        self._methods["nno_addStake"] = self.nno_add_stake
        self._methods["nno_withdrawStake"] = self.nno_withdraw_stake
        self._methods["nno_startValidating"] = self.nno_start_validating
        self._methods["nno_stopValidating"] = self.nno_stop_validating

        # Validator client methods (for separate validator)
        self._methods["validator_getBlockTemplate"] = self.validator_get_block_template
        self._methods["validator_submitBlock"] = self.validator_submit_block
        self._methods["validator_isSelected"] = self.validator_is_selected
        self._methods["validator_getPendingTransactions"] = self.validator_get_pending_transactions
        self._methods["validator_getSyncStatus"] = self.validator_get_sync_status

        # Network discovery methods
        self._methods["nno_getNodes"] = self.nno_get_nodes
        self._methods["nno_getNetworkInfo"] = self.nno_get_network_info


    def handle_request(self, request: dict, client_ip: str = None) -> dict:
        """Handle a JSON-RPC request"""
        req_id = request.get("id")

        # Validate request
        if "jsonrpc" not in request or request["jsonrpc"] != "2.0":
            return self._error_response(req_id, INVALID_REQUEST)

        method = request.get("method")
        if not method:
            return self._error_response(req_id, INVALID_REQUEST)

        if method not in self._methods:
            return self._error_response(req_id, METHOD_NOT_FOUND)

        params = request.get("params", [])

        try:
            # Special handling for eth_sendRawTransaction to pass client_ip
            if method == "eth_sendRawTransaction":
                if params:
                    result = self._methods[method](params[0], client_ip)
                else:
                    result = self._methods[method](client_ip=client_ip)
            else:
                result = self._methods[method](*params) if params else self._methods[method]()
            return self._success_response(req_id, result)
        except TypeError as e:
            return self._error_response(req_id, RPCError(-32602, f"Invalid params: {e}"))
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            return self._error_response(req_id, RPCError(-32000, f"{e}\n{tb}"))

    def handle_batch(self, requests: List[dict], client_ip: str = None) -> List[dict]:
        """Handle batch requests"""
        return [self.handle_request(req, client_ip) for req in requests]

    def _success_response(self, req_id: Any, result: Any) -> dict:
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    def _error_response(self, req_id: Any, error: RPCError) -> dict:
        return {"jsonrpc": "2.0", "id": req_id, "error": error.to_dict()}

    # Web3 methods
    def web3_client_version(self) -> str:
        from nanopy import __version__
        return f"NanoPy/{__version__}/python"

    def web3_sha3(self, data: str) -> str:
        return to_hex(keccak(to_bytes(hexstr=data)))

    # Net methods
    def net_version(self) -> str:
        return str(self.node.chain_id)

    def net_listening(self) -> bool:
        return True

    def net_peer_count(self) -> str:
        if hasattr(self.node, 'p2p') and self.node.p2p:
            return hex(len(self.node.p2p.peers))
        return "0x0"

    # Eth methods
    def eth_chain_id(self) -> str:
        return hex(self.node.chain_id)

    def eth_protocol_version(self) -> str:
        return "0x41"  # Protocol version 65

    def eth_syncing(self) -> Union[bool, dict]:
        return False  # Not syncing

    def eth_coinbase(self) -> str:
        return self.node.coinbase

    def eth_mining(self) -> bool:
        return self.node.is_mining

    def eth_hashrate(self) -> str:
        return hex(self.node.hashrate if hasattr(self.node, 'hashrate') else 0)

    def eth_gas_price(self) -> str:
        return hex(self.node.gas_price)

    def eth_accounts(self) -> List[str]:
        return self.node.accounts

    def eth_block_number(self) -> str:
        return hex(self.node.block_number)

    def eth_get_balance(self, address: str, block: str = "latest") -> str:
        balance = self.node.get_balance(address, block)
        return hex(balance)

    def eth_get_storage_at(self, address: str, position: str, block: str = "latest") -> str:
        slot = int(position, 16)
        value = self.node.get_storage_at(address, slot, block)
        return to_hex(value.to_bytes(32, 'big'))

    def eth_get_transaction_count(self, address: str, block: str = "latest") -> str:
        count = self.node.get_transaction_count(address, block)
        return hex(count)

    def eth_get_block_tx_count_by_hash(self, block_hash: str) -> Optional[str]:
        block = self.node.get_block_by_hash(block_hash)
        if block:
            return hex(len(block.transactions))
        return None

    def eth_get_block_tx_count_by_number(self, block_number: str) -> Optional[str]:
        block = self.node.get_block_by_number(block_number)
        if block:
            return hex(len(block.transactions))
        return None

    def eth_get_code(self, address: str, block: str = "latest") -> str:
        code = self.node.get_code(address, block)
        return to_hex(code)

    def eth_sign(self, address: str, message: str) -> str:
        return self.node.sign_message(address, message)

    def eth_send_transaction(self, tx_data: dict) -> str:
        return self.node.send_transaction(tx_data)

    def eth_send_raw_transaction(self, raw_tx: str, client_ip: str = None) -> str:
        """Send a raw transaction with logging for rejected TX (spam detection)"""
        try:
            return self.node.send_raw_transaction(raw_tx)
        except Exception as e:
            # Log rejected transaction only (spam detection)
            error_msg = str(e)
            rpc_logger.warning(f"TX_REJECTED | IP: {client_ip or 'unknown'} | Error: {error_msg[:100]}")
            raise

    def eth_call(self, tx_data: dict, block: str = "latest") -> str:
        import traceback
        import sys
        try:
            return self.node.call(tx_data, block)
        except Exception as e:
            # Log full traceback for debugging
            sys.stderr.write(f"eth_call error: {e}\n")
            traceback.print_exc(file=sys.stderr)
            sys.stderr.flush()
            raise

    def eth_estimate_gas(self, tx_data: dict, block: str = "latest") -> str:
        gas = self.node.estimate_gas(tx_data, block)
        return hex(gas)

    def eth_get_block_by_hash(self, block_hash: str, full_txs: bool = False) -> Optional[dict]:
        block = self.node.get_block_by_hash(block_hash)
        if block:
            return block.to_dict(full_transactions=full_txs)
        return None

    def eth_get_block_by_number(self, block_number: str, full_txs: bool = False) -> Optional[dict]:
        block = self.node.get_block_by_number(block_number)
        if block:
            return block.to_dict(full_transactions=full_txs)
        return None

    def eth_get_transaction_by_hash(self, tx_hash: str) -> Optional[dict]:
        tx = self.node.get_transaction_by_hash(tx_hash)
        if tx:
            return tx.to_dict()
        return None

    def eth_get_tx_by_block_hash_and_index(self, block_hash: str, index: str) -> Optional[dict]:
        block = self.node.get_block_by_hash(block_hash)
        if block:
            idx = int(index, 16)
            if idx < len(block.transactions):
                return block.transactions[idx].to_dict()
        return None

    def eth_get_tx_by_block_number_and_index(self, block_number: str, index: str) -> Optional[dict]:
        block = self.node.get_block_by_number(block_number)
        if block:
            idx = int(index, 16)
            if idx < len(block.transactions):
                return block.transactions[idx].to_dict()
        return None

    def eth_get_transaction_receipt(self, tx_hash: str) -> Optional[dict]:
        receipt = self.node.get_transaction_receipt(tx_hash)
        if receipt:
            return receipt.to_dict()
        return None

    def eth_new_filter(self, filter_params: dict) -> str:
        return self.node.new_filter(filter_params)

    def eth_new_block_filter(self) -> str:
        return self.node.new_block_filter()

    def eth_new_pending_tx_filter(self) -> str:
        return self.node.new_pending_transaction_filter()

    def eth_uninstall_filter(self, filter_id: str) -> bool:
        return self.node.uninstall_filter(filter_id)

    def eth_get_filter_changes(self, filter_id: str) -> List:
        return self.node.get_filter_changes(filter_id)

    def eth_get_filter_logs(self, filter_id: str) -> List:
        return self.node.get_filter_logs(filter_id)

    def eth_get_logs(self, filter_params: dict) -> List[dict]:
        return self.node.get_logs(filter_params)

    def eth_max_priority_fee_per_gas(self) -> str:
        return hex(self.node.max_priority_fee)

    def eth_fee_history(self, block_count: str, newest_block: str, reward_percentiles: List[float]) -> dict:
        return self.node.fee_history(int(block_count, 16), newest_block, reward_percentiles)

    # TxPool methods
    def txpool_content(self) -> dict:
        return self.node.txpool.content()

    def txpool_status(self) -> dict:
        return self.node.txpool.status()

    # EVM methods (dev mode)
    def evm_mine(self) -> str:
        """Deprecated - use validator to produce blocks instead"""
        raise ValueError("Mining deprecated - use nanopy-validator to produce blocks")

    def evm_increase_time(self, seconds: int) -> str:
        self.node.increase_time(seconds)
        return hex(seconds)

    def evm_set_next_block_timestamp(self, timestamp: int) -> str:
        self.node.set_next_block_timestamp(timestamp)
        return hex(timestamp)

    def evm_snapshot(self) -> str:
        snapshot_id = self.node.snapshot()
        return hex(snapshot_id)

    def evm_revert(self, snapshot_id: str) -> bool:
        return self.node.revert(int(snapshot_id, 16))

    # NanoNode staking methods
    def nno_get_validators(self) -> list:
        return self.node.get_validators()

    def nno_get_stake(self, address: str) -> str:
        return hex(self.node.get_stake(address))

    def nno_register_validator(self, address: str, stake: str) -> bool:
        stake_amount = int(stake, 16)
        return self.node.register_validator(address, stake_amount)

    def nno_add_stake(self, address: str, amount: str) -> bool:
        stake_amount = int(amount, 16)
        return self.node.add_stake(address, stake_amount)

    def nno_withdraw_stake(self, address: str) -> str:
        amount = self.node.withdraw_stake(address)
        return hex(amount)

    def nno_start_validating(self) -> bool:
        self.node.start_validating()
        return True

    def nno_stop_validating(self) -> bool:
        self.node.stop_validating()
        return True

    # Validator client methods
    def validator_get_block_template(self, coinbase: str) -> dict:
        """
        Get a block template for the validator to build a block.
        Returns all data needed to construct and sign a block.
        """
        import time

        parent = self.node.latest_block
        pending_txs = self.node.txpool.get_pending_for_block(self.node.config.gas_limit)

        # Convert transactions to serializable format
        tx_list = []
        for tx in pending_txs:
            tx_list.append(tx.to_dict())

        return {
            "parentHash": to_hex(parent.hash),
            "blockNumber": hex(parent.number + 1),
            "timestamp": hex(int(time.time())),
            "gasLimit": hex(self.node.config.gas_limit),
            "coinbase": coinbase,
            "transactions": tx_list,
            "stateRoot": to_hex(parent.header.state_root),
            "difficulty": hex(1),  # PoS uses difficulty 1
        }

    def validator_submit_block(self, block_data: dict) -> dict:
        """
        Submit a block built by the validator client.
        The node will validate and add it to the chain.
        """
        try:
            # Reconstruct block from data
            from nanopy.core.block import Block, BlockHeader
            from nanopy.core.transaction import SignedTransaction

            # Parse transactions
            transactions = []
            for tx_data in block_data.get("transactions", []):
                tx = SignedTransaction.from_dict(tx_data)
                transactions.append(tx)

            # Create block header
            header = BlockHeader(
                parent_hash=to_bytes(hexstr=block_data["parentHash"]),
                uncle_hash=to_bytes(hexstr=block_data.get("uncleHash", "0x" + "00" * 32)),
                coinbase=block_data["coinbase"],
                state_root=bytes(32),  # Will be computed
                transactions_root=bytes(32),  # Will be computed
                receipts_root=bytes(32),  # Will be computed
                logs_bloom=bytes(256),
                difficulty=int(block_data.get("difficulty", "0x1"), 16),
                number=int(block_data["blockNumber"], 16),
                gas_limit=int(block_data["gasLimit"], 16),
                gas_used=0,  # Will be computed
                timestamp=int(block_data["timestamp"], 16),
                extra_data=b"NanoPy",
                mix_hash=bytes(32),
                nonce=bytes(8),  # PoS uses zero nonce
                base_fee_per_gas=self.node.latest_block.header.base_fee_per_gas,
            )

            # Create and process block via consensus engine
            block, receipts = self.node.consensus.create_block(
                parent=self.node.latest_block,
                transactions=transactions,
                coinbase=block_data["coinbase"],
                state=self.node.state,
                timestamp=int(block_data["timestamp"], 16),
            )

            # Add to chain
            self.node.blocks.append(block)
            self.node.blocks_by_hash[block.hash] = block

            # Store receipts
            for receipt in receipts:
                self.node.receipts[to_hex(receipt.tx_hash)[2:]] = receipt
                if self.node.chaindb:
                    self.node.chaindb.put_receipt(to_hex(receipt.tx_hash), receipt.to_dict())

            # Persist block
            if self.node.chaindb:
                self.node.chaindb.put_block(block.to_dict(full_transactions=True))

            # Persist state
            if self.node.statedb:
                self.node._persist_state_changes(transactions)

            # Remove from txpool
            self.node.txpool.remove_mined(transactions)

            # Notify WebSocket subscribers of new block
            self.node._notify_new_block(block, receipts)

            # Broadcast via P2P
            if self.node.p2p:
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.ensure_future(self.node.p2p.broadcast_block(block.to_dict()))
                    else:
                        loop.run_until_complete(self.node.p2p.broadcast_block(block.to_dict()))
                except Exception:
                    pass

            # Calculate rewards
            # Block reward from consensus engine
            block_reward = self.node.consensus.BLOCK_REWARD  # 2 NPY in wei

            # Gas fees = sum of (gas_used * gas_price) for each tx
            gas_fees = 0
            for receipt in receipts:
                # Find the tx to get gas price
                for tx in transactions:
                    if tx.hash() == receipt.tx_hash:
                        gas_fees += receipt.gas_used * tx.transaction.effective_gas_price
                        break

            return {
                "success": True,
                "blockHash": to_hex(block.hash),
                "blockNumber": hex(block.number),
                "gasUsed": hex(block.header.gas_used),
                "transactionCount": len(block.transactions),
                "blockReward": hex(block_reward),
                "gasFees": hex(gas_fees),
                "totalReward": hex(block_reward + gas_fees),
            }

        except Exception as e:
            import traceback
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
            }

    def validator_is_selected(self, address: str) -> dict:
        """
        Check if the given address is selected as the next validator.
        """
        if not hasattr(self.node, 'pos') or not self.node.pos:
            return {"selected": False, "error": "PoS not enabled"}

        selected = self.node.pos.select_validator(
            self.node.block_number,
            self.node.latest_block.hash
        )

        return {
            "selected": selected and selected.lower() == address.lower(),
            "selectedValidator": selected,
            "blockNumber": hex(self.node.block_number),
            "yourAddress": address,
        }

    def validator_get_pending_transactions(self, gas_limit: str = None) -> list:
        """
        Get pending transactions for block building.
        """
        limit = int(gas_limit, 16) if gas_limit else self.node.config.gas_limit
        pending = self.node.txpool.get_pending_for_block(limit)
        return [tx.to_dict() for tx in pending]

    def validator_get_sync_status(self) -> dict:
        """
        Get the sync status of the node.
        Validator should only produce blocks when node is synced.
        """
        # Check if we have peers and if we're behind
        peer_count = 0
        if hasattr(self.node, 'p2p') and self.node.p2p:
            peer_count = len(self.node.p2p.peers)

        # For now, consider synced if we have the chain
        # In production, would compare with peer block heights
        return {
            "syncing": False,  # TODO: Implement proper sync detection
            "currentBlock": hex(self.node.block_number),
            "highestBlock": hex(self.node.block_number),  # TODO: Get from peers
            "peerCount": peer_count,
            "ready": True,  # Node is ready to accept blocks
        }

    # Network discovery methods
    def nno_get_nodes(self) -> dict:
        """
        Get list of known nodes in the network.
        Returns RPC endpoints for validators and users.
        """
        from nanopy.node.main import MAINNET_BOOTNODES

        # Official RPC nodes (hardcoded for now, could be dynamic later)
        rpc_nodes = [
            {
                "url": "http://51.68.125.99:8545",
                "name": "NanoPy Node 1 (OVH)",
                "location": "EU",
                "status": "active",
            },
        ]

        # Get connected peers from P2P
        connected_peers = []
        if hasattr(self.node, 'p2p') and self.node.p2p:
            for peer_id, peer_obj in self.node.p2p.peers.items():
                connected_peers.append({
                    "peerId": str(peer_id),
                    "address": str(getattr(peer_obj, 'address', 'unknown')),
                })

        return {
            "rpcNodes": rpc_nodes,
            "bootnodes": MAINNET_BOOTNODES,
            "connectedPeers": connected_peers,
            "totalPeers": len(connected_peers),
        }

    def nno_get_network_info(self) -> dict:
        """
        Get comprehensive network information.
        Useful for explorers, wallets, and validators.
        """
        from nanopy.node.main import MAINNET_BOOTNODES

        peer_count = 0
        if hasattr(self.node, 'p2p') and self.node.p2p:
            peer_count = len(self.node.p2p.peers)

        # Get validator count
        validator_count = 0
        if hasattr(self.node, 'pos') and self.node.pos:
            validator_count = len(self.node.pos.validators)

        return {
            "network": {
                "name": "NanoPy Mainnet" if self.node.config.chain_id == 7770 else ("Pyralis Testnet" if self.node.config.chain_id == 77777 else f"Chain {self.node.config.chain_id}"),
                "chainId": self.node.config.chain_id,
                "consensus": "PoS",
                "blockTime": self.node.config.block_time,
            },
            "node": {
                "version": __import__("nanopy").__version__,
                "peerId": self.node.p2p.peer_id if hasattr(self.node, 'p2p') and self.node.p2p else None,
                "rpcPort": self.node.config.rpc_port,
                "p2pPort": self.node.config.p2p_port,
            },
            "chain": {
                "blockNumber": self.node.block_number,
                "latestBlockHash": to_hex(self.node.latest_block.hash) if self.node.latest_block else None,
                "gasLimit": self.node.config.gas_limit,
            },
            "peers": {
                "count": peer_count,
                "maxPeers": self.node.config.max_peers,
                "bootnodes": len(MAINNET_BOOTNODES),
            },
            "validators": {
                "count": validator_count,
                "minStake": "10000000000000000000000",  # 10,000 NPY in wei
            },
            "rpcEndpoints": [
                "http://51.68.125.99:8545",
            ],
        }


class RPCHandler(BaseHTTPRequestHandler):
    """HTTP handler for JSON-RPC requests"""

    rpc: NanoPyRPC = None

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        # Get client IP for logging
        client_ip = self.client_address[0]

        try:
            request = json.loads(body)

            # Handle batch or single request
            if isinstance(request, list):
                response = self.rpc.handle_batch(request, client_ip)
            else:
                response = self.rpc.handle_request(request, client_ip)

        except json.JSONDecodeError:
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": PARSE_ERROR.to_dict()
            }

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress logging


class ReuseAddrHTTPServer(HTTPServer):
    """HTTPServer with SO_REUSEADDR to allow quick restart"""
    allow_reuse_address = True


def start_rpc_server(node: 'NanoPyNode', host: str = "127.0.0.1", port: int = 8545) -> HTTPServer:
    """
    Start the JSON-RPC server

    Args:
        node: NanoPyNode instance
        host: Host to bind to
        port: Port to listen on

    Returns:
        HTTPServer instance
    """
    RPCHandler.rpc = NanoPyRPC(node)
    server = ReuseAddrHTTPServer((host, port), RPCHandler)

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    return server
