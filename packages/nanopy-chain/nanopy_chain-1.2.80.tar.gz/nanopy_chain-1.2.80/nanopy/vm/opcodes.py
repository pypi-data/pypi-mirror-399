"""
NanoPy VM Opcodes - Complete EVM opcode definitions
"""

from enum import IntEnum


class Opcodes(IntEnum):
    """
    Complete EVM Opcodes
    https://www.evm.codes/
    """

    # Stop and Arithmetic Operations (0x00-0x0b)
    STOP = 0x00
    ADD = 0x01
    MUL = 0x02
    SUB = 0x03
    DIV = 0x04
    SDIV = 0x05
    MOD = 0x06
    SMOD = 0x07
    ADDMOD = 0x08
    MULMOD = 0x09
    EXP = 0x0A
    SIGNEXTEND = 0x0B

    # Comparison & Bitwise Logic Operations (0x10-0x1d)
    LT = 0x10
    GT = 0x11
    SLT = 0x12
    SGT = 0x13
    EQ = 0x14
    ISZERO = 0x15
    AND = 0x16
    OR = 0x17
    XOR = 0x18
    NOT = 0x19
    BYTE = 0x1A
    SHL = 0x1B  # EIP-145
    SHR = 0x1C  # EIP-145
    SAR = 0x1D  # EIP-145

    # SHA3 (0x20)
    SHA3 = 0x20

    # Environmental Information (0x30-0x3f)
    ADDRESS = 0x30
    BALANCE = 0x31
    ORIGIN = 0x32
    CALLER = 0x33
    CALLVALUE = 0x34
    CALLDATALOAD = 0x35
    CALLDATASIZE = 0x36
    CALLDATACOPY = 0x37
    CODESIZE = 0x38
    CODECOPY = 0x39
    GASPRICE = 0x3A
    EXTCODESIZE = 0x3B
    EXTCODECOPY = 0x3C
    RETURNDATASIZE = 0x3D  # EIP-211
    RETURNDATACOPY = 0x3E  # EIP-211
    EXTCODEHASH = 0x3F  # EIP-1052

    # Block Information (0x40-0x4a)
    BLOCKHASH = 0x40
    COINBASE = 0x41
    TIMESTAMP = 0x42
    NUMBER = 0x43
    PREVRANDAO = 0x44  # Was DIFFICULTY, renamed in Paris (The Merge)
    GASLIMIT = 0x45
    CHAINID = 0x46  # EIP-1344
    SELFBALANCE = 0x47  # EIP-1884
    BASEFEE = 0x48  # EIP-3198

    # Stack, Memory, Storage and Flow Operations (0x50-0x5b)
    POP = 0x50
    MLOAD = 0x51
    MSTORE = 0x52
    MSTORE8 = 0x53
    SLOAD = 0x54
    SSTORE = 0x55
    JUMP = 0x56
    JUMPI = 0x57
    PC = 0x58
    MSIZE = 0x59
    GAS = 0x5A
    JUMPDEST = 0x5B

    # Push Operations (0x5f-0x7f)
    PUSH0 = 0x5F  # EIP-3855
    PUSH1 = 0x60
    PUSH2 = 0x61
    PUSH3 = 0x62
    PUSH4 = 0x63
    PUSH5 = 0x64
    PUSH6 = 0x65
    PUSH7 = 0x66
    PUSH8 = 0x67
    PUSH9 = 0x68
    PUSH10 = 0x69
    PUSH11 = 0x6A
    PUSH12 = 0x6B
    PUSH13 = 0x6C
    PUSH14 = 0x6D
    PUSH15 = 0x6E
    PUSH16 = 0x6F
    PUSH17 = 0x70
    PUSH18 = 0x71
    PUSH19 = 0x72
    PUSH20 = 0x73
    PUSH21 = 0x74
    PUSH22 = 0x75
    PUSH23 = 0x76
    PUSH24 = 0x77
    PUSH25 = 0x78
    PUSH26 = 0x79
    PUSH27 = 0x7A
    PUSH28 = 0x7B
    PUSH29 = 0x7C
    PUSH30 = 0x7D
    PUSH31 = 0x7E
    PUSH32 = 0x7F

    # Duplication Operations (0x80-0x8f)
    DUP1 = 0x80
    DUP2 = 0x81
    DUP3 = 0x82
    DUP4 = 0x83
    DUP5 = 0x84
    DUP6 = 0x85
    DUP7 = 0x86
    DUP8 = 0x87
    DUP9 = 0x88
    DUP10 = 0x89
    DUP11 = 0x8A
    DUP12 = 0x8B
    DUP13 = 0x8C
    DUP14 = 0x8D
    DUP15 = 0x8E
    DUP16 = 0x8F

    # Exchange Operations (0x90-0x9f)
    SWAP1 = 0x90
    SWAP2 = 0x91
    SWAP3 = 0x92
    SWAP4 = 0x93
    SWAP5 = 0x94
    SWAP6 = 0x95
    SWAP7 = 0x96
    SWAP8 = 0x97
    SWAP9 = 0x98
    SWAP10 = 0x99
    SWAP11 = 0x9A
    SWAP12 = 0x9B
    SWAP13 = 0x9C
    SWAP14 = 0x9D
    SWAP15 = 0x9E
    SWAP16 = 0x9F

    # Logging Operations (0xa0-0xa4)
    LOG0 = 0xA0
    LOG1 = 0xA1
    LOG2 = 0xA2
    LOG3 = 0xA3
    LOG4 = 0xA4

    # System Operations (0xf0-0xff)
    CREATE = 0xF0
    CALL = 0xF1
    CALLCODE = 0xF2
    RETURN = 0xF3
    DELEGATECALL = 0xF4  # EIP-7
    CREATE2 = 0xF5  # EIP-1014
    STATICCALL = 0xFA  # EIP-214
    REVERT = 0xFD  # EIP-140
    INVALID = 0xFE
    SELFDESTRUCT = 0xFF


# Gas costs for opcodes (Berlin/London)
GAS_COSTS = {
    # Zero gas
    Opcodes.STOP: 0,
    Opcodes.RETURN: 0,
    Opcodes.REVERT: 0,

    # Base (2 gas)
    Opcodes.ADDRESS: 2,
    Opcodes.ORIGIN: 2,
    Opcodes.CALLER: 2,
    Opcodes.CALLVALUE: 2,
    Opcodes.CALLDATASIZE: 2,
    Opcodes.CODESIZE: 2,
    Opcodes.GASPRICE: 2,
    Opcodes.COINBASE: 2,
    Opcodes.TIMESTAMP: 2,
    Opcodes.NUMBER: 2,
    Opcodes.PREVRANDAO: 2,
    Opcodes.GASLIMIT: 2,
    Opcodes.CHAINID: 2,
    Opcodes.BASEFEE: 2,
    Opcodes.POP: 2,
    Opcodes.PC: 2,
    Opcodes.MSIZE: 2,
    Opcodes.RETURNDATASIZE: 2,

    # Very Low (3 gas)
    Opcodes.ADD: 3,
    Opcodes.SUB: 3,
    Opcodes.MUL: 5,
    Opcodes.DIV: 5,
    Opcodes.SDIV: 5,
    Opcodes.MOD: 5,
    Opcodes.SMOD: 5,
    Opcodes.ADDMOD: 8,
    Opcodes.MULMOD: 8,
    Opcodes.SIGNEXTEND: 5,
    Opcodes.LT: 3,
    Opcodes.GT: 3,
    Opcodes.SLT: 3,
    Opcodes.SGT: 3,
    Opcodes.EQ: 3,
    Opcodes.ISZERO: 3,
    Opcodes.AND: 3,
    Opcodes.OR: 3,
    Opcodes.XOR: 3,
    Opcodes.NOT: 3,
    Opcodes.BYTE: 3,
    Opcodes.SHL: 3,
    Opcodes.SHR: 3,
    Opcodes.SAR: 3,
    Opcodes.CALLDATALOAD: 3,
    Opcodes.MLOAD: 3,
    Opcodes.MSTORE: 3,
    Opcodes.MSTORE8: 3,
    Opcodes.PUSH0: 2,

    # Low (5 gas)
    Opcodes.EXP: 10,  # + 50 * byte_size

    # Mid (8 gas)
    Opcodes.JUMP: 8,
    Opcodes.JUMPI: 10,
    Opcodes.JUMPDEST: 1,
    Opcodes.GAS: 2,
    Opcodes.SELFBALANCE: 5,

    # High (10 gas)

    # SHA3 (30 + 6 * word_size)
    Opcodes.SHA3: 30,

    # Storage (Berlin pricing - cold/warm)
    Opcodes.SLOAD: 2100,  # Cold: 2100, Warm: 100
    Opcodes.SSTORE: 2900,  # Complex pricing

    # External (Berlin pricing)
    Opcodes.BALANCE: 2600,  # Cold: 2600, Warm: 100
    Opcodes.EXTCODESIZE: 2600,
    Opcodes.EXTCODECOPY: 2600,
    Opcodes.EXTCODEHASH: 2600,
    Opcodes.BLOCKHASH: 20,

    # Memory operations
    Opcodes.CALLDATACOPY: 3,  # + 3 * word_size
    Opcodes.CODECOPY: 3,
    Opcodes.RETURNDATACOPY: 3,

    # Call operations (base costs)
    Opcodes.CALL: 100,  # + address_access + value_transfer + memory
    Opcodes.CALLCODE: 100,
    Opcodes.DELEGATECALL: 100,
    Opcodes.STATICCALL: 100,

    # Contract creation
    Opcodes.CREATE: 32000,
    Opcodes.CREATE2: 32000,

    # Logging
    Opcodes.LOG0: 375,
    Opcodes.LOG1: 375 + 375,
    Opcodes.LOG2: 375 + 375 * 2,
    Opcodes.LOG3: 375 + 375 * 3,
    Opcodes.LOG4: 375 + 375 * 4,

    # Special
    Opcodes.SELFDESTRUCT: 5000,  # + 25000 if new account
    Opcodes.INVALID: 0,
}

# PUSH operations gas cost
for i in range(1, 33):
    GAS_COSTS[Opcodes.PUSH1 + i - 1] = 3

# DUP operations gas cost
for i in range(1, 17):
    GAS_COSTS[Opcodes.DUP1 + i - 1] = 3

# SWAP operations gas cost
for i in range(1, 17):
    GAS_COSTS[Opcodes.SWAP1 + i - 1] = 3


def get_gas_cost(opcode: int) -> int:
    """Get base gas cost for opcode"""
    return GAS_COSTS.get(opcode, 0)


def opcode_name(opcode: int) -> str:
    """Get opcode name"""
    try:
        return Opcodes(opcode).name
    except ValueError:
        return f"UNKNOWN(0x{opcode:02x})"
