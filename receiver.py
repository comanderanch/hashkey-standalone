"""
receiver.py — Docker receiver container entrypoint
Non-interactive pipeline: transmission → verify hash → rebuild payload
Reads from /output/ volume:
  - folded_input.json  (the fold from sender)
  - transmission.json  (hash + uid from sender)
Prints verified payload to stdout.
"""

import json
import hashlib
from pathlib import Path

SEED = "haskell_texas_bridge_2026"

def compute_hash(obj):
    json_bytes = json.dumps(obj, sort_keys=True).encode('utf-8')
    return hashlib.sha256(json_bytes).hexdigest()

def main():
    print("=" * 60)
    print("RECEIVER — hashkey-standalone Docker test")
    print("=" * 60)

    output_dir = Path("/output")

    # Step 1 — Read transmission (what crossed the wire)
    tx_path = output_dir / "transmission.json"
    if not tx_path.exists():
        print("[!] transmission.json not found — run sender first")
        return
    transmission = json.loads(tx_path.read_text())
    uid       = transmission["uid"]
    hash_key  = transmission["hash_key"]
    timestamp = transmission["timestamp"]
    print(f"[+] Transmission received")
    print(f"[+] UID:      {uid}")
    print(f"[+] Hash key: {hash_key[:16]}...")

    # Step 2 — Read fold from shared volume
    fold_path = output_dir / "folded_input.json"
    if not fold_path.exists():
        print("[!] folded_input.json not found in shared volume")
        return
    folded = json.loads(fold_path.read_text())
    print(f"[+] Fold loaded — strand length: {folded['strand_length']} bits")

    # Step 3 — Recompute hash and verify
    hash_obj = {
        "uid":       uid,
        "seed":      SEED,
        "input":     folded,
        "timestamp": timestamp
    }
    recomputed = compute_hash(hash_obj)

    if recomputed == hash_key:
        print(f"[✔] Hash verified — MATCH")
    else:
        print(f"[✗] Hash MISMATCH")
        print(f"    Expected:   {hash_key}")
        print(f"    Recomputed: {recomputed}")
        return

    # Step 4 — Rebuild payload
    payload = folded.get("payload")
    if not payload:
        print("[!] No payload in fold")
        return

    print()
    print("=" * 60)
    print("PAYLOAD REBUILT AT RECEIVER")
    print("=" * 60)
    print(f"  message:     {payload.get('message')}")
    print(f"  sender:      {payload.get('sender')}")
    print(f"  destination: {payload.get('destination')}")
    print(f"  content:     {payload['payload'].get('content')}")
    print(f"  timestamp:   {payload['payload'].get('timestamp')}")
    print(f"  strand:      {folded['strand_length']} bits")
    print(f"  payload_hash:{folded['payload_hash'][:16]}...")
    print()
    print("RECEIVER COMPLETE — data rebuilt from hash address")

if __name__ == "__main__":
    main()
