# NanoPy

Ethereum-compatible PoS blockchain in Python.

## Install

```bash
pip install nanopy-chain
nanopy-node
```

## Features

- PoS consensus
- EVM compatible
- libp2p P2P networking
- JSON-RPC (HTTP + WebSocket on same port)
- `eth_subscribe` for real-time events

## RPC

Single port serves HTTP and WebSocket:

```bash
# HTTP
curl -X POST http://localhost:8545 -d '{"method":"eth_blockNumber",...}'

# WebSocket (same port)
wscat -c ws://localhost:8545
> {"method":"eth_subscribe","params":["newHeads"],...}
```

Subscriptions: `newHeads`, `newPendingTransactions`, `logs`

## Network

| Property | Value |
|----------|-------|
| Chain ID | 7770 |
| Token | NPY |
| RPC | 8545 |
| P2P | 30303 |

## CLI

```bash
nanopy-node              # Start node
nanopy-node --testnet    # Testnet
nanopy wallet            # Generate wallet
nanopy balance 0x...     # Check balance
```

## License

MIT
