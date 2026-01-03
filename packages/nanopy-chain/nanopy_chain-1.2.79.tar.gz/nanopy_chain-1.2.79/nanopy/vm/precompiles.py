"""
NanoPy VM Precompiles - Ethereum precompiled contracts
"""

from typing import Tuple, Optional
import hashlib

from eth_utils import keccak
from py_ecc.bn128 import (
    bn128_curve,
    bn128_pairing,
    add as bn128_add,
    multiply as bn128_multiply,
    FQ,
    FQ2,
)
from py_ecc.secp256k1 import ecdsa_raw_recover


# Precompile addresses (0x01 - 0x0a)
ECRECOVER = 0x01
SHA256 = 0x02
RIPEMD160 = 0x03
IDENTITY = 0x04
MODEXP = 0x05
BN128_ADD = 0x06
BN128_MUL = 0x07
BN128_PAIRING = 0x08
BLAKE2F = 0x09
POINT_EVALUATION = 0x0A  # EIP-4844


def ecrecover(input_data: bytes) -> Tuple[int, bytes]:
    """
    ECRECOVER precompile (0x01)
    Recovers public key from signature

    Input: 128 bytes
        - 32 bytes: message hash
        - 32 bytes: v (recovery id)
        - 32 bytes: r
        - 32 bytes: s

    Returns: (gas_used, recovered_address as 32 bytes)
    """
    gas = 3000

    if len(input_data) < 128:
        input_data = input_data.ljust(128, b'\x00')

    msg_hash = input_data[0:32]
    v = int.from_bytes(input_data[32:64], 'big')
    r = int.from_bytes(input_data[64:96], 'big')
    s = int.from_bytes(input_data[96:128], 'big')

    # Validate v
    if v not in (27, 28):
        return gas, b'\x00' * 32

    try:
        # Recover public key
        from eth_keys import keys
        signature = keys.Signature(vrs=(v - 27, r, s))
        public_key = signature.recover_public_key_from_msg_hash(msg_hash)
        address = public_key.to_canonical_address()
        return gas, address.rjust(32, b'\x00')
    except Exception:
        return gas, b'\x00' * 32


def sha256_precompile(input_data: bytes) -> Tuple[int, bytes]:
    """
    SHA256 precompile (0x02)

    Gas: 60 + 12 * ceil(len(input) / 32)
    """
    word_count = (len(input_data) + 31) // 32
    gas = 60 + 12 * word_count

    result = hashlib.sha256(input_data).digest()
    return gas, result


def ripemd160_precompile(input_data: bytes) -> Tuple[int, bytes]:
    """
    RIPEMD160 precompile (0x03)

    Gas: 600 + 120 * ceil(len(input) / 32)
    """
    word_count = (len(input_data) + 31) // 32
    gas = 600 + 120 * word_count

    result = hashlib.new('ripemd160', input_data).digest()
    return gas, result.rjust(32, b'\x00')


def identity(input_data: bytes) -> Tuple[int, bytes]:
    """
    Identity precompile (0x04)
    Just returns the input

    Gas: 15 + 3 * ceil(len(input) / 32)
    """
    word_count = (len(input_data) + 31) // 32
    gas = 15 + 3 * word_count

    return gas, input_data


def modexp(input_data: bytes) -> Tuple[int, bytes]:
    """
    Modular exponentiation precompile (0x05)
    Computes: base^exp % mod

    Input:
        - 32 bytes: base_length
        - 32 bytes: exp_length
        - 32 bytes: mod_length
        - base_length bytes: base
        - exp_length bytes: exponent
        - mod_length bytes: modulus
    """
    if len(input_data) < 96:
        input_data = input_data.ljust(96, b'\x00')

    base_len = int.from_bytes(input_data[0:32], 'big')
    exp_len = int.from_bytes(input_data[32:64], 'big')
    mod_len = int.from_bytes(input_data[64:96], 'big')

    # Read values
    data = input_data[96:]
    base = int.from_bytes(data[:base_len].ljust(base_len, b'\x00'), 'big')
    exp = int.from_bytes(data[base_len:base_len + exp_len].ljust(exp_len, b'\x00'), 'big')
    mod = int.from_bytes(data[base_len + exp_len:base_len + exp_len + mod_len].ljust(mod_len, b'\x00'), 'big')

    # Gas calculation (EIP-2565)
    def mult_complexity(x: int) -> int:
        x = max(x, 1)
        if x <= 64:
            return x ** 2
        elif x <= 1024:
            return x ** 2 // 4 + 96 * x - 3072
        else:
            return x ** 2 // 16 + 480 * x - 199680

    max_length = max(base_len, mod_len)
    words = (max_length + 7) // 8
    iteration_count = max(exp_len * 8 - 1, 0) if exp_len > 32 else max(exp.bit_length() - 1, 0)
    gas = max(200, mult_complexity(max_length) * max(iteration_count, 1) // 3)

    # Compute
    if mod == 0:
        result = b'\x00' * mod_len
    else:
        result = pow(base, exp, mod).to_bytes(mod_len, 'big')

    return gas, result


def bn128_add_precompile(input_data: bytes) -> Tuple[int, bytes]:
    """
    BN128 elliptic curve addition (0x06)
    Used for zkSNARKs

    Input: 128 bytes (2 points)
    Output: 64 bytes (1 point)
    Gas: 150 (Berlin)
    """
    gas = 150

    if len(input_data) < 128:
        input_data = input_data.ljust(128, b'\x00')

    try:
        x1 = int.from_bytes(input_data[0:32], 'big')
        y1 = int.from_bytes(input_data[32:64], 'big')
        x2 = int.from_bytes(input_data[64:96], 'big')
        y2 = int.from_bytes(input_data[96:128], 'big')

        # Point at infinity
        if x1 == 0 and y1 == 0:
            p1 = None
        else:
            p1 = (FQ(x1), FQ(y1))

        if x2 == 0 and y2 == 0:
            p2 = None
        else:
            p2 = (FQ(x2), FQ(y2))

        if p1 is None:
            result = p2
        elif p2 is None:
            result = p1
        else:
            result = bn128_add(p1, p2)

        if result is None:
            return gas, b'\x00' * 64

        x = int(result[0]).to_bytes(32, 'big')
        y = int(result[1]).to_bytes(32, 'big')
        return gas, x + y

    except Exception:
        return gas, None  # Invalid input


def bn128_mul_precompile(input_data: bytes) -> Tuple[int, bytes]:
    """
    BN128 elliptic curve scalar multiplication (0x07)

    Input: 96 bytes (point + scalar)
    Output: 64 bytes (point)
    Gas: 6000 (Berlin)
    """
    gas = 6000

    if len(input_data) < 96:
        input_data = input_data.ljust(96, b'\x00')

    try:
        x = int.from_bytes(input_data[0:32], 'big')
        y = int.from_bytes(input_data[32:64], 'big')
        s = int.from_bytes(input_data[64:96], 'big')

        if x == 0 and y == 0:
            return gas, b'\x00' * 64

        point = (FQ(x), FQ(y))
        result = bn128_multiply(point, s)

        if result is None:
            return gas, b'\x00' * 64

        rx = int(result[0]).to_bytes(32, 'big')
        ry = int(result[1]).to_bytes(32, 'big')
        return gas, rx + ry

    except Exception:
        return gas, None


def bn128_pairing_precompile(input_data: bytes) -> Tuple[int, bytes]:
    """
    BN128 pairing check (0x08)
    Used for zkSNARK verification

    Input: Multiple of 192 bytes
    Gas: 45000 + 34000 * k (Berlin)
    """
    if len(input_data) % 192 != 0:
        return 45000, None

    k = len(input_data) // 192
    gas = 45000 + 34000 * k

    if k == 0:
        return gas, b'\x00' * 31 + b'\x01'

    try:
        points = []
        for i in range(k):
            offset = i * 192
            x1 = int.from_bytes(input_data[offset:offset + 32], 'big')
            y1 = int.from_bytes(input_data[offset + 32:offset + 64], 'big')
            x2_i = int.from_bytes(input_data[offset + 64:offset + 96], 'big')
            x2_r = int.from_bytes(input_data[offset + 96:offset + 128], 'big')
            y2_i = int.from_bytes(input_data[offset + 128:offset + 160], 'big')
            y2_r = int.from_bytes(input_data[offset + 160:offset + 192], 'big')

            if x1 == 0 and y1 == 0:
                p1 = None
            else:
                p1 = (FQ(x1), FQ(y1))

            p2 = (FQ2([x2_r, x2_i]), FQ2([y2_r, y2_i]))
            points.append((p1, p2))

        # Pairing check
        result = bn128_pairing.pairing_check(points)

        if result:
            return gas, b'\x00' * 31 + b'\x01'
        else:
            return gas, b'\x00' * 32

    except Exception:
        return gas, None


def blake2f(input_data: bytes) -> Tuple[int, bytes]:
    """
    BLAKE2b F compression function (0x09)

    Input: 213 bytes
        - 4 bytes: rounds
        - 64 bytes: h (state)
        - 128 bytes: m (message block)
        - 16 bytes: t (offset counters)
        - 1 byte: f (final block flag)
    """
    if len(input_data) != 213:
        return 0, None

    rounds = int.from_bytes(input_data[0:4], 'big')
    gas = rounds  # 1 gas per round

    h = input_data[4:68]
    m = input_data[68:196]
    t = input_data[196:212]
    f = input_data[212]

    if f not in (0, 1):
        return gas, None

    # Use hashlib's blake2b compression
    # Note: This is simplified, real implementation needs F function
    try:
        import hashlib
        # Create blake2b state and update
        h_state = [int.from_bytes(h[i:i+8], 'little') for i in range(0, 64, 8)]
        # ... full implementation would use the F compression function
        return gas, h  # Simplified
    except Exception:
        return gas, None


# Precompile registry
PRECOMPILES = {
    ECRECOVER: ecrecover,
    SHA256: sha256_precompile,
    RIPEMD160: ripemd160_precompile,
    IDENTITY: identity,
    MODEXP: modexp,
    BN128_ADD: bn128_add_precompile,
    BN128_MUL: bn128_mul_precompile,
    BN128_PAIRING: bn128_pairing_precompile,
    BLAKE2F: blake2f,
}


def is_precompile(address: int) -> bool:
    """Check if address is a precompile"""
    return 1 <= address <= 10


def call_precompile(address: int, input_data: bytes) -> Tuple[int, Optional[bytes]]:
    """
    Call a precompile contract

    Returns: (gas_used, output_data or None on error)
    """
    if address in PRECOMPILES:
        return PRECOMPILES[address](input_data)
    return 0, None
