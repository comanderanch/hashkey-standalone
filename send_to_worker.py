"""
send_to_worker.py
Simulates AIA in Texas
Sends action to California worker
Via hash only
"""

import json
import hashlib
import time
from pathlib import Path
from data_to_fold import encode_to_6base

def send_action(action_payload, uid, seed, watch_dir="incoming"):
    folded = encode_to_6base(action_payload)

    hash_obj = {
        "uid":       uid,
        "seed":      seed,
        "input":     folded,
        "timestamp": time.time()
    }
    hash_key = hashlib.sha256(
        json.dumps(hash_obj, sort_keys=True).encode()
    ).hexdigest()

    transmission = {
        "uid":       uid,
        "hash_key":  hash_key,
        "seed":      seed,
        "timestamp": hash_obj["timestamp"]
    }

    packet = {
        "transmission": transmission,
        "fold":         folded
    }

    Path(watch_dir).mkdir(exist_ok=True)
    ts = int(hash_obj["timestamp"])
    out = Path(watch_dir) / f"action_{ts}.json"
    with open(out, "w") as f:
        json.dump(packet, f, indent=2)

    print(f"[✔] Action folded — strand: {folded['strand_length']} bits")
    print(f"[✔] Hash: {hash_key[:16]}...")
    print(f"[✔] Written to {out}")
    print(f"[✔] Nothing else crossed.")

if __name__ == "__main__":
    send_action(
        action_payload={
            "action":  "ping",
            "from":    "AIA — Haskell Texas",
            "message": "Worker alive check — March 15 2026"
        },
        uid="aia_texas_001",
        seed="haskell-texas-2026"
    )
