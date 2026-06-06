"""Periodic gap scanner: snapshot + text report over the aggregator's output.

Single source of the scan snapshot, consumed by both `aggregate.py --scan-only`
(JSON) and gap_report (text), so the two cannot drift.
"""
from __future__ import annotations
from .schema import DefensePack, BriefRequirements


def _ps_status(pack: DefensePack) -> str:
    ps = pack.position_statement
    if ps is None:
        return "absent"
    if not (ps.stance and ps.what_matters_most and ps.non_negotiables):
        return "incomplete"
    return "present"


def build_scan_snapshot(pack: DefensePack, requirements: "BriefRequirements | None" = None) -> dict:
    ror_min = requirements.ror_minimum if requirements else None
    return {
        "schema_version": "1.0",
        "project_name": pack.project_name,
        "context": pack.context,
        "phase": pack.phase_at_export,
        "scaffolding_level": pack.scaffolding_level,
        "artifacts": {
            "position_statement": _ps_status(pack),
            "records_of_resistance": {
                "count": len(pack.records_of_resistance),
                "minimum": ror_min,
            },
            # Disclosure is auto-generated whenever a PS exists, so it is
            # effectively never "absent" in a pack with a PS.
            "ai_use_log": "present" if pack.ai_use_log is not None else "absent",
            "reflection": "present" if pack.reflection is not None else "absent",
            "disclosure": "present" if pack.disclosure is not None else "absent",
        },
        "gaps": [
            {
                "artifact": g.artifact,
                "severity": g.severity.value if hasattr(g.severity, "value") else g.severity,
                "message": g.message,
            }
            for g in pack.gaps
        ],
    }
