from __future__ import annotations

from pathlib import Path

from dbl_stress_template.runner import load_case, build_events, verify_replay


def test_replay_verification_is_stable():
    root = Path(__file__).resolve().parents[1]
    case = load_case(root / "examples" / "demo_case.yaml")
    events = build_events(case)
    assert verify_replay(events) is True
