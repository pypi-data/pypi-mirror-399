#!/usr/bin/env python3
"""
NanoPy Faucet - Multi-Network Token Distributor
Supports NanoPy L1 Testnet and Turbo L2 Testnet
"""

import click
from aiohttp import web
import os
import json
import time
import asyncio
from typing import Dict, Optional
from dataclasses import dataclass
from eth_account import Account
from eth_utils import to_checksum_address

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# Network configurations
@dataclass
class NetworkConfig:
    chain_id: int
    name: str
    rpc: str
    symbol: str
    amount: float  # tokens per claim
    cooldown: int  # seconds
    is_l2: bool = False


NETWORKS = {
    "testnet": NetworkConfig(
        chain_id=77700,
        name="NanoPy Testnet",
        rpc="http://51.68.125.99:8546",
        symbol="NPY",
        amount=10.0,
        cooldown=3600,  # 1 hour
        is_l2=False,
    ),
    "turbo": NetworkConfig(
        chain_id=777702,
        name="NanoPy Turbo L2 Testnet",
        rpc="http://51.68.125.99:8548",
        symbol="NPY",
        amount=100.0,  # More for L2 testing
        cooldown=1800,  # 30 minutes
        is_l2=True,
    ),
}

# Rate limiting per network
claim_history: Dict[str, Dict[str, float]] = {"testnet": {}, "turbo": {}}
ip_claims: Dict[str, Dict[str, list]] = {"testnet": {}, "turbo": {}}
MAX_CLAIMS_PER_IP = 10


class Faucet:
    def __init__(self, private_key: str, network: NetworkConfig):
        self.account = Account.from_key(private_key)
        self.network = network
        self.amount_wei = int(network.amount * 10**18)

    async def get_nonce(self) -> int:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(self.network.rpc, json={
                "jsonrpc": "2.0",
                "method": "eth_getTransactionCount",
                "params": [self.account.address, "pending"],
                "id": 1
            }) as resp:
                data = await resp.json()
                return int(data["result"], 16)

    async def get_balance(self) -> int:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(self.network.rpc, json={
                "jsonrpc": "2.0",
                "method": "eth_getBalance",
                "params": [self.account.address, "latest"],
                "id": 1
            }) as resp:
                data = await resp.json()
                return int(data["result"], 16)

    async def send_tokens(self, to_address: str) -> dict:
        import aiohttp

        nonce = await self.get_nonce()

        tx = {
            "nonce": nonce,
            "to": to_checksum_address(to_address),
            "value": self.amount_wei,
            "gas": 21000,
            "gasPrice": 1000000000,  # 1 Gwei
            "chainId": self.network.chain_id,
        }

        signed = self.account.sign_transaction(tx)
        raw_tx = signed.raw_transaction.hex()
        if not raw_tx.startswith("0x"):
            raw_tx = "0x" + raw_tx

        async with aiohttp.ClientSession() as session:
            async with session.post(self.network.rpc, json={
                "jsonrpc": "2.0",
                "method": "eth_sendRawTransaction",
                "params": [raw_tx],
                "id": 1
            }) as resp:
                data = await resp.json()
                if "error" in data:
                    return {"success": False, "error": data["error"]["message"]}
                return {"success": True, "txHash": data["result"]}


def get_faucet(app, network_id: str) -> Optional[Faucet]:
    """Get faucet for network."""
    return app.get(f"faucet_{network_id}")


async def index_handler(request):
    """Serve main page."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()
    return web.Response(text=html, content_type="text/html")


async def networks_handler(request):
    """Get available networks."""
    result = {}
    for net_id, net in NETWORKS.items():
        faucet = get_faucet(request.app, net_id)
        if faucet:
            balance = await faucet.get_balance()
            result[net_id] = {
                "chainId": net.chain_id,
                "name": net.name,
                "symbol": net.symbol,
                "amount": net.amount,
                "cooldown": net.cooldown,
                "cooldownFormatted": f"{net.cooldown // 60} minutes",
                "isL2": net.is_l2,
                "faucetAddress": faucet.account.address,
                "balance": balance / 10**18,
                "rpc": net.rpc,
            }
    return web.json_response(result)


async def status_handler(request):
    """Get faucet status for a network."""
    network_id = request.query.get("network", "testnet")

    if network_id not in NETWORKS:
        return web.json_response({"error": "Unknown network"}, status=400)

    faucet = get_faucet(request.app, network_id)
    if not faucet:
        return web.json_response({"error": "Faucet not configured"}, status=500)

    net = NETWORKS[network_id]
    balance = await faucet.get_balance()

    return web.json_response({
        "network": network_id,
        "chainId": net.chain_id,
        "name": net.name,
        "address": faucet.account.address,
        "balance": balance / 10**18,
        "amountPerClaim": net.amount,
        "cooldownMinutes": net.cooldown // 60,
        "isL2": net.is_l2,
    })


async def claim_handler(request):
    """Handle faucet claim."""
    try:
        data = await request.json()
        address = data.get("address", "").strip()
        network_id = data.get("network", "testnet")

        # Validate network
        if network_id not in NETWORKS:
            return web.json_response({"success": False, "error": "Unknown network"})

        faucet = get_faucet(request.app, network_id)
        if not faucet:
            return web.json_response({"success": False, "error": "Faucet not configured for this network"})

        net = NETWORKS[network_id]

        # Validate address
        if not address or len(address) != 42 or not address.startswith("0x"):
            return web.json_response({"success": False, "error": "Invalid address"})

        try:
            address = to_checksum_address(address)
        except:
            return web.json_response({"success": False, "error": "Invalid address format"})

        # Rate limiting
        now = time.time()
        addr_key = address.lower()
        client_ip = request.headers.get("X-Forwarded-For", request.remote)

        # Check address cooldown
        if addr_key in claim_history[network_id]:
            elapsed = now - claim_history[network_id][addr_key]
            if elapsed < net.cooldown:
                remaining = int((net.cooldown - elapsed) / 60)
                return web.json_response({
                    "success": False,
                    "error": f"Already claimed. Try again in {remaining} min"
                })

        # Check IP limit
        if client_ip in ip_claims[network_id]:
            ip_claims[network_id][client_ip] = [
                t for t in ip_claims[network_id][client_ip] if now - t < net.cooldown
            ]
            if len(ip_claims[network_id][client_ip]) >= MAX_CLAIMS_PER_IP:
                return web.json_response({
                    "success": False,
                    "error": f"IP limit reached ({MAX_CLAIMS_PER_IP} wallets). Try later."
                })

        # Check faucet balance
        balance = await faucet.get_balance()
        if balance < faucet.amount_wei:
            return web.json_response({
                "success": False,
                "error": "Faucet is empty. Please try again later."
            })

        # Send tokens
        result = await faucet.send_tokens(address)

        if result["success"]:
            claim_history[network_id][addr_key] = now
            if client_ip not in ip_claims[network_id]:
                ip_claims[network_id][client_ip] = []
            ip_claims[network_id][client_ip].append(now)

            return web.json_response({
                "success": True,
                "txHash": result["txHash"],
                "amount": net.amount,
                "network": net.name,
                "symbol": net.symbol,
            })
        else:
            return web.json_response(result)

    except Exception as e:
        return web.json_response({"success": False, "error": str(e)})


async def check_handler(request):
    """Check if address can claim."""
    address = request.query.get("address", "").strip().lower()
    network_id = request.query.get("network", "testnet")

    if network_id not in NETWORKS:
        return web.json_response({"canClaim": False, "error": "Unknown network"})

    net = NETWORKS[network_id]

    if not address or not address.startswith("0x"):
        return web.json_response({"canClaim": False, "error": "Invalid address"})

    now = time.time()
    if address in claim_history[network_id]:
        elapsed = now - claim_history[network_id][address]
        if elapsed < net.cooldown:
            remaining = int(net.cooldown - elapsed)
            return web.json_response({
                "canClaim": False,
                "remainingSeconds": remaining,
            })

    return web.json_response({"canClaim": True})


@click.command()
@click.option("--private-key", required=True, envvar="FAUCET_KEY", help="Faucet wallet private key")
@click.option("--host", default="0.0.0.0", help="Server host")
@click.option("--port", default=8081, help="Server port")
def main(private_key: str, host: str, port: int):
    """Start the NanoPy multi-network faucet."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()

    # Create faucets for all networks
    faucets = {}
    for net_id, net in NETWORKS.items():
        faucets[net_id] = Faucet(private_key=private_key, network=net)

    # Display info
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Network")
    table.add_column("Chain ID")
    table.add_column("Amount")
    table.add_column("Cooldown")
    table.add_column("Type")

    for net_id, net in NETWORKS.items():
        table.add_row(
            net.name,
            str(net.chain_id),
            f"{net.amount} {net.symbol}",
            f"{net.cooldown // 60} min",
            "L2" if net.is_l2 else "L1",
        )

    console.print(Panel(f"""
[bold cyan]NanoPy Multi-Network Faucet[/bold cyan]

[dim]Faucet Address:[/dim]  {faucets['testnet'].account.address}
[dim]Server:[/dim]          http://{host}:{port}

[dim]Press Ctrl+C to stop[/dim]
""", title="[bold green]NanoPy Faucet[/bold green]", border_style="green"))

    console.print(table)

    app = web.Application()

    # Store faucets
    for net_id, faucet in faucets.items():
        app[f"faucet_{net_id}"] = faucet

    # Routes
    app.router.add_get("/", index_handler)
    app.router.add_get("/networks", networks_handler)
    app.router.add_get("/status", status_handler)
    app.router.add_post("/claim", claim_handler)
    app.router.add_get("/check", check_handler)
    app.router.add_static("/static", STATIC_DIR, name="static")

    web.run_app(app, host=host, port=port, print=None)


if __name__ == "__main__":
    main()
