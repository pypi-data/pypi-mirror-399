"""
NanoPy Network Configurations
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Network:
    """Network configuration."""
    chain_id: int
    name: str
    rpc: str
    db: str
    symbol: str = "NPY"
    explorer: Optional[str] = None
    is_l2: bool = False
    l1_chain_id: Optional[int] = None


# All supported networks
NETWORKS: Dict[int, Network] = {
    # L1 Networks
    7770: Network(
        chain_id=7770,
        name="NanoPy Mainnet",
        rpc="http://51.68.125.99:8545",
        db="nanopy_scan.db",
        symbol="NPY",
    ),
    77700: Network(
        chain_id=77700,
        name="NanoPy Testnet",
        rpc="http://51.68.125.99:8546",
        db="testnet_scan.db",
        symbol="NPY",
    ),

    # L2 Networks (Turbo)
    77702: Network(
        chain_id=77702,
        name="NanoPy Turbo L2",
        rpc="http://51.68.125.99:8547",
        db="turbo_scan.db",
        symbol="NPY",
        is_l2=True,
        l1_chain_id=7770,
    ),
    777702: Network(
        chain_id=777702,
        name="NanoPy Turbo L2 Testnet",
        rpc="http://51.68.125.99:8548",
        db="turbo_testnet_scan.db",
        symbol="NPY",
        is_l2=True,
        l1_chain_id=77700,
    ),

    # Legacy
    77777: Network(
        chain_id=77777,
        name="Pyralis Testnet",
        rpc="http://127.0.0.1:8545",
        db="pyralis_scan.db",
        symbol="NPY",
    ),
}

# CLI shortcuts
NETWORK_ALIASES = {
    "mainnet": 7770,
    "testnet": 77700,
    "turbo": 77702,
    "turbo-testnet": 777702,
    "l2": 77702,
    "l2-testnet": 777702,
}


def get_network(chain_id: int) -> Optional[Network]:
    """Get network by chain ID."""
    return NETWORKS.get(chain_id)


def get_network_by_alias(alias: str) -> Optional[Network]:
    """Get network by alias name."""
    chain_id = NETWORK_ALIASES.get(alias.lower())
    return NETWORKS.get(chain_id) if chain_id else None


def get_network_name(chain_id: int) -> str:
    """Get network name from chain ID."""
    network = NETWORKS.get(chain_id)
    return network.name if network else f"Chain {chain_id}"


def list_networks() -> Dict[int, Network]:
    """Get all networks."""
    return NETWORKS
