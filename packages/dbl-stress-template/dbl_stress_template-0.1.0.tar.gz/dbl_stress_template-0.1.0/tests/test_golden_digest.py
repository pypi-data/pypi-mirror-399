from __future__ import annotations

from pathlib import Path

from dbl_stress_template.runner import load_case, build_events


def test_golden_decision_digest():
    root = Path(__file__).resolve().parents[1]
    case = load_case(root / "examples" / "demo_case.yaml")
    events = build_events(case)
    decision = events[-1]
    assert decision.kind == "DECISION"
    expected_refs = tuple(
        sorted(
            [
                f"{case.case_id}-intent",
                f"{case.case_id}-execution",
                f"{case.case_id}-proof",
            ]
        )
    )
    assert decision.refs == expected_refs
    assert decision.digest == "2f7de6f1ea1d41b8938287901c507ab70a8630eb7c70589e598d39040e3ca9d2"
