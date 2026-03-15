"""
data_to_fold.py
Takes any JSON data file
Encodes into 6-base pair fold strand
Seals JSON inside the fold
Writes to folded_input/folded_input.json
Ready for hashkey_generator.py to hash and seal
No AIA dependency. Standalone.
"""

import json
import hashlib
from pathlib import Path
from color_fold_encoder import expand_rgb_to_fold_state

def encode_to_6base(data_dict):
    data_bytes = json.dumps(data_dict, sort_keys=True).encode('utf-8')
    data_hash = hashlib.sha256(data_bytes).hexdigest()

    r = int(data_hash[0:2], 16)
    g = int(data_hash[2:4], 16)
    b = int(data_hash[4:6], 16)

    fold_state = expand_rgb_to_fold_state(r, g, b)

    am_freq = int(data_hash[6:10], 16) % 1170 + 530
    fm_freq = int(data_hash[10:14], 16) % 205 + 875

    am_binary = f"{am_freq:016b}"
    fm_binary = f"{fm_freq:016b}"

    l1_val = int(data_hash[14:17], 16) % 4096
    l2_val = int(data_hash[17:20], 16) % 4096
    l1_binary = f"{l1_val:012b}"
    l2_binary = f"{l2_val:012b}"

    hue_val = int(data_hash[20:22], 16) % 360
    hue_binary = f"{hue_val:09b}"

    six_base_strand = (
        am_binary +
        fold_state['binary_folded'] +
        hue_binary +
        fm_binary +
        l1_binary +
        l2_binary
    )

    folded_package = {
        "strand": six_base_strand,
        "strand_length": len(six_base_strand),
        "bases": {
            "A_am_freq":    am_binary,
            "T_rgb":        fold_state['binary_folded'],
            "C_hue":        hue_binary,
            "G_fm_freq":    fm_binary,
            "L1_link":      l1_binary,
            "L2_link":      l2_binary
        },
        "values": {
            "r": r, "g": g, "b": b,
            "am_freq_khz": am_freq,
            "fm_freq_mhz": fm_freq / 10.0,
            "hue_degrees": hue_val,
            "l1_neighbor": l1_val,
            "l2_neighbor": l2_val
        },
        "payload": data_dict,
        "payload_hash": data_hash
    }

    return folded_package

def fold_data_file(input_path, output_path="folded_input/folded_input.json"):
    with open(input_path, 'r') as f:
        data = json.load(f)

    folded = encode_to_6base(data)

    Path(output_path).parent.mkdir(exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(folded, f, indent=2)

    print(f"[+] Data folded into 6-base pair strand")
    print(f"[+] Strand length: {folded['strand_length']} bits")
    print(f"[+] Payload hash: {folded['payload_hash'][:16]}...")
    print(f"[+] AM: {folded['values']['am_freq_khz']} kHz")
    print(f"[+] FM: {folded['values']['fm_freq_mhz']} MHz")
    print(f"[+] Hue: {folded['values']['hue_degrees']}°")
    print(f"[+] L1 neighbor: {folded['values']['l1_neighbor']}")
    print(f"[+] L2 neighbor: {folded['values']['l2_neighbor']}")
    print(f"[✔] Written to {output_path} — ready for hashkey_generator.py")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python data_to_fold.py <your_data.json>")
    else:
        fold_data_file(sys.argv[1])
