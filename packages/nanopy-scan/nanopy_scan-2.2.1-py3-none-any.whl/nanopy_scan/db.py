#!/usr/bin/env python3
"""
NanoPy Scan - SQLite Database for blockchain indexing
"""

import sqlite3
import os
import threading
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class Database:
    """SQLite database for blockchain indexing."""

    def __init__(self, db_path: str = "nanopy_scan.db"):
        self.db_path = db_path
        self._local = threading.local()
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        """Get thread-local connection."""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    @contextmanager
    def _cursor(self):
        """Context manager for cursor."""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def _init_db(self):
        """Initialize database schema."""
        with self._cursor() as cursor:
            # Blocks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS blocks (
                    number INTEGER PRIMARY KEY,
                    hash TEXT UNIQUE NOT NULL,
                    parent_hash TEXT,
                    timestamp INTEGER NOT NULL,
                    miner TEXT,
                    gas_used INTEGER DEFAULT 0,
                    gas_limit INTEGER DEFAULT 0,
                    tx_count INTEGER DEFAULT 0,
                    size INTEGER DEFAULT 0,
                    extra_data TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    hash TEXT PRIMARY KEY,
                    block_number INTEGER NOT NULL,
                    block_hash TEXT,
                    tx_index INTEGER,
                    from_addr TEXT NOT NULL,
                    to_addr TEXT,
                    value TEXT DEFAULT '0',
                    gas INTEGER DEFAULT 0,
                    gas_price TEXT DEFAULT '0',
                    gas_used INTEGER DEFAULT 0,
                    nonce INTEGER,
                    input_data TEXT,
                    status INTEGER DEFAULT 1,
                    timestamp INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (block_number) REFERENCES blocks(number)
                )
            """)

            # Addresses table (for caching balances)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS addresses (
                    address TEXT PRIMARY KEY,
                    balance TEXT DEFAULT '0',
                    tx_count INTEGER DEFAULT 0,
                    first_seen INTEGER,
                    last_seen INTEGER,
                    is_contract INTEGER DEFAULT 0,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Stats table (for network statistics)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stats (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_blocks_timestamp ON blocks(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_blocks_miner ON blocks(miner)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_block ON transactions(block_number)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_from ON transactions(from_addr)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_to ON transactions(to_addr)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_timestamp ON transactions(timestamp)")

    def get_latest_block_number(self) -> int:
        """Get the latest indexed block number."""
        with self._cursor() as cursor:
            cursor.execute("SELECT MAX(number) FROM blocks")
            result = cursor.fetchone()[0]
            return result if result is not None else -1

    def insert_block(self, block: Dict[str, Any]) -> bool:
        """Insert a block into the database."""
        with self._cursor() as cursor:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO blocks
                    (number, hash, parent_hash, timestamp, miner, gas_used, gas_limit, tx_count, size, extra_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    block['number'],
                    block['hash'],
                    block.get('parent_hash', ''),
                    block['timestamp'],
                    block.get('miner', ''),
                    block.get('gas_used', 0),
                    block.get('gas_limit', 0),
                    block.get('tx_count', 0),
                    block.get('size', 0),
                    block.get('extra_data', ''),
                ))
                return True
            except Exception as e:
                print(f"Error inserting block: {e}")
                return False

    def insert_transaction(self, tx: Dict[str, Any]) -> bool:
        """Insert a transaction into the database."""
        with self._cursor() as cursor:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO transactions
                    (hash, block_number, block_hash, tx_index, from_addr, to_addr, value, gas, gas_price, gas_used, nonce, input_data, status, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tx['hash'],
                    tx['block_number'],
                    tx.get('block_hash', ''),
                    tx.get('tx_index', 0),
                    tx.get('from_addr', ''),
                    tx.get('to_addr', ''),
                    str(tx.get('value', '0')),
                    tx.get('gas', 0),
                    str(tx.get('gas_price', '0')),
                    tx.get('gas_used', 0),
                    tx.get('nonce', 0),
                    tx.get('input_data', ''),
                    tx.get('status', 1),
                    tx.get('timestamp', 0),
                ))
                return True
            except Exception as e:
                print(f"Error inserting transaction: {e}")
                return False

    def update_address(self, address: str, balance: str = None, tx_count: int = None,
                       is_contract: bool = False, block_number: int = None):
        """Update or insert address info."""
        with self._cursor() as cursor:
            # Check if exists
            cursor.execute("SELECT * FROM addresses WHERE address = ?", (address.lower(),))
            existing = cursor.fetchone()

            if existing:
                updates = []
                params = []
                if balance is not None:
                    updates.append("balance = ?")
                    params.append(balance)
                if tx_count is not None:
                    updates.append("tx_count = tx_count + ?")
                    params.append(tx_count)
                if block_number is not None:
                    updates.append("last_seen = ?")
                    params.append(block_number)
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(address.lower())

                cursor.execute(f"UPDATE addresses SET {', '.join(updates)} WHERE address = ?", params)
            else:
                cursor.execute("""
                    INSERT INTO addresses (address, balance, tx_count, first_seen, last_seen, is_contract)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (address.lower(), balance or '0', tx_count or 1, block_number, block_number, int(is_contract)))

    def set_stat(self, key: str, value: str):
        """Set a statistics value."""
        with self._cursor() as cursor:
            cursor.execute("""
                INSERT OR REPLACE INTO stats (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value))

    def get_stat(self, key: str) -> Optional[str]:
        """Get a statistics value."""
        with self._cursor() as cursor:
            cursor.execute("SELECT value FROM stats WHERE key = ?", (key,))
            result = cursor.fetchone()
            return result[0] if result else None

    def get_block(self, number: int) -> Optional[Dict]:
        """Get block by number."""
        with self._cursor() as cursor:
            cursor.execute("SELECT * FROM blocks WHERE number = ?", (number,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_block_by_hash(self, hash: str) -> Optional[Dict]:
        """Get block by hash."""
        with self._cursor() as cursor:
            cursor.execute("SELECT * FROM blocks WHERE hash = ?", (hash,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_blocks(self, limit: int = 25, offset: int = 0) -> List[Dict]:
        """Get blocks with pagination (newest first)."""
        with self._cursor() as cursor:
            cursor.execute("""
                SELECT * FROM blocks ORDER BY number DESC LIMIT ? OFFSET ?
            """, (limit, offset))
            return [dict(row) for row in cursor.fetchall()]

    def get_transaction(self, hash: str) -> Optional[Dict]:
        """Get transaction by hash."""
        with self._cursor() as cursor:
            cursor.execute("SELECT * FROM transactions WHERE hash = ?", (hash,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_transactions(self, limit: int = 25, offset: int = 0) -> List[Dict]:
        """Get transactions with pagination (newest first)."""
        with self._cursor() as cursor:
            cursor.execute("""
                SELECT * FROM transactions ORDER BY block_number DESC, tx_index DESC LIMIT ? OFFSET ?
            """, (limit, offset))
            return [dict(row) for row in cursor.fetchall()]

    def get_block_transactions(self, block_number: int) -> List[Dict]:
        """Get all transactions in a block."""
        with self._cursor() as cursor:
            cursor.execute("""
                SELECT * FROM transactions WHERE block_number = ? ORDER BY tx_index
            """, (block_number,))
            return [dict(row) for row in cursor.fetchall()]

    def get_address_transactions(self, address: str, limit: int = 25, offset: int = 0) -> List[Dict]:
        """Get transactions for an address."""
        addr_lower = address.lower()
        with self._cursor() as cursor:
            cursor.execute("""
                SELECT * FROM transactions
                WHERE from_addr = ? OR to_addr = ?
                ORDER BY block_number DESC, tx_index DESC
                LIMIT ? OFFSET ?
            """, (addr_lower, addr_lower, limit, offset))
            return [dict(row) for row in cursor.fetchall()]

    def get_address_tx_count(self, address: str) -> int:
        """Get transaction count for an address."""
        addr_lower = address.lower()
        with self._cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM transactions WHERE from_addr = ? OR to_addr = ?
            """, (addr_lower, addr_lower))
            return cursor.fetchone()[0]

    def get_address(self, address: str) -> Optional[Dict]:
        """Get address info."""
        with self._cursor() as cursor:
            cursor.execute("SELECT * FROM addresses WHERE address = ?", (address.lower(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_total_blocks(self) -> int:
        """Get total number of indexed blocks."""
        with self._cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM blocks")
            return cursor.fetchone()[0]

    def get_total_transactions(self) -> int:
        """Get total number of indexed transactions."""
        with self._cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM transactions")
            return cursor.fetchone()[0]

    def get_total_addresses(self) -> int:
        """Get total number of unique addresses."""
        with self._cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM addresses")
            return cursor.fetchone()[0]

    def get_recent_tps(self, seconds: int = 60) -> float:
        """Calculate transactions per second over recent period."""
        with self._cursor() as cursor:
            # Get latest block timestamp
            cursor.execute("SELECT MAX(timestamp) FROM blocks")
            latest = cursor.fetchone()[0]
            if not latest:
                return 0.0

            # Count transactions in time window
            cursor.execute("""
                SELECT COUNT(*) FROM transactions WHERE timestamp > ?
            """, (latest - seconds,))
            tx_count = cursor.fetchone()[0]
            return tx_count / seconds if seconds > 0 else 0.0

    def get_validators(self, limit: int = 10) -> List[Dict]:
        """Get top block producers (validators/miners)."""
        with self._cursor() as cursor:
            cursor.execute("""
                SELECT miner, COUNT(*) as block_count, MAX(timestamp) as last_block
                FROM blocks
                WHERE miner IS NOT NULL AND miner != '' AND miner != '0x0000000000000000000000000000000000000000'
                GROUP BY miner
                ORDER BY block_count DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def search(self, query: str) -> Dict[str, Any]:
        """Search for block, transaction, or address."""
        result = {"type": None, "data": None}

        # Clean query
        query = query.strip()

        # Check if it's a block number
        if query.isdigit():
            block = self.get_block(int(query))
            if block:
                result["type"] = "block"
                result["data"] = block
                return result

        # Check if it's a hash (66 chars with 0x prefix)
        if query.startswith("0x") and len(query) == 66:
            # Try transaction first
            tx = self.get_transaction(query)
            if tx:
                result["type"] = "transaction"
                result["data"] = tx
                return result

            # Try block hash
            block = self.get_block_by_hash(query)
            if block:
                result["type"] = "block"
                result["data"] = block
                return result

        # Check if it's an address (42 chars with 0x prefix)
        if query.startswith("0x") and len(query) == 42:
            result["type"] = "address"
            result["data"] = {"address": query}
            return result

        return result

    def close(self):
        """Close database connection."""
        if hasattr(self._local, 'conn') and self._local.conn:
            self._local.conn.close()
            self._local.conn = None
