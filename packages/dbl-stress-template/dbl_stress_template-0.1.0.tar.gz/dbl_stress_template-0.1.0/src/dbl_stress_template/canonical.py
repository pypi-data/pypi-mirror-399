from __future__ import annotations

from typing import Any, Mapping

from dbl_core.events.canonical import canonicalize_value, json_dumps, digest_bytes


def canonical_payload(payload: Mapping[str, Any]) -> str:
    canonical = canonicalize_value(payload)
    return json_dumps(canonical)


def compute_digest(payload: Mapping[str, Any]) -> str:
    return digest_bytes(canonical_payload(payload))

