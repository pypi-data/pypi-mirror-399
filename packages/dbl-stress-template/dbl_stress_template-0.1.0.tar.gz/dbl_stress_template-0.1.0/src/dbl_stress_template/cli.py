from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .runner import load_case, run_case, write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="DBL stress case runner")
    parser.add_argument("case", type=Path, help="Path to YAML stress case")
    parser.add_argument("--out", type=Path, default=Path("data/v_active.jsonl"))
    parser.add_argument("--append", action="store_true", help="Append to output instead of overwriting")
    args = parser.parse_args()

    case = load_case(args.case)
    result = run_case(case)
    mode = "a" if args.append else "w"
    write_jsonl(list(result.events), args.out, mode=mode)
    print(f"{result.case_id}: verdict={result.verdict} replay_ok={result.replay_ok}")
    sys.exit(0 if result.verdict == "PASS" and result.replay_ok else 2)


if __name__ == "__main__":
    main()
