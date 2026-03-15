"""
sender.py — Docker sender container entrypoint
Non-interactive pipeline: data → fold → hash → transmission
Writes to /output/ volume:
  - folded_input.json  (the fold, KB scale)
  - transmission.json  (hash + uid, what actually transmits)
"""

import json
import hashlib
import time
from pathlib import Path
from data_to_fold import encode_to_6base

UID  = "docker_sender_001"
SEED = "haskell_texas_bridge_2026"

SENDER_DATA = {
    "message": "This payload never crossed the network bridge",
    "sender": "docker_sender",
    "destination": "docker_receiver",
    "payload": {
        "data_type": "text",
        "content": "Only the hash crossed. The data rebuilt here.",
        "timestamp": "2026-03-15"
    }
}

def compute_hash(obj):
    json_bytes = json.dumps(obj, sort_keys=True).encode('utf-8')
    return hashlib.sha256(json_bytes).hexdigest()

def main():
    print("=" * 60)
    print("SENDER — hashkey-standalone Docker test")
    print("=" * 60)

    # Step 1 — Fold the data
    folded = encode_to_6base(SENDER_DATA)
    print(f"[+] Data folded into 6-base pair strand")
    print(f"[+] Strand length: {folded['strand_length']} bits")
    print(f"[+] Payload hash:  {folded['payload_hash'][:16]}...")
    print(f"[+] AM: {folded['values']['am_freq_khz']} kHz")
    print(f"[+] FM: {folded['values']['fm_freq_mhz']} MHz")
    print(f"[+] Hue: {folded['values']['hue_degrees']}°")

    # Step 2 — Generate hash key
    timestamp = time.time()
    hash_obj = {
        "uid":       UID,
        "seed":      SEED,
        "input":     folded,
        "timestamp": timestamp
    }
    hash_key = compute_hash(hash_obj)
    print(f"[+] Hash key: {hash_key[:16]}...")

    # Step 3 — Write fold to output volume
    output_dir = Path("/output")
    output_dir.mkdir(exist_ok=True)

    fold_path = output_dir / "folded_input.json"
    fold_path.write_text(json.dumps(folded, indent=2))
    print(f"[✔] Fold written: {fold_path}")

    # Step 4 — Write transmission (hash + uid only — this is what crosses the wire)
    transmission = {
        "uid":       UID,
        "hash_key":  hash_key,
        "timestamp": timestamp,
        "note":      "Only this file crosses the network. Fold rebuilds at receiver."
    }
    tx_path = output_dir / "transmission.json"
    tx_path.write_text(json.dumps(transmission, indent=2))
    print(f"[✔] Transmission written: {tx_path}")
    print(f"    hash_key: {hash_key}")
    print()
    print("SENDER COMPLETE — hash ready to transmit")

if __name__ == "__main__":
    main()
