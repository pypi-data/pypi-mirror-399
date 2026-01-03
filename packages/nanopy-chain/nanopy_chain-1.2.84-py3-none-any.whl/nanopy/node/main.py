#!/usr/bin/env python3
"""
nanopy-node - Start a NanoPy blockchain node

Usage:
    nanopy-node                     # Start mainnet node (chain_id 7770)
    nanopy-node --testnet           # Start testnet node
    nanopy-node --chain-id 1337     # Start custom chain
"""

import click
import logging
from rich.console import Console
from rich.panel import Panel

# Configure logging to show INFO level messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

console = Console()

# Official NanoPy mainnet bootnodes
# Format: /ip4/IP/tcp/PORT/p2p/PEER_ID
# The Peer ID is required for libp2p connection
MAINNET_BOOTNODES = [
    "/ip4/51.68.125.99/tcp/30303/p2p/16Uiu2HAkwgprTzarapJbEWCDp7d6s6AeX39eVctBt9ftt4EY79V8",  # OVH VPS
]

TESTNET_BOOTNODES = [
    "/ip4/51.68.125.99/tcp/30304/p2p/16Uiu2HAkwnjKfcDVRrEdSE8QpgDVsFQB5doSXX57R9DEE9BjNyQo",  # OVH VPS Testnet
]


@click.command()
@click.option("--chain-id", default=7770, help="Chain ID (default: 7770 NanoPy mainnet)")
@click.option("--rpc-host", default=None, help="RPC server host (default: 0.0.0.0)")
@click.option("--rpc-port", default=8545, help="RPC server port")
@click.option("--p2p-port", default=30303, help="P2P network port")
@click.option("--data-dir", default="./chaindata", help="Data directory")
@click.option("--bootnodes", default="", help="Comma-separated bootstrap nodes")
@click.option("--testnet", is_flag=True, help="Use testnet settings")
@click.option("--no-p2p", is_flag=True, help="Disable P2P networking")
def main(
    chain_id: int,
    rpc_host: str,
    rpc_port: int,
    p2p_port: int,
    data_dir: str,
    bootnodes: str,
    testnet: bool,
    no_p2p: bool,
):
    """
    Start a NanoPy blockchain node.

    NanoPy is an Ethereum-compatible PoS blockchain.

    Examples:

        nanopy-node                          # Join NanoPy mainnet

        nanopy-node --rpc-port 8546          # Custom RPC port

        nanopy-node --bootnodes 1.2.3.4:30303   # Connect to specific node
    """
    from nanopy.node import NanoPyNode
    from nanopy.node.node import NodeConfig

    # Use NodeConfig defaults if not specified
    if rpc_host is None:
        rpc_host = "0.0.0.0"

    # Testnet overrides
    if testnet:
        chain_id = 77777
        data_dir = "./chaindata_testnet"
        # Use different ports for testnet (if not explicitly set)
        if rpc_port == 8545:  # Default mainnet port
            rpc_port = 8546
        if p2p_port == 30303:  # Default mainnet port
            p2p_port = 30304

    # Parse bootnodes - use defaults if none specified
    bootnode_list = []
    if bootnodes:
        bootnode_list = [b.strip() for b in bootnodes.split(",") if b.strip()]
    elif chain_id == 7770:
        bootnode_list = MAINNET_BOOTNODES.copy()
    elif chain_id == 77777 or testnet:
        bootnode_list = TESTNET_BOOTNODES.copy()

    config = NodeConfig(
        chain_id=chain_id,
        gas_limit=30_000_000,
        rpc_host=rpc_host,
        rpc_port=rpc_port,
        data_dir=data_dir,
        persist=True,
        consensus="pos",
        block_time=12,
        staking_contract=None,  # No staking contract yet - use bootstrap mode

        # P2P
        p2p_host="0.0.0.0",
        p2p_port=p2p_port,
        use_libp2p=not no_p2p,
        max_peers=50,
        bootnodes=bootnode_list,
    )

    # Node never runs validator - use nanopy-validator for validation
    config.validator_key = ""

    # Display banner
    network_name = "NanoPy Mainnet" if chain_id == 7770 else f"Chain {chain_id}"
    if testnet or chain_id == 77777:
        network_name = "Pyralis Testnet"

    console.print(Panel(f"""
[bold cyan]{network_name}[/bold cyan]

[dim]Chain ID:[/dim]     {chain_id}
[dim]RPC:[/dim]          http://{rpc_host}:{rpc_port}
[dim]P2P Port:[/dim]     {p2p_port}
[dim]Data Dir:[/dim]     {data_dir}
[dim]Consensus:[/dim]    PoS (Proof of Stake)
[dim]libp2p:[/dim]       {'Enabled' if not no_p2p else 'Disabled'}
[dim]Bootnodes:[/dim]    {len(bootnode_list)} configured
""", title="[bold green]NanoPy Node[/bold green]", border_style="green"))

    console.print("[dim]Use nanopy-validator to run a validator client[/dim]")

    if chain_id == 7770:
        console.print("[dim]Genesis embedded for mainnet - no genesis.json needed![/dim]\n")

    node = NanoPyNode(config)
    node.run()


if __name__ == "__main__":
    main()
