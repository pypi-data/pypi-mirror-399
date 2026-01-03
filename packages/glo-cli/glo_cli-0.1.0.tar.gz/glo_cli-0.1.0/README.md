# glo-cli

**Modern digital signatures. Simpler than PGP, verifiable forever.**

A minimal CLI for the [Glogos Protocol](https://github.com/glogos-org/glogos) - cryptographic attestations using Ed25519 + SHA-256.

## Installation

```bash
pip install glo-cli
```

## Quick Start

```bash
# Create your identity (protected by passphrase)
glo init

# Sign a file
glo sign document.pdf

# Verify a signature
glo verify document.pdf

# Create a message attestation
glo attest "Contract approved by all parties"
```

## Security

Your private key is protected using industry best practices:

| Component      | Algorithm   | Parameters       |
| -------------- | ----------- | ---------------- |
| Key Derivation | Argon2id    | m=64MB, t=3, p=4 |
| Encryption     | AES-256-GCM | 12-byte nonce    |
| Signature      | Ed25519     | RFC 8032         |

This follows OWASP recommendations and provides strong resistance against GPU/ASIC brute-force attacks.

## Commands

### Identity

```bash
glo init              # Create identity (passphrase required)
glo id                # Show your zone ID and public key
glo export            # Export public key
glo export --json     # Export as JSON
glo passwd            # Change passphrase
glo backup            # ⚠️ CRITICAL: Show 24-word recovery phrase
glo backup --verify   # Show and verify you wrote it down
glo restore           # Restore identity from recovery phrase
```

### Signing

```bash
glo sign <file>           # Sign a file (creates .glo file)
glo verify <file>         # Verify a signature
glo batch <dir>           # Sign all files in directory
glo batch <dir> -r        # Sign recursively
```

### Attestations

```bash
glo attest "message"      # Create message attestation
glo hash <file>           # Compute SHA-256 hash
```

### DID (Decentralized Identifier)

```bash
glo did                   # Show your DID
glo did --document        # Show full DID Document
```

### Git Integration

```bash
glo git attest            # Attest current commit
glo git attest <hash>     # Attest specific commit
glo git verify            # Verify current commit
glo git verify <hash>     # Verify specific commit
glo git log               # Show attestation status for recent commits
glo git log 20            # Show last 20 commits
```

### Info

```bash
glo info                  # Show protocol info
glo --version             # Show version
glo --help                # Show help
```

## Signature Format

Signatures are stored as JSON files with `.glo` extension:

```json
{
  "_type": "file",
  "_filename": "document.pdf",
  "_size": 12345,
  "attestation": {
    "id": "abc123...",
    "zone": "def456...",
    "subject": "789abc...",
    "canon": "c794a6fc...",
    "time": 1703500800,
    "refs": ["03b42642..."],
    "proof": "9a06e9a9..."
  },
  "public_key": "c70b1f7e..."
}
```

## Standard Canons

`glo-cli` implements the following protocol canons:

| Name                      | ID            | Description                    |
| ------------------------- | ------------- | ------------------------------ |
| `raw:sha256:1.0`          | `c794a6fc...` | Standard file signatures       |
| `timestamp:simple:1.0`    | `5c25b519...` | Self-reported timestamping     |
| `canon:definition:1.0`    | `df4e66f5...` | Protocol extension definitions |
| `opt:git:commit:1.0`      | `6fd6b8e8...` | Git commit attestations        |
| `opt:glogos:manifest:1.0` | `8e85667a...` | Directory batch manifests      |

## File Structure

```
~/.glogos/
├── zone.json        # Identity info (zone ID, public key, metadata)
├── secret.enc       # Encrypted private key (Default secure mode)
└── secret.key       # Plaintext private key (Only in --insecure mode)
```

## Security Modes

1. **Encrypted (Recommended)**: Private key is protected by Argon2id + AES-256-GCM.
2. **Insecure (`--insecure`)**: Private key stored in plaintext. Useful for CI/CD or automated scripts.

To migrate from insecure to encrypted mode without losing your identity:

```bash
glo migrate
```

## Comparison with GPG

| Feature       | GPG                        | glo                         |
| ------------- | -------------------------- | --------------------------- |
| **UX**        | Complex (20+ questions)    | Zero-config (0 questions)   |
| **Trust**     | Web of Trust / Key Servers | Self-certifying / DAG-based |
| **Storage**   | Complex keyrings           | Minimal JSON files          |
| **Crypto**    | RSA/DSA/ECDSA (Legacy)     | Ed25519 + Argon2id (Modern) |
| **Auditable** | Binary blobs               | Human-readable JSON         |

## Requirements

- Python 3.8+
- [PyNaCl](https://pypi.org/project/PyNaCl/) (Ed25519)
- [argon2-cffi](https://pypi.org/project/argon2-cffi/) (Key derivation)
- [cryptography](https://pypi.org/project/cryptography/) (AES-GCM)

## Protocol

- **Spec**: [GLOGOS.md](https://github.com/glogos-org/glogos/blob/main/GLOGOS.md)
- **Genesis**: [GENESIS.md](https://github.com/glogos-org/glogos/blob/main/GENESIS.md) (Winter Solstice 2025)

## License

[Apache-2.0](LICENSE)
