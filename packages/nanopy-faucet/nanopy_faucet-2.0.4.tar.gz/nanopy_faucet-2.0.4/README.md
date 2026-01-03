# NanoPy Faucet

Testnet faucet for NanoPy L1 and Turbo L2.

## Install

```bash
pip install nanopy-faucet
```

## Quick Start

```bash
# Run faucet (same wallet for both networks)
nanopy-faucet --private-key YOUR_PRIVATE_KEY

# Separate wallets per network
nanopy-faucet --private-key-l1 KEY1 --private-key-l2 KEY2

# Custom port
nanopy-faucet --private-key YOUR_KEY --port 8081
```

Open http://localhost:8081 in your browser.

## Networks

| Network | Chain ID | Amount | Cooldown |
|---------|----------|--------|----------|
| NanoPy Testnet | 77777 | 10 NPY | 1 hour |
| Turbo L2 Testnet | 777702 | 100 NPY | 30 min |

## API

```bash
# Get available networks
curl http://localhost:8081/networks

# Check if address can claim
curl "http://localhost:8081/check?address=0x...&network=testnet"

# Claim tokens
curl -X POST http://localhost:8081/claim \
  -H "Content-Type: application/json" \
  -d '{"address": "0x...", "network": "testnet"}'
```

## Links

- **NanoPy L1**: https://github.com/Web3-League/blockchain-python
- **NanoPy L2**: https://github.com/Web3-League/blockchain-L2
- **Webapp**: https://github.com/Web3-League/dapp-nanopy

## License

MIT
