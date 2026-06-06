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


def _level(snapshot: dict) -> str:
    raw = (snapshot.get("scaffolding_level") or "").lower()
    for name in ("guided", "supported", "independent"):
        if name in raw:
            return name
    return "supported"


# Artifacts with a fillable template worth pointing a Guided-level user to.
# Auto-generated (disclosure) and no-template artifacts (evolution_log,
# workspace_layout, duplicate-record warnings) get no pointer.
_TEMPLATE_HINTS = {
    "position_statement": "position-statement-template.md",
    "record_of_resistance": "record-of-resistance-template.md",
    "ai_use_log": "ai-use-log-template.md",
    "reflection": "reflection-template.md",
}


def gap_report(snapshot: dict) -> str:
    level = _level(snapshot)
    arts = snapshot["artifacts"]
    lines = [f"[ESF gap check: {snapshot.get('project_name') or 'project'}]"]

    ps = arts["position_statement"]
    lines.append(f"Position Statement: {ps}")

    ror = arts["records_of_resistance"]
    if ror["minimum"] is not None:
        lines.append(f"Records of Resistance: {ror['count']} of {ror['minimum']} required")
    else:
        lines.append(f"Records of Resistance: {ror['count']}")

    lines.append(f"AI Use Log: {arts['ai_use_log']}")
    lines.append(f"Reflection: {arts['reflection']}")

    # Filter gaps by scaffolding level. Independent omits INFO; Guided/Supported show all.
    gaps = snapshot.get("gaps", [])
    if level == "independent":
        gaps = [g for g in gaps if g["severity"] in ("hard_stop", "warning")]

    if not gaps:
        lines.append("No gaps. Your artifact list is complete.")
    else:
        lines.append("")
        lines.append("Gaps:")
        for g in gaps:
            line = f"- [{g['severity']}] {g['message']}"
            if level == "guided":
                tmpl = _TEMPLATE_HINTS.get(g["artifact"])
                if tmpl:
                    line += f" (template: esf/toolkit/templates/{tmpl})"
            lines.append(line)

    return "\n".join(lines)
