"""
worker_service.py
OS level daemon — runs at California VPS
Watches for incoming hash transmissions
Verifies integrity
Rebuilds payload from fold
Executes instructions
Folds report — sends back as hash
No persistent connection needed
Receives → executes → reports → sleeps
"""

import json
import hashlib
import time
import os
import subprocess
from pathlib import Path
from data_to_fold import encode_to_6base

WATCH_DIR  = Path("incoming")
DONE_DIR   = Path("executed")
OUT_DIR    = Path("output")
REPORT_DIR = Path("reports")

WATCH_DIR.mkdir(exist_ok=True)
DONE_DIR.mkdir(exist_ok=True)
OUT_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

def verify_transmission(transmission, folded):
    verify_obj = {
        "uid":       transmission["uid"],
        "seed":      transmission["seed"],
        "input":     folded,
        "timestamp": transmission["timestamp"]
    }
    computed = hashlib.sha256(
        json.dumps(verify_obj, sort_keys=True).encode()
    ).hexdigest()
    return computed == transmission["hash_key"]

def execute_payload(payload):
    """
    Execute instruction from payload
    Supports: shell commands, state updates,
    file writes, status checks
    Extend this as needed
    """
    result = {
        "status":    "unknown",
        "output":    "",
        "timestamp": time.time()
    }

    action = payload.get("action", "status")

    if action == "status":
        result["status"] = "ok"
        result["output"] = {
            "machine": os.uname().nodename,
            "uptime":  os.popen("uptime -p").read().strip(),
            "disk":    os.popen("df -h /").read().strip(),
            "memory":  os.popen("free -h").read().strip()
        }

    elif action == "shell":
        cmd = payload.get("command", "echo ok")
        out = subprocess.run(
            cmd, shell=True,
            capture_output=True, text=True, timeout=30
        )
        result["status"] = "executed"
        result["output"] = {
            "stdout": out.stdout.strip(),
            "stderr": out.stderr.strip(),
            "code":   out.returncode
        }

    elif action == "write_file":
        path    = Path(payload.get("path", "output/received.txt"))
        content = payload.get("content", "")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        result["status"] = "written"
        result["output"] = str(path)

    elif action == "ping":
        result["status"] = "alive"
        result["output"] = "worker online — California VPS"

    return result

def build_report(uid, seed, result, original_hash):
    report_data = {
        "worker":        "california_vps",
        "responding_to": original_hash[:16],
        "uid":           uid,
        "result":        result,
        "timestamp":     time.time()
    }

    folded = encode_to_6base(report_data)

    report_hash_obj = {
        "uid":       uid,
        "seed":      seed,
        "input":     folded,
        "timestamp": report_data["timestamp"]
    }
    report_hash = hashlib.sha256(
        json.dumps(report_hash_obj, sort_keys=True).encode()
    ).hexdigest()

    transmission = {
        "uid":       uid,
        "hash_key":  report_hash,
        "seed":      seed,
        "timestamp": report_data["timestamp"]
    }

    ts = int(report_data["timestamp"])
    with open(REPORT_DIR / f"report_{ts}.json", "w") as f:
        json.dump({"transmission": transmission, "fold": folded}, f, indent=2)

    print(f"[✔] Report folded — hash: {report_hash[:16]}...")
    print(f"[✔] Report strand: {folded['strand_length']} bits")
    print(f"[✔] Saved: reports/report_{ts}.json")
    print(f"[✔] Send this hash back to Texas: {report_hash[:16]}...")

def process_transmission(path):
    print(f"\n[+] Incoming: {path.name}")

    with open(path) as f:
        packet = json.load(f)

    transmission = packet["transmission"]
    folded       = packet["fold"]

    print(f"[+] UID: {transmission['uid']}")
    print(f"[+] Hash: {transmission['hash_key'][:16]}...")

    if not verify_transmission(transmission, folded):
        print("[!] Hash mismatch — rejected")
        return

    print("[✔] Integrity verified")

    payload = folded.get("payload", {})
    print(f"[+] Action: {payload.get('action', 'status')}")

    result = execute_payload(payload)
    print(f"[✔] Executed — status: {result['status']}")

    build_report(
        transmission["uid"],
        transmission["seed"],
        result,
        transmission["hash_key"]
    )

    path.rename(DONE_DIR / path.name)
    print(f"[✔] Moved to executed/")

def watch_loop():
    print("== HASHKEY WORKER SERVICE ==")
    print("== California VPS — OS Level ==")
    print(f"[+] Watching: {WATCH_DIR.resolve()}")
    print("[+] Waiting for transmissions...\n")

    while True:
        incoming = list(WATCH_DIR.glob("*.json"))
        for path in incoming:
            try:
                process_transmission(path)
            except Exception as e:
                print(f"[!] Error processing {path.name}: {e}")
        time.sleep(2)

if __name__ == "__main__":
    watch_loop()
