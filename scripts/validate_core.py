#!/usr/bin/env python3
"""Validate auth → project → area against a running API (Phase 2).

Usage:
  python scripts/validate_core.py
  TEST_API_URL=http://127.0.0.1:8000 python scripts/validate_core.py
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from tests.test_core_api import (  # noqa: E402
    _api_reachable,
    test_auth_project_area_flow,
    test_health,
)


def main() -> int:
    if not _api_reachable():
        print("API unreachable. Start backend with DATABASE_URL pointing at 127.0.0.1.")
        return 1

    try:
        test_health()
        print("OK  health")
        test_auth_project_area_flow()
        print("OK  auth → project → area flow")
    except AssertionError as exc:
        print(f"FAIL  {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())