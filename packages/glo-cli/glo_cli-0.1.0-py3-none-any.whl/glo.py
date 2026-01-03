#!/usr/bin/env python3
"""
glo - Glogos Protocol CLI (Unified)

Modern digital signatures. Simpler than GPG, verifiable forever.

Usage:
  glo init [--insecure]           Create identity
  glo sign <file> [file...]       Sign file(s)
  glo verify <file> [file...]     Verify signature(s)
  glo attest <message>            Create attestation
  glo hash <file|string>          SHA-256 hash
  glo id                          Show identity
  glo export                      Export public key
  glo batch <dir>                 Sign directory
  glo chain <file>                Show chain
  glo did                         Show DID
  glo git attest [commit]         Attest git commit
  glo git verify [commit]         Verify commit
  glo git log                     Show git attestations
  glo unlock                      Unlock for session
  glo passwd                      Change passphrase
  glo info                        Protocol info

Security Modes:
  Default:    Private key encrypted with Argon2id + AES-256-GCM
  --insecure: Private key stored in plaintext (for demo/dev)

Protocol: https://github.com/glogos-org/glogos
"""

__version__ = "0.1.0"

import sys
import os
import json
import hashlib
import struct
import argparse
import subprocess
import secrets
import base64
import getpass
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple

# ═══════════════════════════════════════════════════════════════════════════
# Constants (loaded from shared/test-vectors/)
# ═══════════════════════════════════════════════════════════════════════════

def _load_test_vectors():
    """Load constants from shared test vectors files."""
    vectors_dir = Path(__file__).parent.parent.parent / "shared" / "test-vectors"
    
    # Load protocol vectors
    protocol_path = vectors_dir / "protocol-vectors.json"
    if protocol_path.exists():
        data = json.loads(protocol_path.read_text())
        vectors = data.get("vectors", {})
        glr = vectors.get("glr", {}).get("expected", "")
        genesis_id = vectors.get("genesis_attestation", {}).get("id", "")
        canon_ids = vectors.get("canon_ids", {})
    else:
        # Fallback: compute GLR mathematically, load GENESIS_ID from artifact
        glr = hashlib.sha256(b"").hexdigest()
        artifact_path = vectors_dir.parent / "artifacts" / "genesis-artifact.json"
        if artifact_path.exists():
            artifact = json.loads(artifact_path.read_text())
            genesis_id = artifact.get("attestation", {}).get("id", "")
        else:
            genesis_id = ""  # Will fail if used without proper setup
        canon_ids = {}
    
    # Build CANONS dict from protocol vectors
    canons = {}
    for key, val in canon_ids.items():
        if isinstance(val, dict) and "name" in val and "expected_id" in val:
            canons[val["name"]] = val["expected_id"]
    
    # Load optional canons
    opt_path = vectors_dir / "opt-vectors.json"
    if opt_path.exists():
        opt_data = json.loads(opt_path.read_text())
        for key, val in opt_data.get("optional_canons", {}).items():
            if isinstance(val, dict) and "name" in val and "expected_id" in val:
                canons[val["name"]] = val["expected_id"]
    
    return glr, genesis_id, canons

GLR, GENESIS_ID, CANONS = _load_test_vectors()

# Shorthand aliases for CLI convenience
CANON_ALIASES = {
    "raw": "raw:sha256:1.0",
    "timestamp": "timestamp:simple:1.0",
    "definition": "canon:definition:1.0",
    "git": "opt:git:commit:1.0",
    "manifest": "opt:glogos:manifest:1.0",
    "rotate": "opt:key:rotate:1.0",
}

def resolve_canon(name: str) -> str:
    """Resolve canon name/alias to canon ID."""
    if name in CANONS:
        return CANONS[name]
    if name in CANON_ALIASES:
        return CANONS[CANON_ALIASES[name]]
    # Assume it's already a canon ID (hex64)
    return name

# Multibase prefix for Ed25519 public key (base58btc)
MULTICODEC_ED25519_PUB = b'\xed\x01'

# Zone directory (supports GLO_HOME env var for dry runs)
def _get_zone_dir() -> Path:
    custom = os.environ.get('GLO_HOME')
    if custom:
        return Path(custom)
    return Path.home() / ".glogos"

ZONE_DIR = _get_zone_dir()
ZONE_FILE = ZONE_DIR / "zone.json"
SECRET_FILE = ZONE_DIR / "secret.enc"      # Encrypted mode
SECRET_PLAIN = ZONE_DIR / "secret.key"     # Insecure mode
# Session in user-specific dir with restricted permissions
def _get_session_file() -> Path:
    session_dir = Path(tempfile.gettempdir()) / f".glo_{os.getuid() if hasattr(os, 'getuid') else os.getlogin()}"
    session_dir.mkdir(mode=0o700, exist_ok=True)
    return session_dir / "session"
SIG_EXT = ".glo"

# KDF Parameters
ARGON2_MEMORY = 65536
ARGON2_TIME = 3
ARGON2_PARALLELISM = 4
SESSION_TIMEOUT = 300  # 5 minutes
MAX_PASSPHRASE_ATTEMPTS = 5
PASSPHRASE_LOCKOUT_FILE = ZONE_DIR / ".lockout"

# ═══════════════════════════════════════════════════════════════════════════
# Lazy Imports
# ═══════════════════════════════════════════════════════════════════════════

_nacl = None
_argon2 = None
_crypto = None
_mnemonic = None

def _get_nacl():
    global _nacl
    if _nacl is None:
        try:
            import nacl.signing
            import nacl.encoding
            import nacl.exceptions
            _nacl = nacl
        except ImportError:
            _err("pynacl required. Install: pip install pynacl")
    return _nacl

def _get_argon2():
    global _argon2
    if _argon2 is None:
        try:
            import argon2
            _argon2 = argon2
        except ImportError:
            _err("argon2-cffi required. Install: pip install argon2-cffi")
    return _argon2

def _get_crypto():
    global _crypto
    if _crypto is None:
        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            _crypto = (Cipher, algorithms, modes)
        except ImportError:
            _err("cryptography required. Install: pip install cryptography")
    return _crypto

def _get_mnemonic():
    global _mnemonic
    if _mnemonic is None:
        try:
            from mnemonic import Mnemonic
            _mnemonic = Mnemonic("english")
        except ImportError:
            _err("mnemonic required. Install: pip install mnemonic")
    return _mnemonic

def _secret_to_mnemonic(secret_bytes: bytes) -> str:
    """Convert 32-byte secret to 24-word BIP39 mnemonic."""
    m = _get_mnemonic()
    return m.to_mnemonic(secret_bytes)

def _mnemonic_to_secret(mnemonic: str) -> bytes:
    """Convert 24-word BIP39 mnemonic to 32-byte secret seed."""
    m = _get_mnemonic()
    if not m.check(mnemonic):
        raise ValueError("Invalid mnemonic checksum")
    return m.to_entropy(mnemonic)

def get_did_document(zone: dict) -> dict:
    """Generate W3C DID Document for a zone."""
    did_glogos = f"did:glogos:{zone['zone_id']}"
    did_key = to_did_key(zone['public_key'])
    
    doc = {
        "@context": [
            "https://www.w3.org/ns/did/v1",
            "https://w3id.org/security/suites/ed25519-2020/v1"
        ],
        "id": did_glogos,
        "alsoKnownAs": [did_key],
        "verificationMethod": [{
            "id": f"{did_key}#0",
            "type": "Ed25519VerificationKey2020",
            "controller": did_glogos,
            "publicKeyMultibase": to_did_key(zone['public_key']).split(':')[-1]
        }],
        "authentication": [f"{did_key}#0"],
        "assertionMethod": [f"{did_key}#0"]
    }
    
    if zone.get("name"):
        doc["alsoKnownAs"].insert(0, zone["name"])
        
    return doc

# ═══════════════════════════════════════════════════════════════════════════
# Output helpers
# ═══════════════════════════════════════════════════════════════════════════

_NO_COLOR = os.environ.get("NO_COLOR") or not sys.stdout.isatty()

def _c(code: str, t: str) -> str:
    return t if _NO_COLOR else f"\033[{code}m{t}\033[0m"

def _green(t: str) -> str: return _c("32", t)
def _red(t: str) -> str: return _c("31", t)
def _yellow(t: str) -> str: return _c("33", t)
def _cyan(t: str) -> str: return _c("36", t)
def _dim(t: str) -> str: return _c("2", t)
def _bold(t: str) -> str: return _c("1", t)

def _ok(m: str): print(f"{_green('✓')} {m}")
def _err(m: str, code: int = 1): print(f"{_red('✗')} {m}", file=sys.stderr); sys.exit(code)
def _warn(m: str): print(f"{_yellow('⚠')} {m}", file=sys.stderr)
def _info(m: str): print(f"  {m}")

# ═══════════════════════════════════════════════════════════════════════════
# Utilities
# ═══════════════════════════════════════════════════════════════════════════

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_str(s: str) -> str:
    return sha256(s.encode())

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def now_unix() -> int:
    return int(datetime.now(timezone.utc).timestamp())

def now_iso() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def short(h: str, n: int = 8) -> str:
    return h[:n] + "..." if len(h) > n else h

def fmt_bytes(n: int) -> str:
    for u in ['B', 'KB', 'MB', 'GB']:
        if n < 1024: return f"{n:.1f}{u}" if u != 'B' else f"{n}{u}"
        n /= 1024
    return f"{n:.1f}TB"

# ═══════════════════════════════════════════════════════════════════════════
# Base58 (for did:key)
# ═══════════════════════════════════════════════════════════════════════════

BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def base58_encode(data: bytes) -> str:
    n = int.from_bytes(data, 'big')
    result = ''
    while n > 0:
        n, r = divmod(n, 58)
        result = BASE58_ALPHABET[r] + result
    for b in data:
        if b == 0: result = '1' + result
        else: break
    return result or '1'

def to_did_key(public_key_hex: str) -> str:
    pk_bytes = bytes.fromhex(public_key_hex)
    multicodec = MULTICODEC_ED25519_PUB + pk_bytes
    return f"did:key:z{base58_encode(multicodec)}"

def to_did_glogos(zone_id: str) -> str:
    return f"did:glogos:{zone_id}"

# ═══════════════════════════════════════════════════════════════════════════
# Encryption (for secure mode)
# ═══════════════════════════════════════════════════════════════════════════

def derive_key(passphrase: str, salt: bytes) -> bytes:
    from argon2.low_level import hash_secret_raw, Type
    return hash_secret_raw(
        secret=passphrase.encode(),
        salt=salt,
        time_cost=ARGON2_TIME,
        memory_cost=ARGON2_MEMORY,
        parallelism=ARGON2_PARALLELISM,
        hash_len=32,
        type=Type.ID
    )

def encrypt_private_key(private_key: bytes, passphrase: str) -> dict:
    _get_argon2()
    Cipher, algorithms, modes = _get_crypto()
    
    salt = secrets.token_bytes(16)
    nonce = secrets.token_bytes(12)
    key = derive_key(passphrase, salt)
    
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(private_key) + encryptor.finalize()
    
    return {
        "version": 1,
        "algorithm": "argon2id+aes256gcm",
        "salt": base64.b64encode(salt).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "tag": base64.b64encode(encryptor.tag).decode()
    }

def decrypt_private_key(encrypted: dict, passphrase: str) -> bytes:
    _get_argon2()
    Cipher, algorithms, modes = _get_crypto()
    
    salt = base64.b64decode(encrypted["salt"])
    nonce = base64.b64decode(encrypted["nonce"])
    ciphertext = base64.b64decode(encrypted["ciphertext"])
    tag = base64.b64decode(encrypted["tag"])
    
    key = derive_key(passphrase, salt)
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag))
    decryptor = cipher.decryptor()
    
    try:
        return decryptor.update(ciphertext) + decryptor.finalize()
    except Exception:
        raise ValueError("Wrong passphrase")

# ═══════════════════════════════════════════════════════════════════════════
# Zone Management
# ═══════════════════════════════════════════════════════════════════════════

def is_insecure_mode() -> bool:
    """Check if zone is in insecure mode."""
    return SECRET_PLAIN.exists() and not SECRET_FILE.exists()

def zone_exists() -> bool:
    return ZONE_FILE.exists()

def load_zone() -> Dict[str, Any]:
    if not zone_exists():
        _err(f"No identity. Run: glo init")
    try:
        return json.loads(ZONE_FILE.read_text())
    except json.JSONDecodeError:
        _err(f"Corrupted zone: {ZONE_FILE}")

def save_zone(zone: Dict[str, Any]):
    ZONE_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    ZONE_FILE.write_text(json.dumps(zone, indent=2))
    os.chmod(ZONE_FILE, 0o644)

def update_last_attestation(att_id: str):
    """Update last_attestation_id in zone for auto-chain."""
    zone = load_zone()
    zone['last_attestation_id'] = att_id
    save_zone(zone)

def get_auto_refs(zone: Dict) -> List[str]:
    """Get refs for auto-chain mode."""
    last_id = zone.get('last_attestation_id')
    return [last_id] if last_id else [GENESIS_ID]

def check_rate_limit() -> bool:
    """Check if passphrase attempts are rate limited."""
    if not PASSPHRASE_LOCKOUT_FILE.exists():
        return False
    try:
        data = json.loads(PASSPHRASE_LOCKOUT_FILE.read_text())
        if data.get('until', 0) > now_unix():
            remaining = data['until'] - now_unix()
            _err(f"Rate limited. Try again in {remaining}s")
        PASSPHRASE_LOCKOUT_FILE.unlink()
    except:
        pass
    return False

def record_failed_attempt():
    """Record failed passphrase attempt with exponential backoff."""
    attempts = 1
    if PASSPHRASE_LOCKOUT_FILE.exists():
        try:
            data = json.loads(PASSPHRASE_LOCKOUT_FILE.read_text())
            attempts = data.get('attempts', 0) + 1
        except:
            pass
    
    if attempts >= MAX_PASSPHRASE_ATTEMPTS:
        lockout = min(2 ** (attempts - MAX_PASSPHRASE_ATTEMPTS + 1), 3600)  # Max 1 hour
        PASSPHRASE_LOCKOUT_FILE.write_text(json.dumps({
            'attempts': attempts,
            'until': now_unix() + lockout
        }))
        _warn(f"Too many attempts. Locked for {lockout}s")
    else:
        PASSPHRASE_LOCKOUT_FILE.write_text(json.dumps({'attempts': attempts}))

def clear_failed_attempts():
    """Clear failed attempt counter on success."""
    if PASSPHRASE_LOCKOUT_FILE.exists():
        PASSPHRASE_LOCKOUT_FILE.unlink()

def get_private_key(passphrase: str = None) -> bytes:
    """Get private key, handling both secure and insecure modes."""
    # Insecure mode
    if is_insecure_mode():
        return bytes.fromhex(SECRET_PLAIN.read_text().strip())
    
    # Check session
    session_file = _get_session_file()
    if session_file.exists():
        try:
            session = json.loads(session_file.read_text())
            if session.get('expires', 0) > now_unix():
                return bytes.fromhex(session['key'])
            else:
                session_file.unlink()  # Expired, clean up
        except:
            pass
    
    # Secure mode - need passphrase
    check_rate_limit()
    if not passphrase:
        passphrase = os.environ.get('GLO_PASSPHRASE') or getpass.getpass("Passphrase: ")
    
    if not SECRET_FILE.exists():
        _err("No private key found")
    
    encrypted = json.loads(SECRET_FILE.read_text())
    try:
        key = decrypt_private_key(encrypted, passphrase)
        clear_failed_attempts()
        return key
    except ValueError:
        record_failed_attempt()
        _err("Wrong passphrase")

def get_signing_key(passphrase: str = None):
    """Get nacl SigningKey."""
    nacl = _get_nacl()
    return nacl.signing.SigningKey(get_private_key(passphrase))

# ═══════════════════════════════════════════════════════════════════════════
# Attestation
# ═══════════════════════════════════════════════════════════════════════════

def compute_att_id(zone_id: str, subject: str, canon: str, time: int) -> str:
    return sha256(bytes.fromhex(zone_id) + bytes.fromhex(subject) + 
                  bytes.fromhex(canon) + struct.pack('>Q', time))

def compute_refs_hash(refs: List[str]) -> str:
    return GLR if not refs else sha256_str("|".join(sorted(refs)))

def create_attestation(zone: Dict, subject: str, refs: List[str] = None,
                       canon: str = "raw", meta: Dict = None, signing_key=None) -> Dict:
    nacl = _get_nacl()
    refs = refs or [GENESIS_ID]
    canon_id = resolve_canon(canon)
    time = now_unix()
    
    att_id = compute_att_id(zone['zone_id'], subject, canon_id, time)
    refs_hash = compute_refs_hash(refs)
    
    sign_input = (bytes.fromhex(att_id) + bytes.fromhex(subject) +
                  struct.pack('>Q', time) + bytes.fromhex(refs_hash) +
                  bytes.fromhex(canon_id))
    
    if signing_key is None:
        signing_key = get_signing_key()
    
    sig = signing_key.sign(sign_input, encoder=nacl.encoding.RawEncoder).signature
    
    att = {"id": att_id, "zone": zone['zone_id'], "subject": subject,
           "canon": canon_id, "time": time, "refs": refs, "proof": sig.hex()}
    if meta: att["_meta"] = meta
    return att

def verify_attestation(att: Dict, pubkey: str = None) -> Tuple[bool, str]:
    nacl = _get_nacl()
    try:
        if not pubkey and zone_exists():
            z = load_zone()
            if z['zone_id'] == att['zone']: pubkey = z['public_key']
        if not pubkey: return False, "Public key required"
        
        pk_bytes = bytes.fromhex(pubkey)
        if sha256(pk_bytes) != att['zone']:
            return False, "Zone mismatch"
        
        exp_id = compute_att_id(att['zone'], att['subject'], att['canon'], att['time'])
        if exp_id != att['id']: return False, "ID mismatch"
        
        refs_hash = compute_refs_hash(att.get('refs', []))
        sign_input = (bytes.fromhex(att['id']) + bytes.fromhex(att['subject']) +
                      struct.pack('>Q', att['time']) + bytes.fromhex(refs_hash) +
                      bytes.fromhex(att['canon']))
        
        nacl.signing.VerifyKey(pk_bytes).verify(sign_input, bytes.fromhex(att['proof']))
        return True, "Valid"
    except nacl.exceptions.BadSignatureError:
        return False, "Invalid signature"
    except Exception as e:
        return False, str(e)

# ═══════════════════════════════════════════════════════════════════════════
# File operations
# ═══════════════════════════════════════════════════════════════════════════

def sig_path(p: Path) -> Path:
    return p.with_suffix(p.suffix + SIG_EXT)

def sign_file(p: Path, zone: Dict, refs: List[str] = None, force: bool = False, signing_key=None, out_path: Path = None) -> Dict:
    if not p.exists(): _err(f"Not found: {p}")
    sp = out_path or sig_path(p)
    if sp.exists() and not force: _err(f"Exists: {sp} (use -f)")
    
    att = create_attestation(zone, sha256_file(p), refs, "raw",
                             {"filename": p.name, "size": p.stat().st_size, "signed_at": now_iso()},
                             signing_key)
    
    output = {"attestation": att, "public_key": zone['public_key']}
    sp.write_text(json.dumps(output, indent=2))
    return att

def verify_file(p: Path, pubkey: str = None) -> Tuple[bool, str, Dict]:
    sp = sig_path(p)
    if not p.exists(): return False, f"Not found: {p}", None
    if not sp.exists(): return False, f"No signature: {sp}", None
    
    try:
        data = json.loads(sp.read_text())
        att = data.get('attestation', data)
        # Prioritize pubkey from sig file, then param, then local zone
        pubkey = data.get('public_key') or pubkey
    except: return False, f"Invalid sig file", None
    
    if sha256_file(p) != att['subject']:
        return False, "File modified", att
    
    ok, msg = verify_attestation(att, pubkey)
    return ok, msg, att

# ═══════════════════════════════════════════════════════════════════════════
# Git Integration
# ═══════════════════════════════════════════════════════════════════════════

def git_cmd(*args) -> Tuple[int, str, str]:
    result = subprocess.run(["git"] + list(args), capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def git_root() -> Optional[Path]:
    code, out, _ = git_cmd("rev-parse", "--show-toplevel")
    return Path(out) if code == 0 else None

def git_attestations_dir() -> Path:
    root = git_root()
    if not root: _err("Not a git repository")
    return root / ".glogos" / "git"

# ═══════════════════════════════════════════════════════════════════════════
# Commands
# ═══════════════════════════════════════════════════════════════════════════

def cmd_init(args):
    if zone_exists() and not args.force:
        _warn(f"Identity exists: {ZONE_FILE}")
        z = load_zone()
        _info(f"Zone: {_cyan(z['zone_id'])}")
        _info(f"Mode: {'insecure' if is_insecure_mode() else 'encrypted'}")
        _info(f"Use -f to regenerate")
        return 0
    
    if zone_exists():
        z = load_zone()
        print()
        print(_red("═" * 60))
        print(_red(_bold("  ⚠️  WARNING: ZONE WILL BE PERMANENTLY DESTROYED  ⚠️")))
        print(_red("═" * 60))
        print()
        _info(f"Existing Zone: {_cyan(z['zone_id'])}")
        _info(f"All attestations signed by this zone will be UNVERIFIABLE!")
        print()
        _warn("Have you backed up the 24-word recovery phrase? (glo backup)")
        print()
        confirm = input(f"  Type 'DESTROY {z['zone_id'][:8]}' to confirm: ")
        if confirm != f"DESTROY {z['zone_id'][:8]}":
            _info("Cancelled"); return 0
    
    nacl = _get_nacl()
    sk = nacl.signing.SigningKey.generate()
    pk = sk.verify_key.encode()
    
    zone = {
        "zone_id": sha256(pk),
        "public_key": pk.hex(),
        "created_at": now_iso(),
    }
    if args.name:
        zone["name"] = args.name
    
    ZONE_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    
    if args.insecure:
        # Insecure mode - plaintext
        SECRET_PLAIN.write_text(sk.encode().hex())
        os.chmod(SECRET_PLAIN, 0o600)
        if SECRET_FILE.exists(): SECRET_FILE.unlink()
    else:
        # Secure mode - encrypted
        print(f"\n🔐 Create passphrase (min 8 chars)")
        while True:
            passphrase = getpass.getpass("  Passphrase: ")
            if len(passphrase) < 8:
                _warn("Too short"); continue
            confirm = getpass.getpass("  Confirm: ")
            if passphrase != confirm:
                _warn("Mismatch"); continue
            break
        
        encrypted = encrypt_private_key(sk.encode(), passphrase)
        SECRET_FILE.write_text(json.dumps(encrypted, indent=2))
        os.chmod(SECRET_FILE, 0o600)
        if SECRET_PLAIN.exists(): SECRET_PLAIN.unlink()
    
    save_zone(zone)
    
    print()
    _ok("Identity created!")
    print()
    if zone.get('name'):
        _info(f"Name:       {_bold(zone['name'])}")
    _info(f"Zone ID:    {_cyan(zone['zone_id'])}")
    _info(f"Public Key: {_dim(zone['public_key'])}")
    _info(f"Mode:       {'🔓 insecure' if args.insecure else '🔐 encrypted'}")
    _info(f"Saved:      {ZONE_FILE}")
    print()
    if not args.insecure:
        _warn("Remember your passphrase!")
    return 0

def cmd_sign(args):
    zone = load_zone()
    # Auto-chain: use last attestation ID unless --genesis or --ref specified
    if args.genesis:
        refs = [GENESIS_ID]
    elif args.ref:
        refs = args.ref
    else:
        refs = get_auto_refs(zone)  # Auto-chain mode
    
    signing_key = get_signing_key()
    ok, fail = 0, 0
    last_att_id = None
    
    for f in args.files:
        p = Path(f)
        try:
            # Handle output directory
            if hasattr(args, 'output_dir') and args.output_dir:
                out_dir = Path(args.output_dir)
                out_dir.mkdir(parents=True, exist_ok=True)
                out_path = out_dir / (p.name + SIG_EXT)
            else:
                out_path = None
            
            att = sign_file(p, zone, refs, args.force, signing_key, out_path)
            last_att_id = att['id']
            
            if args.quiet: print(out_path or sig_path(p))
            elif args.json: print(json.dumps(att, indent=2))
            else:
                _ok(f"Signed: {p}")
                _info(f"Attestation: {short(att['id'], 16)}")
                _info(f"Subject: {short(att['subject'], 16)}")
                _info(f"Output:  {out_path or sig_path(p)}")
            ok += 1
            if args.chain: refs = [att['id']]
        except SystemExit: fail += 1
        except Exception as e:
            print(f"{_red('✗')} {p}: {e}", file=sys.stderr); fail += 1
    
    # Update last attestation for auto-chain (unless --no-update)
    if last_att_id and not getattr(args, 'no_update', False):
        update_last_attestation(last_att_id)
    
    if not args.quiet and len(args.files) > 1:
        print(); _info(f"Signed: {ok}, Failed: {fail}")
    return 0 if fail == 0 else 1

def cmd_verify(args):
    pubkey = args.key or (load_zone()['public_key'] if zone_exists() else None)
    ok, fail = 0, 0
    
    for f in args.files:
        p = Path(f)
        if p.suffix == SIG_EXT: p = p.with_suffix('')
        
        valid, msg, att = verify_file(p, pubkey)
        
        if args.quiet: print("valid" if valid else "invalid")
        elif args.json and att:
            print(json.dumps({"valid": valid, "message": msg, "attestation": att}, indent=2))
        elif valid:
            _ok(f"Valid: {p}")
            if att and '_meta' in att:
                _info(f"Signed: {att['_meta'].get('signed_at', '?')}")
                _info(f"Zone:   {short(att['zone'], 16)}")
        else:
            print(f"{_red('✗')} Invalid: {p}")
            _info(f"Reason: {msg}")
        
        if valid: ok += 1
        else: fail += 1
    
    if not args.quiet and len(args.files) > 1:
        print(); _info(f"Valid: {ok}, Invalid: {fail}")
    return 0 if fail == 0 else 1

def cmd_attest(args):
    zone = load_zone()
    signing_key = get_signing_key()
    msg = ' '.join(args.message)
    att = create_attestation(zone, sha256_str(msg), args.ref or [GENESIS_ID],
                             args.canon or "raw", {"message": msg, "created_at": now_iso()},
                             signing_key)
    
    if args.output:
        output = {"attestation": att, "public_key": zone['public_key']}
        Path(args.output).write_text(json.dumps(output, indent=2))
        _ok(f"Saved: {args.output}")
    
    if args.quiet: print(att['id'])
    elif args.json: print(json.dumps(att, indent=2))
    else:
        print(f"\n{_bold('📜 Attestation')}\n")
        _info(f"ID:      {_cyan(att['id'])}")
        _info(f"Zone:    {short(att['zone'], 16)}")
        _info(f"Subject: {short(att['subject'], 16)}")
        _info(f"Time:    {datetime.fromtimestamp(att['time'], timezone.utc).isoformat()}")
        if not args.output: print(f"\n{_dim('(use -o to save)')}")
    return 0

def cmd_hash(args):
    if args.string:
        h = sha256_str(args.input)
        if args.quiet: print(h)
        else: _info(f'String: "{args.input[:50]}..."' if len(args.input) > 50 else f'String: "{args.input}"'); print(f"SHA-256: {_cyan(h)}")
    else:
        p = Path(args.input)
        if not p.exists(): _err(f"Not found: {p}")
        h = sha256_file(p)
        if args.quiet: print(h)
        else: _info(f"File: {p} ({fmt_bytes(p.stat().st_size)})"); print(f"SHA-256: {_cyan(h)}")
    return 0

def cmd_id(args):
    z = load_zone()
    if args.json:
        data = {"zone_id": z['zone_id'], "public_key": z['public_key'], 
                "created_at": z.get('created_at'), "mode": "insecure" if is_insecure_mode() else "encrypted"}
        if z.get('name'):
            data['name'] = z['name']
        print(json.dumps(data, indent=2))
    else:
        name_str = f": {z['name']}" if z.get('name') else ""
        print(f"\n{_bold(f'🔑 Identity{name_str}')}\n")
        print("─" * 64)
        if z.get('name'):
            _info(f"Name:       {_bold(z['name'])}")
        _info(f"Zone ID:    {_cyan(z['zone_id'])}")
        _info(f"Public Key: {_dim(z['public_key'])}")
        _info(f"Created:    {z.get('created_at', '?')}")
        _info(f"Mode:       {'🔓 insecure' if is_insecure_mode() else '🔐 encrypted'}")
        print("─" * 64 + "\n")
    return 0

def cmd_export(args):
    z = load_zone()
    if args.json:
        data = json.dumps({"zone_id": z['zone_id'], "public_key": z['public_key'], "created_at": z.get('created_at')}, indent=2)
    else:
        data = z['public_key']
    
    if args.output: Path(args.output).write_text(data); _ok(f"Exported: {args.output}")
    else: print(data)
    return 0

def cmd_batch(args):
    zone = load_zone()
    d = Path(args.directory)
    if not d.is_dir(): _err(f"Not a directory: {d}")
    
    files = [f for f in (d.rglob('*') if args.recursive else d.iterdir()) 
             if f.is_file() and not f.name.endswith(SIG_EXT)]
    
    if not files: _warn("No files"); return 0
    
    manifest_entries = []
    
    # Dry-run mode
    if args.dry_run:
        _info(f"Dry-run: would sign {len(files)} file(s)")
        for p in sorted(files):
            sp = sig_path(p)
            status = "skip (exists)" if sp.exists() and not args.force else "sign"
            _info(f"  [{status}] {p.relative_to(d)}")
        return 0
    
    if not args.quiet: _info(f"Found {len(files)} file(s)")
    
    signing_key = get_signing_key()
    refs, ok, fail = args.ref or [GENESIS_ID], 0, 0
    last_att_id = None
    
    for p in sorted(files):
        try:
            sp = sig_path(p)
            if sp.exists() and not args.force:
                if not args.quiet: _info(f"Skip: {p.relative_to(d)}")
                continue
            att = sign_file(p, zone, refs, True, signing_key)
            last_att_id = att['id']
            
            if getattr(args, 'manifest', False):
                manifest_entries.append({
                    "path": str(p.relative_to(d)).replace('\\', '/'),
                    "subject": att['subject'],
                    "signature_file": str(p.relative_to(d)).replace('\\', '/') + SIG_EXT
                })
            
            if not args.quiet: _ok(f"Signed: {p.relative_to(d)}")
            ok += 1
            if args.chain: refs = [att['id']]
        except Exception as e:
            print(f"{_red('✗')} {p}: {e}", file=sys.stderr); fail += 1
    
    # Generate Manifest
    if getattr(args, 'manifest', False) and not args.dry_run and manifest_entries:
        manifest_path = d / "manifest.json"
        manifest_data = {
            "zone": zone['zone_id'],
            "root": d.name,
            "files": manifest_entries
        }
        manifest_path.write_text(json.dumps(manifest_data, indent=2))
        if not args.quiet: _ok(f"Manifest: {manifest_path}")

        # Sign manifest (using custom canon for manifest)
        man_canon = resolve_canon("manifest")
        man_att = create_attestation(zone, sha256_file(manifest_path), refs, man_canon,
                                     {"filename": "manifest.json", "type": "manifest", "created_at": now_iso()},
                                     signing_key)
        
        out = {"attestation": man_att, "public_key": zone['public_key']}
        sig_path(manifest_path).write_text(json.dumps(out, indent=2))
        if not args.quiet: _ok(f"Signed manifest: {sig_path(manifest_path)}")
        last_att_id = man_att['id']

    # Update last attestation for auto-chain
    if last_att_id:
        update_last_attestation(last_att_id)
    
    if not args.quiet: print(); _info(f"Signed: {ok}, Skip/Fail: {fail}")
    return 0 if fail == 0 else 1

def cmd_chain(args):
    p = Path(args.file)
    if p.suffix != SIG_EXT: p = sig_path(p)
    if not p.exists(): _err(f"Not found: {p}")
    
    data = json.loads(p.read_text())
    att = data.get('attestation', data)
    
    if args.json: print(json.dumps(att, indent=2))
    else:
        print(f"\n{_bold('📜 Chain')}\n")
        print(f"┌─ {_cyan(short(att['id'], 16))}")
        _info(f"│  Zone:    {short(att['zone'], 16)}")
        _info(f"│  Subject: {short(att['subject'], 16)}")
        _info(f"│  Time:    {datetime.fromtimestamp(att['time'], timezone.utc).isoformat()}")
        if '_meta' in att:
            if 'filename' in att['_meta']: _info(f"│  File:    {att['_meta']['filename']}")
            if 'message' in att['_meta']: _info(f"│  Msg:     {att['_meta']['message'][:40]}...")
        for i, r in enumerate(att.get('refs', [])):
            pre = "└" if i == len(att['refs']) - 1 else "├"
            if r == GLR: print(f"{pre}─→ {_yellow('GLR')} (Root)")
            elif r == GENESIS_ID: print(f"{pre}─→ {_green('Genesis')} (2025-12-21)")
            else: print(f"{pre}─→ {_dim(short(r, 16))}")
        print()
    return 0

def cmd_did(args):
    z = load_zone()
    did_glogos = to_did_glogos(z['zone_id'])
    did_key = to_did_key(z['public_key'])
    
    if args.document:
        doc = get_did_document(z)
        print(json.dumps(doc, indent=2))
    elif args.json:
        print(json.dumps({"did:glogos": did_glogos, "did:key": did_key}, indent=2))
    else:
        print(f"\n{_bold('🆔 DIDs')}\n")
        _info(f"did:glogos  {_cyan(did_glogos)}")
        _info(f"did:key     {_cyan(did_key)}")
        print()
    return 0

def cmd_unlock(args):
    if is_insecure_mode():
        _warn("Already in insecure mode")
        return 0
    
    passphrase = getpass.getpass("Passphrase: ")
    try:
        key = get_private_key(passphrase)
    except:
        _err("Wrong passphrase")
    
    timeout = args.timeout or SESSION_TIMEOUT
    session = {"key": key.hex(), "expires": now_unix() + timeout}
    session_file = _get_session_file()
    session_file.write_text(json.dumps(session))
    os.chmod(session_file, 0o600)
    
    _ok(f"Unlocked for {timeout}s")
    return 0

def cmd_lock(args):
    session_file = _get_session_file()
    if session_file.exists():
        session_file.unlink()
        _ok("Session locked")
    else:
        _info("No session to lock")
    return 0

def cmd_passwd(args):
    if is_insecure_mode():
        _err("Cannot change passphrase in insecure mode. Migrate first with: glo init -f")
    
    old_pass = getpass.getpass("Current passphrase: ")
    try:
        private_key = get_private_key(old_pass)
    except:
        _err("Wrong passphrase")
    
    print("\n  Create new passphrase:")
    while True:
        new_pass = getpass.getpass("  New passphrase: ")
        if len(new_pass) < 8: _warn("Too short"); continue
        confirm = getpass.getpass("  Confirm: ")
        if new_pass != confirm: _warn("Mismatch"); continue
        break
    
    # Backup before overwrite
    backup_path = SECRET_FILE.with_suffix('.enc.bak')
    import shutil
    shutil.copy2(SECRET_FILE, backup_path)
    
    encrypted = encrypt_private_key(private_key, new_pass)
    SECRET_FILE.write_text(json.dumps(encrypted, indent=2))
    
    _ok("Passphrase changed")
    _info(f"Backup: {backup_path}")
    return 0

def cmd_migrate(args):
    """Migrate from insecure to encrypted mode."""
    if not zone_exists():
        _err("No zone found. Run: glo init")
    
    if not is_insecure_mode():
        _err("Already in encrypted mode")
    
    _info("Current mode: insecure (plaintext)")
    _info(f"Private key: {SECRET_PLAIN}")
    
    if args.dry_run:
        _info("Dry-run: Would encrypt private key with passphrase")
        _info(f"         Would create: {SECRET_FILE}")
        _info(f"         Would delete: {SECRET_PLAIN}")
        return 0
    
    # Read plaintext key
    private_key = bytes.fromhex(SECRET_PLAIN.read_text().strip())
    
    # Get passphrase
    print(f"\n🔐 Create passphrase (min 8 chars)")
    while True:
        passphrase = getpass.getpass("  Passphrase: ")
        if len(passphrase) < 8:
            _warn("Too short"); continue
        confirm = getpass.getpass("  Confirm: ")
        if passphrase != confirm:
            _warn("Mismatch"); continue
        break
    
    # Encrypt
    encrypted = encrypt_private_key(private_key, passphrase)
    SECRET_FILE.write_text(json.dumps(encrypted, indent=2))
    os.chmod(SECRET_FILE, 0o600)
    
    # Backup and remove plaintext
    backup = SECRET_PLAIN.with_suffix('.key.bak')
    SECRET_PLAIN.rename(backup)
    
    _ok("Migrated to encrypted mode!")
    _info(f"Encrypted: {SECRET_FILE}")
    _info(f"Backup: {backup}")
    _warn("Delete backup after verifying: rm " + str(backup))
    return 0

def cmd_backup(args):
    """Backup private key as BIP39 mnemonic."""
    if not zone_exists():
        _err("No zone found. Run: glo init")
    
    zone = load_zone()
    private_key = get_private_key()
    mnemonic_words = _secret_to_mnemonic(private_key)
    word_list = mnemonic_words.split()
    
    if args.json:
        print(json.dumps({
            "zone_id": zone['zone_id'],
            "mnemonic": mnemonic_words,
            "word_count": len(word_list)
        }, indent=2))
        return 0
    
    print()
    print(_red("═" * 64))
    print(_red(_bold("  ⚠️  CRITICAL: BACKUP YOUR RECOVERY PHRASE  ⚠️")))
    print(_red("═" * 64))
    print()
    print("  Write down these 24 words and store in a SAFE place.")
    print("  This is the ONLY way to recover your zone if you lose")
    print("  your passphrase or device.")
    print()
    print(_yellow("  NEVER share these words with anyone."))
    print(_yellow("  NEVER take a screenshot or store digitally."))
    print()
    print("─" * 64)
    print()
    
    # Display words in 4 columns
    for row in range(6):
        cols = []
        for col in range(4):
            idx = row * 4 + col
            cols.append(f"{idx+1:2}. {_cyan(word_list[idx].ljust(12))}")
        print("  " + "  ".join(cols))
    
    print()
    print("─" * 64)
    print()
    _info(f"Zone ID: {zone['zone_id']}")
    print()
    
    if args.verify:
        print("  Verify by entering words 1, 12, and 24:")
        try:
            w1 = input(f"  Word 1: ").strip().lower()
            w12 = input(f"  Word 12: ").strip().lower()
            w24 = input(f"  Word 24: ").strip().lower()
            
            if w1 == word_list[0] and w12 == word_list[11] and w24 == word_list[23]:
                _ok("Verification passed!")
            else:
                _err("Verification failed. Please write down the words again.")
        except (KeyboardInterrupt, EOFError):
            print()
            _warn("Verification cancelled")
    else:
        _warn("Use --verify to confirm you wrote down the words correctly.")
    
    return 0

def cmd_restore(args):
    """Restore zone from BIP39 mnemonic."""
    m = _get_mnemonic()
    nacl = _get_nacl()
    
    if zone_exists() and not args.force:
        z = load_zone()
        _warn(f"Zone already exists: {short(z['zone_id'], 16)}")
        _info("Use -f to overwrite (DANGER: old zone will be lost!)")
        return 1
    
    print()
    print(_bold("🔑 Restore Zone from Recovery Phrase"))
    print()
    
    if args.mnemonic:
        mnemonic_input = " ".join(args.mnemonic)
    else:
        print("  Enter your 24-word recovery phrase.")
        print("  Separate words with spaces or enter one per line.")
        print("  Type 'done' when finished.")
        print()
        
        words = []
        while len(words) < 24:
            try:
                remaining = 24 - len(words)
                line = input(f"  ({len(words)+1}-{min(len(words)+4, 24)}) [{remaining} remaining]: ").strip().lower()
                if line == 'done':
                    break
                # Handle space-separated input
                line_words = line.split()
                words.extend(line_words)
            except (KeyboardInterrupt, EOFError):
                print()
                _warn("Cancelled")
                return 1
        
        if len(words) != 24:
            _err(f"Expected 24 words, got {len(words)}")
        
        mnemonic_input = " ".join(words[:24])
    
    # Convert mnemonic to entropy (private key seed)
    try:
        private_key = _mnemonic_to_secret(mnemonic_input)
    except Exception as e:
        _err(str(e))
    
    # Generate keypair
    sk = nacl.signing.SigningKey(private_key)
    pk = sk.verify_key.encode()
    new_zone_id = sha256(pk)
    
    # Show zone ID before proceeding
    print()
    _info(f"Recovered Zone ID: {_cyan(new_zone_id)}")
    
    if zone_exists() and args.force:
        old_zone = load_zone()
        if old_zone['zone_id'] != new_zone_id:
            print()
            _warn("Zone ID does not match existing zone!")
            _info(f"Existing: {old_zone['zone_id'][:32]}...")
            _info(f"Restored: {new_zone_id[:32]}...")
            confirm = input("  Type 'OVERWRITE' to proceed: ")
            if confirm != 'OVERWRITE':
                _info("Cancelled")
                return 1
    
    # Save zone
    zone = {
        "zone_id": new_zone_id,
        "public_key": pk.hex(),
        "created_at": now_iso(),
        "restored_at": now_iso(),
    }
    
    ZONE_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    
    if args.insecure:
        SECRET_PLAIN.write_text(private_key.hex())
        os.chmod(SECRET_PLAIN, 0o600)
        if SECRET_FILE.exists(): SECRET_FILE.unlink()
    else:
        print(f"\n🔐 Create passphrase for restored zone (min 8 chars)")
        while True:
            passphrase = getpass.getpass("  Passphrase: ")
            if len(passphrase) < 8:
                _warn("Too short"); continue
            confirm = getpass.getpass("  Confirm: ")
            if passphrase != confirm:
                _warn("Mismatch"); continue
            break
        
        encrypted = encrypt_private_key(private_key, passphrase)
        SECRET_FILE.write_text(json.dumps(encrypted, indent=2))
        os.chmod(SECRET_FILE, 0o600)
        if SECRET_PLAIN.exists(): SECRET_PLAIN.unlink()
    
    save_zone(zone)
    
    print()
    _ok("Zone restored successfully!")
    print()
    _info(f"Zone ID:    {_cyan(zone['zone_id'])}")
    _info(f"Public Key: {_dim(zone['public_key'])}")
    _info(f"Mode:       {'🔓 insecure' if args.insecure else '🔐 encrypted'}")
    print()
    return 0


def cmd_git(args):
    zone = load_zone()
    subcmd = args.git_cmd
    
    if subcmd == "attest":
        signing_key = get_signing_key()
        commit = args.commit or "HEAD"
        code, commit_hash, _ = git_cmd("rev-parse", commit)
        if code != 0: _err(f"Invalid commit: {commit}")
        
        _, msg, _ = git_cmd("log", "-1", "--format=%s", commit_hash)
        subject = sha256_str(commit_hash)
        canon = resolve_canon("git")
        
        att = create_attestation(zone, subject, [GENESIS_ID], canon, 
                                 {"commit": commit_hash, "message": msg}, signing_key)
        
        output = {"attestation": att, "public_key": zone['public_key'], "_commit": {"hash": commit_hash, "message": msg}}
        output_json = json.dumps(output, indent=2)
        
        # Store in git notes (primary, portable)
        code, _, err = git_cmd("notes", "--ref=glogos", "add", "-f", "-m", output_json, commit_hash)
        if code != 0: _err(f"Failed to add git note: {err}")
        
        # Also store as file (backup)
        att_dir = git_attestations_dir()
        att_dir.mkdir(parents=True, exist_ok=True)
        out_file = att_dir / f"{commit_hash}.json"
        out_file.write_text(output_json)
        
        _ok(f"Attested: {commit_hash[:8]}")
        _info(f"Message: {msg[:50]}")
        _info(f"Stored: git notes + {out_file.name}")
    
    elif subcmd == "verify":
        commit = args.commit or "HEAD"
        code, commit_hash, _ = git_cmd("rev-parse", commit)
        if code != 0: _err(f"Invalid commit: {commit}")
        
        # Read from git notes
        code, note_content, _ = git_cmd("notes", "--ref=glogos", "show", commit_hash)
        if code != 0: _err(f"No attestation for {commit_hash[:8]}")
        
        try:
            data = json.loads(note_content)
        except json.JSONDecodeError: _err("Invalid JSON in git note")

        ok, msg = verify_attestation(data['attestation'], data['public_key'])
        
        if ok: 
            _ok(f"Valid: {commit_hash[:8]}")
            _info(f"Signer: {short(data['attestation']['zone'], 16)}")
        else: _err(f"Invalid: {msg}")
    
    elif subcmd == "log":
        n = args.count or 10
        att_dir = git_attestations_dir()
        
        code, commits, _ = git_cmd("log", f"-{n}", "--format=%H")
        if code != 0: _err("Not a git repository")
        
        print(f"\n{_bold('Git Attestations')}\n")
        for commit_hash in commits.split('\n'):
            if not commit_hash: continue
            att_file = att_dir / f"{commit_hash}.json"
            _, msg, _ = git_cmd("log", "-1", "--format=%s", commit_hash)
            
            # Check git notes first, then file
            note_code, _, _ = git_cmd("notes", "--ref=glogos", "show", commit_hash)
            has_attestation = note_code == 0 or att_file.exists()
            
            if has_attestation:
                print(f"  {_green('●')} {commit_hash[:8]}  {msg[:40]}")
            else:
                print(f"  {_dim('○')} {commit_hash[:8]}  {msg[:40]}")
        print()
    
    return 0

def cmd_info(args):
    print(f"\n{_bold('Glogos Protocol')}\n")
    _info(f"Version: {__version__}")
    _info(f"GLR:     {short(GLR, 16)}")
    _info(f"Genesis: {short(GENESIS_ID, 16)}")
    print("\n  Canons:")
    for n, i in CANONS.items(): _info(f"  {n}: {short(i, 16)}")
    print(f"\n  Zone: {ZONE_FILE}")
    _info(f"Exists: {'yes' if zone_exists() else 'no'}")
    if zone_exists():
        _info(f"Mode: {'insecure' if is_insecure_mode() else 'encrypted'}")
    print("\n  https://github.com/glogos-org/glogos\n")
    return 0

def cmd_rotate(args):
    """Rotate to a new key while maintaining zone identity."""
    if not zone_exists():
        _err("No zone found. Run: glo init")
    
    zone = load_zone()
    old_zone_id = zone['zone_id']
    old_public_key = zone['public_key']
    
    print(f"\n{_bold('🔄 Key Rotation')}\n")
    print("═" * 60)
    _warn("This will generate a NEW key and create a rotation attestation.")
    _warn("Your zone_id will remain the same, but the signing key will change.")
    print()
    _info(f"Current Zone:   {_cyan(old_zone_id)}")
    _info(f"Current Key:    {_dim(old_public_key)}")
    print("═" * 60)
    print()
    
    if not args.force:
        confirm = input("  Type 'ROTATE' to confirm: ")
        if confirm != "ROTATE":
            _info("Cancelled")
            return 0
    
    # Get current signing key to sign the rotation attestation
    old_signing_key = get_signing_key()
    
    # Generate new keypair
    nacl = _get_nacl()
    new_sk = nacl.signing.SigningKey.generate()
    new_pk = new_sk.verify_key.encode()
    new_public_key_hex = new_pk.hex()
    
    # The subject is the hash of the new public key
    subject = sha256(new_pk)
    
    # Create rotation attestation signed by OLD key
    refs = get_auto_refs(zone)
    rotation_canon = resolve_canon("opt:key:rotate:1.0")
    
    att = create_attestation(
        zone=zone,
        subject=subject,
        refs=refs,
        canon="opt:key:rotate:1.0",
        meta={
            "type": "key_rotation",
            "new_public_key": new_public_key_hex,
            "old_public_key": old_public_key,
            "reason": args.reason if hasattr(args, 'reason') and args.reason else "scheduled"
        },
        signing_key=old_signing_key
    )
    
    # Save rotation attestation to file
    rotation_file = ZONE_DIR / "rotations" / f"{att['id']}.json"
    rotation_file.parent.mkdir(parents=True, exist_ok=True)
    
    rotation_record = {
        "attestation": att,
        "public_key": old_public_key  # The key that signed this
    }
    rotation_file.write_text(json.dumps(rotation_record, indent=2))
    
    # Update zone with new key (keep same zone_id!)
    zone['public_key'] = new_public_key_hex
    zone['rotated_at'] = now_iso()
    zone['rotation_count'] = zone.get('rotation_count', 0) + 1
    zone['last_rotation_id'] = att['id']
    
    # Save new private key
    if args.insecure:
        SECRET_PLAIN.write_text(new_sk.encode().hex())
        os.chmod(SECRET_PLAIN, 0o600)
        if SECRET_FILE.exists(): SECRET_FILE.unlink()
    else:
        print(f"\n🔐 Create passphrase for NEW key (min 8 chars)")
        while True:
            passphrase = getpass.getpass("  Passphrase: ")
            if len(passphrase) < 8:
                _warn("Too short"); continue
            confirm = getpass.getpass("  Confirm: ")
            if passphrase != confirm:
                _warn("Mismatch"); continue
            break
        
        encrypted = encrypt_private_key(new_sk.encode(), passphrase)
        SECRET_FILE.write_text(json.dumps(encrypted, indent=2))
        os.chmod(SECRET_FILE, 0o600)
        if SECRET_PLAIN.exists(): SECRET_PLAIN.unlink()
    
    # Update last attestation for auto-chain
    update_last_attestation(att['id'])
    save_zone(zone)
    
    print()
    _ok("Key rotated successfully!")
    print()
    _info(f"Zone ID:         {_cyan(zone['zone_id'])} (unchanged)")
    _info(f"New Public Key:  {_green(new_public_key_hex)}")
    _info(f"Rotation ID:     {_dim(att['id'])}")
    _info(f"Saved:           {rotation_file}")
    print()
    _warn("⚠️  Backup your NEW 24-word recovery phrase!")
    _info("Run: glo backup --verify")
    print()
    return 0

# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

# Global verbose flag
_VERBOSE = False

def _debug(m: str):
    """Print debug message if verbose mode enabled."""
    if _VERBOSE: print(f"{_dim('▸')} {_dim(m)}")

def main() -> int:
    global _VERBOSE
    p = argparse.ArgumentParser(prog='glo', description='Glogos CLI - Modern digital signatures')
    p.add_argument('-v', '--version', action='version', version=f'glo {__version__}')
    p.add_argument('-V', '--verbose', action='store_true', help='Verbose output')
    sp = p.add_subparsers(dest='cmd', metavar='CMD')
    
    # init
    s = sp.add_parser('init', help='Create identity')
    s.add_argument('-f', '--force', action='store_true')
    s.add_argument('--insecure', action='store_true', help='No passphrase (dev mode)')
    s.add_argument('-n', '--name', metavar='NAME', help='Human-readable zone name (e.g. Zone-1)')
    
    # sign
    s = sp.add_parser('sign', help='Sign file(s)')
    s.add_argument('files', nargs='+', metavar='FILE')
    s.add_argument('-r', '--ref', action='append', metavar='ID', help='Custom ref ID')
    s.add_argument('-g', '--genesis', action='store_true', help='Reset refs to Genesis (disable auto-chain)')
    s.add_argument('-o', '--output-dir', metavar='DIR', help='Output directory for .glo files')
    s.add_argument('-f', '--force', action='store_true')
    s.add_argument('-c', '--chain', action='store_true', help='Chain multiple files (each refs previous)')
    s.add_argument('--no-update', action='store_true', help='Do not update last_attestation_id')
    s.add_argument('-q', '--quiet', action='store_true')
    s.add_argument('-j', '--json', action='store_true')
    
    # verify
    s = sp.add_parser('verify', help='Verify signature(s)')
    s.add_argument('files', nargs='+', metavar='FILE')
    s.add_argument('-k', '--key', metavar='PUBKEY')
    s.add_argument('-q', '--quiet', action='store_true')
    s.add_argument('-j', '--json', action='store_true')
    
    # attest
    s = sp.add_parser('attest', help='Create attestation')
    s.add_argument('message', nargs='+')
    s.add_argument('-r', '--ref', action='append', metavar='ID')
    s.add_argument('-c', '--canon', choices=['raw', 'timestamp', 'definition'])
    s.add_argument('-o', '--output', metavar='FILE')
    s.add_argument('-q', '--quiet', action='store_true')
    s.add_argument('-j', '--json', action='store_true')
    
    # hash
    s = sp.add_parser('hash', help='SHA-256 hash')
    s.add_argument('input')
    s.add_argument('-s', '--string', action='store_true')
    s.add_argument('-q', '--quiet', action='store_true')
    
    # id
    s = sp.add_parser('id', help='Show identity')
    s.add_argument('-j', '--json', action='store_true')
    
    # export
    s = sp.add_parser('export', help='Export public key')
    s.add_argument('-j', '--json', action='store_true')
    s.add_argument('-o', '--output', metavar='FILE')
    
    # batch
    s = sp.add_parser('batch', help='Sign directory')
    s.add_argument('directory')
    s.add_argument('-r', '--recursive', action='store_true')
    s.add_argument('-m', '--manifest', action='store_true', help='Generate manifest.json')
    s.add_argument('-f', '--force', action='store_true')
    s.add_argument('-c', '--chain', action='store_true')
    s.add_argument('--ref', action='append', metavar='ID')
    s.add_argument('-n', '--dry-run', action='store_true', help='Preview without signing')
    s.add_argument('-q', '--quiet', action='store_true')
    
    # chain
    s = sp.add_parser('chain', help='Show chain')
    s.add_argument('file')
    s.add_argument('-j', '--json', action='store_true')
    
    # did
    s = sp.add_parser('did', help='DID identifiers')
    s.add_argument('-d', '--document', action='store_true')
    s.add_argument('-j', '--json', action='store_true')
    
    # unlock/lock
    s = sp.add_parser('unlock', help='Unlock for session')
    s.add_argument('-t', '--timeout', type=int, metavar='SEC')
    sp.add_parser('lock', help='Lock session')
    
    # passwd
    sp.add_parser('passwd', help='Change passphrase')
    
    # git
    s = sp.add_parser('git', help='Git integration')
    gs = s.add_subparsers(dest='git_cmd')
    g1 = gs.add_parser('attest', help='Attest commit')
    g1.add_argument('commit', nargs='?')
    g2 = gs.add_parser('verify', help='Verify commit')
    g2.add_argument('commit', nargs='?')
    g3 = gs.add_parser('log', help='Show attestations')
    g3.add_argument('count', nargs='?', type=int)
    
    # info
    sp.add_parser('info', help='Protocol info')
    
    # migrate
    s = sp.add_parser('migrate', help='Migrate insecure zone to encrypted')
    s.add_argument('-n', '--dry-run', action='store_true', help='Preview only')
    
    # backup
    s = sp.add_parser('backup', help='Backup zone as recovery phrase')
    s.add_argument('--verify', action='store_true', help='Verify backup by entering words')
    s.add_argument('-j', '--json', action='store_true', help='JSON output')
    
    # restore
    s = sp.add_parser('restore', help='Restore zone from recovery phrase')
    s.add_argument('mnemonic', nargs='*', metavar='WORD', help='24 recovery words')
    s.add_argument('-f', '--force', action='store_true', help='Overwrite existing zone')
    s.add_argument('--insecure', action='store_true', help='No passphrase (dev mode)')
    
    # rotate
    s = sp.add_parser('rotate', help='Rotate to new key')
    s.add_argument('-f', '--force', action='store_true', help='Skip confirmation')
    s.add_argument('--insecure', action='store_true', help='No passphrase (dev mode)')
    s.add_argument('--reason', help='Rotation reason (scheduled, compromised, upgrade)')
    
    args = p.parse_args()
    _VERBOSE = getattr(args, 'verbose', False)
    if not args.cmd: p.print_help(); return 0
    
    cmds = {
        'init': cmd_init, 'sign': cmd_sign, 'verify': cmd_verify, 'attest': cmd_attest,
        'hash': cmd_hash, 'id': cmd_id, 'export': cmd_export, 'batch': cmd_batch,
        'chain': cmd_chain, 'did': cmd_did, 'unlock': cmd_unlock, 'lock': cmd_lock,
        'passwd': cmd_passwd, 'git': cmd_git, 'info': cmd_info, 'migrate': cmd_migrate,
        'backup': cmd_backup, 'restore': cmd_restore, 'rotate': cmd_rotate
    }
    return cmds[args.cmd](args)

if __name__ == '__main__':
    try: sys.exit(main())
    except KeyboardInterrupt: print(); sys.exit(130)
    except BrokenPipeError: sys.exit(0)
