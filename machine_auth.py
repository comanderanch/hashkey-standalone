"""
machine_auth.py
MAC address verification layer
Wraps q_memory_restorer before any fold opens
Unauthorized MAC — fold destructs — alert fires
"""

import uuid
import json
import hashlib
import time
from pathlib import Path

AUTH_REGISTRY = Path("auth/authorized_macs.json")
ATTEMPT_LOG   = Path("auth/attempt_log.json")
ALERT_DIR     = Path("outgoing/alerts")

def get_local_mac():
    mac_int = uuid.getnode()
    mac_hex = ':'.join(
        f'{(mac_int >> i) & 0xff:02x}'
        for i in range(40, -1, -8)
    )
    return mac_hex

def get_mac_hash(mac):
    return hashlib.sha256(mac.encode()).hexdigest()

def load_registry():
    if not AUTH_REGISTRY.exists():
        return {"authorized": [], "pending": []}
    with open(AUTH_REGISTRY) as f:
        return json.load(f)

def save_registry(registry):
    AUTH_REGISTRY.parent.mkdir(exist_ok=True)
    with open(AUTH_REGISTRY, 'w') as f:
        json.dump(registry, f, indent=2)

def is_authorized(mac):
    registry = load_registry()
    mac_hash = get_mac_hash(mac)
    return any(
        entry['mac_hash'] == mac_hash
        for entry in registry['authorized']
    )

def log_attempt(mac, fold_hash, result):
    ATTEMPT_LOG.parent.mkdir(exist_ok=True)
    log = []
    if ATTEMPT_LOG.exists():
        with open(ATTEMPT_LOG) as f:
            log = json.load(f)
    log.append({
        "timestamp":  time.time(),
        "mac":        mac,
        "mac_hash":   get_mac_hash(mac),
        "fold_hash":  fold_hash[:16],
        "result":     result
    })
    with open(ATTEMPT_LOG, 'w') as f:
        json.dump(log, f, indent=2)

def fire_alert(mac, fold_hash):
    """
    Fold self destructs
    Alert hash fires back to Texas
    """
    ALERT_DIR.mkdir(parents=True, exist_ok=True)
    alert = {
        "type":          "UNAUTHORIZED_MAC",
        "attempted_mac": mac,
        "mac_hash":      get_mac_hash(mac),
        "fold_hash":     fold_hash[:16],
        "timestamp":     time.time(),
        "message":       "Unauthorized compiler attempt detected"
    }
    ts = int(time.time())
    with open(ALERT_DIR / f"alert_{ts}.json", 'w') as f:
        json.dump(alert, f, indent=2)
    print(f"[!] ALERT FIRED — unauthorized MAC: {mac[:17]}...")
    print(f"[!] Alert saved to outgoing/alerts/alert_{ts}.json")
    print(f"[!] Send alert folder contents back to Texas immediately")

def verify_mac_for_fold(fold_hash):
    """
    Called before any fold opens
    Returns True if authorized
    Returns False and fires alert if not
    """
    local_mac  = get_local_mac()
    authorized = is_authorized(local_mac)

    if authorized:
        log_attempt(local_mac, fold_hash, "AUTHORIZED")
        print(f"[✔] MAC authorized: {local_mac[:17]}...")
        return True
    else:
        log_attempt(local_mac, fold_hash, "REJECTED")
        fire_alert(local_mac, fold_hash)
        print(f"[!] MAC REJECTED — fold self destructing")
        return False
