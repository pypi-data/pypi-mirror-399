"""
NanoPy VM - EVM-compatible virtual machine
Uses py-evm for real Ethereum compatibility
"""

from nanopy.vm.evm import NanoPyEVM, ExecutionContext, ExecutionResult
from nanopy.vm.opcodes import Opcodes
from nanopy.vm.precompiles import PRECOMPILES

__all__ = [
    "NanoPyEVM",
    "ExecutionContext",
    "ExecutionResult",
    "Opcodes",
    "PRECOMPILES",
]
