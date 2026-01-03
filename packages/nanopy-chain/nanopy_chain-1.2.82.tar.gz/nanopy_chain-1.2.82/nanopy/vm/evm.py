"""
NanoPy EVM - Ethereum Virtual Machine implementation
Uses py-evm as the core execution engine
"""

import logging
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple, Any
from enum import IntEnum

from eth_utils import keccak, to_bytes, to_hex

logger = logging.getLogger(__name__)

from nanopy.core.state import StateDB
from nanopy.core.account import compute_contract_address, compute_create2_address
from nanopy.vm.opcodes import Opcodes, get_gas_cost, opcode_name
from nanopy.vm.precompiles import is_precompile, call_precompile
from nanopy.vm.gas_costs import (
    DEFAULT_GAS_COSTS,
    G_CALL, G_CALL_VALUE, G_CALL_STIPEND, G_NEW_ACCOUNT,
    G_STATICCALL, G_DELEGATECALL,
    G_COLD_ACCOUNT_ACCESS, G_WARM_ACCESS,
    G_SSTORE_SET, G_SSTORE_RESET, G_SSTORE_CLEARS_REFUND,
    G_COLD_SLOAD,
)


class ExecutionError(Exception):
    """EVM execution error"""
    pass


class OutOfGasError(ExecutionError):
    """Out of gas error"""
    pass


class InvalidJumpError(ExecutionError):
    """Invalid jump destination"""
    pass


class StackUnderflowError(ExecutionError):
    """Stack underflow"""
    pass


class StackOverflowError(ExecutionError):
    """Stack overflow (max 1024)"""
    pass


class RevertError(ExecutionError):
    """REVERT opcode executed"""
    def __init__(self, data: bytes = b""):
        self.data = data
        super().__init__(f"Execution reverted: {to_hex(data)}")


@dataclass
class Log:
    """EVM log entry"""
    address: str
    topics: List[bytes]
    data: bytes

    def to_dict(self) -> dict:
        return {
            "address": self.address,
            "topics": [to_hex(t) for t in self.topics],
            "data": to_hex(self.data),
        }


@dataclass
class ExecutionContext:
    """EVM execution context"""
    # Transaction context
    origin: str                    # tx.origin (original sender)
    gas_price: int                 # tx.gasPrice

    # Message context
    caller: str                    # msg.sender
    address: str                   # address(this)
    value: int                     # msg.value
    data: bytes                    # msg.data (calldata)
    gas: int                       # Available gas

    # Code context
    code: bytes = b""              # Contract code
    is_static: bool = False        # Static call (no state changes)

    # Block context
    coinbase: str = ""             # block.coinbase
    timestamp: int = 0             # block.timestamp
    number: int = 0                # block.number
    prevrandao: int = 0            # block.prevrandao (was difficulty)
    gas_limit: int = 30_000_000    # block.gaslimit
    chain_id: int = 1337           # block.chainid
    base_fee: int = 0              # block.basefee


@dataclass
class ExecutionResult:
    """Result of EVM execution"""
    success: bool
    gas_used: int
    gas_refund: int = 0
    return_data: bytes = b""
    logs: List[Log] = field(default_factory=list)
    error: Optional[str] = None

    # Contract creation
    contract_address: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "gasUsed": self.gas_used,
            "gasRefund": self.gas_refund,
            "returnData": to_hex(self.return_data),
            "logs": [log.to_dict() for log in self.logs],
            "error": self.error,
            "contractAddress": self.contract_address,
        }


class Memory:
    """EVM memory (expandable byte array)"""

    def __init__(self):
        self._data = bytearray()

    def __len__(self) -> int:
        return len(self._data)

    def extend(self, offset: int, size: int) -> int:
        """Extend memory if needed, return gas cost"""
        if size == 0:
            return 0

        # Protection against unreasonable memory expansion (max 1MB)
        MAX_MEMORY = 1024 * 1024
        needed = offset + size
        if needed > MAX_MEMORY:
            # Return a huge gas cost that will cause OOG
            return 2**63

        current = len(self._data)

        if needed <= current:
            return 0

        # Calculate gas cost for expansion
        old_words = (current + 31) // 32
        new_words = (needed + 31) // 32
        old_cost = old_words * 3 + (old_words ** 2) // 512
        new_cost = new_words * 3 + (new_words ** 2) // 512
        gas_cost = new_cost - old_cost

        # Extend
        self._data.extend(b'\x00' * (needed - current))

        return gas_cost

    def load(self, offset: int) -> int:
        """Load 32-byte word from memory"""
        self.extend(offset, 32)
        return int.from_bytes(self._data[offset:offset + 32], 'big')

    def load_bytes(self, offset: int, size: int) -> bytes:
        """Load arbitrary bytes from memory"""
        if size == 0:
            return b""
        self.extend(offset, size)
        return bytes(self._data[offset:offset + size])

    def store(self, offset: int, value: int):
        """Store 32-byte word to memory"""
        self.extend(offset, 32)
        self._data[offset:offset + 32] = value.to_bytes(32, 'big')

    def store8(self, offset: int, value: int):
        """Store single byte to memory"""
        self.extend(offset, 1)
        self._data[offset] = value & 0xFF

    def store_bytes(self, offset: int, data: bytes):
        """Store arbitrary bytes to memory"""
        if len(data) == 0:
            return
        self.extend(offset, len(data))
        self._data[offset:offset + len(data)] = data


class Stack:
    """EVM stack (max 1024 items, 256-bit words)"""

    MAX_SIZE = 1024
    MAX_VALUE = 2 ** 256 - 1

    def __init__(self):
        self._items: List[int] = []

    def __len__(self) -> int:
        return len(self._items)

    def push(self, value: int):
        if len(self._items) >= self.MAX_SIZE:
            raise StackOverflowError()
        self._items.append(value & self.MAX_VALUE)

    def pop(self) -> int:
        if not self._items:
            raise StackUnderflowError()
        return self._items.pop()

    def peek(self, depth: int = 0) -> int:
        if depth >= len(self._items):
            raise StackUnderflowError()
        return self._items[-(depth + 1)]

    def swap(self, depth: int):
        if depth >= len(self._items):
            raise StackUnderflowError()
        self._items[-1], self._items[-(depth + 1)] = self._items[-(depth + 1)], self._items[-1]

    def dup(self, depth: int):
        if depth > len(self._items):
            raise StackUnderflowError()
        if len(self._items) >= self.MAX_SIZE:
            raise StackOverflowError()
        self._items.append(self._items[-depth])


class NanoPyEVM:
    """
    Ethereum Virtual Machine implementation

    Executes EVM bytecode with full opcode support.
    Uses py-evm compatible interfaces for state management.
    """

    def __init__(self, state: StateDB):
        self.state = state
        self.logs: List[Log] = []
        self.gas_refund = 0
        self.return_data = b""

        # Access lists (EIP-2929)
        self._accessed_addresses: set = set()
        self._accessed_storage_keys: set = set()

    def execute(self, context: ExecutionContext, _is_child_call: bool = False) -> ExecutionResult:
        """
        Execute EVM bytecode

        Args:
            context: Execution context with code, gas, etc.
            _is_child_call: Internal flag - True when called recursively for CALL/CREATE

        Returns:
            ExecutionResult with success/failure and outputs
        """
        # Debug: log context
        if len(context.data) >= 4:
            selector = context.data[:4].hex()
            logger.debug(f"[EVM EXECUTE] {context.address[:10]}... selector=0x{selector} is_static={context.is_static} value={context.value} is_child={_is_child_call}")

        # Save parent state if this is a child call (to restore after)
        if _is_child_call:
            saved_logs = self.logs
            saved_gas_refund = self.gas_refund
            saved_return_data = self.return_data
            # For child calls, we don't reset access lists - they inherit from parent
            # and changes persist back to parent (EIP-2929 warm storage access)

        # Reset state for this execution (but keep access lists for child calls)
        self.logs = []
        self.gas_refund = 0
        self.return_data = b""

        # Initialize access list only for top-level calls
        if not _is_child_call:
            self._accessed_addresses = {context.origin, context.caller, context.address, context.coinbase}
            self._accessed_storage_keys = set()
        else:
            # Add child call addresses to access list (they become warm)
            self._accessed_addresses.add(context.address)

        # Check for precompile
        address_int = int(context.address, 16) if context.address.startswith("0x") else int(context.address, 16)
        if is_precompile(address_int):
            gas_used, output = call_precompile(address_int, context.data)
            result = ExecutionResult(success=False, gas_used=context.gas, error="Precompile error") if output is None else ExecutionResult(success=True, gas_used=gas_used, return_data=output)
            # Restore parent state if this was a child call
            if _is_child_call:
                saved_logs.extend(self.logs)
                self.logs = saved_logs
                self.gas_refund = saved_gas_refund + self.gas_refund
                # DON'T restore return_data - parent needs to see precompile's output
            return result

        # Create snapshot for revert
        snapshot = self.state.snapshot()
        result = None

        try:
            gas_used, return_data = self._execute_code(context)

            result = ExecutionResult(
                success=True,
                gas_used=gas_used,
                gas_refund=self.gas_refund,
                return_data=return_data,
                logs=self.logs,
            )

        except RevertError as e:
            self.state.revert(snapshot)
            result = ExecutionResult(
                success=False,
                gas_used=context.gas,  # All gas consumed on revert
                return_data=e.data,
                error="Execution reverted",
            )

        except OutOfGasError:
            self.state.revert(snapshot)
            result = ExecutionResult(
                success=False,
                gas_used=context.gas,
                error="Out of gas",
            )

        except Exception as e:
            logger.debug(f"[EVM EXCEPTION] {context.address[:10]}... error={type(e).__name__}: {str(e)[:100]}")
            import traceback
            traceback.print_exc()
            self.state.revert(snapshot)
            result = ExecutionResult(
                success=False,
                gas_used=context.gas,
                error=str(e),
            )

        # Restore parent state if this was a child call
        if _is_child_call:
            # Merge child logs into parent logs (don't discard them!)
            saved_logs.extend(self.logs)
            self.logs = saved_logs
            # Accumulate gas refund
            self.gas_refund = saved_gas_refund + self.gas_refund
            # DON'T restore return_data - the parent needs to see the child's return data!
            # self.return_data stays as is (contains child's return data)
            # Don't restore access lists - changes from child persist to parent

        return result

    def _execute_code(self, ctx: ExecutionContext) -> Tuple[int, bytes]:
        """Execute bytecode, return (gas_used, return_data)"""
        stack = Stack()
        memory = Memory()
        pc = 0
        gas_remaining = ctx.gas
        trace_after_call = 0  # Counter to trace opcodes after CALL

        code = ctx.code
        code_len = len(code)

        # Find valid JUMPDEST positions
        jumpdests = set()
        i = 0
        while i < code_len:
            op = code[i]
            if op == Opcodes.JUMPDEST:
                jumpdests.add(i)
            if Opcodes.PUSH1 <= op <= Opcodes.PUSH32:
                i += op - Opcodes.PUSH1 + 2
            else:
                i += 1

        while pc < code_len:
            opcode = code[pc]

            # Trace after CALL for debugging
            if trace_after_call > 0:
                stack_top = hex(stack.peek()) if len(stack) > 0 else "empty"
                logger.debug(f"[TRACE] pc={pc} op={opcode_name(opcode)} stack_top={stack_top} stack_size={len(stack)}")
                trace_after_call -= 1

            # Check gas
            gas_cost = get_gas_cost(opcode)
            if gas_remaining < gas_cost:
                raise OutOfGasError()
            gas_remaining -= gas_cost

            # Execute opcode
            if opcode == Opcodes.STOP:
                break

            elif opcode == Opcodes.ADD:
                a, b = stack.pop(), stack.pop()
                stack.push((a + b) % (2 ** 256))

            elif opcode == Opcodes.MUL:
                a, b = stack.pop(), stack.pop()
                stack.push((a * b) % (2 ** 256))

            elif opcode == Opcodes.SUB:
                a, b = stack.pop(), stack.pop()
                stack.push((a - b) % (2 ** 256))

            elif opcode == Opcodes.DIV:
                a, b = stack.pop(), stack.pop()
                stack.push(a // b if b != 0 else 0)

            elif opcode == Opcodes.SDIV:
                a, b = stack.pop(), stack.pop()
                if b == 0:
                    stack.push(0)
                else:
                    # Signed division
                    sign = -1 if (a >> 255) ^ (b >> 255) else 1
                    a = a if a < 2**255 else a - 2**256
                    b = b if b < 2**255 else b - 2**256
                    result = abs(a) // abs(b) * sign
                    stack.push(result % (2 ** 256))

            elif opcode == Opcodes.MOD:
                a, b = stack.pop(), stack.pop()
                stack.push(a % b if b != 0 else 0)

            elif opcode == Opcodes.SMOD:
                a, b = stack.pop(), stack.pop()
                if b == 0:
                    stack.push(0)
                else:
                    a = a if a < 2**255 else a - 2**256
                    b = b if b < 2**255 else b - 2**256
                    result = abs(a) % abs(b)
                    if a < 0:
                        result = -result
                    stack.push(result % (2 ** 256))

            elif opcode == Opcodes.ADDMOD:
                a, b, n = stack.pop(), stack.pop(), stack.pop()
                stack.push((a + b) % n if n != 0 else 0)

            elif opcode == Opcodes.MULMOD:
                a, b, n = stack.pop(), stack.pop(), stack.pop()
                stack.push((a * b) % n if n != 0 else 0)

            elif opcode == Opcodes.EXP:
                base, exp = stack.pop(), stack.pop()
                # Additional gas for exp size
                exp_bytes = (exp.bit_length() + 7) // 8
                extra_gas = 50 * exp_bytes
                if gas_remaining < extra_gas:
                    raise OutOfGasError()
                gas_remaining -= extra_gas
                stack.push(pow(base, exp, 2 ** 256))

            elif opcode == Opcodes.SIGNEXTEND:
                b, x = stack.pop(), stack.pop()
                if b < 31:
                    sign_bit = 1 << (b * 8 + 7)
                    if x & sign_bit:
                        stack.push(x | (2 ** 256 - sign_bit))
                    else:
                        stack.push(x & (sign_bit - 1))
                else:
                    stack.push(x)

            elif opcode == Opcodes.LT:
                a, b = stack.pop(), stack.pop()
                stack.push(1 if a < b else 0)

            elif opcode == Opcodes.GT:
                a, b = stack.pop(), stack.pop()
                stack.push(1 if a > b else 0)

            elif opcode == Opcodes.SLT:
                a, b = stack.pop(), stack.pop()
                a = a if a < 2**255 else a - 2**256
                b = b if b < 2**255 else b - 2**256
                stack.push(1 if a < b else 0)

            elif opcode == Opcodes.SGT:
                a, b = stack.pop(), stack.pop()
                a = a if a < 2**255 else a - 2**256
                b = b if b < 2**255 else b - 2**256
                stack.push(1 if a > b else 0)

            elif opcode == Opcodes.EQ:
                a, b = stack.pop(), stack.pop()
                stack.push(1 if a == b else 0)

            elif opcode == Opcodes.ISZERO:
                a = stack.pop()
                result = 1 if a == 0 else 0
                # Debug ISZERO after CALL (checking call success)
                if pc > 0 and code[pc-1] == Opcodes.CALL:
                    logger.debug(f"[EVM ISZERO] After CALL: input={a} result={result}")
                stack.push(result)

            elif opcode == Opcodes.AND:
                a, b = stack.pop(), stack.pop()
                stack.push(a & b)

            elif opcode == Opcodes.OR:
                a, b = stack.pop(), stack.pop()
                stack.push(a | b)

            elif opcode == Opcodes.XOR:
                a, b = stack.pop(), stack.pop()
                stack.push(a ^ b)

            elif opcode == Opcodes.NOT:
                a = stack.pop()
                stack.push((2 ** 256 - 1) ^ a)

            elif opcode == Opcodes.BYTE:
                i, x = stack.pop(), stack.pop()
                if i >= 32:
                    stack.push(0)
                else:
                    stack.push((x >> (248 - i * 8)) & 0xFF)

            elif opcode == Opcodes.SHL:
                shift, value = stack.pop(), stack.pop()
                if shift >= 256:
                    stack.push(0)
                else:
                    stack.push((value << shift) % (2 ** 256))

            elif opcode == Opcodes.SHR:
                shift, value = stack.pop(), stack.pop()
                if shift >= 256:
                    stack.push(0)
                else:
                    stack.push(value >> shift)

            elif opcode == Opcodes.SAR:
                shift, value = stack.pop(), stack.pop()
                if shift >= 256:
                    stack.push(2 ** 256 - 1 if value >= 2 ** 255 else 0)
                else:
                    if value >= 2 ** 255:
                        # Negative - fill with 1s
                        stack.push((value >> shift) | ((2 ** 256 - 1) << (256 - shift)))
                    else:
                        stack.push(value >> shift)

            elif opcode == Opcodes.SHA3:
                offset, size = stack.pop(), stack.pop()
                gas_remaining -= memory.extend(offset, size)
                data = memory.load_bytes(offset, size)
                # Additional gas for data size
                word_count = (size + 31) // 32
                extra_gas = 6 * word_count
                if gas_remaining < extra_gas:
                    raise OutOfGasError()
                gas_remaining -= extra_gas
                stack.push(int.from_bytes(keccak(data), 'big'))

            elif opcode == Opcodes.ADDRESS:
                stack.push(int(ctx.address, 16))

            elif opcode == Opcodes.BALANCE:
                address = hex(stack.pop())[2:].zfill(40)
                address = "0x" + address
                # Access cost
                if address not in self._accessed_addresses:
                    self._accessed_addresses.add(address)
                    gas_remaining -= 2500  # Cold access
                stack.push(self.state.get_balance(address))

            elif opcode == Opcodes.ORIGIN:
                stack.push(int(ctx.origin, 16))

            elif opcode == Opcodes.CALLER:
                stack.push(int(ctx.caller, 16))

            elif opcode == Opcodes.CALLVALUE:
                stack.push(ctx.value)

            elif opcode == Opcodes.CALLDATALOAD:
                offset = stack.pop()
                data = ctx.data[offset:offset + 32].ljust(32, b'\x00')
                stack.push(int.from_bytes(data, 'big'))

            elif opcode == Opcodes.CALLDATASIZE:
                stack.push(len(ctx.data))

            elif opcode == Opcodes.CALLDATACOPY:
                dest_offset, offset, size = stack.pop(), stack.pop(), stack.pop()
                gas_remaining -= memory.extend(dest_offset, size)
                word_count = (size + 31) // 32
                gas_remaining -= 3 * word_count
                if gas_remaining < 0:
                    raise OutOfGasError()
                data = ctx.data[offset:offset + size].ljust(size, b'\x00')
                memory.store_bytes(dest_offset, data)

            elif opcode == Opcodes.CODESIZE:
                stack.push(len(ctx.code))

            elif opcode == Opcodes.CODECOPY:
                dest_offset, offset, size = stack.pop(), stack.pop(), stack.pop()
                gas_remaining -= memory.extend(dest_offset, size)
                word_count = (size + 31) // 32
                gas_remaining -= 3 * word_count
                if gas_remaining < 0:
                    raise OutOfGasError()
                data = ctx.code[offset:offset + size].ljust(size, b'\x00')
                memory.store_bytes(dest_offset, data)

            elif opcode == Opcodes.GASPRICE:
                stack.push(ctx.gas_price)

            elif opcode == Opcodes.EXTCODESIZE:
                address = hex(stack.pop())[2:].zfill(40)
                address = "0x" + address
                if address not in self._accessed_addresses:
                    self._accessed_addresses.add(address)
                    gas_remaining -= 2500
                stack.push(len(self.state.get_code(address)))

            elif opcode == Opcodes.EXTCODECOPY:
                address = hex(stack.pop())[2:].zfill(40)
                address = "0x" + address
                dest_offset, offset, size = stack.pop(), stack.pop(), stack.pop()
                if address not in self._accessed_addresses:
                    self._accessed_addresses.add(address)
                    gas_remaining -= 2500
                gas_remaining -= memory.extend(dest_offset, size)
                ext_code = self.state.get_code(address)
                data = ext_code[offset:offset + size].ljust(size, b'\x00')
                memory.store_bytes(dest_offset, data)

            elif opcode == Opcodes.RETURNDATASIZE:
                rds = len(self.return_data)
                logger.debug(f"[EVM RETURNDATASIZE] {ctx.address[:10]}... size={rds}")
                stack.push(rds)

            elif opcode == Opcodes.RETURNDATACOPY:
                dest_offset, offset, size = stack.pop(), stack.pop(), stack.pop()
                if offset + size > len(self.return_data):
                    raise ExecutionError("Return data out of bounds")
                gas_remaining -= memory.extend(dest_offset, size)
                data = self.return_data[offset:offset + size]
                memory.store_bytes(dest_offset, data)

            elif opcode == Opcodes.EXTCODEHASH:
                address = hex(stack.pop())[2:].zfill(40)
                address = "0x" + address
                if address not in self._accessed_addresses:
                    self._accessed_addresses.add(address)
                    gas_remaining -= 2500
                if not self.state.account_exists(address):
                    stack.push(0)
                else:
                    stack.push(int.from_bytes(self.state.get_code_hash(address), 'big'))

            elif opcode == Opcodes.BLOCKHASH:
                block_num = stack.pop()
                # Only last 256 blocks
                if ctx.number - 256 <= block_num < ctx.number:
                    # Would need block storage to implement properly
                    stack.push(0)
                else:
                    stack.push(0)

            elif opcode == Opcodes.COINBASE:
                stack.push(int(ctx.coinbase, 16) if ctx.coinbase else 0)

            elif opcode == Opcodes.TIMESTAMP:
                stack.push(ctx.timestamp)

            elif opcode == Opcodes.NUMBER:
                stack.push(ctx.number)

            elif opcode == Opcodes.PREVRANDAO:
                stack.push(ctx.prevrandao)

            elif opcode == Opcodes.GASLIMIT:
                stack.push(ctx.gas_limit)

            elif opcode == Opcodes.CHAINID:
                stack.push(ctx.chain_id)

            elif opcode == Opcodes.SELFBALANCE:
                stack.push(self.state.get_balance(ctx.address))

            elif opcode == Opcodes.BASEFEE:
                stack.push(ctx.base_fee)

            elif opcode == Opcodes.POP:
                stack.pop()

            elif opcode == Opcodes.MLOAD:
                offset = stack.pop()
                gas_remaining -= memory.extend(offset, 32)
                stack.push(memory.load(offset))

            elif opcode == Opcodes.MSTORE:
                offset, value = stack.pop(), stack.pop()
                gas_remaining -= memory.extend(offset, 32)
                memory.store(offset, value)

            elif opcode == Opcodes.MSTORE8:
                offset, value = stack.pop(), stack.pop()
                gas_remaining -= memory.extend(offset, 1)
                memory.store8(offset, value)

            elif opcode == Opcodes.SLOAD:
                key = stack.pop().to_bytes(32, 'big')
                storage_key = (ctx.address, key)
                if storage_key not in self._accessed_storage_keys:
                    self._accessed_storage_keys.add(storage_key)
                    gas_remaining -= 2000  # Cold access
                value = self.state.get_storage(ctx.address, key)
                stack.push(int.from_bytes(value, 'big'))

            elif opcode == Opcodes.SSTORE:
                if ctx.is_static:
                    logger.debug(f"[EVM SSTORE] BLOCKED - static context! {ctx.address[:10]}...")
                    raise ExecutionError("SSTORE in static context")
                key = stack.pop().to_bytes(32, 'big')
                value = stack.pop().to_bytes(32, 'big')
                storage_key = (ctx.address, key)
                if storage_key not in self._accessed_storage_keys:
                    self._accessed_storage_keys.add(storage_key)
                    gas_remaining -= G_COLD_SLOAD
                # EIP-2200: Complex gas calculation based on current/new values
                current = self.state.get_storage(ctx.address, key)
                if current == value:
                    gas_remaining -= G_WARM_ACCESS  # No-op
                elif current == bytes(32):
                    gas_remaining -= G_SSTORE_SET  # Zero to non-zero
                else:
                    gas_remaining -= G_SSTORE_RESET  # Non-zero to non-zero
                    if value == bytes(32):
                        self.gas_refund += G_SSTORE_CLEARS_REFUND  # Clear storage refund
                if gas_remaining < 0:
                    logger.debug(f"[EVM SSTORE] OUT OF GAS! {ctx.address[:10]}... gas_remaining={gas_remaining}")
                    raise OutOfGasError()
                logger.debug(f"[EVM SSTORE] {ctx.address[:10]}... slot={int.from_bytes(key, 'big')} value={int.from_bytes(value, 'big')} gas_left={gas_remaining}")
                self.state.set_storage(ctx.address, key, value)

            elif opcode == Opcodes.JUMP:
                dest = stack.pop()
                if dest not in jumpdests:
                    raise InvalidJumpError(f"Invalid jump to {dest}")
                pc = dest
                continue

            elif opcode == Opcodes.JUMPI:
                dest, cond = stack.pop(), stack.pop()
                if cond != 0:
                    if dest not in jumpdests:
                        raise InvalidJumpError(f"Invalid jump to {dest}")
                    # Debug: show what opcode is at destination
                    if dest < code_len:
                        logger.debug(f"[EVM JUMPI] Jumping to {dest}, opcode there: {opcode_name(code[dest])}")
                    pc = dest
                    continue

            elif opcode == Opcodes.PC:
                stack.push(pc)

            elif opcode == Opcodes.MSIZE:
                stack.push(len(memory))

            elif opcode == Opcodes.GAS:
                stack.push(gas_remaining)

            elif opcode == Opcodes.JUMPDEST:
                pass  # Marker only

            elif opcode == Opcodes.PUSH0:
                stack.push(0)

            elif Opcodes.PUSH1 <= opcode <= Opcodes.PUSH32:
                n = opcode - Opcodes.PUSH1 + 1
                value = int.from_bytes(code[pc + 1:pc + 1 + n].ljust(n, b'\x00'), 'big')
                stack.push(value)
                pc += n

            elif Opcodes.DUP1 <= opcode <= Opcodes.DUP16:
                depth = opcode - Opcodes.DUP1 + 1
                stack.dup(depth)

            elif Opcodes.SWAP1 <= opcode <= Opcodes.SWAP16:
                depth = opcode - Opcodes.SWAP1 + 1
                stack.swap(depth)

            elif Opcodes.LOG0 <= opcode <= Opcodes.LOG4:
                if ctx.is_static:
                    raise ExecutionError("LOG in static context")
                topic_count = opcode - Opcodes.LOG0
                offset, size = stack.pop(), stack.pop()
                logger.debug(f"[EVM LOG{topic_count}] offset={offset} size={size} stack_size={len(stack)}")
                topics = [stack.pop().to_bytes(32, 'big') for _ in range(topic_count)]
                gas_remaining -= memory.extend(offset, size)
                gas_remaining -= 8 * size  # Log data gas
                if gas_remaining < 0:
                    raise OutOfGasError()
                data = memory.load_bytes(offset, size)
                self.logs.append(Log(address=ctx.address, topics=topics, data=data))

            elif opcode == Opcodes.CREATE:
                if ctx.is_static:
                    raise ExecutionError("CREATE in static context")
                value, offset, size = stack.pop(), stack.pop(), stack.pop()
                gas_remaining -= memory.extend(offset, size)
                init_code = memory.load_bytes(offset, size)

                # Create new contract
                nonce = self.state.get_nonce(ctx.address)
                new_address = compute_contract_address(ctx.address, nonce)
                self.state.increment_nonce(ctx.address)

                # Transfer value and execute init code
                if value > 0:
                    if not self.state.transfer(ctx.address, new_address, value):
                        stack.push(0)
                        pc += 1
                        continue

                # Execute init code
                child_ctx = ExecutionContext(
                    origin=ctx.origin,
                    gas_price=ctx.gas_price,
                    caller=ctx.address,
                    address=new_address,
                    value=value,
                    data=b"",
                    gas=gas_remaining,
                    code=init_code,
                    coinbase=ctx.coinbase,
                    timestamp=ctx.timestamp,
                    number=ctx.number,
                    prevrandao=ctx.prevrandao,
                    gas_limit=ctx.gas_limit,
                    chain_id=ctx.chain_id,
                    base_fee=ctx.base_fee,
                )

                result = self.execute(child_ctx, _is_child_call=True)
                gas_remaining -= result.gas_used

                if result.success:
                    self.state.set_code(new_address, result.return_data)
                    stack.push(int(new_address, 16))
                else:
                    stack.push(0)

                self.return_data = result.return_data

            elif opcode == Opcodes.CREATE2:
                if ctx.is_static:
                    raise ExecutionError("CREATE2 in static context")
                value, offset, size, salt = stack.pop(), stack.pop(), stack.pop(), stack.pop()
                gas_remaining -= memory.extend(offset, size)
                init_code = memory.load_bytes(offset, size)

                # Hash init code for address
                init_code_hash = keccak(init_code)
                salt_bytes = salt.to_bytes(32, 'big')
                new_address = compute_create2_address(ctx.address, salt_bytes, init_code_hash)

                # Transfer and execute (similar to CREATE)
                if value > 0:
                    if not self.state.transfer(ctx.address, new_address, value):
                        stack.push(0)
                        pc += 1
                        continue

                child_ctx = ExecutionContext(
                    origin=ctx.origin,
                    gas_price=ctx.gas_price,
                    caller=ctx.address,
                    address=new_address,
                    value=value,
                    data=b"",
                    gas=gas_remaining,
                    code=init_code,
                    coinbase=ctx.coinbase,
                    timestamp=ctx.timestamp,
                    number=ctx.number,
                    prevrandao=ctx.prevrandao,
                    gas_limit=ctx.gas_limit,
                    chain_id=ctx.chain_id,
                    base_fee=ctx.base_fee,
                )

                result = self.execute(child_ctx, _is_child_call=True)
                gas_remaining -= result.gas_used

                if result.success:
                    self.state.set_code(new_address, result.return_data)
                    stack.push(int(new_address, 16))
                else:
                    stack.push(0)

                self.return_data = result.return_data

            elif opcode == Opcodes.CALL:
                gas_limit = stack.pop()
                to_addr = hex(stack.pop())[2:].zfill(40)
                to_addr = "0x" + to_addr
                value = stack.pop()
                args_offset, args_size = stack.pop(), stack.pop()
                ret_offset, ret_size = stack.pop(), stack.pop()

                if ctx.is_static and value > 0:
                    raise ExecutionError("Value transfer in static context")

                gas_remaining -= memory.extend(args_offset, args_size)
                gas_remaining -= memory.extend(ret_offset, ret_size)

                if to_addr not in self._accessed_addresses:
                    self._accessed_addresses.add(to_addr)
                    gas_remaining -= 2500

                call_data = memory.load_bytes(args_offset, args_size)
                child_code = self.state.get_code(to_addr)

                # Debug: log CALL details
                if len(call_data) >= 4:
                    selector = call_data[:4].hex()
                    logger.debug(f"[EVM CALL] {ctx.address[:10]}... -> {to_addr[:10]}... selector=0x{selector} value={value} code_len={len(child_code)}")

                # EIP-150: CALL gas calculation
                # Base cost for CALL opcode
                gas_remaining -= G_CALL

                # Extra cost for value transfer
                if value > 0:
                    gas_remaining -= G_CALL_VALUE
                    # Extra cost for creating new account - skip if account exists
                    if not self.state.account_exists(to_addr):
                        gas_remaining -= G_NEW_ACCOUNT

                if gas_remaining < 0:
                    raise OutOfGasError()

                # Calculate call gas (63/64 rule) - keep 1/64 for parent
                max_call_gas = gas_remaining - gas_remaining // 64
                call_gas = min(gas_limit, max_call_gas)

                # Stipend for value transfers
                stipend = G_CALL_STIPEND if value > 0 else 0

                if value > 0:
                    if not self.state.transfer(ctx.address, to_addr, value):
                        logger.debug(f"[EVM CALL] Transfer failed: {ctx.address} -> {to_addr} value={value}")
                        stack.push(0)
                        pc += 1
                        continue

                child_ctx = ExecutionContext(
                    origin=ctx.origin,
                    gas_price=ctx.gas_price,
                    caller=ctx.address,
                    address=to_addr,
                    value=value,
                    data=call_data,
                    gas=call_gas + stipend,
                    code=child_code,
                    coinbase=ctx.coinbase,
                    timestamp=ctx.timestamp,
                    number=ctx.number,
                    prevrandao=ctx.prevrandao,
                    gas_limit=ctx.gas_limit,
                    chain_id=ctx.chain_id,
                    base_fee=ctx.base_fee,
                )

                # Deduct call_gas from parent (not stipend - that's free)
                gas_remaining -= call_gas

                result = self.execute(child_ctx, _is_child_call=True)

                # Return unused gas to parent
                gas_remaining += (call_gas + stipend) - result.gas_used
                logger.debug(f"[EVM CALL] After child execute, gas_remaining={gas_remaining}, result.success={result.success}")

                self.return_data = result.return_data
                if result.success:
                    memory.store_bytes(ret_offset, result.return_data[:ret_size])
                    stack.push(1)
                    logger.debug(f"[EVM CALL] Success! return_data={result.return_data.hex() if result.return_data else 'empty'} stack_size={len(stack)} gas_remaining={gas_remaining} pc={pc}")
                else:
                    stack.push(0)
                    logger.debug(f"[EVM CALL] Failed! error={result.error if hasattr(result, 'error') else 'unknown'}")
                logger.debug(f"[EVM CALL] Continuing parent execution after CALL...")
                # Debug: show next few opcodes
                next_ops = []
                for i in range(5):
                    if pc + 1 + i < code_len:
                        next_ops.append(opcode_name(code[pc + 1 + i]))
                logger.debug(f"[EVM CALL] Next opcodes: {next_ops}")
                # Trace next 20 instructions
                trace_after_call = 20

            elif opcode == Opcodes.STATICCALL:
                gas_limit = stack.pop()
                to_addr = hex(stack.pop())[2:].zfill(40)
                to_addr = "0x" + to_addr
                args_offset, args_size = stack.pop(), stack.pop()
                ret_offset, ret_size = stack.pop(), stack.pop()

                gas_remaining -= memory.extend(args_offset, args_size)
                gas_remaining -= memory.extend(ret_offset, ret_size)

                # Base cost for STATICCALL
                gas_remaining -= G_STATICCALL

                if to_addr not in self._accessed_addresses:
                    self._accessed_addresses.add(to_addr)
                    gas_remaining -= G_COLD_ACCOUNT_ACCESS

                if gas_remaining < 0:
                    raise OutOfGasError()

                call_data = memory.load_bytes(args_offset, args_size)
                child_code = self.state.get_code(to_addr)

                # 63/64 rule
                max_call_gas = gas_remaining - gas_remaining // 64
                call_gas = min(gas_limit, max_call_gas)

                child_ctx = ExecutionContext(
                    origin=ctx.origin,
                    gas_price=ctx.gas_price,
                    caller=ctx.address,
                    address=to_addr,
                    value=0,
                    data=call_data,
                    gas=call_gas,
                    code=child_code,
                    is_static=True,
                    coinbase=ctx.coinbase,
                    timestamp=ctx.timestamp,
                    number=ctx.number,
                    prevrandao=ctx.prevrandao,
                    gas_limit=ctx.gas_limit,
                    chain_id=ctx.chain_id,
                    base_fee=ctx.base_fee,
                )

                # Deduct call_gas from parent
                gas_remaining -= call_gas

                result = self.execute(child_ctx, _is_child_call=True)

                # Return unused gas to parent
                gas_remaining += call_gas - result.gas_used

                self.return_data = result.return_data
                if result.success:
                    memory.store_bytes(ret_offset, result.return_data[:ret_size])
                    stack.push(1)
                else:
                    stack.push(0)

            elif opcode == Opcodes.DELEGATECALL:
                gas_limit = stack.pop()
                to_addr = hex(stack.pop())[2:].zfill(40)
                to_addr = "0x" + to_addr
                args_offset, args_size = stack.pop(), stack.pop()
                ret_offset, ret_size = stack.pop(), stack.pop()

                gas_remaining -= memory.extend(args_offset, args_size)
                gas_remaining -= memory.extend(ret_offset, ret_size)

                # Base cost for DELEGATECALL
                gas_remaining -= G_DELEGATECALL

                if to_addr not in self._accessed_addresses:
                    self._accessed_addresses.add(to_addr)
                    gas_remaining -= G_COLD_ACCOUNT_ACCESS

                if gas_remaining < 0:
                    raise OutOfGasError()

                call_data = memory.load_bytes(args_offset, args_size)
                child_code = self.state.get_code(to_addr)

                # 63/64 rule
                max_call_gas = gas_remaining - gas_remaining // 64
                call_gas = min(gas_limit, max_call_gas)

                # DELEGATECALL: use caller's context
                child_ctx = ExecutionContext(
                    origin=ctx.origin,
                    gas_price=ctx.gas_price,
                    caller=ctx.caller,  # Keep original caller
                    address=ctx.address,  # Keep current address
                    value=ctx.value,  # Keep original value
                    data=call_data,
                    gas=call_gas,
                    code=child_code,
                    is_static=ctx.is_static,
                    coinbase=ctx.coinbase,
                    timestamp=ctx.timestamp,
                    number=ctx.number,
                    prevrandao=ctx.prevrandao,
                    gas_limit=ctx.gas_limit,
                    chain_id=ctx.chain_id,
                    base_fee=ctx.base_fee,
                )

                # Deduct call_gas from parent
                gas_remaining -= call_gas

                result = self.execute(child_ctx, _is_child_call=True)

                # Return unused gas to parent
                gas_remaining += call_gas - result.gas_used

                self.return_data = result.return_data
                if result.success:
                    memory.store_bytes(ret_offset, result.return_data[:ret_size])
                    stack.push(1)
                else:
                    stack.push(0)

            elif opcode == Opcodes.RETURN:
                offset, size = stack.pop(), stack.pop()
                gas_remaining -= memory.extend(offset, size)
                return_data = memory.load_bytes(offset, size)
                logger.debug(f"[EVM RETURN] {ctx.address[:10]}... size={size} gas_left={gas_remaining}")
                return ctx.gas - gas_remaining, return_data

            elif opcode == Opcodes.REVERT:
                offset, size = stack.pop(), stack.pop()
                gas_remaining -= memory.extend(offset, size)
                return_data = memory.load_bytes(offset, size)
                # Debug: decode revert reason
                logger.debug(f"[EVM REVERT] address={ctx.address[:10]}... size={size} data={return_data.hex()[:100] if return_data else 'empty'}...")
                raise RevertError(return_data)

            elif opcode == Opcodes.INVALID:
                raise ExecutionError("Invalid opcode")

            elif opcode == Opcodes.SELFDESTRUCT:
                if ctx.is_static:
                    raise ExecutionError("SELFDESTRUCT in static context")
                recipient = hex(stack.pop())[2:].zfill(40)
                recipient = "0x" + recipient

                balance = self.state.get_balance(ctx.address)
                self.state.add_balance(recipient, balance)
                self.state.delete_account(ctx.address)
                break

            else:
                raise ExecutionError(f"Unknown opcode: {opcode_name(opcode)}")

            pc += 1

        logger.debug(f"[EVM _execute_code] Exited loop normally for {ctx.address[:10]}... pc={pc} code_len={len(ctx.code)}")
        return ctx.gas - gas_remaining, b""
