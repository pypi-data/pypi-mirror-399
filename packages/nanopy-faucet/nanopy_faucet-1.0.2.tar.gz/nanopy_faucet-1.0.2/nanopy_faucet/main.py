#!/usr/bin/env python3
"""
NanoPy Faucet - Testnet Token Distributor
"""

import click
from aiohttp import web
import os
import json
import time
import asyncio
from typing import Dict
from eth_account import Account
from eth_utils import to_checksum_address

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# Rate limiting: track claims per address and IP
claim_history: Dict[str, float] = {}  # address -> last claim timestamp
ip_claims: Dict[str, list] = {}  # ip -> list of claim timestamps (for counting)
MAX_CLAIMS_PER_IP = 10  # Max 10 different wallets per IP per cooldown period


class Faucet:
    def __init__(self, private_key: str, rpc_url: str, amount: float, cooldown: int, chain_id: int):
        self.account = Account.from_key(private_key)
        self.rpc_url = rpc_url
        self.amount_wei = int(amount * 10**18)
        self.cooldown = cooldown  # seconds
        self.chain_id = chain_id
        self.nonce = None

    async def get_nonce(self) -> int:
        """Get current nonce from RPC."""
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(self.rpc_url, json={
                "jsonrpc": "2.0",
                "method": "eth_getTransactionCount",
                "params": [self.account.address, "pending"],
                "id": 1
            }) as resp:
                data = await resp.json()
                return int(data["result"], 16)

    async def get_balance(self) -> int:
        """Get faucet balance."""
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(self.rpc_url, json={
                "jsonrpc": "2.0",
                "method": "eth_getBalance",
                "params": [self.account.address, "latest"],
                "id": 1
            }) as resp:
                data = await resp.json()
                return int(data["result"], 16)

    async def send_tokens(self, to_address: str) -> dict:
        """Send tokens to address."""
        import aiohttp

        # Get nonce
        nonce = await self.get_nonce()

        # Build transaction
        tx = {
            "nonce": nonce,
            "to": to_checksum_address(to_address),
            "value": self.amount_wei,
            "gas": 21000,
            "gasPrice": 1000000000,  # 1 Gwei
            "chainId": self.chain_id,
        }

        # Sign transaction
        signed = self.account.sign_transaction(tx)
        raw_tx = signed.raw_transaction.hex()
        if not raw_tx.startswith("0x"):
            raw_tx = "0x" + raw_tx

        # Send transaction
        async with aiohttp.ClientSession() as session:
            async with session.post(self.rpc_url, json={
                "jsonrpc": "2.0",
                "method": "eth_sendRawTransaction",
                "params": [raw_tx],
                "id": 1
            }) as resp:
                data = await resp.json()
                if "error" in data:
                    return {"success": False, "error": data["error"]["message"]}
                return {"success": True, "txHash": data["result"]}


async def index_handler(request):
    """Serve index.html with config injected."""
    faucet: Faucet = request.app["faucet"]

    index_path = os.path.join(STATIC_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Inject config
    html = html.replace("__RPC_URL__", request.app["rpc_url"])
    html = html.replace("__FAUCET_ADDRESS__", faucet.account.address)
    html = html.replace("__AMOUNT__", str(request.app["amount"]))
    html = html.replace("__COOLDOWN__", str(faucet.cooldown // 3600))  # hours

    return web.Response(text=html, content_type="text/html")


async def claim_handler(request):
    """Handle faucet claim."""
    faucet: Faucet = request.app["faucet"]

    try:
        data = await request.json()
        address = data.get("address", "").strip()

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

        # Check address limit (1 claim per address per cooldown)
        if addr_key in claim_history:
            elapsed = now - claim_history[addr_key]
            if elapsed < faucet.cooldown:
                remaining = int((faucet.cooldown - elapsed) / 3600)
                return web.json_response({
                    "success": False,
                    "error": f"Address already claimed. Try again in {remaining}h"
                })

        # Check IP limit (max 10 different wallets per IP per cooldown)
        if client_ip in ip_claims:
            # Filter out old claims
            ip_claims[client_ip] = [t for t in ip_claims[client_ip] if now - t < faucet.cooldown]
            if len(ip_claims[client_ip]) >= MAX_CLAIMS_PER_IP:
                return web.json_response({
                    "success": False,
                    "error": f"IP limit reached ({MAX_CLAIMS_PER_IP} wallets/day). Try again later."
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
            # Record claim by address
            claim_history[addr_key] = now
            # Record claim by IP (for counting)
            if client_ip not in ip_claims:
                ip_claims[client_ip] = []
            ip_claims[client_ip].append(now)

            return web.json_response({
                "success": True,
                "txHash": result["txHash"],
                "amount": request.app["amount"]
            })
        else:
            return web.json_response(result)

    except Exception as e:
        return web.json_response({"success": False, "error": str(e)})


async def status_handler(request):
    """Get faucet status."""
    faucet: Faucet = request.app["faucet"]

    balance = await faucet.get_balance()

    return web.json_response({
        "address": faucet.account.address,
        "balance": balance / 10**18,
        "amountPerClaim": request.app["amount"],
        "cooldownHours": faucet.cooldown // 3600,
    })


@click.command()
@click.option("--rpc", default="http://51.68.125.99:8546", help="RPC endpoint URL (default: Pyralis testnet)")
@click.option("--private-key", required=True, help="Faucet wallet private key")
@click.option("--amount", default=10.0, help="NPY amount per claim (default: 10)")
@click.option("--cooldown", default=24, help="Cooldown in hours between claims (default: 24)")
@click.option("--chain-id", default=77777, help="Chain ID (default: 77777 Pyralis)")
@click.option("--host", default="0.0.0.0", help="Server host")
@click.option("--port", default=8081, help="Server port")
def main(rpc: str, private_key: str, amount: float, cooldown: int, chain_id: int, host: str, port: int):
    """Start the NanoPy testnet faucet."""
    from rich.console import Console
    from rich.panel import Panel

    console = Console()

    # Create faucet
    faucet = Faucet(
        private_key=private_key,
        rpc_url=rpc,
        amount=amount,
        cooldown=cooldown * 3600,  # Convert to seconds
        chain_id=chain_id,
    )

    console.print(Panel(f"""
[bold cyan]NanoPy Faucet[/bold cyan]

[dim]Faucet Address:[/dim]  {faucet.account.address}
[dim]Amount/Claim:[/dim]    {amount} NPY
[dim]Cooldown:[/dim]        {cooldown} hours
[dim]RPC Node:[/dim]        {rpc}
[dim]Server:[/dim]          http://{host}:{port}

[dim]Press Ctrl+C to stop[/dim]
""", title="[bold green]Pyralis Testnet Faucet[/bold green]", border_style="green"))

    app = web.Application()
    app["faucet"] = faucet
    app["rpc_url"] = rpc
    app["amount"] = amount

    # Routes
    app.router.add_get("/", index_handler)
    app.router.add_post("/claim", claim_handler)
    app.router.add_get("/status", status_handler)
    app.router.add_static("/static", STATIC_DIR, name="static")

    web.run_app(app, host=host, port=port, print=None)


if __name__ == "__main__":
    main()
