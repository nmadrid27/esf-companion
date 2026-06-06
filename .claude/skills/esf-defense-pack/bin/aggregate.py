#!/usr/bin/env python3
"""CLI for the Defense Pack aggregator.

Usage:
    aggregate.py <workspace-dir> [--out PATH] [--scan-only]

Emits pack.json to stdout (default) or --out path.
With --scan-only, exits after emitting gaps[] for the periodic gap scanner.
With --strict, exits non-zero when the pack has a HARD_STOP gap (for CI callers).
"""
from __future__ import annotations
import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from esf_pack.aggregate import aggregate_from_dir, resolve_requirements
from esf_pack.gaps import has_hard_stop
from esf_pack.scan import build_scan_snapshot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--scan-only", action="store_true",
                    help="Emit only gaps[] (for periodic gap scanner)")
    ap.add_argument("--strict", action="store_true",
                    help="Exit non-zero if the pack has a HARD_STOP gap (for CI)")
    args = ap.parse_args()

    if args.scan_only:
        requirements = resolve_requirements(args.workspace)
        pack = aggregate_from_dir(args.workspace, requirements)
        payload = build_scan_snapshot(pack, requirements)
    else:
        pack = aggregate_from_dir(args.workspace)
        payload = asdict(pack)

    out_json = json.dumps(payload, indent=2, default=str)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(out_json, encoding="utf-8")
    else:
        sys.stdout.write(out_json + "\n")

    # --strict: signal non-defensibility to automated callers without changing
    # default behavior (the SKILL flow reads gaps[] from pack.json itself).
    if args.strict and has_hard_stop(pack.gaps):
        sys.exit(1)


if __name__ == "__main__":
    main()
