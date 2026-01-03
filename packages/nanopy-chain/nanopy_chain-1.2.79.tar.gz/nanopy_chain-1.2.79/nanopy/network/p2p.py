"""
NanoPy P2P Network - Peer-to-peer networking for blockchain
Handles node discovery, block sync, and transaction broadcast
"""

import asyncio
import json
import hashlib
import time
import threading
from typing import Dict, List, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import IntEnum

from eth_utils import to_hex


class MessageType(IntEnum):
    """P2P message types"""
    # Handshake
    HELLO = 0x00
    DISCONNECT = 0x01
    PING = 0x02
    PONG = 0x03

    # Peer discovery
    GET_PEERS = 0x10
    PEERS = 0x11

    # Block sync
    GET_BLOCK_HEADERS = 0x20
    BLOCK_HEADERS = 0x21
    GET_BLOCK_BODIES = 0x22
    BLOCK_BODIES = 0x23
    NEW_BLOCK = 0x24
    NEW_BLOCK_HASHES = 0x25

    # Transactions
    TRANSACTIONS = 0x30
    GET_POOLED_TRANSACTIONS = 0x31
    POOLED_TRANSACTIONS = 0x32


@dataclass
class Peer:
    """Connected peer information"""
    host: str
    port: int
    node_id: str = ""
    chain_id: int = 0
    best_block: int = 0
    best_hash: str = ""
    connected_at: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    reader: Optional[asyncio.StreamReader] = None
    writer: Optional[asyncio.StreamWriter] = None

    @property
    def address(self) -> str:
        return f"{self.host}:{self.port}"

    def __hash__(self):
        return hash(self.address)


@dataclass
class P2PConfig:
    """P2P network configuration"""
    host: str = "0.0.0.0"
    port: int = 30303
    max_peers: int = 25
    node_id: str = ""
    chain_id: int = 1337
    network_id: int = 1337
    bootnodes: List[str] = field(default_factory=list)


class P2PNetwork:
    """
    P2P Network Manager

    Handles:
    - Peer connections and discovery
    - Block synchronization
    - Transaction propagation
    """

    def __init__(self, config: P2PConfig, node=None):
        self.config = config
        self.node = node  # Reference to NanoPyNode

        # Generate node ID if not provided
        if not config.node_id:
            self.config.node_id = hashlib.sha256(
                f"{config.host}:{config.port}:{time.time()}".encode()
            ).hexdigest()[:32]

        # Peer management
        self.peers: Dict[str, Peer] = {}
        self.pending_peers: Set[str] = set()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self.banned_peers: Set[str] = set()

        # Callbacks
        self._on_new_block: Optional[Callable] = None
        self._on_new_transaction: Optional[Callable] = None

        # Server
        self._server = None
        self._running = False

    @property
    def peer_count(self) -> int:
        return len(self.peers)

    @property
    def is_syncing(self) -> bool:
        if not self.node:
            return False
        # Check if any peer has higher block
        for peer in self.peers.values():
            if peer.best_block > self.node.block_number:
                return True
        return False

    # Connection handling

    async def start(self):
        """Start P2P server"""
        self._running = True
        self._loop = asyncio.get_event_loop()

        # Start TCP server
        self._server = await asyncio.start_server(
            self._handle_connection,
            self.config.host,
            self.config.port
        )


        # Connect to bootnodes
        for bootnode in self.config.bootnodes:
            asyncio.create_task(self._connect_to_bootnode(bootnode))

        # Start background tasks
        asyncio.create_task(self._peer_discovery_loop())
        asyncio.create_task(self._sync_loop())
        asyncio.create_task(self._ping_loop())

    async def stop(self):
        """Stop P2P server"""
        self._running = False

        # Disconnect all peers
        for peer in list(self.peers.values()):
            await self._disconnect_peer(peer, "shutdown")

        if self._server:
            self._server.close()
            await self._server.wait_closed()

    async def _handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle incoming peer connection"""
        addr = writer.get_extra_info('peername')
        peer_addr = f"{addr[0]}:{addr[1]}"

        if peer_addr in self.banned_peers:
            writer.close()
            return

        if len(self.peers) >= self.config.max_peers:
            writer.close()
            return

        peer = Peer(
            host=addr[0],
            port=addr[1],
            reader=reader,
            writer=writer
        )

        # Add peer to dict so handlers can access self.node
        self.peers[peer.address] = peer

        # Send hello
        await self._send_hello(peer)

        # Handle messages
        await self._handle_peer(peer)

        # Remove peer when done
        self.peers.pop(peer.address, None)

    async def connect_to_peer(self, host: str, port: int) -> Optional[Peer]:
        """Connect to a peer"""
        peer_addr = f"{host}:{port}"

        if peer_addr in self.peers:
            return self.peers[peer_addr]

        if peer_addr in self.banned_peers:
            return None

        if peer_addr in self.pending_peers:
            return None

        self.pending_peers.add(peer_addr)

        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=10
            )

            peer = Peer(
                host=host,
                port=port,
                reader=reader,
                writer=writer
            )

            # Send hello
            await self._send_hello(peer)

            # Wait for HELLO response
            try:
                length_data = await asyncio.wait_for(reader.read(4), timeout=10)
                if length_data:
                    msg_length = int.from_bytes(length_data, 'big')
                    msg_data = await asyncio.wait_for(reader.read(msg_length), timeout=10)
                    if msg_data:
                        msg_type = msg_data[0]
                        if msg_type == 0x00:  # HELLO
                            payload = json.loads(msg_data[1:].decode())
                            peer.node_id = payload.get("node_id", "")
                            peer.chain_id = payload.get("chain_id", 0)
                            peer.best_block = payload.get("best_block", 0)
                            peer.best_hash = payload.get("best_hash", "")
            except asyncio.TimeoutError:
                pass
            except Exception:
                pass

            self.peers[peer.address] = peer

            # Start handling messages in background
            asyncio.create_task(self._handle_peer(peer))

            return peer

        except asyncio.TimeoutError:
            return None
        except ConnectionRefusedError:
            return None
        except OSError:
            return None
        except Exception:
            return None
        finally:
            self.pending_peers.discard(peer_addr)

    async def _connect_to_bootnode(self, bootnode: str):
        """Connect to a bootnode"""
        try:
            host, port = bootnode.split(":")
            await self.connect_to_peer(host, int(port))
        except Exception:
            pass

    async def _disconnect_peer(self, peer: Peer, reason: str = ""):
        """Disconnect from peer"""
        peer_addr = peer.address

        try:
            await self._send_message(peer, MessageType.DISCONNECT, {"reason": reason})
            if peer.writer:
                peer.writer.close()
        except:
            pass

        self.peers.pop(peer_addr, None)

    # Message handling

    async def _handle_peer(self, peer: Peer):
        """Handle messages from peer"""
        try:
            while self._running and peer.reader:
                # Read message length (4 bytes)
                length_data = await asyncio.wait_for(
                    peer.reader.readexactly(4),
                    timeout=60
                )

                msg_length = int.from_bytes(length_data, 'big')

                if msg_length > 10 * 1024 * 1024:  # 10MB max
                    break

                # Read message
                msg_data = await asyncio.wait_for(
                    peer.reader.readexactly(msg_length),
                    timeout=30
                )

                # Parse message
                msg_type = msg_data[0]
                payload = json.loads(msg_data[1:].decode()) if len(msg_data) > 1 else {}

                # Handle message
                await self._handle_message(peer, msg_type, payload)

                peer.last_seen = time.time()

        except asyncio.IncompleteReadError:
            pass
        except asyncio.TimeoutError:
            pass
        except ConnectionResetError:
            pass
        except Exception:
            pass

        if peer.address in self.peers:
            del self.peers[peer.address]

    async def _handle_message(self, peer: Peer, msg_type: int, payload: dict):
        """Handle a message from peer"""

        if msg_type == MessageType.HELLO:
            await self._handle_hello(peer, payload)

        elif msg_type == MessageType.PING:
            await self._send_message(peer, MessageType.PONG, {})

        elif msg_type == MessageType.PONG:
            pass  # Update last_seen already done

        elif msg_type == MessageType.GET_PEERS:
            await self._handle_get_peers(peer)

        elif msg_type == MessageType.PEERS:
            await self._handle_peers(peer, payload)

        elif msg_type == MessageType.GET_BLOCK_HEADERS:
            await self._handle_get_block_headers(peer, payload)

        elif msg_type == MessageType.BLOCK_HEADERS:
            await self._handle_block_headers(peer, payload)

        elif msg_type == MessageType.NEW_BLOCK:
            await self._handle_new_block(peer, payload)

        elif msg_type == MessageType.NEW_BLOCK_HASHES:
            await self._handle_new_block_hashes(peer, payload)

        elif msg_type == MessageType.TRANSACTIONS:
            await self._handle_transactions(peer, payload)

        elif msg_type == MessageType.GET_BLOCK_BODIES:
            await self._handle_get_block_bodies(peer, payload)

        elif msg_type == MessageType.BLOCK_BODIES:
            await self._handle_block_bodies(peer, payload)

    async def _send_message(self, peer: Peer, msg_type: MessageType, payload: dict):
        """Send message to peer"""
        if not peer.writer:
            return

        try:
            payload_bytes = json.dumps(payload).encode()
            msg = bytes([msg_type]) + payload_bytes
            length = len(msg).to_bytes(4, 'big')

            peer.writer.write(length + msg)
            await peer.writer.drain()
        except Exception:
            pass

    # Protocol handlers

    async def _send_hello(self, peer: Peer):
        """Send hello message"""
        payload = {
            "version": 1,
            "node_id": self.config.node_id,
            "chain_id": self.config.chain_id,
            "network_id": self.config.network_id,
            "best_block": self.node.block_number if self.node else 0,
            "best_hash": to_hex(self.node.latest_block.hash) if self.node else "",
            "listen_port": self.config.port,
        }
        await self._send_message(peer, MessageType.HELLO, payload)

    async def _handle_hello(self, peer: Peer, payload: dict):
        """Handle hello from peer"""
        # Check chain ID
        if payload.get("chain_id") != self.config.chain_id:
            await self._disconnect_peer(peer, "chain_id mismatch")
            return

        peer.node_id = payload.get("node_id", "")
        peer.chain_id = payload.get("chain_id", 0)
        peer.best_block = payload.get("best_block", 0)
        peer.best_hash = payload.get("best_hash", "")

        # Add to connected peers
        self.peers[peer.address] = peer

        # Request peers
        await self._send_message(peer, MessageType.GET_PEERS, {})

    async def _handle_get_peers(self, peer: Peer):
        """Send peer list"""
        peers = []
        for p in self.peers.values():
            if p.address != peer.address:
                peers.append({"host": p.host, "port": p.port})
        await self._send_message(peer, MessageType.PEERS, {"peers": peers[:10]})

    async def _handle_peers(self, peer: Peer, payload: dict):
        """Handle peer list"""
        for p in payload.get("peers", []):
            if len(self.peers) < self.config.max_peers:
                asyncio.create_task(
                    self.connect_to_peer(p["host"], p["port"])
                )

    async def _handle_get_block_headers(self, peer: Peer, payload: dict):
        """Send block headers"""
        if not self.node:
            return

        start = payload.get("start", 0)
        count = min(payload.get("count", 100), 100)

        headers = []
        for i in range(start, min(start + count, self.node.block_number + 1)):
            block = self.node.blocks[i]
            headers.append(block.header.to_dict())

        await self._send_message(peer, MessageType.BLOCK_HEADERS, {"headers": headers})

    async def _handle_block_headers(self, peer: Peer, payload: dict):
        """Handle block headers - request full blocks"""
        headers = payload.get("headers", [])
        if not headers or not self.node:
            return

        # Request full blocks for these headers
        block_numbers = []
        for header in headers:
            num = int(header.get("number", "0x0"), 16)
            if num > self.node.block_number:
                block_numbers.append(num)

        if block_numbers:
            await self._send_message(peer, MessageType.GET_BLOCK_BODIES, {
                "blocks": block_numbers
            })

    async def _handle_new_block(self, peer: Peer, payload: dict):
        """Handle new block announcement"""
        if not self.node:
            return

        block_data = payload.get("block")
        if not block_data:
            return

        block_number = int(block_data.get("number", "0x0"), 16)

        # Check if we already have this block
        if block_number <= self.node.block_number:
            return

        # Callback to node
        if self._on_new_block:
            self._on_new_block(block_data, peer)

        # Update peer info
        peer.best_block = block_number
        peer.best_hash = block_data.get("hash", "")

        # Propagate to other peers
        await self.broadcast_block(block_data, exclude=peer.address)

    async def _handle_new_block_hashes(self, peer: Peer, payload: dict):
        """Handle new block hash announcements"""
        hashes = payload.get("hashes", [])
        # Request full blocks for unknown hashes
        pass

    async def _handle_transactions(self, peer: Peer, payload: dict):
        """Handle transaction announcements"""
        if not self.node:
            return

        txs = payload.get("transactions", [])
        for tx_data in txs:
            if self._on_new_transaction:
                self._on_new_transaction(tx_data, peer)

    async def _handle_get_block_bodies(self, peer: Peer, payload: dict):
        """Send full block data for requested block numbers"""
        if not self.node:
            return

        block_numbers = payload.get("blocks", [])
        bodies = []

        for num in block_numbers[:100]:
            if 0 <= num <= self.node.block_number:
                block = self.node.blocks[num]
                bodies.append(block.to_dict(full_transactions=True))

        await self._send_message(peer, MessageType.BLOCK_BODIES, {"bodies": bodies})

    async def _handle_block_bodies(self, peer: Peer, payload: dict):
        """Handle received block bodies - import them"""
        if not self.node:
            return

        bodies = payload.get("bodies", [])
        for block_data in bodies:
            block_number = int(block_data.get("number", "0x0"), 16)

            if block_number == self.node.block_number + 1:
                if self._on_new_block:
                    self._on_new_block(block_data, peer)

                peer.best_block = max(peer.best_block, block_number)
                peer.best_hash = block_data.get("hash", "")

    # Broadcasting

    async def broadcast_block(self, block_data: dict, exclude: str = ""):
        """Broadcast new block to all peers"""
        for peer in self.peers.values():
            if peer.address != exclude:
                await self._send_message(peer, MessageType.NEW_BLOCK, {"block": block_data})

    async def broadcast_transaction(self, tx_data: dict, exclude: str = ""):
        """Broadcast transaction to all peers"""
        for peer in self.peers.values():
            if peer.address != exclude:
                await self._send_message(peer, MessageType.TRANSACTIONS, {"transactions": [tx_data]})

    # Background tasks

    async def _peer_discovery_loop(self):
        """Periodically discover new peers"""
        while self._running:
            await asyncio.sleep(30)

            if len(self.peers) < self.config.max_peers // 2:
                for peer in list(self.peers.values()):
                    await self._send_message(peer, MessageType.GET_PEERS, {})

    async def _sync_loop(self):
        """Sync with peers"""
        while self._running:
            await asyncio.sleep(5)

            if not self.node:
                continue

            # Find peer with highest block
            best_peer = None
            for peer in self.peers.values():
                if peer.best_block > self.node.block_number:
                    if not best_peer or peer.best_block > best_peer.best_block:
                        best_peer = peer

            if best_peer:
                # Request headers
                await self._send_message(best_peer, MessageType.GET_BLOCK_HEADERS, {
                    "start": self.node.block_number + 1,
                    "count": 100
                })

    async def _ping_loop(self):
        """Ping peers to keep connections alive"""
        while self._running:
            await asyncio.sleep(15)

            now = time.time()
            for peer in list(self.peers.values()):
                # Disconnect stale peers
                if now - peer.last_seen > 60:
                    await self._disconnect_peer(peer, "timeout")
                else:
                    await self._send_message(peer, MessageType.PING, {})

    # Callbacks

    def on_new_block(self, callback: Callable):
        """Set callback for new blocks"""
        self._on_new_block = callback

    def on_new_transaction(self, callback: Callable):
        """Set callback for new transactions"""
        self._on_new_transaction = callback


def run_p2p_network(config: P2PConfig, node=None) -> P2PNetwork:
    """Run P2P network in background thread"""
    network = P2PNetwork(config, node)

    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(network.start())
        loop.run_forever()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    return network
