"""
auth_registry.py
Manages authorized MAC registry
Handles two step new machine authorization
Step 1 — Texas generates auth request with OTP
Step 2 — New machine confirms with same OTP
Both steps must match within time window
"""

import json
import hashlib
import secrets
import time
from pathlib import Path
from machine_auth import (
    get_local_mac, get_mac_hash,
    load_registry, save_registry, AUTH_REGISTRY
)

PENDING_DIR = Path("auth/pending")
OTP_WINDOW  = 600  # 10 minutes in seconds

def register_first_machine():
    """
    Initial setup — register this machine as primary
    Run once on first authorized machine only
    """
    mac      = get_local_mac()
    mac_hash = get_mac_hash(mac)

    registry = load_registry()

    if registry['authorized']:
        print("[!] Registry already has authorized machines")
        print("[!] Use two step auth to add new machines")
        return

    registry['authorized'].append({
        "mac_hash":   mac_hash,
        "mac_hint":   mac[:8] + "...",
        "role":       "primary",
        "registered": time.time(),
        "label":      input("Label for this machine: ").strip()
    })

    save_registry(registry)
    print(f"[✔] Primary machine registered")
    print(f"[✔] MAC hash: {mac_hash[:16]}...")

def generate_auth_request(new_mac, label):
    """
    STEP 1 — Texas side
    Generate OTP + auth request for new machine
    Fold this and send to new machine
    """
    otp      = secrets.token_hex(16)
    otp_hash = hashlib.sha256(otp.encode()).hexdigest()

    pending = {
        "new_mac_hash": get_mac_hash(new_mac),
        "mac_hint":     new_mac[:8] + "...",
        "otp_hash":     otp_hash,
        "label":        label,
        "expires":      time.time() + OTP_WINDOW,
        "created":      time.time()
    }

    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    pending_file = PENDING_DIR / f"pending_{int(time.time())}.json"
    with open(pending_file, 'w') as f:
        json.dump(pending, f, indent=2)

    print(f"[✔] Auth request generated")
    print(f"[✔] OTP (send separately): {otp}")
    print(f"[✔] Expires in 10 minutes")
    print(f"[!] Fold this and send to new machine:")
    print(json.dumps({
        "action":   "auth_request",
        "otp_hash": otp_hash,
        "label":    label,
        "expires":  pending["expires"]
    }, indent=2))
    return otp

def confirm_auth_request(otp_received):
    """
    STEP 2 — New machine side
    New machine confirms with OTP received
    MAC verified against pending registry
    """
    local_mac = get_local_mac()
    mac_hash  = get_mac_hash(local_mac)
    otp_hash  = hashlib.sha256(otp_received.encode()).hexdigest()
    now       = time.time()

    pending_files = list(PENDING_DIR.glob("pending_*.json")) \
        if PENDING_DIR.exists() else []

    for pf in pending_files:
        with open(pf) as f:
            pending = json.load(f)

        if pending["expires"] < now:
            print(f"[!] Pending request expired")
            pf.unlink()
            continue

        if pending["otp_hash"] != otp_hash:
            print(f"[!] OTP mismatch — rejected")
            continue

        if pending["new_mac_hash"] != mac_hash:
            print(f"[!] MAC mismatch — this is not the registered machine")
            print(f"[!] Expected: {pending['new_mac_hash'][:16]}...")
            print(f"[!] Got:      {mac_hash[:16]}...")
            continue

        # Both match — authorize
        registry = load_registry()
        registry['authorized'].append({
            "mac_hash":   mac_hash,
            "mac_hint":   local_mac[:8] + "...",
            "role":       pending.get("label", "secondary"),
            "registered": now,
            "label":      pending["label"]
        })
        save_registry(registry)
        pf.unlink()

        print(f"[✔] TWO STEP AUTH COMPLETE")
        print(f"[✔] New machine authorized: {local_mac[:17]}...")
        print(f"[✔] Role: {pending['label']}")
        return True

    print("[!] No valid pending auth request found")
    return False

def list_authorized():
    registry = load_registry()
    print("\n== AUTHORIZED MACHINES ==")
    for m in registry['authorized']:
        print(f"  {m['label']:20} | {m['mac_hint']} | {m['role']}")
    print(f"  Total: {len(registry['authorized'])}")

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "register":
        register_first_machine()
    elif cmd == "request":
        new_mac = input("New machine MAC address: ").strip()
        label   = input("Label (e.g. california_vps_backup): ").strip()
        generate_auth_request(new_mac, label)
    elif cmd == "confirm":
        otp = input("Enter OTP received from Texas: ").strip()
        confirm_auth_request(otp)
    elif cmd == "list":
        list_authorized()
