"""
NanoPy Validator - Separate validator process for PoS consensus
"""

import time
import logging
import threading
from typing import Optional

from eth_account import Account

from nanopy.validator.config import ValidatorConfig
from nanopy.validator.client import NodeRPCClient, RPCError

logger = logging.getLogger(__name__)


class Validator:
    """
    Standalone validator client for NanoPy PoS consensus.

    The validator connects to one or more NanoPy nodes via RPC and
    produces blocks when selected by the PoS consensus algorithm.

    Features:
    - Automatic failover between nodes
    - Graceful shutdown
    - Block production loop
    - Stake management
    """

    def __init__(self, config: ValidatorConfig):
        self.config = config
        self._running = False
        self._thread: Optional[threading.Thread] = None

        # Validate config
        errors = config.validate()
        if errors:
            raise ValueError(f"Invalid config: {', '.join(errors)}")

        # Extract validator address from private key
        key_bytes = bytes.fromhex(config.validator_key[2:])
        account = Account.from_key(key_bytes)
        self.address = account.address
        self._private_key = key_bytes

        # Create RPC client
        self.client = NodeRPCClient(
            nodes=config.nodes,
            timeout=config.rpc_timeout,
            max_retries=config.max_retries,
            failover_timeout=config.failover_timeout,
        )

        # Stats
        self.blocks_produced = 0
        self.total_rewards = 0.0  # Total NPY earned
        self.total_gas_fees = 0.0  # Total gas fees earned
        self.last_block_time: Optional[float] = None
        self.start_time: Optional[float] = None

        logger.info(f"Validator initialized: {self.address}")
        logger.info(f"Connected to nodes: {', '.join(config.nodes)}")

    def start(self):
        """Start the validator in a background thread."""
        if self._running:
            logger.warning("Validator already running")
            return

        self._running = True
        self.start_time = time.time()
        self._thread = threading.Thread(target=self._validation_loop, daemon=True)
        self._thread.start()
        logger.info("Validator started")

    def stop(self):
        """Stop the validator gracefully."""
        if not self._running:
            return

        logger.info("Stopping validator...")
        self._running = False
        if self._thread:
            self._thread.join(timeout=self.config.block_time + 5)
        logger.info("Validator stopped")

    def run(self):
        """Run the validator (blocking)."""
        self.start()
        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.stop()

    def _validation_loop(self):
        """Main validation loop - runs in background thread."""
        logger.info(f"Validation loop started (block_time={self.config.block_time}s)")

        while self._running:
            try:
                # Check if node is synced
                sync_status = self.client.get_sync_status()
                if sync_status.get("syncing"):
                    logger.debug("Node is syncing, waiting...")
                    time.sleep(self.config.block_time)
                    continue

                # Check if we're selected as validator
                selection = self.client.is_selected(self.address)

                if selection.get("selected"):
                    logger.info(f"Selected as validator for block {selection['blockNumber']}")
                    self._produce_block()
                else:
                    selected = selection.get("selectedValidator", "unknown")
                    logger.debug(f"Not selected. Current validator: {selected}")

            except RPCError as e:
                logger.error(f"RPC error: {e}")
            except ConnectionError as e:
                logger.error(f"Connection error: {e}")
            except Exception as e:
                logger.exception(f"Unexpected error: {e}")

            # Wait for next block slot
            time.sleep(self.config.block_time)

    def _produce_block(self):
        """Produce a new block."""
        try:
            # Get block template from node
            template = self.client.get_block_template(self.address)
            logger.info(f"Got block template for block {template['blockNumber']}")

            tx_count = len(template.get("transactions", []))
            logger.info(f"Block will contain {tx_count} transactions")

            # Submit block to node
            # The node will execute transactions and compute state root
            result = self.client.submit_block(template)

            if result.get("success"):
                self.blocks_produced += 1
                self.last_block_time = time.time()

                # Get rewards from result (returned by node)
                block_reward_wei = int(result.get('blockReward', '0x0'), 16)
                gas_fees_wei = int(result.get('gasFees', '0x0'), 16)
                block_reward = block_reward_wei / 10**18
                gas_fees = gas_fees_wei / 10**18
                total_reward = block_reward + gas_fees

                # Track cumulative rewards
                self.total_rewards += block_reward
                self.total_gas_fees += gas_fees

                logger.info(
                    f"Block {result['blockNumber']} produced! "
                    f"Hash: {result['blockHash'][:18]}... "
                    f"Txs: {result['transactionCount']} | "
                    f"Reward: +{total_reward:.6f} NPY (Total: {self.total_rewards + self.total_gas_fees:.2f} NPY)"
                )
            else:
                logger.error(f"Block submission failed: {result.get('error')}")

        except Exception as e:
            logger.exception(f"Failed to produce block: {e}")

    def ensure_registered(self, stake: Optional[int] = None):
        """Ensure validator is registered with sufficient stake."""
        try:
            current_stake = self.client.get_stake(self.address)
            if current_stake > 0:
                logger.info(f"Validator already registered with stake: {current_stake / 10**18:.2f} NPY")
                return True

            # Need to register
            stake_amount = stake or self.config.min_stake
            logger.info(f"Registering validator with stake: {stake_amount / 10**18:.2f} NPY")

            result = self.client.register_validator(self.address, stake_amount)
            if result:
                logger.info("Validator registered successfully")
                return True
            else:
                logger.error("Failed to register validator")
                return False

        except Exception as e:
            logger.error(f"Failed to check/register validator: {e}")
            return False

    def get_stats(self) -> dict:
        """Get validator statistics."""
        uptime = time.time() - self.start_time if self.start_time else 0
        return {
            "address": self.address,
            "running": self._running,
            "blocks_produced": self.blocks_produced,
            "total_rewards_npy": self.total_rewards,
            "total_gas_fees_npy": self.total_gas_fees,
            "total_earned_npy": self.total_rewards + self.total_gas_fees,
            "uptime_seconds": int(uptime),
            "last_block_time": self.last_block_time,
            "current_node": self.client.current_node,
        }

    def __repr__(self):
        return f"Validator({self.address}, running={self._running})"
