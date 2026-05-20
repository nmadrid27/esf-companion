#!/usr/bin/env python3
"""CLI for the Defense Pack aggregator.

Usage:
    aggregate.py <workspace-dir> [--out PATH] [--scan-only]

Emits pack.json to stdout (default) or --out path.
With --scan-only, exits after emitting gaps[] for the periodic gap scanner.
"""
from __future__ import annotations
import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from esf_pack.aggregate import aggregate_from_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--scan-only", action="store_true",
                    help="Emit only gaps[] (for periodic gap scanner)")
    args = ap.parse_args()

    pack = aggregate_from_dir(args.workspace)
    payload = asdict(pack)
    if args.scan_only:
        payload = {"gaps": payload["gaps"], "project_name": payload["project_name"]}

    out_json = json.dumps(payload, indent=2, default=str)
    if args.out:
        args.out.write_text(out_json, encoding="utf-8")
    else:
        sys.stdout.write(out_json + "\n")


if __name__ == "__main__":
    main()
