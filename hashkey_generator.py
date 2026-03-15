import os
import json
import hashlib
import time
from pathlib import Path

def sanitize_filename(name):
    return "".join(c for c in name if c.isalnum() or c in ('-', '_')).rstrip()

def create_hash_object(uid, seed, input_data):
    return {
        "uid": uid,
        "seed": seed,
        "input": input_data,
        "timestamp": time.time()
    }

def compute_hash(obj):
    json_bytes = json.dumps(obj, sort_keys=True).encode('utf-8')
    return hashlib.sha256(json_bytes).hexdigest()

def save_hash_data(uid, full_obj, hash_key, save_dir):
    os.makedirs(save_dir, exist_ok=True)

    safe_uid = sanitize_filename(uid)
    full_path = Path(save_dir) / f"{safe_uid}.json"
    txt_path = Path("known_hash.txt")

    full_obj["hash_key"] = hash_key

    with open(full_path, "w") as f:
        json.dump(full_obj, f, indent=2)

    with open(txt_path, "w") as f:
        f.write(hash_key + "\n")

    print(f"[+] Hash key saved: {full_path}")
    print(f"[+] known_hash.txt updated.")
    print(f"[✔] Hash key generated and stored.")

def load_input(input_path):
    with open(input_path, "r") as f:
        return json.load(f)

def main():
    print("== AI-Core HashKey Desktop Prototype ==")

    uid = input("Enter user/device UID: ").strip()
    mode = input("(G)enerate new or (L)oad existing hash key? ").strip().upper()

    if mode != "G":
        print("[!] Only generation is supported in this prototype.")
        return

    seed = input("Enter seed phrase or string: ").strip()

    input_path = Path("folded_input/folded_input.json")
    if not input_path.exists():
        print("[!] Error: folded_input/folded_input.json not found.")
        return

    input_data = load_input(input_path)
    obj = create_hash_object(uid, seed, input_data)
    hash_key = compute_hash(obj)

    save_hash_data(uid, obj, hash_key, Path.home() / ".ai_core/hashkeys")

if __name__ == "__main__":
    main()
