"""
NanoNode Consensus - Proof of Work and Proof of Stake
"""

from nanopy.consensus.pow import ProofOfWork, mine_block
from nanopy.consensus.pos import ProofOfStake
from nanopy.consensus.engine import ConsensusEngine

__all__ = [
    "ProofOfWork",
    "ProofOfStake",
    "mine_block",
    "ConsensusEngine",
]
