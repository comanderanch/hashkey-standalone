import json
import hashlib
import sys
from pathlib import Path

def load_verification_data(hash_data_path):
    with open(hash_data_path, "r") as f:
        return json.load(f)

def load_known_hash(hash_path):
    with open(hash_path, "r") as f:
        return f.read().strip()

def compute_hash(obj):
    json_bytes = json.dumps(obj, sort_keys=True).encode("utf-8")
    return hashlib.sha256(json_bytes).hexdigest()

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 hashkey_verifier.py <folded_input.json> <known_hash.txt>")
        sys.exit(1)

    folded_input_path = Path(sys.argv[1])
    known_hash_path = Path(sys.argv[2])

    if not folded_input_path.exists() or not known_hash_path.exists():
        print("Error: One or both files not found.")
        sys.exit(1)

    # Ask for UID to find matching .json with full metadata
    uid = input("Enter user/device UID: ").strip()
    safe_uid = "".join(c for c in uid if c.isalnum() or c in ('-', '_')).rstrip()
    metadata_path = Path.home() / ".ai_core" / "hashkeys" / f"{safe_uid}.json"

    if not metadata_path.exists():
        print(f"[!] Metadata file not found: {metadata_path}")
        sys.exit(1)

    metadata = load_verification_data(metadata_path)
    known_hash = load_known_hash(known_hash_path)

    # Reconstruct full object from saved metadata
    full_obj = {
        "uid": metadata["uid"],
        "seed": metadata["seed"],
        "input": metadata["input"],
        "timestamp": metadata["timestamp"]
    }

    # Compute and compare
    generated_hash = compute_hash(full_obj)

    if generated_hash == known_hash:
        print("✅ Match: Hashes are identical.")
    else:
        print("❌ Mismatch: Hashes differ.")
        print(f"Generated : {generated_hash}")
        print(f"Expected  : {known_hash}")

if __name__ == "__main__":
    main()
