"""
EVM Gas Costs - Based on Ethereum Yellow Paper and EIPs

Gas costs are organized by category and EIP for clarity.
Default values are for post-Berlin (EIP-2929) and post-London (EIP-3529).
"""

# =============================================================================
# Base Costs (Yellow Paper)
# =============================================================================

G_ZERO = 0          # Nothing paid for operations of the set Wzero
G_BASE = 2          # Amount of gas paid for operations of the set Wbase
G_VERY_LOW = 3      # Amount for operations of the set Wverylow
G_LOW = 5           # Amount for operations of the set Wlow
G_MID = 8           # Amount for operations of the set Wmid
G_HIGH = 10         # Amount for operations of the set Whigh

# =============================================================================
# Transaction Costs
# =============================================================================

G_TRANSACTION = 21000           # Base cost of transaction
G_TX_DATA_ZERO = 4              # Per zero byte of data
G_TX_DATA_NONZERO = 16          # Per non-zero byte of data (EIP-2028: was 68)
G_TX_CREATE = 32000             # Cost for contract creation
G_TX_ACCESS_LIST_ADDR = 2400    # Per address in access list (EIP-2930)
G_TX_ACCESS_LIST_STORAGE = 1900 # Per storage key in access list (EIP-2930)

# =============================================================================
# Memory Costs
# =============================================================================

G_MEMORY = 3                    # Per word of memory expansion
G_COPY = 3                      # Per word for COPY operations

# =============================================================================
# Storage Costs (EIP-2200, EIP-2929, EIP-3529)
# =============================================================================

# EIP-2929: Cold/Warm access
G_COLD_SLOAD = 2100             # Cold SLOAD cost
G_COLD_ACCOUNT_ACCESS = 2600    # Cold account access (BALANCE, EXTCODE*, etc.)
G_WARM_ACCESS = 100             # Warm storage/account access

# SSTORE costs (EIP-2200 with EIP-3529 modifications)
G_SSTORE_SET = 20000            # From zero to non-zero
G_SSTORE_RESET = 2900           # From non-zero to non-zero (or non-zero to zero)
G_SSTORE_CLEARS_REFUND = 4800   # Refund for clearing storage (EIP-3529: was 15000)

# =============================================================================
# Call Costs
# =============================================================================

G_CALL = 100                    # Base cost for CALL
G_CALL_VALUE = 9000             # Extra cost for sending value
G_CALL_STIPEND = 2300           # Free gas given for value transfer
G_NEW_ACCOUNT = 25000           # Cost for creating new account

# Static call and delegate call
G_STATICCALL = 100              # Base cost for STATICCALL
G_DELEGATECALL = 100            # Base cost for DELEGATECALL

# =============================================================================
# Create Costs
# =============================================================================

G_CREATE = 32000                # CREATE opcode
G_CREATE2 = 32000               # CREATE2 opcode
G_CODE_DEPOSIT = 200            # Per byte of code deposited
G_INIT_CODE_WORD = 2            # Per word of init code (EIP-3860)

# =============================================================================
# Log Costs
# =============================================================================

G_LOG = 375                     # Base cost for LOG
G_LOG_DATA = 8                  # Per byte of data
G_LOG_TOPIC = 375               # Per topic

# =============================================================================
# Other Opcodes
# =============================================================================

G_JUMPDEST = 1                  # JUMPDEST cost
G_KECCAK256 = 30                # Base cost for SHA3/KECCAK256
G_KECCAK256_WORD = 6            # Per word for SHA3/KECCAK256

G_EXP = 10                      # Base cost for EXP
G_EXP_BYTE = 50                 # Per byte of exponent

G_BLOCKHASH = 20                # BLOCKHASH opcode
G_SELFDESTRUCT = 5000           # Base SELFDESTRUCT cost
G_SELFDESTRUCT_NEW = 25000      # Extra if creating new account

# EIP-2929 access costs
G_COLD_ACCOUNT_ACCESS_COST = 2600   # Cold EXTCODESIZE, EXTCODECOPY, etc.
G_WARM_STORAGE_READ = 100           # Warm storage read

# =============================================================================
# Precompile Costs
# =============================================================================

G_ECRECOVER = 3000
G_SHA256_BASE = 60
G_SHA256_WORD = 12
G_RIPEMD160_BASE = 600
G_RIPEMD160_WORD = 120
G_IDENTITY_BASE = 15
G_IDENTITY_WORD = 3
G_MODEXP_MIN = 200
G_BN128_ADD = 150               # EIP-1108
G_BN128_MUL = 6000              # EIP-1108
G_BN128_PAIRING_BASE = 45000    # EIP-1108
G_BN128_PAIRING_POINT = 34000   # EIP-1108
G_BLAKE2F_ROUND = 1

# =============================================================================
# Gas Limits
# =============================================================================

MAX_CODE_SIZE = 24576           # EIP-170: max contract code size
MAX_INIT_CODE_SIZE = 49152      # EIP-3860: max init code size (2 * MAX_CODE_SIZE)
STACK_LIMIT = 1024              # Max stack depth


class GasCosts:
    """
    Gas cost configuration class.
    Allows customization for different network configurations.
    """

    def __init__(self, **overrides):
        """Initialize with default costs, allowing overrides."""
        # Set all defaults from module constants
        for name, value in globals().items():
            if name.startswith('G_') or name.startswith('MAX_') or name == 'STACK_LIMIT':
                setattr(self, name, value)

        # Apply any overrides
        for name, value in overrides.items():
            if hasattr(self, name):
                setattr(self, name, value)

    @classmethod
    def berlin(cls):
        """Gas costs for Berlin hard fork (EIP-2929)."""
        return cls()

    @classmethod
    def london(cls):
        """Gas costs for London hard fork (EIP-3529 reduced refunds)."""
        return cls(
            G_SSTORE_CLEARS_REFUND=4800,  # Reduced from 15000
        )

    @classmethod
    def shanghai(cls):
        """Gas costs for Shanghai hard fork."""
        return cls.london()

    @classmethod
    def cancun(cls):
        """Gas costs for Cancun hard fork."""
        return cls.shanghai()


# Default gas costs instance (London+)
DEFAULT_GAS_COSTS = GasCosts.london()
