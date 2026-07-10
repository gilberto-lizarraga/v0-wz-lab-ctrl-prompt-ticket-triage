"""agent — CLI entrypoint. Five commands: connect · learn · triage · solve · report.

Stdlib argparse dispatch (production target: Typer). Run: `python -m agent <cmd>`.
"""
from __future__ import annotations

import argparse
import sys

from . import __version__, connect, learn, pipeline, report, solve, triage


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="agent",
                                description="Disney Agent Support Tickets — CLI triage agent")
    p.add_argument("--version", action="version", version=f"agent {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="ONE command: connect → learn → triage → solve → report")
    run.add_argument("--mock", help="offline: a canonical/raw JSON file")
    run.add_argument("--source", help="live: a connection name from connections.json")
    run.add_argument("--project", help="label for the mock source (default: filename)")
    run.add_argument("--since", help="live time window, e.g. 90d")
    run.add_argument("--redact", action="store_true", help="mask PII on real sources")
    run.add_argument("--eval", metavar="LABELED_JSON", help="calibrate + report F1")
    run.add_argument("--fresh", action="store_true", help="re-propose + re-approve taxonomy")
    run.add_argument("--format", choices=["terminal", "md", "json"], default="terminal")
    run.add_argument("--out", help="write the report to a file")
    run.set_defaults(func=pipeline.run)

    c = sub.add_parser("connect", help="Phase 0: collect + normalize a source → canonical JSON")
    c.add_argument("--mock", help="load a canonical/raw JSON offline (demo path)")
    c.add_argument("--project", help="neutral label for the source container")
    c.add_argument("--since", help="source-native time window, e.g. 90d")
    c.add_argument("--redact", action="store_true", help="mask PII on real sources")
    c.add_argument("--test", metavar="NAME", help="validate auth + reachability only")
    c.add_argument("--discover", metavar="NAME", help="inventory fields + vocab from a sample")
    c.set_defaults(func=connect.run)

    l = sub.add_parser("learn", help="OBSERVE + ADAPT: profile corpus, propose taxonomy")
    l.add_argument("canonical", nargs="?", help="path to a connect canonical JSON")
    l.add_argument("--approve", nargs="?", const="", help="promote draft → taxonomy.json")
    l.add_argument("--auto-approve", action="store_true",
                   help="CI/demo: approve but stamp calibration_status=unreviewed")
    l.add_argument("--eval", metavar="LABELED_JSON",
                   help="calibrate merge threshold via cluster_hint, report F1")
    l.set_defaults(func=learn.run)

    t = sub.add_parser("triage", help="ACT: cluster + effective priority (deterministic)")
    t.add_argument("canonical", help="path to a connect canonical JSON")
    t.set_defaults(func=triage.run)

    s = sub.add_parser("solve", help="ACT: root cause + evidence + playbook (LLM step)")
    s.set_defaults(func=solve.run)

    r = sub.add_parser("report", help="Consolidate into a readable document")
    r.add_argument("canonical", help="path to a connect canonical JSON")
    r.add_argument("--format", choices=["terminal", "md", "json"], default="terminal")
    r.add_argument("--out", help="write to a file instead of stdout")
    r.set_defaults(func=report.run)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
