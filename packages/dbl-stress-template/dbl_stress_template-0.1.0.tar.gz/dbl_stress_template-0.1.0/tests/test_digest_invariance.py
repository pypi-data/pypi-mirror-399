from __future__ import annotations

from pathlib import Path

from dbl_stress_template.runner import load_case, build_events, event_digest


def test_observational_changes_do_not_change_digest():
    root = Path(__file__).resolve().parents[1]
    case = load_case(root / "examples" / "demo_case.yaml")
    events = build_events(case)
    execution = events[1]
    changed = execution.observational | {"latency_ms": 999}
    from dbl_stress_template.model import Event
    changed_event = Event(
        t=execution.t,
        kind=execution.kind,
        id=execution.id,
        ts_utc=execution.ts_utc,
        refs=execution.refs,
        deterministic=execution.deterministic,
        observational=changed,
        digest=execution.digest,
    )
    assert event_digest(changed_event) == execution.digest
