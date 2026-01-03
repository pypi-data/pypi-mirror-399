"""
NanoPy CLI - Command line interface
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="NanoPy")
def cli():
    """
    NanoPy - Ethereum-compatible blockchain in Python

    A lightweight Ethereum fork for development and learning.
    """
    pass


@cli.command()
@click.option("--host", default="127.0.0.1", help="RPC server host")
@click.option("--port", default=8545, help="RPC server port")
@click.option("--chain-id", default=1337, help="Chain ID")
@click.option("--gas-limit", default=30_000_000, help="Block gas limit")
@click.option("--coinbase", default="", help="Coinbase address for block rewards")
def node(host: str, port: int, chain_id: int, gas_limit: int, coinbase: str):
    """Start a NanoPy node"""
    from nanopy.node import NanoPyNode
    from nanopy.node.node import NodeConfig

    config = NodeConfig(
        chain_id=chain_id,
        gas_limit=gas_limit,
        rpc_host=host,
        rpc_port=port,
        coinbase=coinbase,
    )

    node = NanoPyNode(config)
    node.run()


@cli.command()
@click.option("--count", default=10, help="Number of accounts to generate")
def accounts(count: int):
    """Generate test accounts"""
    from nanopy.crypto import generate_keypair

    table = Table(title="Generated Accounts")
    table.add_column("Index", style="cyan")
    table.add_column("Address", style="green")
    table.add_column("Private Key", style="red")

    for i in range(count):
        priv, pub, addr = generate_keypair()
        table.add_row(str(i), addr, priv[:20] + "...")

    console.print(table)
    console.print("\n[yellow]WARNING: Save these private keys! They won't be shown again.[/yellow]")


@cli.command()
@click.option("--words", default="12", type=click.Choice(["12", "24"]), help="Number of words")
def wallet(words: str):
    """Generate HD wallet with mnemonic"""
    from nanopy.crypto.wallet import HDWallet

    hd = HDWallet.create(num_words=int(words))

    console.print(Panel(
        f"[bold green]{hd.mnemonic}[/bold green]",
        title="Mnemonic Phrase",
        subtitle="SAVE THIS SECURELY!"
    ))

    table = Table(title="Derived Accounts")
    table.add_column("Index", style="cyan")
    table.add_column("Address", style="green")

    for i in range(5):
        wallet = hd.derive_account(i)
        table.add_row(str(i), wallet.address)

    console.print(table)


@cli.command()
@click.argument("address")
@click.option("--rpc", default="http://127.0.0.1:8545", help="RPC endpoint")
def balance(address: str, rpc: str):
    """Get account balance"""
    from web3 import Web3

    w3 = Web3(Web3.HTTPProvider(rpc))
    balance_wei = w3.eth.get_balance(address)
    balance_eth = w3.from_wei(balance_wei, 'ether')

    console.print(f"[bold]Address:[/bold] {address}")
    console.print(f"[bold]Balance:[/bold] [green]{balance_eth}[/green] NPY")
    console.print(f"[dim]({balance_wei} Wei)[/dim]")


@cli.command()
@click.argument("to")
@click.argument("amount")
@click.option("--from", "sender", required=True, help="Sender address")
@click.option("--private-key", required=True, help="Private key")
@click.option("--rpc", default="http://127.0.0.1:8545", help="RPC endpoint")
def send(to: str, amount: str, sender: str, private_key: str, rpc: str):
    """Send NPY to an address"""
    from web3 import Web3

    w3 = Web3(Web3.HTTPProvider(rpc))
    amount_wei = w3.to_wei(float(amount), 'ether')

    tx = {
        'from': sender,
        'to': to,
        'value': amount_wei,
        'gas': 21000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(sender),
        'chainId': w3.eth.chain_id,
    }

    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)

    console.print(f"[green]OK[/green] Transaction sent!")
    console.print(f"[bold]Hash:[/bold] {tx_hash.hex()}")


@cli.command()
@click.option("--rpc", default="http://127.0.0.1:8545", help="RPC endpoint")
def info(rpc: str):
    """Get node information"""
    from web3 import Web3

    w3 = Web3(Web3.HTTPProvider(rpc))

    table = Table(title="Node Information")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Chain ID", str(w3.eth.chain_id))
    table.add_row("Block Number", str(w3.eth.block_number))
    table.add_row("Gas Price", f"{w3.from_wei(w3.eth.gas_price, 'gwei')} Gwei")
    table.add_row("Client", w3.client_version)

    console.print(table)


@cli.command()
@click.option("--rpc", default="http://51.68.125.99:8545", help="RPC endpoint")
def nodes(rpc: str):
    """List available NanoPy nodes"""
    import requests

    try:
        response = requests.post(rpc, json={
            "jsonrpc": "2.0",
            "method": "nno_getNodes",
            "params": [],
            "id": 1,
        }, timeout=10)

        result = response.json()
        if "result" in result:
            data = result["result"]

            # RPC Nodes table
            table = Table(title="NanoPy RPC Nodes")
            table.add_column("Name", style="cyan")
            table.add_column("URL", style="green")
            table.add_column("Location", style="yellow")
            table.add_column("Status", style="magenta")

            for node in data.get("rpcNodes", []):
                status_style = "green" if node["status"] == "active" else "red"
                table.add_row(
                    node["name"],
                    node["url"],
                    node["location"],
                    f"[{status_style}]{node['status']}[/{status_style}]"
                )

            console.print(table)

            # Bootnodes
            console.print(f"\n[bold]P2P Bootnodes:[/bold] {len(data.get('bootnodes', []))}")
            for bn in data.get("bootnodes", []):
                console.print(f"  [dim]{bn}[/dim]")

            # Connected peers
            console.print(f"\n[bold]Connected Peers:[/bold] {data.get('totalPeers', 0)}")

        else:
            console.print(f"[red]ERROR[/red] {result.get('error', 'Unknown error')}")

    except requests.exceptions.ConnectionError:
        console.print(f"[red]ERROR[/red] Could not connect to {rpc}")
        console.print("\n[bold]Default NanoPy Nodes:[/bold]")
        console.print("  • http://51.68.125.99:8545 (OVH EU)")


@cli.command()
@click.option("--rpc", default="http://51.68.125.99:8545", help="RPC endpoint")
def network(rpc: str):
    """Get NanoPy network information"""
    import requests

    try:
        response = requests.post(rpc, json={
            "jsonrpc": "2.0",
            "method": "nno_getNetworkInfo",
            "params": [],
            "id": 1,
        }, timeout=10)

        result = response.json()
        if "result" in result:
            data = result["result"]

            # Network info
            net = data.get("network", {})
            console.print(Panel(f"""
[bold cyan]{net.get('name', 'NanoPy')}[/bold cyan]

[dim]Chain ID:[/dim]      {net.get('chainId')}
[dim]Consensus:[/dim]     {net.get('consensus')}
[dim]Block Time:[/dim]    {net.get('blockTime')}s
""", title="[bold green]Network[/bold green]", border_style="green"))

            # Chain info
            chain = data.get("chain", {})
            console.print(f"[bold]Block Number:[/bold] {chain.get('blockNumber')}")
            console.print(f"[bold]Latest Hash:[/bold] {chain.get('latestBlockHash', 'N/A')[:20]}...")

            # Peers
            peers = data.get("peers", {})
            console.print(f"\n[bold]Peers:[/bold] {peers.get('count', 0)}/{peers.get('maxPeers', 50)}")

            # Validators
            validators = data.get("validators", {})
            console.print(f"[bold]Validators:[/bold] {validators.get('count', 0)}")

            # RPC endpoints
            console.print(f"\n[bold]RPC Endpoints:[/bold]")
            for endpoint in data.get("rpcEndpoints", []):
                console.print(f"  • {endpoint}")

        else:
            console.print(f"[red]ERROR[/red] {result.get('error', 'Unknown error')}")

    except requests.exceptions.ConnectionError:
        console.print(f"[red]ERROR[/red] Could not connect to {rpc}")


@cli.command()
@click.option("--rpc", default="http://127.0.0.1:8545", help="RPC endpoint")
def mine(rpc: str):
    """Mine a new block (dev mode)"""
    import requests

    response = requests.post(rpc, json={
        "jsonrpc": "2.0",
        "method": "evm_mine",
        "params": [],
        "id": 1,
    })

    result = response.json()
    if "result" in result:
        console.print(f"[green]OK[/green] Block mined: {result['result']}")
    else:
        console.print(f"[red]ERROR[/red] {result.get('error', 'Unknown error')}")


@cli.command()
@click.argument("contract_file")
@click.option("--from", "sender", required=True, help="Deployer address")
@click.option("--private-key", required=True, help="Private key")
@click.option("--rpc", default="http://127.0.0.1:8545", help="RPC endpoint")
def deploy(contract_file: str, sender: str, private_key: str, rpc: str):
    """Deploy a contract (bytecode file)"""
    from web3 import Web3

    w3 = Web3(Web3.HTTPProvider(rpc))

    with open(contract_file, 'r') as f:
        bytecode = f.read().strip()

    if not bytecode.startswith('0x'):
        bytecode = '0x' + bytecode

    tx = {
        'from': sender,
        'data': bytecode,
        'gas': 3_000_000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(sender),
        'chainId': w3.eth.chain_id,
    }

    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)

    console.print(f"[yellow]PENDING[/yellow] Deploying contract...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    if receipt.status == 1:
        console.print(f"[green]OK[/green] Contract deployed!")
        console.print(f"[bold]Address:[/bold] {receipt.contractAddress}")
        console.print(f"[bold]Gas Used:[/bold] {receipt.gasUsed}")
    else:
        console.print(f"[red]FAILED[/red] Deployment failed!")


def main():
    """Entry point"""
    cli()


if __name__ == "__main__":
    main()
