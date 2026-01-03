"""
NanoPy RPC Server - HTTP + WebSocket on the SAME port

Uses aiohttp to serve both:
- HTTP JSON-RPC (POST /)
- WebSocket JSON-RPC (WS /) with eth_subscribe/eth_unsubscribe

Single port for everything: 8545 (mainnet) or custom port
"""

import json
import asyncio
import logging
import uuid
import threading
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict

from aiohttp import web, WSMsgType
from eth_utils import to_hex

logger = logging.getLogger("nanopy.rpc")


@dataclass
class Subscription:
    """WebSocket subscription"""
    id: str
    type: str  # newHeads, newPendingTransactions, logs
    ws: web.WebSocketResponse
    params: Optional[dict] = None


class SubscriptionManager:
    """Manages WebSocket subscriptions"""

    def __init__(self):
        self.subscriptions: Dict[str, Subscription] = {}
        self.by_type: Dict[str, Set[str]] = defaultdict(set)
        self.by_ws: Dict[web.WebSocketResponse, Set[str]] = defaultdict(set)

    def add(self, sub: Subscription) -> str:
        self.subscriptions[sub.id] = sub
        self.by_type[sub.type].add(sub.id)
        self.by_ws[sub.ws].add(sub.id)
        return sub.id

    def remove(self, sub_id: str) -> bool:
        if sub_id not in self.subscriptions:
            return False
        sub = self.subscriptions[sub_id]
        self.by_type[sub.type].discard(sub_id)
        self.by_ws[sub.ws].discard(sub_id)
        del self.subscriptions[sub_id]
        return True

    def remove_all_for_ws(self, ws: web.WebSocketResponse):
        for sub_id in list(self.by_ws.get(ws, [])):
            self.remove(sub_id)
        self.by_ws.pop(ws, None)

    def get_by_type(self, sub_type: str) -> List[Subscription]:
        return [self.subscriptions[sid] for sid in self.by_type.get(sub_type, []) if sid in self.subscriptions]


class RPC:
    """
    HTTP + WebSocket RPC Server (aiohttp)

    Single port serves both protocols:
    - HTTP POST / -> JSON-RPC
    - WebSocket / -> JSON-RPC with subscriptions
    """

    def __init__(self, node: 'NanoPyNode'):
        self.node = node
        self.subscriptions = SubscriptionManager()
        self.ws_clients: Set[web.WebSocketResponse] = set()
        self._app: Optional[web.Application] = None
        self._runner: Optional[web.AppRunner] = None
        self._site: Optional[web.TCPSite] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

        # Import HTTP RPC handler (methods only)
        from nanopy.network.http_rpc import NanoPyRPC
        self.rpc = NanoPyRPC(node)

    async def start(self, host: str = "0.0.0.0", port: int = 8545):
        """Start the unified server"""
        self._app = web.Application()
        self._app.router.add_route('*', '/', self._handle_request)
        self._app.router.add_route('*', '/{path:.*}', self._handle_request)

        self._runner = web.AppRunner(self._app)
        await self._runner.setup()

        self._site = web.TCPSite(self._runner, host, port)
        await self._site.start()

        self._loop = asyncio.get_event_loop()
        logger.info(f"Unified RPC server started on http://{host}:{port} (HTTP + WebSocket)")

    async def stop(self):
        """Stop the server"""
        if self._site:
            await self._site.stop()
        if self._runner:
            await self._runner.cleanup()

    async def _handle_request(self, request: web.Request) -> web.Response:
        """Route request to HTTP or WebSocket handler"""
        # Check if WebSocket upgrade requested
        if request.headers.get('Upgrade', '').lower() == 'websocket':
            return await self._handle_websocket(request)

        # Handle HTTP
        if request.method == 'OPTIONS':
            return self._cors_response()

        if request.method == 'POST':
            return await self._handle_http(request)

        return web.Response(text="NanoPy RPC Server", status=200)

    def _cors_response(self) -> web.Response:
        return web.Response(
            status=200,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            }
        )

    async def _handle_http(self, request: web.Request) -> web.Response:
        """Handle HTTP JSON-RPC request"""
        try:
            body = await request.json()
        except json.JSONDecodeError:
            return web.json_response(
                {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}},
                headers={'Access-Control-Allow-Origin': '*'}
            )

        client_ip = request.remote

        # Handle batch or single
        if isinstance(body, list):
            response = self.rpc.handle_batch(body, client_ip)
        else:
            response = self.rpc.handle_request(body, client_ip)

        return web.json_response(response, headers={'Access-Control-Allow-Origin': '*'})

    async def _handle_websocket(self, request: web.Request) -> web.WebSocketResponse:
        """Handle WebSocket connection"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.ws_clients.add(ws)
        logger.debug(f"WebSocket connected: {request.remote}")

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    response = await self._handle_ws_message(ws, msg.data)
                    if response:
                        await ws.send_json(response)
                elif msg.type == WSMsgType.ERROR:
                    logger.debug(f"WebSocket error: {ws.exception()}")
        finally:
            self.subscriptions.remove_all_for_ws(ws)
            self.ws_clients.discard(ws)
            logger.debug(f"WebSocket disconnected: {request.remote}")

        return ws

    async def _handle_ws_message(self, ws: web.WebSocketResponse, data: str) -> Optional[dict]:
        """Handle WebSocket JSON-RPC message"""
        try:
            request = json.loads(data)
        except json.JSONDecodeError:
            return {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}

        if isinstance(request, list):
            return [await self._handle_ws_request(ws, req) for req in request]

        return await self._handle_ws_request(ws, request)

    async def _handle_ws_request(self, ws: web.WebSocketResponse, request: dict) -> dict:
        """Handle single WebSocket JSON-RPC request"""
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", [])

        if not method:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": "Invalid Request"}}

        # Subscription methods
        if method == "eth_subscribe":
            return self._eth_subscribe(req_id, ws, params)
        elif method == "eth_unsubscribe":
            return self._eth_unsubscribe(req_id, params)

        # Forward to standard RPC
        return self.rpc.handle_request(request, None)

    def _eth_subscribe(self, req_id: Any, ws: web.WebSocketResponse, params: list) -> dict:
        """Handle eth_subscribe"""
        if not params:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": "Missing subscription type"}}

        sub_type = params[0]
        if sub_type not in ("newHeads", "newPendingTransactions", "logs"):
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": f"Unknown subscription: {sub_type}"}}

        sub_id = "0x" + uuid.uuid4().hex[:32]
        filter_params = params[1] if sub_type == "logs" and len(params) > 1 else None

        sub = Subscription(id=sub_id, type=sub_type, ws=ws, params=filter_params)
        self.subscriptions.add(sub)

        logger.debug(f"Subscription created: {sub_type} -> {sub_id}")
        return {"jsonrpc": "2.0", "id": req_id, "result": sub_id}

    def _eth_unsubscribe(self, req_id: Any, params: list) -> dict:
        """Handle eth_unsubscribe"""
        if not params:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": "Missing subscription ID"}}

        success = self.subscriptions.remove(params[0])
        return {"jsonrpc": "2.0", "id": req_id, "result": success}

    # ========== Event Broadcasting ==========

    async def broadcast_new_head(self, block):
        """Notify newHeads subscribers"""
        subs = self.subscriptions.get_by_type("newHeads")
        print(f"[WS] Broadcasting block {block.number} to {len(subs)} subscribers")
        if not subs:
            return

        header = {
            "number": hex(block.number),
            "hash": to_hex(block.hash),
            "parentHash": to_hex(block.header.parent_hash),
            "sha3Uncles": to_hex(block.header.uncle_hash),
            "logsBloom": to_hex(block.header.logs_bloom),
            "transactionsRoot": to_hex(block.header.transactions_root),
            "stateRoot": to_hex(block.header.state_root),
            "receiptsRoot": to_hex(block.header.receipts_root),
            "miner": block.header.coinbase,
            "difficulty": hex(block.header.difficulty),
            "extraData": to_hex(block.header.extra_data),
            "gasLimit": hex(block.header.gas_limit),
            "gasUsed": hex(block.header.gas_used),
            "timestamp": hex(block.header.timestamp),
            "baseFeePerGas": hex(block.header.base_fee_per_gas) if block.header.base_fee_per_gas else "0x0",
        }

        for sub in subs:
            try:
                await sub.ws.send_json({
                    "jsonrpc": "2.0",
                    "method": "eth_subscription",
                    "params": {"subscription": sub.id, "result": header}
                })
            except Exception:
                pass

    async def broadcast_pending_tx(self, tx_hash: bytes):
        """Notify newPendingTransactions subscribers"""
        subs = self.subscriptions.get_by_type("newPendingTransactions")
        if not subs:
            return

        tx_hash_hex = to_hex(tx_hash)
        for sub in subs:
            try:
                await sub.ws.send_json({
                    "jsonrpc": "2.0",
                    "method": "eth_subscription",
                    "params": {"subscription": sub.id, "result": tx_hash_hex}
                })
            except Exception:
                pass

    async def broadcast_logs(self, logs: List[dict], block_hash: bytes, block_number: int):
        """Notify logs subscribers"""
        subs = self.subscriptions.get_by_type("logs")
        if not subs or not logs:
            return

        for sub in subs:
            filtered = self._filter_logs(logs, sub.params)
            for log in filtered:
                log_data = {**log, "blockHash": to_hex(block_hash), "blockNumber": hex(block_number)}
                try:
                    await sub.ws.send_json({
                        "jsonrpc": "2.0",
                        "method": "eth_subscription",
                        "params": {"subscription": sub.id, "result": log_data}
                    })
                except Exception:
                    pass

    def _filter_logs(self, logs: List[dict], params: Optional[dict]) -> List[dict]:
        """Filter logs by address/topics"""
        if not params:
            return logs

        result = []
        addr_filter = params.get("address")
        topics_filter = params.get("topics", [])

        for log in logs:
            # Address filter
            if addr_filter:
                log_addr = log.get("address", "").lower()
                if isinstance(addr_filter, str):
                    if log_addr != addr_filter.lower():
                        continue
                elif isinstance(addr_filter, list):
                    if log_addr not in [a.lower() for a in addr_filter]:
                        continue

            # Topics filter
            if topics_filter:
                log_topics = log.get("topics", [])
                match = True
                for i, tf in enumerate(topics_filter):
                    if tf is None:
                        continue
                    if i >= len(log_topics):
                        match = False
                        break
                    lt = log_topics[i].lower()
                    if isinstance(tf, str):
                        if lt != tf.lower():
                            match = False
                            break
                    elif isinstance(tf, list):
                        if lt not in [t.lower() for t in tf]:
                            match = False
                            break
                if not match:
                    continue

            result.append(log)

        return result


# Global instance
_rpc_instance: Optional[RPC] = None


def get_rpc() -> Optional[RPC]:
    return _rpc_instance


async def start_rpc(node: 'NanoPyNode', host: str = "0.0.0.0", port: int = 8545) -> RPC:
    """Start HTTP+WS RPC server"""
    global _rpc_instance
    _rpc_instance = RPC(node)
    await _rpc_instance.start(host, port)
    return _rpc_instance
