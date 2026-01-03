# NanoPy Scan

Block explorer for NanoPy blockchain.

## Install

```bash
pip install nanopy-scan
```

## Quick Start

```bash
# Run explorer for testnet
nanopy-scan --network testnet

# Run for L2 Turbo
nanopy-scan --network turbo-testnet

# Custom RPC
nanopy-scan --rpc http://localhost:8545
```

Open http://localhost:8080 in your browser.

## Features

- Browse blocks and transactions
- Search by block number, tx hash, or address
- View account balances and history
- Real-time block updates
- Multi-network support (L1 + L2)

## Networks

| Network | Chain ID | Default Port |
|---------|----------|--------------|
| Testnet | 77777 | 8080 |
| Turbo Testnet | 777702 | 8081 |

## API

```bash
# Get latest blocks
curl http://localhost:8080/api/blocks

# Get block by number
curl http://localhost:8080/api/block/123

# Get transaction
curl http://localhost:8080/api/tx/0x...

# Get address info
curl http://localhost:8080/api/address/0x...
```

## Links

- **NanoPy L1**: https://github.com/Web3-League/blockchain-python
- **NanoPy L2**: https://github.com/Web3-League/blockchain-L2
- **Webapp**: https://github.com/Web3-League/dapp-nanopy

## License

MIT
