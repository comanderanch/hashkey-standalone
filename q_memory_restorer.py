import os
import json
import hashlib
from pathlib import Path

def sanitize_filename(name):
    return "".join(c for c in name if c.isalnum() or c in ('-', '_')).rstrip()

def compute_hash(obj):
    json_bytes = json.dumps(obj, sort_keys=True).encode('utf-8')
    return hashlib.sha256(json_bytes).hexdigest()

def prompt_fold_input():
    print("Enter folded input values (as originally used):")
    try:
        r = int(input("  r (0–255): "))
        g = int(input("  g (0–255): "))
        b = int(input("  b (0–255): "))
        freq = int(input("  frequency: "))
        hue = float(input("  hue (0.0–1.0): "))
    except ValueError:
        print("[!] Invalid input. Aborting.")
        return None
    return {
        "r": r,
        "g": g,
        "b": b,
        "frequency": freq,
        "hue": hue
    }

def try_reconstruct(uid, seed, target_hash):
    folded = prompt_fold_input()
    if not folded:
        return None

    try:
        timestamp = float(input("  original timestamp: "))
    except ValueError:
        print("[!] Invalid timestamp. Aborting.")
        return None

    test_obj = {
        "uid": uid,
        "seed": seed,
        "input": folded,
        "timestamp": timestamp
    }

    test_hash = compute_hash(test_obj)
    if test_hash == target_hash:
        return folded
    else:
        print("❌ Manual reconstruction failed: Hash mismatch.")
        print(f"Generated : {test_hash}")
        print(f"Expected  : {target_hash if target_hash else '[not entered]'}")
        return None

def main():
    print("== AI-Core Memory Recovery Engine ==")

    uid = input("Enter user/device UID: ").strip()
    seed = input("Enter seed phrase: ").strip()

    hashkeys_dir = Path.home() / ".ai_core" / "hashkeys"
    safe_uid = sanitize_filename(uid)
    metadata_path = hashkeys_dir / f"{safe_uid}.json"

    if metadata_path.exists():
        with open(metadata_path, "r") as f:
            data = json.load(f)

        hash_obj = {
            "uid": data["uid"],
            "seed": data["seed"],
            "input": data["input"],
            "timestamp": data["timestamp"]
        }

        generated_hash = compute_hash(hash_obj)
        hash_key = input("Enter target hash key: ").strip()

        if generated_hash == hash_key:
            print(f"\n✅ Match found in {metadata_path}")
            print("🔁 Reconstructed input data:")
            print(json.dumps(data["input"], indent=2))
            return
        else:
            print("❌ Hash mismatch in local file.")
            print(f"Generated : {generated_hash}")
            print(f"Expected  : {hash_key}")
    else:
        print("[ℹ] No local file found — switching to stateless mode.")
        hash_key = input("Enter target hash key: ").strip()

        reconstructed = try_reconstruct(uid, seed, hash_key)
        if reconstructed:
            print("\n✅ Stateless recovery succeeded.")
            print("🔁 Reconstructed input data:")
            print(json.dumps(reconstructed, indent=2))

if __name__ == "__main__":
    main()

