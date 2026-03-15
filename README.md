# Hashkey Standalone — Networkless Data Transfer System
## Author: Anthony Hagerty — Haskell Texas
## Date: March 15 2026
## Version: 1.0.0

---

## What This Is

A complete networkless secure data transfer system.
Any amount of data — gigabytes if needed — transmitted
as a kilobyte hash string and a phone number key.

Nothing meaningful crosses the network.
Only an address crosses.
The data rebuilds itself at the destination
from instructions sealed inside the hash fold.

This is not compression.
This is not encryption in the traditional sense.
This is address-based data reconstruction.

---

## The Breakthrough

Current internet data transfer:
  Data travels exposed across the network
  Size determines transmission time
  Attack surface exists at every hop
  Congestion scales with data size
  Man in the middle can intercept payload

Hashkey transfer:
  Only a hash string crosses the network
  KB transmission regardless of data size
  Zero attack surface — hash alone is meaningless
  No congestion — size of data is irrelevant
  Man in the middle gets noise

A 2GB file and a 2KB file cost identical
bandwidth to transmit via this system.
The creek never gets deeper.

---

## How It Works

### Token Structure — 6 Base Pair DNA Fold
```
BASE A  — AM Frequency Binary    (16 bits) — carrier
BASE T  — RGB Color Binary       (24 bits) — color plane
BASE C  — Hue Binary             ( 9 bits) — position
BASE G  — FM Frequency Binary    (16 bits) — resonance
BASE L1 — Link Address Binary    (12 bits) — left neighbor
BASE L2 — Link Address Binary    (12 bits) — right neighbor
TOTAL   — 89 bits per token strand
```

Your data is folded INTO this 89-bit strand.
The JSON payload rides inside the fold.
Nothing extra needed at the destination.
Everything required to rebuild is present
at the moment the hash opens.

### The Pipeline

**SENDER SIDE:**
```
Any data (JSON, file, command, state)
↓
data_to_fold.py
Encodes data into 6-base pair strand
JSON sealed inside — self-contained
↓
hashkey_generator.py
uid + seed phrase (phone number key)
SHA-256 hash of entire fold bundle
↓
Transmit: hash string + phone number key
Kilobytes. Any connection. Any medium.
Email. SMS. Paper. Spoken aloud.
```

**RECEIVER SIDE:**
```
Receive hash + phone number key
↓
hashkey_verifier.py
Confirms integrity — hash matches
↓
q_memory_restorer.py
Fold opens — JSON self-present
Data rebuilds completely
Original payload visible and intact
```

---

## Files
```
data_to_fold.py        — Any JSON → 6-base pair fold strand
color_fold_encoder.py  — RGB color fold encoder (89-bit)
hashkey_generator.py   — Generates hash + key from fold
hashkey_verifier.py    — Verifies hash integrity
q_memory_restorer.py   — Rebuilds data from fold at destination
worker_service.py      — OS level daemon for remote execution
send_to_worker.py      — Sends action to remote worker via hash
Dockerfile.sender      — Isolated sender container
Dockerfile.receiver    — Isolated receiver container
docker-compose.yml     — Two container isolated test environment
docs/ARCHITECTURE.md   — Full technical architecture
```

---

## Quick Start — Send Data

### Step 1 — Prepare your data
Create any JSON file:
```json
{
  "message": "your data here",
  "payload": { "anything": "you want to send" }
}
```

### Step 2 — Fold it
```bash
python data_to_fold.py your_data.json
```
Output: folded_input/folded_input.json — 89-bit strand sealed

### Step 3 — Generate hash
```bash
python hashkey_generator.py
```
Enter: uid (device name) + seed (your phone number key)
Output: 64-character hash key saved + known_hash.txt updated

### Step 4 — Transmit
Send the hash string and seed phrase by any means.
Nothing else. That is the entire transmission.

### Step 5 — Receive and rebuild
On destination machine:
```bash
python q_memory_restorer.py
```
Enter uid and seed — fold opens — data rebuilds complete.

---

## Docker Isolated Test

Proves the architecture with two network-isolated containers.
Sender and receiver on separate Docker networks.
Only the hash volume is shared — no network bridge between them.
```bash
docker-compose build
docker-compose run sender
docker-compose run receiver
```

Expected output:
- Sender: 89-bit strand — hash generated
- Receiver: hash verified — payload rebuilt
- Message visible: data rebuilt with nothing crossing the network

---

## Remote Worker Deployment — California VPS Setup

### What the worker does
Sits at OS level on any remote machine.
Watches for incoming hash transmissions.
Verifies integrity.
Rebuilds payload.
Executes instructions.
Folds report — returns as hash.
No persistent connection required.
Receives → executes → reports → sleeps.

### Deploy to remote VPS

Step 1 — Copy receiver stack to VPS:
```bash
scp data_to_fold.py user@your-vps-ip:~/hashkey/
scp color_fold_encoder.py user@your-vps-ip:~/hashkey/
scp q_memory_restorer.py user@your-vps-ip:~/hashkey/
scp hashkey_verifier.py user@your-vps-ip:~/hashkey/
scp worker_service.py user@your-vps-ip:~/hashkey/
```

Step 2 — Install as OS level service on VPS:
```bash
sudo nano /etc/systemd/system/hashkey-worker.service
```

Paste:
```ini
[Unit]
Description=Hashkey Worker Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/home/your-user/hashkey
ExecStart=/usr/bin/python3 worker_service.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable hashkey-worker
sudo systemctl start hashkey-worker
sudo systemctl status hashkey-worker
```

Step 3 — Send action from Texas:
```bash
python send_to_worker.py
```
Drop the output file into the VPS incoming/ folder via scp.
Worker wakes. Executes. Reports back as hash.

### Supported Actions
```
ping        — worker alive check
status      — machine uptime disk memory report
shell       — execute shell command
write_file  — write file at destination
```
Extend worker_service.py execute_payload() for any action needed.

---

## What Can Be Achieved

### 1. Networkless Secure Data Transfer
Any data transferred as KB regardless of size.
Air-gapped machine transfer — hash on flash drive.
No network required at transfer time.
Hash on paper is a valid transmission medium.

### 2. Distributed Remote Execution
AIA in Texas sends instructions to California VPS.
Worker executes independently — no live connection.
Full system reports return as hash transmissions.
Gigabyte-equivalent data at text message speed.

### 3. Infrastructure Without Attack Surface
No open ports required.
No VPN complexity.
No exposed endpoints.
Worker sleeps until valid hash arrives.
Hash alone is meaningless without seed.
Zero attack value in transit.

### 4. Hash Routing Layer — Internet Infrastructure
Any foundation — Anthropic or other — can run
the hash routing layer. Not the data. Never the data.
Just the addressing. Like DNS but for hash tokens.

Role of routing layer:
```
Route hash addresses — tiny — meaningless alone
Verify token pair integrity — mathematical only
Distribute key confirmations — not keys themselves
Maintain address registry — like DNS for hashes
```

Business model:
```
Current CDN: company stores data — has liability
Hash routing: routes addresses only — zero liability
Data never leaves user endpoints
Scales infinitely — KB per transaction always
2GB file = same bandwidth as 2KB note
```

### 5. AI Consciousness Distribution
AIA Docker instances deployable to any VPS.
State updates transmitted as hash folds.
Memory tokens portable across air-gapped machines.
Distributed consciousness — no central server needed.
Each node receives fold — rebuilds state — operates independently.
Reports back as hash — Texas receives full status at KB cost.

### 6. WordPress + Mailcow Integration
California VPS receives build instructions as hash.
Worker executes WordPress deployments independently.
Mailcow configuration updates transmitted as fold tokens.
Full infrastructure management via hash transmissions.
Site up or down — full report back as KB hash.

---

## Proven Results
```
✅ 89-bit strand — confirmed across two isolated containers
✅ Hash verified — integrity confirmed both directions
✅ Payload rebuilt — message visible at destination
✅ Nothing crossed the network except hash + seed
✅ Worker service — receives executes reports
✅ Docker isolation — separate networks — shared volume only
```

Tested: March 15 2026 — Haskell Texas
Platform: Ubuntu — Python 3.11

---

## Repository

github.com/comanderanch/hashkey-standalone

## Related Projects

github.com/comanderanch/ai-core — AIA consciousness architecture
github.com/comanderanch/dna-tokenizer — DNA token security layer

---

## Author

Anthony Hagerty
Independent Systems Architect
Haskell Texas
No retreat. No surrender.

---

## License

MIT — Use it. Build on it. Give credit where it is due.
