"""
NanoPy Proof of Stake Consensus

Supports both in-memory validators and on-chain staking contract.
"""

import time
import random
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from eth_utils import to_hex, keccak, to_bytes


@dataclass
class Validator:
    address: str
    stake: int
    registered_at: int
    last_block: int = 0
    blocks_validated: int = 0
    is_active: bool = True


@dataclass
class StakeInfo:
    amount: int
    locked_until: int
    validator: str


# Staking contract function selectors
STAKING_SELECTORS = {
    'getValidators': '0xb7ab4db5',      # getValidators() returns address[]
    'isValidator': '0xfacd743b',         # isValidator(address) returns bool
    'getStake': '0x7a766460',           # getStake(address) returns uint256
    'getValidatorCount': '0x7071688a',  # getValidatorCount() returns uint256
}


class ProofOfStake:
    """
    Proof of Stake consensus engine for NanoPy

    - Validators stake NPY to participate
    - Selection weighted by stake amount
    - Rewards distributed to validators
    - Supports on-chain staking contract
    - Bootstrap mode: Founder can validate before staking contract is deployed
    """

    MIN_STAKE = 10_000 * 10**18  # 10,000 NPY
    BLOCK_REWARD = 2 * 10**18    # 2 NPY per block
    LOCK_PERIOD = 100            # Blocks before unstake

    # Bootstrap validator (PoA) - can validate until staking contract is deployed
    BOOTSTRAP_VALIDATOR = "0x311384E7e4803AdBDB1D8ab46b973eeE0f9cF55B"

    def __init__(self, state=None, staking_contract: str = None, node=None):
        self.state = state
        self.staking_contract = staking_contract  # Contract address
        self.node = node  # Reference to node for contract calls
        self.validators: Dict[str, Validator] = {}
        self.stakes: Dict[str, StakeInfo] = {}
        self.current_validator: Optional[str] = None
        self.last_block_time = 0
        self.block_time = 12  # seconds
        self._contract_validators_cache: List[str] = []
        self._cache_block: int = -1

    def register_validator(self, address: str, stake: int, block_number: int) -> bool:
        """Register a new validator with stake"""
        if stake < self.MIN_STAKE:
            return False

        if address in self.validators:
            return False

        self.validators[address] = Validator(
            address=address,
            stake=stake,
            registered_at=block_number,
        )

        self.stakes[address] = StakeInfo(
            amount=stake,
            locked_until=block_number + self.LOCK_PERIOD,
            validator=address,
        )

        return True

    def add_stake(self, address: str, amount: int, block_number: int) -> bool:
        """Add more stake to existing validator"""
        if address not in self.validators:
            return False

        self.validators[address].stake += amount
        self.stakes[address].amount += amount
        self.stakes[address].locked_until = block_number + self.LOCK_PERIOD

        return True

    def withdraw_stake(self, address: str, block_number: int) -> Tuple[bool, int]:
        """Withdraw stake if lock period passed"""
        if address not in self.validators:
            return False, 0

        stake_info = self.stakes.get(address)
        if not stake_info:
            return False, 0

        if block_number < stake_info.locked_until:
            return False, 0

        amount = stake_info.amount

        del self.validators[address]
        del self.stakes[address]

        return True, amount

    def select_validator(self, block_number: int, block_hash: bytes) -> Optional[str]:
        """Select next validator weighted by stake"""
        active_validators = [v for v in self.validators.values() if v.is_active]

        # Bootstrap mode: if no validators registered, use bootstrap validator
        if not active_validators:
            if self._is_bootstrap_mode():
                return self.BOOTSTRAP_VALIDATOR
            return None

        total_stake = sum(v.stake for v in active_validators)
        if total_stake == 0:
            return None

        # Deterministic random based on block hash
        seed = int.from_bytes(
            keccak(block_hash + block_number.to_bytes(8, 'big'))[:8],
            'big'
        )
        random.seed(seed)

        # Weighted selection
        selection = random.randint(0, total_stake - 1)
        cumulative = 0

        for validator in active_validators:
            cumulative += validator.stake
            if selection < cumulative:
                self.current_validator = validator.address
                return validator.address

        return active_validators[-1].address

    def validate_block(self, block, validator_address: str) -> bool:
        """Verify block was created by valid validator"""
        if validator_address not in self.validators:
            return False

        validator = self.validators[validator_address]
        if not validator.is_active:
            return False

        # Check validator was selected for this block
        expected = self.select_validator(block.number - 1, block.parent_hash)
        if expected != validator_address:
            return False

        return True

    def apply_reward(self, validator_address: str, block_number: int):
        """Apply block reward to validator"""
        if validator_address not in self.validators:
            return

        validator = self.validators[validator_address]
        validator.last_block = block_number
        validator.blocks_validated += 1

        # Add reward to stake (compound)
        validator.stake += self.BLOCK_REWARD
        if validator_address in self.stakes:
            self.stakes[validator_address].amount += self.BLOCK_REWARD

    def slash_validator(self, address: str, reason: str = ""):
        """Slash validator for misbehavior"""
        if address not in self.validators:
            return

        validator = self.validators[address]

        # Slash 10% of stake
        slash_amount = validator.stake // 10
        validator.stake -= slash_amount

        if address in self.stakes:
            self.stakes[address].amount -= slash_amount

        # Deactivate if stake below minimum
        if validator.stake < self.MIN_STAKE:
            validator.is_active = False

    def get_validator_set(self) -> List[dict]:
        """Get list of all validators"""
        return [
            {
                "address": v.address,
                "stake": hex(v.stake),
                "blocks_validated": v.blocks_validated,
                "is_active": v.is_active,
            }
            for v in self.validators.values()
        ]

    def get_total_stake(self) -> int:
        """Get total staked amount"""
        return sum(v.stake for v in self.validators.values())

    def is_validator(self, address: str) -> bool:
        """Check if address is registered validator"""
        # Bootstrap mode: Founder can validate before staking contract exists
        if self._is_bootstrap_mode() and address.lower() == self.BOOTSTRAP_VALIDATOR.lower():
            return True
        # Check on-chain contract first
        if self.staking_contract and self.node:
            return self._is_validator_from_contract(address)
        # Fallback to in-memory
        return address in self.validators and self.validators[address].is_active

    def _is_bootstrap_mode(self) -> bool:
        """Check if we're in bootstrap mode (no staking contract deployed yet)"""
        if not self.staking_contract or not self.node:
            return True
        # Check if staking contract has code
        try:
            code = self.node.get_code(self.staking_contract)
            return code is None or code == b'' or code == '0x'
        except Exception:
            return True

    def get_stake(self, address: str) -> int:
        """Get stake amount for address"""
        # Check on-chain contract first
        if self.staking_contract and self.node:
            return self._get_stake_from_contract(address)
        # Fallback to in-memory
        if address in self.stakes:
            return self.stakes[address].amount
        return 0

    # Contract interaction methods
    def _call_contract(self, data: str) -> str:
        """Call staking contract"""
        if not self.node or not self.staking_contract:
            return "0x"
        try:
            return self.node.call({
                "to": self.staking_contract,
                "data": data,
            })
        except Exception:
            return "0x"

    def _is_validator_from_contract(self, address: str) -> bool:
        """Check isValidator(address) on contract"""
        # Encode: selector + address padded to 32 bytes
        addr = address.lower().replace("0x", "").zfill(64)
        data = STAKING_SELECTORS['isValidator'] + addr
        result = self._call_contract(data)
        if result and len(result) >= 66:
            return int(result[-1], 16) == 1
        return False

    def _get_stake_from_contract(self, address: str) -> int:
        """Get stake amount from contract"""
        addr = address.lower().replace("0x", "").zfill(64)
        data = STAKING_SELECTORS['getStake'] + addr
        result = self._call_contract(data)
        if result and len(result) > 2:
            return int(result, 16)
        return 0

    def _get_validators_from_contract(self) -> List[str]:
        """Get list of validators from contract"""
        data = STAKING_SELECTORS['getValidators']
        result = self._call_contract(data)
        if not result or result == "0x":
            return []
        # Decode dynamic array of addresses
        try:
            hex_data = result[2:]  # Remove 0x
            if len(hex_data) < 128:  # At least offset + length
                return []
            # First 32 bytes = offset to array data
            # Next 32 bytes = array length
            length = int(hex_data[64:128], 16)
            validators = []
            for i in range(length):
                start = 128 + i * 64
                addr_hex = hex_data[start:start+64]
                validators.append("0x" + addr_hex[-40:])
            return validators
        except Exception:
            return []

    def sync_from_contract(self):
        """Sync validator list from contract"""
        if not self.staking_contract or not self.node:
            return
        validators = self._get_validators_from_contract()
        for addr in validators:
            if addr.lower() not in [v.lower() for v in self.validators]:
                stake = self._get_stake_from_contract(addr)
                if stake >= self.MIN_STAKE:
                    self.validators[addr.lower()] = Validator(
                        address=addr,
                        stake=stake,
                        registered_at=0,
                        is_active=True
                    )
