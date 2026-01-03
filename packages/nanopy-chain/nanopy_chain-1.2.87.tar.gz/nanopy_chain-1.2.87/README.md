# NanoPy

The first Ethereum-compatible blockchain written entirely in Python.

> *"Web3 is the developer's sudoku - you solve crypto puzzles, consensus problems, smart contracts... A blockchain in Python? That's not serious! Well that's the point, who cares, it works and it's fun."*

## Why Python?

- **Readable**: Understand the entire blockchain in the world's #1 language
- **Hackable**: Modify consensus, EVM, or networking without recompiling
- **Educational**: Learn blockchain internals without C++/Rust complexity

## Install

```bash
pip install nanopy-chain
```

## Quick Start

```bash
# Run a node
nanopy-node

# Run on testnet
nanopy-node --testnet

# Run a validator (earn NPY rewards)
nanopy-validator --key YOUR_PRIVATE_KEY

# Generate a wallet
nanopy wallet

# Check balance
nanopy balance 0xYourAddress
```

## Features

- **100% Python** - No C extensions, pure Python
- **Full EVM** - Deploy Solidity contracts, use MetaMask, Hardhat, etc.
- **Proof of Stake** - 10,000 NPY minimum stake, ~12s blocks
- **EIP-1559** - Dynamic fee market
- **EIP-2930** - Access lists support
- **libp2p** - Production-grade P2P networking
- **JSON-RPC** - HTTP + WebSocket on same port
- **eth_subscribe** - Real-time events (newHeads, logs, pendingTx)

## Networks

| Network | Chain ID | RPC URL | Status |
|---------|----------|---------|--------|
| Mainnet | 7770 | http://51.68.125.99:8545 | Coming soon |
| Testnet | 77777 | http://51.68.125.99:8546 | ✅ Active |

### Add to MetaMask

- **Network Name**: NanoPy Testnet
- **RPC URL**: http://51.68.125.99:8546
- **Chain ID**: 77777
- **Symbol**: NPY

## Layer 2: Turbo

NanoPy Turbo is our Go-based L2 for high-throughput applications.

| Network | Chain ID | RPC URL |
|---------|----------|---------|
| Turbo Testnet | 777702 | http://51.68.125.99:8548 |

See [blockchain-L2](https://github.com/Web3-League/blockchain-L2) repo.

## JSON-RPC

Single port serves both HTTP and WebSocket:

```bash
# HTTP
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'

# WebSocket (same port)
wscat -c ws://localhost:8545
> {"jsonrpc":"2.0","method":"eth_subscribe","params":["newHeads"],"id":1}
```

### Supported Methods

- `eth_blockNumber`, `eth_getBlockByNumber`, `eth_getBlockByHash`
- `eth_getBalance`, `eth_getTransactionCount`
- `eth_sendRawTransaction`, `eth_getTransactionReceipt`
- `eth_call`, `eth_estimateGas`
- `eth_getLogs`, `eth_subscribe`, `eth_unsubscribe`
- `net_version`, `eth_chainId`

## Deploy a Contract

```python
from web3 import Web3

w3 = Web3(Web3.HTTPProvider('http://51.68.125.99:8546'))

# Deploy with your favorite tool: Hardhat, Foundry, or raw Web3
```

## Architecture

```
nanopy/
├── nanolib/          # libp2p networking (Python port)
├── nanopy/
│   ├── core/         # Blockchain, blocks, transactions
│   ├── evm/          # Ethereum Virtual Machine
│   ├── consensus/    # Proof of Stake
│   ├── rpc/          # JSON-RPC server
│   └── p2p/          # Peer discovery, sync
└── contracts/        # Solidity contracts (DEX, NFT, Bridge)
```

## Links

- **PyPI**: https://pypi.org/project/nanopy-chain/
- **Webapp**: https://github.com/Web3-League/dapp-nanopy
- **L2 Turbo**: https://github.com/Web3-League/blockchain-L2

## License

MIT
