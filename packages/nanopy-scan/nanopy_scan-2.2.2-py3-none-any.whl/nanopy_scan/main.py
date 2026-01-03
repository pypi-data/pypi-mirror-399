#!/usr/bin/env python3
"""
NanoPy Scan - Blockchain Explorer with SQLite indexing
"""

import click
import asyncio
import os
import json
import webbrowser
from aiohttp import web
from typing import Optional

from .db import Database
from .indexer import Indexer
from .networks import get_network_name, get_network_by_alias, NETWORKS, NETWORK_ALIASES

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# Global instances
db: Optional[Database] = None
indexer: Optional[Indexer] = None
rpc_url: str = ""


def json_response(data, status=200):
    """Create JSON response with CORS headers."""
    return web.json_response(data, status=status, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    })


# ============= API Endpoints =============

async def api_status(request):
    """Get indexer and network status."""
    global db, rpc_url

    chain_id = db.get_stat("chain_id") or "0"
    chain_height = db.get_stat("chain_height") or "0"
    last_sync = db.get_stat("last_sync") or "0"

    indexed_blocks = db.get_total_blocks()
    indexed_txs = db.get_total_transactions()
    total_addresses = db.get_total_addresses()
    tps = db.get_recent_tps(60)

    chain_id_int = int(chain_id)
    network_name = get_network_name(chain_id_int)

    return json_response({
        "chainId": chain_id_int,
        "networkName": network_name,
        "chainHeight": int(chain_height),
        "indexedBlocks": indexed_blocks,
        "indexedTransactions": indexed_txs,
        "totalAddresses": total_addresses,
        "tps": round(tps, 4),
        "lastSync": int(last_sync),
        "rpcUrl": rpc_url,
    })


async def api_stats(request):
    """Get network statistics for dashboard."""
    global db

    # Get validators (top block producers)
    validators = db.get_validators(10)

    # Get recent blocks for average block time
    recent_blocks = db.get_blocks(limit=20)
    avg_block_time = 12.0  # Default
    if len(recent_blocks) >= 2:
        time_diff = recent_blocks[0]["timestamp"] - recent_blocks[-1]["timestamp"]
        if time_diff > 0:
            avg_block_time = time_diff / (len(recent_blocks) - 1)

    # Calculate 24h stats
    total_txs = db.get_total_transactions()
    total_blocks = db.get_total_blocks()

    return json_response({
        "validators": [
            {
                "address": v["miner"],
                "blockCount": v["block_count"],
                "lastBlock": v["last_block"],
            }
            for v in validators
        ],
        "avgBlockTime": round(avg_block_time, 2),
        "totalBlocks": total_blocks,
        "totalTransactions": total_txs,
        "tps": round(db.get_recent_tps(60), 4),
    })


async def api_blocks(request):
    """Get blocks with pagination."""
    global db

    page = int(request.query.get("page", 1))
    limit = min(int(request.query.get("limit", 25)), 100)
    offset = (page - 1) * limit

    blocks = db.get_blocks(limit=limit, offset=offset)
    total = db.get_total_blocks()

    return json_response({
        "blocks": blocks,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
    })


async def api_block(request):
    """Get single block by number or hash."""
    global db

    block_id = request.match_info.get("id", "")

    if block_id.startswith("0x"):
        block = db.get_block_by_hash(block_id)
    else:
        try:
            block = db.get_block(int(block_id))
        except ValueError:
            return json_response({"error": "Invalid block identifier"}, status=400)

    if not block:
        return json_response({"error": "Block not found"}, status=404)

    # Get transactions for this block
    transactions = db.get_block_transactions(block["number"])

    return json_response({
        "block": block,
        "transactions": transactions,
    })


async def api_transactions(request):
    """Get transactions with pagination."""
    global db

    page = int(request.query.get("page", 1))
    limit = min(int(request.query.get("limit", 25)), 100)
    offset = (page - 1) * limit

    transactions = db.get_transactions(limit=limit, offset=offset)
    total = db.get_total_transactions()

    return json_response({
        "transactions": transactions,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
    })


async def api_transaction(request):
    """Get single transaction by hash."""
    global db

    tx_hash = request.match_info.get("hash", "")
    tx = db.get_transaction(tx_hash)

    if not tx:
        return json_response({"error": "Transaction not found"}, status=404)

    return json_response({"transaction": tx})


async def api_address(request):
    """Get address info and transactions."""
    global db, indexer

    address = request.match_info.get("address", "")
    page = int(request.query.get("page", 1))
    limit = min(int(request.query.get("limit", 25)), 100)
    offset = (page - 1) * limit

    # Get balance from RPC
    balance = "0"
    if indexer:
        try:
            balance = await indexer.get_balance(address)
        except:
            pass

    # Get transactions
    transactions = db.get_address_transactions(address, limit=limit, offset=offset)
    total = db.get_address_tx_count(address)

    # Get address info from DB
    addr_info = db.get_address(address)

    return json_response({
        "address": address,
        "balance": balance,
        "transactionCount": total,
        "firstSeen": addr_info["first_seen"] if addr_info else None,
        "lastSeen": addr_info["last_seen"] if addr_info else None,
        "transactions": transactions,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit if total > 0 else 1,
    })


async def api_search(request):
    """Search for block, transaction, or address."""
    global db

    query = request.query.get("q", "").strip()
    if not query:
        return json_response({"error": "Query required"}, status=400)

    result = db.search(query)
    return json_response(result)


async def api_validators(request):
    """Get validators list."""
    global db

    limit = min(int(request.query.get("limit", 50)), 100)
    validators = db.get_validators(limit)

    return json_response({
        "validators": [
            {
                "address": v["miner"],
                "blockCount": v["block_count"],
                "lastBlock": v["last_block"],
            }
            for v in validators
        ]
    })


async def api_network(request):
    """Get network status including node health."""
    global db, indexer, rpc_url
    import time

    # Get chain info from indexer
    chain_id = 0
    chain_height = 0
    peer_count = 0
    gas_price = 0
    node_online = False
    last_block_time = 0

    if indexer:
        try:
            # Check node connectivity
            chain_id = await indexer.get_chain_id()
            chain_height = await indexer.get_block_number()
            node_online = chain_height > 0

            # Get peer count
            peer_result = await indexer._rpc_call("net_peerCount")
            if peer_result:
                peer_count = int(peer_result, 16) if peer_result.startswith("0x") else 0

            # Get gas price
            gas_result = await indexer._rpc_call("eth_gasPrice")
            if gas_result:
                gas_price = int(gas_result, 16) if gas_result.startswith("0x") else 0

        except Exception as e:
            node_online = False

    # Get latest block timestamp from DB
    recent_blocks = db.get_blocks(limit=1)
    if recent_blocks:
        last_block_time = recent_blocks[0].get("timestamp", 0)

    # Calculate time since last block
    now = int(time.time())
    seconds_since_block = now - last_block_time if last_block_time > 0 else 0

    # Determine network health
    # If last block > 120 seconds ago, network might be stalled (12s block time)
    network_healthy = node_online and seconds_since_block < 120

    # Get indexed stats
    indexed_blocks = db.get_total_blocks()
    last_sync = db.get_stat("last_sync") or "0"

    network_name = get_network_name(chain_id)

    return json_response({
        "node": {
            "url": rpc_url,
            "online": node_online,
            "chainId": chain_id,
            "networkName": network_name,
            "blockHeight": chain_height,
            "peerCount": peer_count,
            "gasPrice": gas_price,
            "gasPriceGwei": round(gas_price / 1e9, 2),
        },
        "indexer": {
            "indexedBlocks": indexed_blocks,
            "lastSync": int(last_sync),
            "syncedWith": chain_height,
            "isSynced": indexed_blocks >= chain_height if chain_height > 0 else False,
        },
        "network": {
            "healthy": network_healthy,
            "lastBlockTime": last_block_time,
            "secondsSinceBlock": seconds_since_block,
            "tps": round(db.get_recent_tps(60), 4),
        }
    })


# ============= Static Files =============

async def index_handler(request):
    """Serve index.html."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()
    return web.Response(text=html, content_type="text/html")


async def serve_static(request):
    """Serve static files."""
    filename = request.match_info.get("filename", "")
    filepath = os.path.join(STATIC_DIR, filename)

    if not os.path.exists(filepath):
        return web.Response(text="Not found", status=404)

    content_type = "text/plain"
    if filename.endswith(".css"):
        content_type = "text/css"
    elif filename.endswith(".js"):
        content_type = "application/javascript"
    elif filename.endswith(".html"):
        content_type = "text/html"

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    return web.Response(text=content, content_type=content_type)


# ============= Background Tasks =============

async def start_indexer(app):
    """Start the indexer as a background task."""
    global indexer
    if indexer:
        # Try WebSocket first, fallback to polling
        app["indexer_task"] = asyncio.create_task(
            indexer.run_continuous(poll_interval=3, use_websocket=True)
        )


async def stop_indexer(app):
    """Stop the indexer."""
    global indexer
    if indexer:
        indexer.stop()
        await indexer.close()

    if "indexer_task" in app:
        app["indexer_task"].cancel()
        try:
            await app["indexer_task"]
        except asyncio.CancelledError:
            pass


# ============= Main =============

@click.command()
@click.option("--rpc", default=None, help="RPC endpoint URL (overrides --network)")
@click.option("--network", "-n", default="mainnet", help=f"Network: {', '.join(NETWORK_ALIASES.keys())}")
@click.option("--host", default="127.0.0.1", help="Server host")
@click.option("--port", default=8080, help="Server port")
@click.option("--db-path", default=None, help="SQLite database path")
@click.option("--no-browser", is_flag=True, help="Don't open browser")
@click.option("--reset", is_flag=True, help="Delete existing database and resync from scratch")
def main(rpc: str, network: str, host: str, port: int, db_path: str, no_browser: bool, reset: bool):
    """Start the NanoPy blockchain explorer."""
    global db, indexer, rpc_url

    from rich.console import Console
    from rich.panel import Panel

    console = Console()

    # Get network config
    net = get_network_by_alias(network)
    if not net:
        console.print(f"[red]Unknown network: {network}[/red]")
        console.print(f"[dim]Available: {', '.join(NETWORK_ALIASES.keys())}[/dim]")
        return

    # Use network defaults, allow overrides
    rpc = rpc or net.rpc
    db_path = db_path or net.db

    rpc_url = rpc

    # Reset database if requested
    if reset and os.path.exists(db_path):
        os.remove(db_path)
        console.print(f"[yellow]Database {db_path} deleted[/yellow]")

    # Initialize database
    db = Database(db_path)
    indexer = Indexer(db, rpc)

    console.print(Panel(f"""
[bold cyan]NanoPy Scan[/bold cyan]

[dim]Explorer:[/dim]    http://{host}:{port}
[dim]RPC Node:[/dim]    {rpc}
[dim]WebSocket:[/dim]   {rpc.replace('http://', 'ws://').replace('https://', 'wss://')}
[dim]Database:[/dim]    {db_path}
[dim]Sync Mode:[/dim]   WebSocket (real-time) with HTTP fallback

[dim]API Endpoints:[/dim]
  /api/status         - Network status
  /api/blocks         - List blocks
  /api/transactions   - List transactions
  /api/address/:addr  - Address info
  /api/validators     - Validators list

[dim]Press Ctrl+C to stop[/dim]
""", title="[bold green]Blockchain Explorer[/bold green]", border_style="green"))

    # Open browser
    if not no_browser:
        webbrowser.open(f"http://{host}:{port}")

    # Create app
    app = web.Application()

    # API routes
    app.router.add_get("/api/status", api_status)
    app.router.add_get("/api/stats", api_stats)
    app.router.add_get("/api/blocks", api_blocks)
    app.router.add_get("/api/block/{id}", api_block)
    app.router.add_get("/api/transactions", api_transactions)
    app.router.add_get("/api/tx/{hash}", api_transaction)
    app.router.add_get("/api/address/{address}", api_address)
    app.router.add_get("/api/search", api_search)
    app.router.add_get("/api/validators", api_validators)
    app.router.add_get("/api/network", api_network)

    # Static routes
    app.router.add_get("/", index_handler)
    app.router.add_get("/block/{id}", index_handler)
    app.router.add_get("/tx/{hash}", index_handler)
    app.router.add_get("/address/{address}", index_handler)
    app.router.add_get("/blocks", index_handler)
    app.router.add_get("/transactions", index_handler)
    app.router.add_get("/validators", index_handler)
    app.router.add_get("/network", index_handler)
    app.router.add_get("/static/{filename}", serve_static)

    # Background indexer
    app.on_startup.append(start_indexer)
    app.on_cleanup.append(stop_indexer)

    # Run
    web.run_app(app, host=host, port=port, print=None)


if __name__ == "__main__":
    main()
