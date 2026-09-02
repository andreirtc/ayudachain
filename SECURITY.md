# Security Policy

## Reporting a Vulnerability

The AyudaChain team takes security seriously, especially given our focus on public relief funds, anti-corruption transparency, and citizen data protection under the **Data Privacy Act of 2012 (Republic Act No. 10173)**.

If you discover a potential security vulnerability in AyudaChain, please DO NOT create a public issue on GitHub.

Instead, please send an encrypted or private report to:
- **Email**: `ralphandreicastillo326@gmail.com`
- **Subject Line**: `[SECURITY] AyudaChain Vulnerability Report`

Please include:
1. Description of the vulnerability and its potential impact.
2. Step-by-step reproduction instructions or proof-of-concept code.
3. Affected components (`contracts/`, `backend/`, `frontend/`).
4. Any proposed remediations.

We will acknowledge receipt within 48 hours and work with you on an expedited patch before any public disclosure.

## Security Architecture Principles

- **Zero PII On-Chain**: No citizen personal information (names, national ID numbers, contact numbers, exact household coordinates) may ever be committed to the blockchain. Only cryptographic digests (`bytes32 receiptHash`, `bytes32 recordHash`) are anchored.
- **Access Control**: Critical smart contract functions (`releaseFund`, `allocateFund`, `confirmDistribution`) are restricted to `onlyAuthorized` operators.
- **Append-Only Immutability**: Batches and distributions cannot be overwritten or deleted on-chain once stamped.
