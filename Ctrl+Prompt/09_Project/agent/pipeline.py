"""run — one command that does the whole pipeline.

connect → learn → (auto-approve gate) → triage → solve → report.
For power users, the individual commands still exist. Use `run` for the demo.
"""
from __future__ import annotations

import os
from argparse import Namespace

from . import connect, learn, report, solve, triage


def _line(msg):
    print(f"\n\033[1m▶ {msg}\033[0m" if os.isatty(1) else f"\n▶ {msg}")


def run(args) -> int:
    # 1) connect
    if args.mock:
        project = args.project or os.path.splitext(os.path.basename(args.mock))[0]
        cargs = Namespace(mock=args.mock, project=project, since=None,
                          redact=args.redact, test=None, discover=None)
    else:
        if not args.source:
            print("Usage: agent run --mock <file>  |  agent run --source <connection>")
            return 2
        project = args.source
        cargs = Namespace(mock=None, project=project, since=args.since,
                          redact=args.redact, test=None, discover=None)
    _line("connect")
    rc = connect.run(cargs)
    if rc:
        return rc
    canonical = os.path.join("data", f"{project}.canonical.json")

    # 2) learn — profile + propose (+ calibrate if --eval)
    _line("learn (profile + propose taxonomy)")
    learn.run(Namespace(canonical=canonical, approve=None,
                        auto_approve=False, eval=args.eval))

    # 3) gate — reuse an approved taxonomy, else auto-approve the draft for this run
    if os.path.exists("taxonomy.json") and not args.fresh:
        print("gate: reusing existing approved taxonomy.json")
    else:
        _line("learn --approve (auto, unreviewed unless calibrated)")
        learn.run(Namespace(canonical=None, approve="", auto_approve=True, eval=None))
        print("  note: auto-approved for this run — use `learn --approve` to review by hand")

    # 4) triage
    _line("triage")
    triage.run(Namespace(canonical=canonical))

    # 5) solve
    _line("solve")
    solve.run(Namespace())

    # 6) report
    _line("report")
    report.run(Namespace(canonical=canonical, format=args.format, out=args.out))
    return 0
