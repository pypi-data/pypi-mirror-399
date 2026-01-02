from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
import json
import yaml

from .canonical import compute_digest
from .model import Event, RunResult, StressCase


def load_case(path: Path) -> StressCase:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return StressCase(
        case_id=str(data["case_id"]),
        trigger=str(data["trigger"]),
        normative_question=str(data["normative_question"]),
        authority=tuple(data.get("authority", [])),
        irreversibility=str(data["irreversibility"]),
        replay_requirement=str(data["replay_requirement"]),
        observations=dict(data.get("observations", {})),
        execution=dict(data.get("execution", {})),
        failure_signals=tuple(data.get("failure_signals", [])),
        ts_utc=str(data.get("ts_utc", "1970-01-01T00:00:00Z")),
    )


def verdict_from_case(case: StressCase) -> str:
    return "FAIL" if case.failure_signals else "PASS"


def event_digest(event: Event) -> str:
    payload = {
        "t": event.t,
        "kind": event.kind,
        "id": event.id,
        "refs": event.refs,
        "deterministic": event.deterministic,
    }
    return compute_digest(payload)


def build_events(case: StressCase) -> list[Event]:
    verdict = verdict_from_case(case)
    base_refs: list[str] = []

    events: list[Event] = []

    def add_event(kind: str, eid: str, t: int, deterministic: Mapping[str, Any], observational: Mapping[str, Any]) -> None:
        ev = Event(
            t=t,
            kind=kind,
            id=eid,
            ts_utc=case.ts_utc,
            refs=tuple(sorted(base_refs)),
            deterministic=deterministic,
            observational=observational,
            digest="",
        )
        digest = event_digest(ev)
        ev = Event(
            t=ev.t,
            kind=ev.kind,
            id=ev.id,
            ts_utc=ev.ts_utc,
            refs=ev.refs,
            deterministic=ev.deterministic,
            observational=ev.observational,
            digest=digest,
        )
        events.append(ev)
        base_refs.append(eid)

    add_event(
        kind="INTENT",
        eid=f"{case.case_id}-intent",
        t=0,
        deterministic={
            "case_id": case.case_id,
            "trigger": case.trigger,
            "normative_question": case.normative_question,
            "authority": case.authority,
            "irreversibility": case.irreversibility,
            "replay_requirement": case.replay_requirement,
        },
        observational={},
    )

    add_event(
        kind="EXECUTION",
        eid=f"{case.case_id}-execution",
        t=1,
        deterministic={"case_id": case.case_id},
        observational=case.execution,
    )

    add_event(
        kind="PROOF",
        eid=f"{case.case_id}-proof",
        t=2,
        deterministic={"case_id": case.case_id},
        observational=case.observations,
    )

    add_event(
        kind="DECISION",
        eid=f"{case.case_id}-decision",
        t=3,
        deterministic={
            "case_id": case.case_id,
            "verdict": verdict,
            "failure_signals": case.failure_signals,
        },
        observational={},
    )

    return events


def verify_replay(events: list[Event]) -> bool:
    for ev in events:
        if ev.digest != event_digest(ev):
            return False
    return True


def run_case(case: StressCase) -> RunResult:
    events = build_events(case)
    replay_ok = verify_replay(events)
    verdict = verdict_from_case(case)
    return RunResult(
        case_id=case.case_id,
        verdict=verdict,
        failure_signals=tuple(case.failure_signals),
        events=tuple(events),
        replay_ok=replay_ok,
    )


def write_jsonl(events: list[Event], out_path: Path, *, mode: str = "w") -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open(mode, encoding="utf-8") as f:
        for ev in events:
            line = {
                "t": ev.t,
                "kind": ev.kind,
                "id": ev.id,
                "ts_utc": ev.ts_utc,
                "refs": list(ev.refs),
                "deterministic": ev.deterministic,
                "observational": ev.observational,
                "digest": ev.digest,
            }
            f.write(json.dumps(line, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
            f.write("\n")
