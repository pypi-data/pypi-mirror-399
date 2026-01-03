#!/usr/bin/env python3
"""
NanoPy Scan - Multi-Network Blockchain Explorer with SQLite indexing
"""

import click
import asyncio
import os
import json
import time
import webbrowser
from aiohttp import web
from typing import Optional, Dict

from .db import Database
from .indexer import Indexer
from .networks import get_network_name, get_network_by_alias, NETWORKS, NETWORK_ALIASES, Network

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# Multi-network instances
networks_config: Dict[str, dict] = {}  # network_id -> {db, indexer, rpc_url, config}
current_network: str = "testnet"


def get_db(network_id: str = None) -> Database:
    """Get database for network."""
    net_id = network_id or current_network
    return networks_config.get(net_id, {}).get("db")


def get_indexer(network_id: str = None) -> Indexer:
    """Get indexer for network."""
    net_id = network_id or current_network
    return networks_config.get(net_id, {}).get("indexer")


def get_rpc_url(network_id: str = None) -> str:
    """Get RPC URL for network."""
    net_id = network_id or current_network
    return networks_config.get(net_id, {}).get("rpc_url", "")


def json_response(data, status=200):
    """Create JSON response with CORS headers."""
    return web.json_response(data, status=status, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    })


def get_network_from_request(request) -> str:
    """Get network ID from request query param."""
    return request.query.get("network", current_network)


# ============= API Endpoints =============

async def api_networks(request):
    """Get available networks."""
    result = {}
    for net_id, net_data in networks_config.items():
        config = net_data["config"]
        db = net_data["db"]
        result[net_id] = {
            "chainId": config.chain_id,
            "name": config.name,
            "symbol": config.symbol,
            "rpc": config.rpc,
            "isL2": config.is_l2,
            "indexedBlocks": db.get_total_blocks() if db else 0,
        }
    return json_response(result)


async def api_status(request):
    """Get indexer and network status."""
    network_id = get_network_from_request(request)
    db = get_db(network_id)
    rpc_url = get_rpc_url(network_id)

    if not db:
        return json_response({"error": "Network not configured"}, status=400)

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
        "networkId": network_id,
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
    network_id = get_network_from_request(request)
    db = get_db(network_id)

    if not db:
        return json_response({"error": "Network not configured"}, status=400)

    validators = db.get_validators(10)
    recent_blocks = db.get_blocks(limit=20)
    avg_block_time = 12.0
    if len(recent_blocks) >= 2:
        time_diff = recent_blocks[0]["timestamp"] - recent_blocks[-1]["timestamp"]
        if time_diff > 0:
            avg_block_time = time_diff / (len(recent_blocks) - 1)

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
    network_id = get_network_from_request(request)
    db = get_db(network_id)

    if not db:
        return json_response({"error": "Network not configured"}, status=400)

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
    network_id = get_network_from_request(request)
    db = get_db(network_id)

    if not db:
        return json_response({"error": "Network not configured"}, status=400)

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

    transactions = db.get_block_transactions(block["number"])

    return json_response({
        "block": block,
        "transactions": transactions,
    })


async def api_transactions(request):
    """Get transactions with pagination."""
    network_id = get_network_from_request(request)
    db = get_db(network_id)

    if not db:
        return json_response({"error": "Network not configured"}, status=400)

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
    network_id = get_network_from_request(request)
    db = get_db(network_id)

    if not db:
        return json_response({"error": "Network not configured"}, status=400)

    tx_hash = request.match_info.get("hash", "")
    tx = db.get_transaction(tx_hash)

    if not tx:
        return json_response({"error": "Transaction not found"}, status=404)

    return json_response({"transaction": tx})


async def api_address(request):
    """Get address info and transactions."""
    network_id = get_network_from_request(request)
    db = get_db(network_id)
    indexer = get_indexer(network_id)

    if not db:
        return json_response({"error": "Network not configured"}, status=400)

    address = request.match_info.get("address", "")
    page = int(request.query.get("page", 1))
    limit = min(int(request.query.get("limit", 25)), 100)
    offset = (page - 1) * limit

    balance = "0"
    if indexer:
        try:
            balance = await indexer.get_balance(address)
        except:
            pass

    transactions = db.get_address_transactions(address, limit=limit, offset=offset)
    total = db.get_address_tx_count(address)
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
    network_id = get_network_from_request(request)
    db = get_db(network_id)

    if not db:
        return json_response({"error": "Network not configured"}, status=400)

    query = request.query.get("q", "").strip()
    if not query:
        return json_response({"error": "Query required"}, status=400)

    result = db.search(query)
    return json_response(result)


async def api_validators(request):
    """Get validators list."""
    network_id = get_network_from_request(request)
    db = get_db(network_id)

    if not db:
        return json_response({"error": "Network not configured"}, status=400)

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


async def api_network_status(request):
    """Get network status including node health."""
    network_id = get_network_from_request(request)
    db = get_db(network_id)
    indexer = get_indexer(network_id)
    rpc_url = get_rpc_url(network_id)

    if not db:
        return json_response({"error": "Network not configured"}, status=400)

    chain_id = 0
    chain_height = 0
    peer_count = 0
    gas_price = 0
    node_online = False
    last_block_time = 0

    if indexer:
        try:
            chain_id = await indexer.get_chain_id()
            chain_height = await indexer.get_block_number()
            node_online = chain_height > 0

            peer_result = await indexer._rpc_call("net_peerCount")
            if peer_result:
                peer_count = int(peer_result, 16) if peer_result.startswith("0x") else 0

            gas_result = await indexer._rpc_call("eth_gasPrice")
            if gas_result:
                gas_price = int(gas_result, 16) if gas_result.startswith("0x") else 0

        except Exception:
            node_online = False

    recent_blocks = db.get_blocks(limit=1)
    if recent_blocks:
        last_block_time = recent_blocks[0].get("timestamp", 0)

    now = int(time.time())
    seconds_since_block = now - last_block_time if last_block_time > 0 else 0
    network_healthy = node_online and seconds_since_block < 120

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

async def start_indexers(app):
    """Start indexers for all networks."""
    for net_id, net_data in networks_config.items():
        indexer = net_data.get("indexer")
        if indexer:
            task = asyncio.create_task(
                indexer.run_continuous(poll_interval=3, use_websocket=True)
            )
            app[f"indexer_task_{net_id}"] = task
            print(f"Started indexer for {net_id}")


async def stop_indexers(app):
    """Stop all indexers."""
    for net_id, net_data in networks_config.items():
        indexer = net_data.get("indexer")
        if indexer:
            indexer.stop()
            await indexer.close()

        task_key = f"indexer_task_{net_id}"
        if task_key in app:
            app[task_key].cancel()
            try:
                await app[task_key]
            except asyncio.CancelledError:
                pass


# ============= Main =============

@click.command()
@click.option("--host", default="0.0.0.0", help="Server host")
@click.option("--port", default=8080, help="Server port")
@click.option("--no-browser", is_flag=True, help="Don't open browser")
@click.option("--reset", is_flag=True, help="Delete existing databases and resync")
def main(host: str, port: int, no_browser: bool, reset: bool):
    """Start the NanoPy multi-network blockchain explorer."""
    global networks_config, current_network

    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()

    # Configure networks to index (testnet L1 + turbo L2 testnet)
    networks_to_index = ["testnet", "turbo-testnet"]

    for net_alias in networks_to_index:
        net = get_network_by_alias(net_alias)
        if not net:
            continue

        db_path = net.db
        if reset and os.path.exists(db_path):
            os.remove(db_path)
            console.print(f"[yellow]Database {db_path} deleted[/yellow]")

        db = Database(db_path)
        indexer = Indexer(db, net.rpc)

        networks_config[net_alias] = {
            "db": db,
            "indexer": indexer,
            "rpc_url": net.rpc,
            "config": net,
        }

    current_network = "testnet"

    # Display info
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Network")
    table.add_column("Chain ID")
    table.add_column("RPC")
    table.add_column("Database")

    for net_id, net_data in networks_config.items():
        config = net_data["config"]
        table.add_row(
            config.name,
            str(config.chain_id),
            config.rpc,
            config.db,
        )

    console.print(Panel(f"""
[bold cyan]NanoPy Scan - Multi-Network Explorer[/bold cyan]

[dim]Explorer:[/dim]    http://{host}:{port}
[dim]Networks:[/dim]    {len(networks_config)} configured

[dim]API Endpoints:[/dim]
  /api/networks         - List available networks
  /api/status?network=  - Network status
  /api/blocks?network=  - List blocks
  /api/transactions     - List transactions
  /api/address/:addr    - Address info

[dim]Press Ctrl+C to stop[/dim]
""", title="[bold green]Blockchain Explorer[/bold green]", border_style="green"))

    console.print(table)

    if not no_browser:
        webbrowser.open(f"http://{host}:{port}")

    app = web.Application()

    # API routes
    app.router.add_get("/api/networks", api_networks)
    app.router.add_get("/api/status", api_status)
    app.router.add_get("/api/stats", api_stats)
    app.router.add_get("/api/blocks", api_blocks)
    app.router.add_get("/api/block/{id}", api_block)
    app.router.add_get("/api/transactions", api_transactions)
    app.router.add_get("/api/tx/{hash}", api_transaction)
    app.router.add_get("/api/address/{address}", api_address)
    app.router.add_get("/api/search", api_search)
    app.router.add_get("/api/validators", api_validators)
    app.router.add_get("/api/network", api_network_status)

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

    # Background indexers
    app.on_startup.append(start_indexers)
    app.on_cleanup.append(stop_indexers)

    web.run_app(app, host=host, port=port, print=None)


if __name__ == "__main__":
    main()
