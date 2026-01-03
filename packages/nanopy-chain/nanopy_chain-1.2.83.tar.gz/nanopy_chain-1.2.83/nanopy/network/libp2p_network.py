"""
NanoPy libp2p Network - Decentralized P2P networking using libp2p
Handles peer discovery, block sync, and transaction gossip

Uses trio for async (required by py-libp2p)
"""

import json
import hashlib
import time
import logging
import os
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

# Check for trio and libp2p availability
LIBP2P_AVAILABLE = False
INetStream = None  # Type stub for when libp2p not available
trio = None
TProtocol = None
Multiaddr = None

try:
    import trio
    from nanolib import new_host
    from nanolib.crypto.secp256k1 import create_new_key_pair
    from nanolib.network.stream.net_stream import NetStream as INetStream
    from nanolib.peer.peerinfo import info_from_p2p_addr
    from nanolib.custom_types import TProtocol
    from multiaddr import Multiaddr
    LIBP2P_AVAILABLE = True
except ImportError:
    pass

from eth_utils import to_hex

logger = logging.getLogger(__name__)


class NanoPyProtocol(Enum):
    """NanoPy P2P protocol IDs"""
    HANDSHAKE = "/nanopy/handshake/1.0.0"
    BLOCK_SYNC = "/nanopy/blocksync/1.0.0"
    BLOCK_ANNOUNCE = "/nanopy/blockannounce/1.0.0"
    TX_GOSSIP = "/nanopy/txgossip/1.0.0"
    CHAIN_SYNC = "/nanopy/chainsync/1.0.0"


@dataclass
class LibP2PConfig:
    """libp2p network configuration"""
    listen_addrs: List[str] = field(default_factory=lambda: ["/ip4/0.0.0.0/tcp/30303"])
    bootstrap_peers: List[str] = field(default_factory=list)
    chain_id: int = 7770
    network_id: int = 7770
    max_peers: int = 50
    private_key: Optional[bytes] = None
    data_dir: str = "./chaindata"  # For persistent P2P key


def get_stable_node_key(data_dir: str) -> bytes:
    """
    Generate a stable P2P node key derived from data_dir path.
    This is NOT a wallet key - just for stable Peer ID.
    The key is deterministic based on the absolute path of data_dir.
    No file is stored.
    """
    # Get absolute path for consistency
    abs_path = os.path.abspath(data_dir)

    # Create deterministic key from path hash
    # This gives same Peer ID as long as data_dir is the same
    key_bytes = hashlib.sha256(f"nanopy-nodekey:{abs_path}".encode()).digest()

    logger.debug(f"Node key derived from: {abs_path}")
    return key_bytes


@dataclass
class LibP2PPeer:
    """Connected peer information"""
    peer_id: str
    peer_id_obj: Any = None  # nanolib.peer.id.ID object for new_stream()
    addrs: List[str] = field(default_factory=list)
    chain_id: int = 0
    best_block: int = 0
    best_hash: str = ""
    connected_at: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)

    def __hash__(self):
        return hash(self.peer_id)


class LibP2PNetwork:
    """
    libp2p-based P2P Network for NanoPy using trio
    """

    def __init__(self, config: LibP2PConfig, node=None):
        if not LIBP2P_AVAILABLE:
            raise ImportError("libp2p not installed. Install with: pip install libp2p")

        self.config = config
        self.node = node

        self._host = None
        self.peers: Dict[str, LibP2PPeer] = {}
        self._running = False

        self._on_new_block: Optional[Callable] = None
        self._on_new_transaction: Optional[Callable] = None

    @property
    def peer_count(self) -> int:
        return len(self.peers)

    @property
    def peer_id(self) -> str:
        if self._host:
            return str(self._host.get_id())
        return ""

    @property
    def is_syncing(self) -> bool:
        if not self.node:
            return False
        for peer in self.peers.values():
            if peer.best_block > self.node.block_number:
                return True
        return False

    async def start(self):
        """Start the libp2p network (trio async)"""
        logger.debug("Starting P2P network...")
        self._running = True

        # Generate stable key pair (deterministic from data_dir)
        if self.config.private_key:
            key_bytes = self.config.private_key
            logger.debug("Using provided private key")
        else:
            key_bytes = get_stable_node_key(self.config.data_dir)

        key_pair = create_new_key_pair(key_bytes)

        # Create host with bootstrap peers for auto-discovery
        bootstrap_addrs = self.config.bootstrap_peers if self.config.bootstrap_peers else None
        self._host = new_host(key_pair=key_pair, bootstrap=bootstrap_addrs)
        logger.debug(f"Host created, peer_id={self._host.get_id()}")

        # Setup protocol handlers
        self._host.set_stream_handler(
            TProtocol(NanoPyProtocol.HANDSHAKE.value),
            self._handle_handshake
        )
        self._host.set_stream_handler(
            TProtocol(NanoPyProtocol.BLOCK_SYNC.value),
            self._handle_block_sync
        )
        self._host.set_stream_handler(
            TProtocol(NanoPyProtocol.BLOCK_ANNOUNCE.value),
            self._handle_block_announce
        )
        self._host.set_stream_handler(
            TProtocol(NanoPyProtocol.CHAIN_SYNC.value),
            self._handle_chain_sync
        )

        # Convert listen addresses to Multiaddr
        listen_maddrs = [Multiaddr(addr) for addr in self.config.listen_addrs]

        # Use host.run() which properly starts Swarm.run() first, then listen()
        async with self._host.run(listen_maddrs):
            logger.debug(f"P2P started. Peer ID: {self.peer_id}")

            # Connect to bootstrap peers that weren't auto-connected
            async with trio.open_nursery() as nursery:
                for peer_addr in self.config.bootstrap_peers:
                    nursery.start_soon(self._connect_to_bootstrap, peer_addr)

                # Background tasks
                nursery.start_soon(self._sync_loop)
                nursery.start_soon(self._heartbeat_loop)

                # Keep running
                while self._running:
                    await trio.sleep(1)

    async def stop(self):
        """Stop the network"""
        self._running = False
        if self._host:
            await self._host.close()

    # Protocol Handlers

    async def _handle_handshake(self, stream: INetStream):
        """Handle incoming handshake"""
        try:
            peer_id = str(stream.muxed_conn.peer_id)
            data = await stream.read(4096)
            handshake = json.loads(data.decode())

            if handshake.get("chain_id") != self.config.chain_id:
                await stream.close()
                return

            peer = LibP2PPeer(
                peer_id=peer_id,
                peer_id_obj=stream.muxed_conn.peer_id,  # Need this for sync!
                chain_id=handshake.get("chain_id", 0),
                best_block=handshake.get("best_block", 0),
                best_hash=handshake.get("best_hash", "")
            )
            self.peers[peer_id] = peer

            response = {
                "chain_id": self.config.chain_id,
                "network_id": self.config.network_id,
                "best_block": self.node.block_number if self.node else 0,
                "best_hash": to_hex(self.node.latest_block.hash) if self.node else "",
                "version": "nanopy/1.0.0"
            }
            await stream.write(json.dumps(response).encode())
            await stream.close()
            logger.debug(f"Handshake completed with {peer_id[:16]}")

        except Exception as e:
            logger.debug(f"Handshake error: {e}")

    async def _handle_block_sync(self, stream: INetStream):
        """Handle block sync request - sends all blocks, client filters what it needs"""
        try:
            if not self.node:
                await stream.close()
                return

            # Read request from client (start block number)
            try:
                req_data = await stream.read(1024)
                request = json.loads(req_data.decode()) if req_data else {}
                start = request.get("start", 0)
                logger.debug(f"Received sync request from peer, start={start}")
            except Exception:
                start = 0

            # Send blocks AFTER start (client has block 'start', needs start+1 onwards)
            blocks = []
            begin = start + 1  # Start from next block
            end = min(begin + 50, self.node.block_number + 1)
            for i in range(begin, end):
                if i < len(self.node.blocks):
                    block = self.node.blocks[i]
                    blocks.append(block.to_dict(full_transactions=True))

            response = {"blocks": blocks, "total": self.node.block_number, "start": begin}
            data = json.dumps(response).encode()
            logger.debug(f"Sending blocks {begin}-{end-1} ({len(blocks)} blocks)")

            # Send in chunks if needed
            for i in range(0, len(data), 60000):
                chunk = data[i:i+60000]
                await stream.write(chunk)
            await stream.close()

        except Exception as e:
            logger.warning(f"Block sync error: {e}")

    async def _handle_block_announce(self, stream: INetStream):
        """Handle new block announcement"""
        try:
            peer_id = str(stream.muxed_conn.peer_id)
            data = await stream.read(65536)
            announcement = json.loads(data.decode())

            block_data = announcement.get("block")
            if block_data:
                if peer_id in self.peers:
                    block_num = int(block_data.get("number", "0x0"), 16)
                    self.peers[peer_id].best_block = block_num
                    self.peers[peer_id].best_hash = block_data.get("hash", "")
                    self.peers[peer_id].last_seen = time.time()

                if self._on_new_block:
                    self._on_new_block(block_data, self.peers.get(peer_id))

            await stream.close()

        except Exception as e:
            logger.debug(f"Block announce error: {e}")

    async def _handle_chain_sync(self, stream: INetStream):
        """Handle chain sync request"""
        try:
            status = {
                "chain_id": self.config.chain_id,
                "best_block": self.node.block_number if self.node else 0,
                "best_hash": to_hex(self.node.latest_block.hash) if self.node else "",
            }
            await stream.write(json.dumps(status).encode())
            await stream.close()
        except Exception as e:
            logger.debug(f"Chain sync error: {e}")

    # Connection

    async def _connect_to_bootstrap(self, peer_addr: str):
        """Connect to a bootstrap peer"""
        try:
            maddr = Multiaddr(peer_addr)
            peer_info = info_from_p2p_addr(maddr)

            await self._host.connect(peer_info)

            stream = await self._host.new_stream(
                peer_info.peer_id,
                [TProtocol(NanoPyProtocol.HANDSHAKE.value)]
            )

            handshake = {
                "chain_id": self.config.chain_id,
                "network_id": self.config.network_id,
                "best_block": self.node.block_number if self.node else 0,
                "best_hash": to_hex(self.node.latest_block.hash) if self.node else "",
                "version": "nanopy/1.0.0"
            }
            await stream.write(json.dumps(handshake).encode())

            data = await stream.read(4096)
            response = json.loads(data.decode())
            await stream.close()

            peer = LibP2PPeer(
                peer_id=str(peer_info.peer_id),
                peer_id_obj=peer_info.peer_id,  # Store the ID object
                addrs=[peer_addr],
                chain_id=response.get("chain_id", 0),
                best_block=response.get("best_block", 0),
                best_hash=response.get("best_hash", "")
            )
            self.peers[peer.peer_id] = peer
            logger.debug(f"Connected to bootstrap {peer.peer_id[:16]}")

        except Exception as e:
            logger.warning(f"Failed to connect to {peer_addr}: {e}")

    # Broadcasting

    async def broadcast_block(self, block_data: dict):
        """Broadcast new block to all peers"""
        if not self._running:
            return

        message = json.dumps({"block": block_data}).encode()

        for peer_id in list(self.peers.keys()):
            try:
                stream = await self._host.new_stream(
                    peer_id,
                    [TProtocol(NanoPyProtocol.BLOCK_ANNOUNCE.value)]
                )
                await stream.write(message)
                await stream.close()
            except Exception as e:
                logger.debug(f"Broadcast to {peer_id[:16]} failed: {e}")

    async def broadcast_transaction(self, tx_data: dict):
        """Broadcast transaction"""
        if not self._running:
            return
        # TODO: implement tx gossip
        pass

    # Sync

    async def request_blocks(self, peer_id: str, start: int = 0, count: int = 50) -> List[dict]:
        """Request blocks from a peer starting at 'start'"""
        try:
            stream = await self._host.new_stream(
                peer_id,
                [TProtocol(NanoPyProtocol.BLOCK_SYNC.value)]
            )

            # Send request with start block
            request = json.dumps({"start": start}).encode()
            await stream.write(request)

            # Read response
            chunks = []
            while True:
                try:
                    chunk = await stream.read(65536)
                    if not chunk:
                        break
                    chunks.append(chunk)
                except Exception:
                    break
            await stream.close()

            data = b"".join(chunks)
            if not data:
                logger.debug("No data received from peer for blocks")
                return []

            response = json.loads(data.decode())
            blocks = response.get("blocks", [])
            logger.debug(f"Received {len(blocks)} blocks from peer (start={start})")
            return blocks

        except Exception as e:
            logger.debug(f"Request blocks failed: {e}")
            return []

    async def sync_with_peer(self, peer: LibP2PPeer):
        """Sync blockchain with a peer - sync in batches from current block"""
        if not self.node:
            logger.debug("sync_with_peer: no node")
            return

        if not peer.peer_id_obj:
            logger.debug(f"No peer_id_obj for {peer.peer_id[:16]}, skipping sync")
            return

        target = peer.best_block
        current = self.node.block_number

        # Only sync if peer has more blocks
        if target <= current:
            return

        logger.debug(f"[P2P] Syncing {current} -> {target} from peer {peer.peer_id[:16]}")

        # Sync in batches of 50 blocks
        while self.node.block_number < target:
            start = self.node.block_number
            blocks = await self.request_blocks(peer.peer_id_obj, start, 50)
            if not blocks:
                logger.debug("No blocks received, stopping sync")
                break

            # Process blocks in order
            new_count = 0
            for block_data in sorted(blocks, key=lambda b: int(b.get("number", "0x0"), 16)):
                block_num = int(block_data.get("number", "0x0"), 16)
                if block_num > self.node.block_number:
                    logger.debug(f"[P2P] Processing block {block_num} from sync")
                    if self._on_new_block:
                        self._on_new_block(block_data, peer)
                    new_count += 1

            # If no new blocks processed, stop to avoid infinite loop
            if new_count == 0:
                break

            logger.debug(f"Sync progress {self.node.block_number}/{target}")

        logger.debug(f"Sync complete. Block: {self.node.block_number if self.node else 0}")

    # Background Tasks

    async def _sync_loop(self):
        """Periodic sync"""
        while self._running:
            await trio.sleep(10)

            if not self.node:
                continue

            best_peer = None
            local_block = self.node.block_number
            logger.debug(f"[P2P] Checking {len(self.peers)} peers, local block={local_block}")
            for peer in self.peers.values():
                logger.debug(f"[P2P] Peer {peer.peer_id[:16]}: best_block={peer.best_block}, local={local_block}")
                if peer.best_block > local_block:
                    if not best_peer or peer.best_block > best_peer.best_block:
                        best_peer = peer

            if best_peer:
                logger.debug(f"[P2P] Found peer ahead: {best_peer.peer_id[:16]} at block {best_peer.best_block} (local={local_block})")
                await self.sync_with_peer(best_peer)
            else:
                logger.debug(f"[P2P] No peers ahead. Local block: {local_block}, peers: {len(self.peers)}")

    async def _heartbeat_loop(self):
        """Keep connections alive"""
        while self._running:
            await trio.sleep(30)

            now = time.time()
            stale = []

            for peer_id, peer in self.peers.items():
                if now - peer.last_seen > 120:
                    stale.append(peer_id)
                elif peer.peer_id_obj:
                    try:
                        stream = await self._host.new_stream(
                            peer.peer_id_obj,
                            [TProtocol(NanoPyProtocol.CHAIN_SYNC.value)]
                        )
                        await stream.write(b"{}")
                        data = await stream.read(4096)
                        status = json.loads(data.decode())
                        await stream.close()

                        new_best = status.get("best_block", peer.best_block)
                        if new_best != peer.best_block:
                            logger.debug(f"[P2P] Peer {peer_id[:16]} updated: {peer.best_block} -> {new_best}")
                        peer.best_block = new_best
                        peer.last_seen = time.time()
                    except Exception as e:
                        logger.debug(f"[P2P] Heartbeat to {peer_id[:16]} failed: {e}")

            for peer_id in stale:
                logger.debug(f"Removing stale peer {peer_id[:16]}")
                del self.peers[peer_id]

    # Callbacks

    def on_new_block(self, callback: Callable):
        self._on_new_block = callback

    def on_new_transaction(self, callback: Callable):
        self._on_new_transaction = callback


def run_libp2p_network(config: LibP2PConfig, node=None, on_new_block: Callable = None, on_new_tx: Callable = None) -> LibP2PNetwork:
    """Run libp2p network in background thread using trio

    Args:
        config: LibP2P configuration
        node: Node instance for block/state access
        on_new_block: Callback for new blocks (set BEFORE thread starts to avoid race)
        on_new_tx: Callback for new transactions
    """
    import threading

    network = LibP2PNetwork(config, node)

    # Set callbacks BEFORE starting thread to avoid race condition
    if on_new_block:
        network._on_new_block = on_new_block
        logger.debug("on_new_block callback set before P2P start")
    if on_new_tx:
        network._on_new_transaction = on_new_tx

    def run():
        try:
            trio.run(network.start)
        except Exception as e:
            logger.error(f"libp2p error: {e}")

    thread = threading.Thread(target=run, daemon=True, name="libp2p-network")
    thread.start()

    # Wait a bit and check if thread is still alive
    time.sleep(1.0)
    if not thread.is_alive():
        logger.warning("P2P network thread died immediately!")

    return network
