from __future__ import annotations

import argparse
import sys

from .api import collect_spec
from .redaction import RedactionCategory, RedactionConfig


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="hostxray", add_help=True)

    p.add_argument(
        "--profile",
        default="standard",
        choices=["minimal", "standard", "full"],
        help="Collection profile controlling breadth/time.",
    )
    p.add_argument(
        "--format",
        default="json",
        choices=["json"],
        help="Output format.",
    )
    p.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON.",
    )
    p.add_argument(
        "--unsafe",
        action="store_true",
        help="Disable safe-mode (do not redact by default).",
    )
    p.add_argument(
        "--redact",
        nargs="+",
        choices=[c.value for c in RedactionCategory],
        help="Explicit redaction categories (overrides safe-mode).",
    )

    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    redaction: RedactionConfig | None = None
    if args.redact:
        redaction = RedactionConfig(
            enabled=True,
            categories={RedactionCategory(x) for x in args.redact},
        )

    spec = collect_spec(
        profile=args.profile,
        safe_mode=(not args.unsafe),
        redaction=redaction,
    )

    indent = 2 if args.pretty else None
    sys.stdout.write(spec.to_json(indent=indent))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
