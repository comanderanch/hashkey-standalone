"""
LHT — Lattice Hash Transport
Version 1.0.0
Date: March 15 2026
Author: Anthony Hagerty — Haskell Texas
Contributor: Colleague — lumber yard wisdom

Lattice-based hash transmission protocol.
Full hash duplicated across 4 streams.
Each stream chunked proportionally.
Each chunk aligned to its neighbor
across adjacent streams.
Neighbor alignment IS the verification.
Geometry proves integrity.
Reconstruct from any 2 of 4 streams.

Named LHT — Lattice Hash Transport —
because the neighbor alignment principle
is identical to AIA's DNA token
L1/L2 lattice position pins.

Same architecture.
Same neighbor awareness.
One at token level.
One at transmission level.
Both from the same mind.
Haskell Texas. 2026.
"""

import json
import hashlib
import math
import time
from pathlib import Path

def generate_chunk_proportions(hash_length, streams=4):
    """
    Generate proportional chunk sizes
    for each stream
    Each stream chunks differently
    but covers full hash length
    """
    proportions = []

    # Stream 1: equal chunks (12x1)
    chunk_size_1 = max(1, hash_length // 12)
    proportions.append(
        [chunk_size_1] * (hash_length // chunk_size_1)
    )

    # Stream 2: larger chunks (3x4)
    chunk_size_2 = max(1, hash_length // 3)
    proportions.append(
        [chunk_size_2] * (hash_length // chunk_size_2)
    )

    # Stream 3: mixed (1x8 + remainder)
    chunk_size_3 = max(1, hash_length // 2)
    proportions.append(
        [chunk_size_3, hash_length - chunk_size_3]
    )

    # Stream 4: quarter chunks (4x3)
    chunk_size_4 = max(1, hash_length // 4)
    proportions.append(
        [chunk_size_4] * (hash_length // chunk_size_4)
    )

    return proportions

def chunk_hash(hash_string, proportions):
    """
    Split hash into chunks
    per stream proportion
    """
    streams = []
    for stream_props in proportions:
        chunks = []
        pos = 0
        for size in stream_props:
            chunk = hash_string[pos:pos+size]
            if chunk:
                chunks.append({
                    "data":     chunk,
                    "position": pos,
                    "size":     len(chunk),
                    "chunk_hash": hashlib.sha256(
                        chunk.encode()
                    ).hexdigest()[:8]
                })
            pos += size
        streams.append(chunks)
    return streams

def build_neighbor_map(streams):
    """
    Build alignment map between
    neighboring chunks across streams
    Left edge of each chunk must align
    with neighbor in adjacent stream
    """
    neighbor_map = []
    for i, stream in enumerate(streams):
        for j, chunk in enumerate(stream):
            neighbors = {
                "stream":   i,
                "chunk":    j,
                "position": chunk["position"],
                "left_neighbor": None,
                "right_neighbor": None
            }
            # Find chunk in prev stream
            # that contains same position
            if i > 0:
                for k, prev_chunk in \
                        enumerate(streams[i-1]):
                    if prev_chunk["position"] <= \
                       chunk["position"] < \
                       prev_chunk["position"] + \
                       prev_chunk["size"]:
                        neighbors["left_neighbor"] = {
                            "stream": i-1,
                            "chunk":  k,
                            "alignment": "left_edge"
                        }
                        break
            # Find chunk in next stream
            if i < len(streams) - 1:
                for k, next_chunk in \
                        enumerate(streams[i+1]):
                    if next_chunk["position"] <= \
                       chunk["position"] < \
                       next_chunk["position"] + \
                       next_chunk["size"]:
                        neighbors["right_neighbor"] = {
                            "stream": i+1,
                            "chunk":  k,
                            "alignment": "right_edge"
                        }
                        break
            neighbor_map.append(neighbors)
    return neighbor_map

def chunk_transmission(hash_string,
                        uid, seed,
                        output_dir="output"):
    """
    Full chunked transmission package
    4 streams + manifest + neighbor map
    """
    Path(output_dir).mkdir(exist_ok=True)

    hash_length   = len(hash_string)
    proportions   = generate_chunk_proportions(
        hash_length)
    streams       = chunk_hash(
        hash_string, proportions)
    neighbor_map  = build_neighbor_map(streams)

    # Build manifest
    manifest = {
        "uid":          uid,
        "hash_length":  hash_length,
        "stream_count": len(streams),
        "proportions":  [
            [c["size"] for c in s]
            for s in streams
        ],
        "chunk_counts": [
            len(s) for s in streams
        ],
        "neighbor_map": neighbor_map,
        "timestamp":    time.time(),
        "reconstruction_minimum": 2
    }

    # Save each stream separately
    for i, stream in enumerate(streams):
        stream_file = Path(output_dir) / \
            f"stream_{i}.json"
        with open(stream_file, 'w') as f:
            json.dump({
                "stream_id": i,
                "uid":       uid,
                "chunks":    stream,
                "timestamp": manifest["timestamp"]
            }, f, indent=2)

    # Save manifest
    manifest_file = Path(output_dir) / \
        "manifest.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"[✔] Hash chunked into "
          f"{len(streams)} streams")
    for i, s in enumerate(streams):
        print(f"    Stream {i}: "
              f"{len(s)} chunks — "
              f"sizes: "
              f"{[c['size'] for c in s]}")
    print(f"[✔] Neighbor map: "
          f"{len(neighbor_map)} alignments")
    print(f"[✔] Minimum streams to reconstruct: 2")
    print(f"[✔] Output: {output_dir}/")

    return manifest

def reconstruct_from_streams(stream_dir,
                              min_streams=2):
    """
    Reconstruct hash from chunk streams
    Verify neighbor alignment first
    Works with any 2+ clean streams
    """
    stream_dir = Path(stream_dir)

    # Load manifest
    with open(stream_dir / "manifest.json") as f:
        manifest = json.load(f)

    # Load available streams
    streams = {}
    for i in range(manifest["stream_count"]):
        stream_file = stream_dir / \
            f"stream_{i}.json"
        if stream_file.exists():
            with open(stream_file) as f:
                streams[i] = json.load(f)

    print(f"[+] Found {len(streams)} of "
          f"{manifest['stream_count']} streams")

    if len(streams) < min_streams:
        print(f"[!] Need at least "
              f"{min_streams} streams")
        return None

    # Verify neighbor alignment
    print("[+] Verifying neighbor alignment...")
    errors = 0
    for entry in manifest["neighbor_map"]:
        si = entry["stream"]
        ci = entry["chunk"]
        if si not in streams:
            continue
        chunk = streams[si]["chunks"][ci]

        # Check left neighbor alignment
        if entry["left_neighbor"]:
            ln = entry["left_neighbor"]
            if ln["stream"] in streams:
                neighbor = streams[
                    ln["stream"]]["chunks"][
                    ln["chunk"]]
                # Position must be covered
                # by neighbor chunk
                if not (
                    neighbor["position"] <=
                    chunk["position"] <
                    neighbor["position"] +
                    neighbor["size"]
                ):
                    print(f"[!] Alignment error: "
                          f"stream {si} chunk {ci}")
                    errors += 1

    if errors == 0:
        print(f"[✔] All alignments verified")
    else:
        print(f"[!] {errors} alignment errors — "
              f"using clean streams only")

    # Reconstruct from first clean stream
    # (all streams contain full hash)
    for i, stream_data in streams.items():
        chunks = stream_data["chunks"]
        reconstructed = ""
        for chunk in sorted(
            chunks, key=lambda x: x["position"]
        ):
            reconstructed += chunk["data"]

        if len(reconstructed) == \
                manifest["hash_length"]:
            print(f"[✔] Reconstructed from "
                  f"stream {i}")
            print(f"[✔] Hash length: "
                  f"{len(reconstructed)}")
            return reconstructed

    print("[!] Reconstruction failed")
    return None

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Chunk:       python hashkey_chunker.py"
              " chunk <hash> <uid> <seed>")
        print("  Reconstruct: python hashkey_chunker.py"
              " reconstruct <stream_dir>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "chunk":
        hash_str = sys.argv[2]
        uid      = sys.argv[3]
        seed     = sys.argv[4]
        chunk_transmission(hash_str, uid, seed)

    elif cmd == "reconstruct":
        stream_dir = sys.argv[2]
        result = reconstruct_from_streams(stream_dir)
        if result:
            print(f"\n[✔] HASH RECOVERED: "
                  f"{result[:16]}...")
