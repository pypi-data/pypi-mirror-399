#!/usr/bin/env python3
"""
Simple OpenTimestamps stamping via HTTP API.
No OpenSSL dependency - uses calendars directly.

Usage:
    python ots_stamp.py stamp file.pdf       # Creates file.pdf.ots
    python ots_stamp.py info file.pdf.ots    # Shows timestamp info
"""
import sys
import hashlib
import requests
from pathlib import Path

# OpenTimestamps calendar servers
CALENDARS = [
    "https://a.pool.opentimestamps.org",
    "https://b.pool.opentimestamps.org",
    "https://a.pool.eternitywall.com",
]

def sha256_file(filepath):
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.digest()

def stamp_file(filepath):
    """Submit file hash to OpenTimestamps calendars."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: File not found: {filepath}")
        return False

    file_hash = sha256_file(path)
    print(f"SHA-256: {file_hash.hex()}")

    # Try each calendar
    for calendar in CALENDARS:
        try:
            url = f"{calendar}/digest"
            response = requests.post(
                url,
                data=file_hash,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            if response.status_code == 200:
                ots_path = path.with_suffix(path.suffix + '.ots')
                with open(ots_path, 'wb') as f:
                    f.write(response.content)
                print(f"Timestamp submitted to: {calendar}")
                print(f"Proof saved: {ots_path}")
                print(f"\nNote: Bitcoin confirmation takes ~1-2 hours.")
                print(f"Run 'ots upgrade {ots_path}' later to complete the proof.")
                return True
        except Exception as e:
            print(f"Calendar {calendar} failed: {e}")
            continue

    print("Error: All calendars failed")
    return False

def info_file(ots_path):
    """Display basic info about an .ots file."""
    path = Path(ots_path)
    if not path.exists():
        print(f"Error: File not found: {ots_path}")
        return

    with open(path, 'rb') as f:
        data = f.read()

    # Check for OTS magic bytes
    if data[:3] == b'\x00\x4f\x54':
        print(f"File: {ots_path}")
        print(f"Format: OpenTimestamps proof")
        print(f"Size: {len(data)} bytes")
        print(f"\nTo verify, install full OTS client or use:")
        print(f"  https://opentimestamps.org (drag & drop)")
    else:
        print(f"Warning: May not be a valid .ots file")

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        print("\nCommands:")
        print("  stamp <file>     Create timestamp proof")
        print("  info <file.ots>  Show proof info")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    filepath = sys.argv[2]

    if cmd == "stamp":
        stamp_file(filepath)
    elif cmd == "info":
        info_file(filepath)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
