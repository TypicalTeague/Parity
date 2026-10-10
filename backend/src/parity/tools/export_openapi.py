"""Export the executable FastAPI schema deterministically."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from parity.api.app import app


def render_openapi() -> str:
    return json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    rendered = render_openapi()
    if args.check:
        return 0 if args.path.exists() and args.path.read_text() == rendered else 1
    args.path.parent.mkdir(parents=True, exist_ok=True)
    args.path.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
