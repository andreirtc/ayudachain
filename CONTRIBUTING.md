# Contributing to AyudaChain 🇵🇭

Thank you for your interest in contributing to **AyudaChain**! We are building an immutable, transparent, and resilient digital trail for disaster relief and public aid distribution in the Philippines.

## Code of Conduct

All contributors are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Please treat all community members with respect and professionalism.

## Repository Architecture

AyudaChain is structured into three primary domains:
- **`contracts/`**: Solidity 0.8.20 smart contracts deployed on EVM / Polygon Amoy testnet. Manages immutable relief fund batch releases, barangay allocations, and SHA-256 receipt integrity anchors.
- **`backend/`**: Python REST API with SQLite persistence. Implements AI entity resolution (fuzzy matching, token-set Levenshtein distance), anomaly detection, and receipt hashing.
- **`frontend/`**: Next.js 15 App Router + React 19 + TypeScript + Tailwind CSS application featuring the public transparency portal, DAFAC QR scanner, and fraud simulator.
- **`docs/`**: Architectural specifications, blockchain gas analysis, user guide, and demo scripts.

## Development Workflow

### 1. Fork & Clone
```bash
git clone https://github.com/andreirtc/ayudachain.git
cd ayudachain
```

### 2. Environment Configuration
Copy the example environment configuration:
```bash
cp .env.example .env
```

### 3. Running the Entire Stack Locally
You can start all three layers (Hardhat node + Python API + Next.js frontend) with one script:
```bash
bash start_ayudachain.sh
```
Or start components independently:
- **Blockchain**: `npm --prefix contracts run node` and `npm --prefix contracts run deploy:local`
- **Backend**: `python3 backend/server.py 8000`
- **Frontend**: `npm --prefix frontend run dev`

## Testing Guidelines

Before opening a Pull Request, make sure all test suites pass:

```bash
# 1. Run all unit tests from root
npm test

# 2. Smart contract tests (100% passing required)
npm run test:contracts

# 3. Python backend unit & AI tests
npm run test:backend

# 4. Frontend TypeScript compilation audit
npm run typecheck
```

## Pull Request Guidelines

1. **Branch Naming**: Use clear prefixes:
   - `feat/your-feature-name`
   - `fix/issue-description`
   - `docs/documentation-update`
2. **Commit Messages**: Follow Conventional Commits format (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`).
3. **Privacy First**: Never commit personally identifiable information (PII) or real citizen data to tests or repositories. Use synthetic DAFAC identifiers (e.g. `DFC-2026-XXXX`).
4. **Gas Efficiency**: Any changes to `AyudaChainRegistry.sol` must be accompanied by updated gas benchmarks and test coverage.
