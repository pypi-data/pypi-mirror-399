#!/usr/bin/env python3
"""
NanoPy Scan - Blockchain Indexer
Syncs blockchain data to SQLite database

Supports:
- WebSocket subscription (eth_subscribe newHeads) for real-time updates
- HTTP polling fallback when WebSocket is not available
"""

import asyncio
import aiohttp
import json
import time
from typing import Optional, Dict, Any, Callable
from .db import Database


class Indexer:
    """Indexes blockchain data from RPC to SQLite."""

    def __init__(self, db: Database, rpc_url: str):
        self.db = db
        self.rpc_url = rpc_url
        self._running = False
        self._session: Optional[aiohttp.ClientSession] = None
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._ws_connected = False
        self._on_new_block: Optional[Callable] = None  # Callback for new blocks

    @property
    def ws_url(self) -> str:
        """Convert HTTP URL to WebSocket URL (same port with aiohttp)."""
        return self.rpc_url.replace("http://", "ws://").replace("https://", "wss://")

    async def _rpc_call(self, method: str, params: list = None) -> Any:
        """Make an RPC call via HTTP."""
        if not self._session:
            self._session = aiohttp.ClientSession()

        try:
            async with self._session.post(self.rpc_url, json={
                "jsonrpc": "2.0",
                "method": method,
                "params": params or [],
                "id": 1
            }, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                data = await resp.json()
                if "error" in data:
                    print(f"RPC Error: {data['error']}")
                    return None
                return data.get("result")
        except Exception as e:
            print(f"RPC call failed: {e}")
            return None

    def _hex_to_int(self, hex_val: str) -> int:
        """Convert hex string to int."""
        if not hex_val or not hex_val.startswith("0x"):
            return 0
        return int(hex_val, 16)

    async def get_chain_id(self) -> int:
        """Get chain ID from node."""
        result = await self._rpc_call("eth_chainId")
        return self._hex_to_int(result) if result else 0

    async def get_block_number(self) -> int:
        """Get latest block number from node."""
        result = await self._rpc_call("eth_blockNumber")
        return self._hex_to_int(result) if result else 0

    async def get_block(self, number: int, with_txs: bool = True) -> Optional[Dict]:
        """Get block by number."""
        hex_num = hex(number)
        result = await self._rpc_call("eth_getBlockByNumber", [hex_num, with_txs])
        return result

    async def get_tx_receipt(self, tx_hash: str) -> Optional[Dict]:
        """Get transaction receipt."""
        return await self._rpc_call("eth_getTransactionReceipt", [tx_hash])

    async def get_balance(self, address: str) -> str:
        """Get address balance."""
        result = await self._rpc_call("eth_getBalance", [address, "latest"])
        if result:
            return str(self._hex_to_int(result))
        return "0"

    async def index_block(self, block_number: int) -> bool:
        """Index a single block and its transactions."""
        block_data = await self.get_block(block_number, with_txs=True)
        if not block_data:
            return False

        # Parse block
        block = {
            "number": self._hex_to_int(block_data.get("number", "0x0")),
            "hash": block_data.get("hash", ""),
            "parent_hash": block_data.get("parentHash", ""),
            "timestamp": self._hex_to_int(block_data.get("timestamp", "0x0")),
            "miner": block_data.get("miner", "").lower(),
            "gas_used": self._hex_to_int(block_data.get("gasUsed", "0x0")),
            "gas_limit": self._hex_to_int(block_data.get("gasLimit", "0x0")),
            "tx_count": len(block_data.get("transactions", [])),
            "size": self._hex_to_int(block_data.get("size", "0x0")),
            "extra_data": block_data.get("extraData", ""),
        }

        self.db.insert_block(block)

        # Index transactions
        transactions = block_data.get("transactions", [])
        for i, tx in enumerate(transactions):
            if isinstance(tx, str):
                # Transaction hash only, need to fetch full tx
                continue

            # Get receipt for gas used and status
            receipt = await self.get_tx_receipt(tx.get("hash", ""))
            gas_used = 0
            status = 1
            if receipt:
                gas_used = self._hex_to_int(receipt.get("gasUsed", "0x0"))
                status = self._hex_to_int(receipt.get("status", "0x1"))

            tx_data = {
                "hash": tx.get("hash", ""),
                "block_number": block["number"],
                "block_hash": block["hash"],
                "tx_index": i,
                "from_addr": tx.get("from", "").lower(),
                "to_addr": (tx.get("to") or "").lower(),
                "value": str(self._hex_to_int(tx.get("value", "0x0"))),
                "gas": self._hex_to_int(tx.get("gas", "0x0")),
                "gas_price": str(self._hex_to_int(tx.get("gasPrice", "0x0"))),
                "gas_used": gas_used,
                "nonce": self._hex_to_int(tx.get("nonce", "0x0")),
                "input_data": tx.get("input", "0x"),
                "status": status,
                "timestamp": block["timestamp"],
            }

            self.db.insert_transaction(tx_data)

            # Update address records
            if tx_data["from_addr"]:
                self.db.update_address(tx_data["from_addr"], tx_count=1, block_number=block["number"])
            if tx_data["to_addr"]:
                self.db.update_address(tx_data["to_addr"], tx_count=1, block_number=block["number"])

        # Notify callback if set
        if self._on_new_block:
            try:
                self._on_new_block(block)
            except Exception:
                pass

        return True

    async def sync(self, batch_size: int = 10):
        """Sync database with blockchain."""
        local_height = self.db.get_latest_block_number()
        chain_height = await self.get_block_number()

        if chain_height <= local_height:
            return 0

        synced = 0
        start_block = local_height + 1

        print(f"Syncing blocks {start_block} to {chain_height}...")

        for block_num in range(start_block, chain_height + 1):
            success = await self.index_block(block_num)
            if success:
                synced += 1
                if synced % 10 == 0:
                    print(f"Indexed block {block_num}/{chain_height}")
            else:
                print(f"Failed to index block {block_num}")
                break

        return synced

    # ========== WebSocket Support ==========

    async def _connect_websocket(self) -> bool:
        """Connect to WebSocket endpoint."""
        if not self._session:
            self._session = aiohttp.ClientSession()

        try:
            self._ws = await self._session.ws_connect(
                self.ws_url,
                timeout=aiohttp.ClientTimeout(total=10)
            )
            self._ws_connected = True
            print(f"WebSocket connected to {self.ws_url}")
            return True
        except Exception as e:
            print(f"WebSocket connection failed: {e}")
            self._ws_connected = False
            return False

    async def _subscribe_new_heads(self) -> Optional[str]:
        """Subscribe to newHeads via WebSocket."""
        if not self._ws or not self._ws_connected:
            return None

        try:
            await self._ws.send_json({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "eth_subscribe",
                "params": ["newHeads"]
            })

            # Wait for subscription confirmation
            msg = await asyncio.wait_for(self._ws.receive(), timeout=10)
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = json.loads(msg.data)
                if "result" in data:
                    sub_id = data["result"]
                    print(f"Subscribed to newHeads: {sub_id}")
                    return sub_id
                elif "error" in data:
                    print(f"Subscription error: {data['error']}")
        except Exception as e:
            print(f"Subscribe failed: {e}")

        return None

    async def _listen_websocket(self, max_idle: int = 120):
        """
        Listen for WebSocket messages (newHeads notifications).
        Returns after max_idle seconds without receiving a block.
        Default 120s = ~10 blocks at 12s block time.
        """
        last_block_time = time.time()

        while self._running and self._ws and not self._ws.closed:
            try:
                # Short timeout to allow checking idle time
                msg = await asyncio.wait_for(self._ws.receive(), timeout=5)

                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)

                    # Check if it's a subscription notification
                    if data.get("method") == "eth_subscription":
                        params = data.get("params", {})
                        result = params.get("result", {})

                        # New block header received
                        block_number = self._hex_to_int(result.get("number", "0x0"))
                        if block_number > 0:
                            last_block_time = time.time()
                            print(f"[WS] New block: {block_number}")
                            await self.index_block(block_number)

                            # Update stats
                            chain_id = await self.get_chain_id()
                            self.db.set_stat("chain_height", str(block_number))
                            self.db.set_stat("chain_id", str(chain_id))
                            self.db.set_stat("last_sync", str(int(time.time())))

                elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                    print("WebSocket closed or error")
                    self._ws_connected = False
                    break

            except asyncio.TimeoutError:
                # Check if idle too long (no blocks received)
                idle_time = time.time() - last_block_time
                if idle_time > max_idle:
                    print(f"WebSocket idle for {int(idle_time)}s, reconnecting...")
                    self._ws_connected = False
                    break

                # Send ping to keep connection alive
                if self._ws and not self._ws.closed:
                    try:
                        await self._ws.ping()
                    except Exception:
                        self._ws_connected = False
                        break
            except Exception as e:
                print(f"WebSocket error: {e}")
                self._ws_connected = False
                break

        # Clean up WebSocket
        if self._ws and not self._ws.closed:
            try:
                await self._ws.close()
            except:
                pass
        self._ws = None
        self._ws_connected = False

    async def run_websocket(self):
        """Run indexer with WebSocket subscription."""
        self._running = True
        print("Starting WebSocket indexer...")

        # Initial sync
        try:
            synced = await self.sync()
            if synced > 0:
                print(f"Initial sync: {synced} blocks")
        except Exception as e:
            print(f"Initial sync error: {e}")

        while self._running:
            # Connect WebSocket
            connected = await self._connect_websocket()

            if connected:
                # Subscribe to newHeads
                sub_id = await self._subscribe_new_heads()

                if sub_id:
                    # Listen for new blocks
                    await self._listen_websocket()
                else:
                    print("Failed to subscribe, falling back to polling")

            # If WebSocket fails, wait before retry
            if self._running:
                print("WebSocket disconnected, reconnecting in 5s...")
                await asyncio.sleep(5)

    async def run_continuous(self, poll_interval: int = 3, use_websocket: bool = True):
        """
        Run continuous indexing with WebSocket auto-reconnect.

        Args:
            poll_interval: Seconds between polls (used as fallback)
            use_websocket: Try WebSocket first, fallback to polling
        """
        self._running = True
        ws_retry_interval = 30  # Retry WebSocket every 30s if disconnected
        last_ws_attempt = 0

        # Initial sync and stats update
        try:
            synced = await self.sync()
            if synced > 0:
                print(f"Initial sync: {synced} blocks")

            # Update stats
            chain_height = await self.get_block_number()
            chain_id = await self.get_chain_id()
            self.db.set_stat("chain_height", str(chain_height))
            self.db.set_stat("chain_id", str(chain_id))
            self.db.set_stat("last_sync", str(int(time.time())))
        except Exception as e:
            print(f"Initial sync error: {e}")

        print(f"Starting indexer (WebSocket + HTTP fallback)...")

        while self._running:
            current_time = time.time()

            # Try WebSocket if enabled and not connected
            if use_websocket and not self._ws_connected:
                if current_time - last_ws_attempt >= ws_retry_interval:
                    last_ws_attempt = current_time
                    try:
                        connected = await self._connect_websocket()
                        if connected:
                            sub_id = await self._subscribe_new_heads()
                            if sub_id:
                                print("WebSocket connected - real-time mode")
                                # Listen until disconnected (non-blocking with timeout)
                                await self._listen_websocket()
                                print("WebSocket disconnected, will retry...")
                    except Exception as e:
                        print(f"WebSocket error: {e}")
                        self._ws_connected = False

            # Always do HTTP polling as backup (catches missed blocks)
            try:
                synced = await self.sync()
                if synced > 0:
                    print(f"[HTTP] Synced {synced} blocks")

                # Update stats
                chain_height = await self.get_block_number()
                chain_id = await self.get_chain_id()
                self.db.set_stat("chain_height", str(chain_height))
                self.db.set_stat("chain_id", str(chain_id))
                self.db.set_stat("last_sync", str(int(time.time())))

            except Exception as e:
                print(f"HTTP sync error: {e}")

            await asyncio.sleep(poll_interval)

    def stop(self):
        """Stop the indexer."""
        self._running = False

    async def close(self):
        """Close resources."""
        self.stop()
        if self._ws and not self._ws.closed:
            await self._ws.close()
            self._ws = None
        if self._session:
            await self._session.close()
            self._session = None
