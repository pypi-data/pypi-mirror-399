from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({k: _freeze(v) for k, v in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(v) for v in value)
    if isinstance(value, tuple):
        return tuple(_freeze(v) for v in value)
    return value


@dataclass(frozen=True)
class StressCase:
    case_id: str
    trigger: str
    normative_question: str
    authority: tuple[str, ...]
    irreversibility: str
    replay_requirement: str
    observations: Mapping[str, Any]
    execution: Mapping[str, Any]
    failure_signals: tuple[str, ...]
    ts_utc: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "observations", _freeze(dict(self.observations)))
        object.__setattr__(self, "execution", _freeze(dict(self.execution)))


@dataclass(frozen=True)
class Event:
    t: int
    kind: str
    id: str
    ts_utc: str
    refs: tuple[str, ...]
    deterministic: Mapping[str, Any]
    observational: Mapping[str, Any]
    digest: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "deterministic", _freeze(dict(self.deterministic)))
        object.__setattr__(self, "observational", _freeze(dict(self.observational)))


@dataclass(frozen=True)
class RunResult:
    case_id: str
    verdict: str
    failure_signals: tuple[str, ...]
    events: tuple[Event, ...]
    replay_ok: bool
