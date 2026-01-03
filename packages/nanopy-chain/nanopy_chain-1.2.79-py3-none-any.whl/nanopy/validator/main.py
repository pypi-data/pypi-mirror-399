#!/usr/bin/env python3
"""
NanoPy Validator Client CLI

Usage:
    nanopy-validator --validator-key 0x... --nodes http://localhost:8545
    nanopy-validator --config validator.json
"""

import sys
import logging
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from nanopy.validator.config import ValidatorConfig
from nanopy.validator.validator import Validator

console = Console()

# Official NanoPy RPC nodes (hardcoded for security)
# These are the only trusted nodes for validators
# Update via: pip install --upgrade nanopy-chain
MAINNET_RPC_NODES = [
    "http://51.68.125.99:8545",  # OVH VPS EU
]

TESTNET_RPC_NODES = [
    "http://51.68.125.99:8546",  # OVH VPS EU Testnet (Pyralis)
]


def setup_logging(level: str):
    """Setup logging configuration."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def print_banner(config: ValidatorConfig, address: str):
    """Print startup banner."""
    table = Table(show_header=False, box=None)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Address", address)
    table.add_row("Nodes", ", ".join(config.nodes))
    table.add_row("Block Time", f"{config.block_time}s")
    table.add_row("Log Level", config.log_level)

    panel = Panel(
        table,
        title="[bold blue]NanoPy Validator Client[/bold blue]",
        border_style="blue",
    )
    console.print(panel)


def main():
    parser = argparse.ArgumentParser(
        description="NanoPy Validator Client - Separate validator for PoS consensus"
    )

    parser.add_argument(
        "--validator-key",
        type=str,
        help="Validator private key (hex with 0x prefix)",
    )

    parser.add_argument(
        "--nodes",
        type=str,
        default=None,
        help="Comma-separated list of node RPC endpoints (default: official mainnet nodes)",
    )

    parser.add_argument(
        "--mainnet",
        action="store_true",
        default=True,
        help="Use official mainnet nodes (default)",
    )

    parser.add_argument(
        "--testnet",
        action="store_true",
        help="Use testnet nodes",
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to JSON config file",
    )

    parser.add_argument(
        "--block-time",
        type=int,
        default=12,
        help="Block production interval in seconds (default: 12)",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log level (default: INFO)",
    )

    parser.add_argument(
        "--register",
        action="store_true",
        help="Register as validator if not already registered",
    )

    parser.add_argument(
        "--stake",
        type=float,
        default=10000,
        help="Stake amount in NPY for registration (default: 10000)",
    )

    args = parser.parse_args()

    # Load config
    if args.config:
        try:
            config = ValidatorConfig.from_file(args.config)
        except Exception as e:
            console.print(f"[red]Error loading config: {e}[/red]")
            sys.exit(1)

        # Override with command line args if provided
        if args.validator_key:
            config.validator_key = args.validator_key
    else:
        # Build config from args
        if not args.validator_key:
            console.print("[red]Error: --validator-key is required[/red]")
            console.print("Usage: nanopy-validator --validator-key 0x...")
            sys.exit(1)

        # Determine nodes to use (priority: --nodes > --testnet > mainnet default)
        if args.nodes:
            # User specified nodes explicitly
            node_list = [n.strip() for n in args.nodes.split(",")]
        elif args.testnet:
            # Use testnet nodes
            node_list = TESTNET_RPC_NODES.copy()
            if not node_list:
                console.print("[red]Error: No testnet nodes configured yet[/red]")
                sys.exit(1)
        else:
            # Default: use mainnet nodes (hardcoded for security)
            node_list = MAINNET_RPC_NODES.copy()

        console.print(f"[dim]Using {len(node_list)} official node(s)[/dim]")

        config = ValidatorConfig(
            validator_key=args.validator_key,
            nodes=node_list,
            block_time=args.block_time,
            log_level=args.log_level,
        )

    # Validate config
    errors = config.validate()
    if errors:
        for error in errors:
            console.print(f"[red]Config error: {error}[/red]")
        sys.exit(1)

    # Setup logging
    setup_logging(config.log_level)

    # Create validator
    try:
        validator = Validator(config)
    except Exception as e:
        console.print(f"[red]Failed to create validator: {e}[/red]")
        sys.exit(1)

    # Print banner
    print_banner(config, validator.address)

    # Check node connectivity
    console.print("\n[cyan]Checking node connectivity...[/cyan]")
    healthy_node = validator.client.get_healthy_node()
    if not healthy_node:
        console.print("[red]Error: Could not connect to any node[/red]")
        sys.exit(1)
    console.print(f"[green]Connected to: {healthy_node}[/green]")

    # Get chain info
    try:
        chain_id = validator.client.get_chain_id()
        block_number = validator.client.get_block_number()
        console.print(f"[green]Chain ID: {chain_id}, Block: {block_number}[/green]")
    except Exception as e:
        console.print(f"[red]Failed to get chain info: {e}[/red]")
        sys.exit(1)

    # Register if requested
    if args.register:
        stake_wei = int(args.stake * 10**18)
        console.print(f"\n[cyan]Registering validator with {args.stake} NPY stake...[/cyan]")
        if validator.ensure_registered(stake_wei):
            console.print("[green]Validator registered![/green]")
        else:
            console.print("[yellow]Warning: Registration may have failed[/yellow]")

    # Check validator status
    try:
        stake = validator.client.get_stake(validator.address)
        if stake > 0:
            console.print(f"[green]Validator stake: {stake / 10**18:.2f} NPY[/green]")
        else:
            console.print("[yellow]Warning: No stake found. Use --register to register.[/yellow]")
    except Exception as e:
        console.print(f"[yellow]Could not check stake: {e}[/yellow]")

    # Start validation
    console.print("\n[bold green]Starting validation...[/bold green]")
    console.print("[dim]Press Ctrl+C to stop[/dim]\n")

    try:
        validator.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down...[/yellow]")
    finally:
        stats = validator.get_stats()
        console.print(f"\n[bold cyan]═══ Validator Stats ═══[/bold cyan]")
        console.print(f"[cyan]Blocks produced: {stats['blocks_produced']}[/cyan]")
        console.print(f"[cyan]Uptime: {stats['uptime_seconds']} seconds[/cyan]")
        console.print(f"[green]Block rewards: {stats['total_rewards_npy']:.2f} NPY[/green]")
        console.print(f"[green]Gas fees: {stats['total_gas_fees_npy']:.6f} NPY[/green]")
        console.print(f"[bold green]Total earned: {stats['total_earned_npy']:.2f} NPY[/bold green]")


if __name__ == "__main__":
    main()
