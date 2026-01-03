"""
Validator Client Configuration
"""

from dataclasses import dataclass, field
from typing import List, Optional
import json
import os


@dataclass
class ValidatorConfig:
    """
    Configuration for the validator client.

    The validator client connects to one or more NanoPy nodes via RPC
    and produces blocks when selected by the PoS consensus.
    """

    # Validator private key (hex string with 0x prefix)
    validator_key: str = ""

    # List of node RPC endpoints (for failover)
    nodes: List[str] = field(default_factory=lambda: ["http://localhost:8545"])

    # Block production interval in seconds
    block_time: int = 12

    # Timeout for RPC calls in seconds
    rpc_timeout: int = 10

    # Timeout before trying next node on failure
    failover_timeout: int = 5

    # Maximum retries per node before failover
    max_retries: int = 3

    # Minimum stake required (in wei)
    min_stake: int = 10_000 * 10**18  # 10,000 NPY

    # Log level
    log_level: str = "INFO"

    # Data directory for validator state
    data_dir: str = "./validator_data"

    @classmethod
    def from_file(cls, path: str) -> "ValidatorConfig":
        """Load configuration from JSON file."""
        with open(path, "r") as f:
            data = json.load(f)
        return cls(**data)

    @classmethod
    def from_env(cls) -> "ValidatorConfig":
        """Load configuration from environment variables."""
        config = cls()

        if os.environ.get("VALIDATOR_KEY"):
            config.validator_key = os.environ["VALIDATOR_KEY"]

        if os.environ.get("VALIDATOR_NODES"):
            config.nodes = os.environ["VALIDATOR_NODES"].split(",")

        if os.environ.get("VALIDATOR_BLOCK_TIME"):
            config.block_time = int(os.environ["VALIDATOR_BLOCK_TIME"])

        if os.environ.get("VALIDATOR_LOG_LEVEL"):
            config.log_level = os.environ["VALIDATOR_LOG_LEVEL"]

        return config

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "validator_key": self.validator_key[:10] + "..." if self.validator_key else "",
            "nodes": self.nodes,
            "block_time": self.block_time,
            "rpc_timeout": self.rpc_timeout,
            "failover_timeout": self.failover_timeout,
            "max_retries": self.max_retries,
            "log_level": self.log_level,
        }

    def save(self, path: str):
        """Save configuration to JSON file (without private key)."""
        data = self.to_dict()
        data["validator_key"] = ""  # Never save private key
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def validate(self) -> List[str]:
        """Validate configuration. Returns list of errors."""
        errors = []

        if not self.validator_key:
            errors.append("validator_key is required")
        elif not self.validator_key.startswith("0x"):
            errors.append("validator_key must start with 0x")
        elif len(self.validator_key) != 66:  # 0x + 64 hex chars
            errors.append("validator_key must be 32 bytes (66 chars with 0x)")

        if not self.nodes:
            errors.append("at least one node endpoint is required")

        for node in self.nodes:
            if not node.startswith("http://") and not node.startswith("https://"):
                errors.append(f"invalid node URL: {node}")

        if self.block_time < 1:
            errors.append("block_time must be at least 1 second")

        return errors
