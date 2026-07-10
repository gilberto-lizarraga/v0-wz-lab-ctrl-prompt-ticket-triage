"""Live source collection — descriptor-driven, stdlib only (urllib + csv).

Supports real REST sources (Jira Cloud, generic paginated REST) and file sources
(CSV / JSON exports). Secrets are resolved from environment variables by NAME.
"""
from __future__ import annotations

import base64
import csv
import glob
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

try:
    import yaml            # type: ignore
    _HAVE_YAML = True
except ImportError:
    _HAVE_YAML = False

_ENV_RE = re.compile(r"\$\{(\w+)(?::-([^}]*))?\}")


# ── config loading ─────────────────────────────────────────────────────────
def _read_config(path: str):
    with open(path, encoding="utf-8") as fh:
        if path.endswith((".yaml", ".yml")) and _HAVE_YAML:
            return yaml.safe_load(fh)
        return json.load(fh)


def load_connections() -> dict:
    for path in ("connections.yaml", "connections.json", "connections.example.json"):
        if os.path.exists(path):
            return _read_config(path)
    raise SystemExit("No connections file. Copy connections.example.json → connections.json")


def get_connection(name: str) -> dict:
    conf = load_connections()
    for c in conf.get("connections", []):
        if c.get("name") == name:
            return c
    raise SystemExit(f"Connection '{name}' not found. Check your connections file.")


def load_descriptor(path: str) -> dict:
    # allow .yaml in config but prefer a .json sibling when PyYAML is absent
    if path.endswith((".yaml", ".yml")) and not _HAVE_YAML:
        alt = os.path.splitext(path)[0] + ".json"
        if os.path.exists(alt):
            path = alt
    if not os.path.exists(path):
        raise SystemExit(f"Descriptor not found: {path}")
    return _read_config(path)


def resolve_env(value, extra: dict | None = None):
    """Expand ${VAR} / ${VAR:-default}. Lookup order: environment → connection vars → default."""
    if not isinstance(value, str):
        return value
    extra = extra or {}

    def repl(m):
        var, default = m.group(1), m.group(2)
        if var in os.environ:
            return os.environ[var]
        if var in extra:
            return str(extra[var])
        if default is not None:
            return default
        raise SystemExit(f"Variable {var} is not set (env or connection 'vars').")

    return _ENV_RE.sub(repl, value)


# ── JSONPath-lite + mapping ────────────────────────────────────────────────
def resolve_path(obj, path: str):
    if not path.startswith("$"):
        return path
    cur = obj
    for part in path.lstrip("$").lstrip(".").split("."):
        if part in ("", "[*]"):
            continue
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
    return cur


def _map_value(record, expr, kind):
    if not isinstance(expr, str):
        return expr
    if expr.startswith("= "):
        return expr[2:]
    if "||" in expr:
        for alt in expr.split("||"):
            v = _map_value(record, alt.strip(), kind)
            if v not in (None, ""):
                return v
        return None
    if kind == "file":
        return record.get(expr)               # column name
    return resolve_path(record, expr)          # rest json path


def _coerce_text(v):
    if v is None:
        return ""
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


def apply_mapping(record: dict, descriptor: dict) -> dict:
    kind = descriptor.get("kind", "rest")
    mp = descriptor["mapping"]
    norm = descriptor.get("normalize", {})
    unmapped_key = descriptor.get("capture_unmapped", "raw_extra")

    out = {}
    for canon, expr in mp.items():
        out[canon] = _map_value(record, expr, kind)

    # normalize declared_priority + status via the descriptor tables
    for field, table in norm.items():
        raw = out.get(field)
        key = str(raw).strip().lower() if raw is not None else None
        low_table = {str(k).lower(): v for k, v in table.items() if k != "default"}
        first = re.split(r"[^a-z0-9]+", key)[0] if key else None
        if key in low_table:
            out[field] = low_table[key]
        elif first in low_table:               # e.g. "p1 - major bug ..." → "p1"
            out[field] = low_table[first]
        else:
            out[field] = table.get("default")

    out["title"] = _coerce_text(out.get("title"))
    out["body"] = _coerce_text(out.get("body")) or _coerce_text(out.get("title"))

    mapped_sources = set()
    for expr in mp.values():
        if not isinstance(expr, str) or expr.startswith("= "):
            continue
        for alt in expr.split("||"):
            alt = alt.strip()
            if alt.startswith("$"):
                mapped_sources.add(alt.lstrip("$").lstrip(".").split(".")[0])
            elif kind == "file":
                mapped_sources.add(alt)
    extra = {k: v for k, v in record.items() if k not in mapped_sources}
    out[unmapped_key] = extra
    return out


# ── HTTP ───────────────────────────────────────────────────────────────────
def _auth_headers(auth: dict) -> dict:
    method = (auth or {}).get("method", "none")
    if method == "none":
        return {}
    if method == "basic":
        user = os.environ.get(auth.get("user_env", ""), "")
        token = os.environ.get(auth.get("token_env", ""), "")
        raw = base64.b64encode(f"{user}:{token}".encode()).decode()
        return {"Authorization": f"Basic {raw}"}
    if method in ("bearer", "oauth2"):
        token = os.environ.get(auth.get("token_env", ""), "")
        return {"Authorization": f"Bearer {token}"}
    if method == "api_token":
        token = os.environ.get(auth.get("token_env", ""), "")
        header = auth.get("header", "Authorization")
        return {header: token}
    raise SystemExit(f"Unsupported auth method: {method}")


def _http_get(url: str, headers: dict, params: dict, timeout: int = 30):
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={**headers, "Accept": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise SystemExit(f"Auth failed ({e.code}). Check your token env vars.")
            if e.code == 429 and attempt < 3:
                wait = int(e.headers.get("Retry-After", 2 ** attempt))
                time.sleep(wait)
                continue
            raise SystemExit(f"HTTP {e.code} from {url}")
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise SystemExit(f"Network error: {e}. Consider `--mock` for the demo.")
    return {}


# ── collectors ─────────────────────────────────────────────────────────────
def effective_request(conn: dict, descriptor: dict) -> tuple[str, dict]:
    """Build the resolved URL + query for a REST connection (no network). Preview-friendly."""
    cvars = conn.get("vars") or {}
    base = resolve_env(conn["base_url"], cvars).rstrip("/")
    t = descriptor["transport"]
    url = base + t["list_path"]
    query = {k: resolve_env(v, cvars) for k, v in (t.get("query") or {}).items()}
    # connection-level query override (per-company project / JQL / filters)
    for k, v in (conn.get("query") or {}).items():
        query[k] = resolve_env(v, cvars)
    return url, query


def _collect_rest(conn: dict, descriptor: dict, limit: int | None = None) -> list[dict]:
    cvars = conn.get("vars") or {}
    headers = _auth_headers(conn.get("auth", {}))
    for k, v in (conn.get("headers") or {}).items():
        headers[k] = resolve_env(v, cvars)

    t = descriptor["transport"]
    url, query = effective_request(conn, descriptor)
    pg = descriptor.get("pagination", {"style": "none"})
    style = pg.get("style", "none")
    selector = t.get("record_selector", "$")

    records: list[dict] = []
    if style == "offset":
        start = 0
        size = pg.get("page_size", 100)
        while True:
            params = {**query, pg.get("offset_param", "startAt"): start,
                      pg.get("page_size_param", "maxResults"): size}
            resp = _http_get(url, headers, params)
            batch = resolve_path(resp, selector) or []
            records.extend(batch)
            total = resolve_path(resp, pg.get("total_path", "$.total"))
            start += len(batch) or size
            if not batch or (total is not None and start >= total):
                break
            if limit and len(records) >= limit:
                break
    else:  # 'none' or single page
        resp = _http_get(url, headers, query)
        records = resolve_path(resp, selector) or []

    if limit:
        records = records[:limit]
    return records


def _collect_file(conn: dict, descriptor: dict, limit: int | None = None) -> list[dict]:
    path = resolve_env(conn.get("path", descriptor.get("path", "")))
    matches = glob.glob(path)
    if not matches:
        raise SystemExit(f"No files matched: {path}")
    rows: list[dict] = []
    for fp in matches:
        if fp.endswith((".json", ".ndjson")):
            data = _read_config(fp) if fp.endswith(".json") else \
                [json.loads(l) for l in open(fp, encoding="utf-8") if l.strip()]
            rows.extend(data.get("tickets", data) if isinstance(data, dict) else data)
        else:  # csv
            with open(fp, encoding="utf-8-sig", newline="") as fh:
                rows.extend(list(csv.DictReader(fh)))
    return rows[:limit] if limit else rows


def collect(name: str, limit: int | None = None) -> tuple[list[dict], dict]:
    """Return (mapped_canonical_records, meta) for a named live/file connection."""
    conn = get_connection(name)
    descriptor = load_descriptor(conn["descriptor"])
    kind = descriptor.get("kind", "rest")
    raw = _collect_rest(conn, descriptor, limit) if kind in ("rest", "graphql") \
        else _collect_file(conn, descriptor, limit)
    mapped = [apply_mapping(r, descriptor) for r in raw]
    meta = {"connection": name, "descriptor": os.path.basename(conn["descriptor"]),
            "kind": kind, "n_raw": len(raw)}
    return mapped, meta


# ── test / discover ────────────────────────────────────────────────────────
def test(name: str) -> int:
    conn = get_connection(name)
    descriptor = load_descriptor(conn["descriptor"])
    kind = descriptor.get("kind", "rest")
    print(f"connect --test {name} ({kind}) …")
    try:
        if kind == "file":
            path = resolve_env(conn.get("path", descriptor.get("path", "")),
                               conn.get("vars"))
            n = len(glob.glob(path))
            print(f"  Files matched: {n} ({path})  →  {'OK' if n else 'NONE FOUND'}")
            return 0 if n else 1
        url, query = effective_request(conn, descriptor)     # preview before any network
        print(f"  URL:   {url}")
        for k, v in query.items():
            print(f"  {k+':':<7}{v}")
        sample, _ = collect(name, limit=1)
        print(f"  Reachable: yes (auth ok) · sample records: {len(sample)}  →  OK")
        return 0
    except SystemExit as e:
        print(f"  FAILED: {e}")
        return 1


def discover(name: str) -> int:
    conn = get_connection(name)
    descriptor = load_descriptor(conn["descriptor"])
    sample, meta = collect(name, limit=50)
    print(f"Probing {name} ({meta['kind']}) … sample n={len(sample)}")
    if not sample:
        print("  No records returned.")
        return 1
    fields = {}
    for rec in sample:
        for k, v in rec.items():
            if k == "raw_extra":
                for ek in (v or {}):
                    fields.setdefault(f"raw_extra.{ek}", 0)
                    fields[f"raw_extra.{ek}"] += 1
            else:
                fields.setdefault(k, 0)
                fields[k] += 1 if v not in (None, "") else 0
    n = len(sample)
    print("Fields seen (coverage):")
    for k, c in sorted(fields.items(), key=lambda x: -x[1]):
        tag = "→ UNMAPPED (raw_extra)" if k.startswith("raw_extra.") else "→ mapped"
        print(f"  {k:<28} {round(100*c/n):>3}%   {tag}")
    prios = sorted({str(r.get('declared_priority')) for r in sample})
    print(f"Priority vocabulary (normalized): {prios}")
    return 0
