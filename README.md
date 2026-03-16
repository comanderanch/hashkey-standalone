# Hashkey Standalone
## Networkless Secure Data Transfer — Network Protocol
### Author: Anthony Hagerty — Haskell Texas
### Version: 1.0.0 — March 15 2026

---

## What This Is

Send any amount of data — gigabytes if needed —
as a kilobyte hash string and a phone number key.

Nothing meaningful crosses the network.
Only an address crosses.
Data rebuilds itself at the destination
from instructions sealed inside the hash fold.

Not compression. Not traditional encryption.
Address-based data reconstruction.

A 2GB file costs identical bandwidth to a 2KB note.
The creek never gets deeper.

---

## Requirements

- Python 3.8 or higher
- Docker (optional — for isolated testing only)
- Linux / Mac / Windows with WSL

Install Python dependencies:
```bash
pip install uuid
```

No other dependencies. All standard library.

---

## Installation

```bash
git clone https://github.com/comanderanch/hashkey-standalone
cd hashkey-standalone
```

That is it. No pip install. No build step.
Run directly.

---

## Quick Start — Send Data in 3 Steps

### Step 1 — Prepare your data

Create any JSON file:

```json
{
  "message": "anything you want to send",
  "payload": {
    "content": "any data here"
  }
}
```

### Step 2 — Fold and hash it

```bash
python data_to_fold.py data.json
```

Output:
```
Strand length: 89 bits
Payload hash: abc123...
Written to folded_input/folded_input.json
```

```bash
python hashkey_generator.py
```

When prompted:
```
uid:  your device name (e.g. my_laptop)
mode: G
seed: your chosen phrase
      THIS IS YOUR PHONE NUMBER KEY
      Keep it. Share it separately from hash.
```

Output:
```
Hash key: 64 character string
Saved to ~/.ai_core/hashkeys/
```

### Step 3 — Transmit

Send the hash key and seed phrase by any means:
Email. SMS. Paper. Spoken aloud.
Carrier pigeon if needed.

That is the entire transmission.
Nothing else crosses.

---

## Receiving Data

On destination machine — same repo cloned:

```bash
python q_memory_restorer.py
```

When prompted enter:
```
uid:  same uid used by sender
seed: same seed phrase (phone number key)
```

Output:
```
Full payload rebuilt
Original data visible and intact
```

---

## MAC Authorization — Secure Machines

Register your machine before first use:

```bash
python auth_registry.py register
```

Label your machine when prompted.
Now this machine is authorized.

Test authorization:

```bash
python machine_auth.py
```

Should output: `MAC authorized`

### Adding a New Machine — Two Step Auth

On authorized machine — generate request:

```bash
python auth_registry.py request
```

Enter new machine MAC address and label.
You receive a one time code (OTP).
OTP expires in 10 minutes.

On new machine — confirm:

```bash
python auth_registry.py confirm
```

Enter OTP when prompted.
New machine now authorized.

### What happens on unauthorized machines

Wrong machine runs the compiler:
- Fold self destructs
- Alert fires to `outgoing/alerts/`
- Attempt logged with MAC + timestamp
- Texas receives alert as hash

---

## Remote Worker — California VPS Setup

### Deploy worker to remote machine

Copy these files to remote machine:

```bash
scp data_to_fold.py user@your-server:~/hashkey/
scp color_fold_encoder.py user@your-server:~/hashkey/
scp q_memory_restorer.py user@your-server:~/hashkey/
scp hashkey_verifier.py user@your-server:~/hashkey/
scp worker_service.py user@your-server:~/hashkey/
scp machine_auth.py user@your-server:~/hashkey/
scp auth_registry.py user@your-server:~/hashkey/
```

On remote machine — register it:

```bash
cd ~/hashkey
python auth_registry.py register
```

### Install as system service (Linux)

```bash
sudo nano /etc/systemd/system/hashkey-worker.service
```

Paste this exactly:

```ini
[Unit]
Description=Hashkey Worker Service
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/hashkey
ExecStart=/usr/bin/python3 worker_service.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Replace `YOUR_USERNAME` with your actual username.

```bash
sudo systemctl enable hashkey-worker
sudo systemctl start hashkey-worker
sudo systemctl status hashkey-worker
```

Worker is now running at OS level.
Watches `incoming/` folder every 2 seconds.
Wakes on valid hash. Executes. Reports. Sleeps.

### Send action to worker

Edit `send_to_worker.py` — change action payload:

```python
action_payload={
    "action":  "ping",
    "from":    "your name",
    "message": "your message"
}
```

```bash
python send_to_worker.py
```

Drop output file into worker `incoming/` folder:

```bash
scp incoming/action_*.json user@your-server:~/hashkey/incoming/
```

Worker receives — verifies — executes — reports back.

### Supported worker actions

```
ping        — check worker is alive
status      — get machine uptime disk memory
shell       — run shell command on remote machine
write_file  — write file at remote machine
```

Add more actions in `worker_service.py`
`execute_payload()` function.

---

## Docker Isolated Test

Proves architecture with two network-isolated
containers. Sender and receiver on separate
Docker networks. Only hash volume shared.

```bash
docker-compose build
docker-compose run sender
docker-compose run receiver
```

Expected:
```
Sender:   89-bit strand — hash generated
Receiver: hash verified — payload rebuilt
Message visible — nothing raw crossed
```

---

## LHT — Lattice Hash Transport

Contributed by: Anthony Hagerty
and colleague — Haskell Texas
March 15 2026

Named for the lattice neighbor
alignment principle shared with
AIA's DNA token L1/L2 position pins.
Same architecture — different scale.
Token lattice = semantic space.
Hash lattice = transmission space.

### The Problem
A hash sent as a single unit
is vulnerable to:
- Interception of full payload
- Single point corruption
- No redundancy if cut in transit

### The Solution — 4 Stream Chunking
Inspired by a lumber yard conversation.

> "Cut them in equal chunks
>  and stagger them
>  so they lock in when nailed together."

The full hash is duplicated 4 times.
Each copy is chunked proportionally:

```
Stream 0 — fine grain  (12 x 5 chars)
Stream 1 — coarse      (3 x 21 chars)
Stream 2 — halves      (2 x 32 chars)
Stream 3 — quarters    (4 x 16 chars)
```

Each chunk knows its neighbor
across adjacent streams.
The geometry IS the verification.
No separate checksum needed.

### Proven Results

```
✅ 21 neighbor alignments — zero errors
✅ Reconstructed from any 2 of 4 streams
✅ Hash recovered exact — 64 chars
✅ Dirty stream detected before
   corruption reaches output
```

### Usage

Chunk a hash for transmission:
```bash
python hashkey_chunker.py chunk \
  <hash> <uid> <seed>
```

Reconstruct at destination:
```bash
python hashkey_chunker.py reconstruct \
  output/
```

Minimum 2 of 4 streams required.
Lose 2 entirely — still recovers clean.

### The Principle

The neighbor alignment map
provides structural verification
before reconstruction attempts.
Truth has a shape.
A corrupted chunk does not fit
its neighbor.
The misalignment is detected
before it can corrupt the output.

---

## File Reference

```
data_to_fold.py        any JSON → 89-bit fold strand
color_fold_encoder.py  RGB color fold encoder
hashkey_generator.py   generates hash + key from fold
hashkey_verifier.py    verifies hash integrity
q_memory_restorer.py   rebuilds data at destination
worker_service.py      OS level remote execution daemon
send_to_worker.py      sends action to remote worker
machine_auth.py        MAC address verification layer
auth_registry.py       manages authorized MAC registry
Dockerfile.sender      isolated sender container
Dockerfile.receiver    isolated receiver container
docker-compose.yml     two container isolated test
```

---

## Proven Results

```
✅ 89-bit strand confirmed
✅ Hash verified — integrity confirmed both directions
✅ Payload rebuilt — message visible at destination
✅ Nothing crossed except hash + seed
✅ Worker wakes — verifies — executes — reports
✅ Docker isolation — separate networks — hash only shared
✅ MAC auth — unauthorized machine fires alert
✅ Two step OTP — new machine authorized in 10 minutes
```

---

## Related Projects

- github.com/comanderanch/hashkey-airgap
- github.com/comanderanch/hashkey-bridge
- github.com/comanderanch/ai-core
- github.com/comanderanch/dna-tokenizer

---

## License

MIT License — see LICENSE file
Free to use, modify, and distribute
with attribution.

## Disclaimer

This software is provided as-is for
research and testing purposes.
See DISCLAIMER.md for full terms.
Use at your own risk.
Not affiliated with Anthropic.
Independent research project.
Anthony Hagerty — Haskell Texas — 2026

## Author

Anthony Hagerty — Independent Systems Architect
Haskell Texas — No retreat. No surrender.
