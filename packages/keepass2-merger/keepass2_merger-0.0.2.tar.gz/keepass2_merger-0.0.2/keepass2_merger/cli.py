"""Interactive KeePass2 database merger CLI."""

from __future__ import annotations

import argparse
import getpass
import sys
import textwrap
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional, Sequence, Tuple

try:
    import curses
except Exception:  # pragma: no cover - optional runtime dependency
    curses = None  # type: ignore[assignment]

try:  # pragma: no cover - exercised in runtime, not unit tests
    from pykeepass import PyKeePass
except ImportError:  # pragma: no cover - guarded at runtime
    PyKeePass = None  # type: ignore[assignment]


@dataclass
class DiffItem:
    """Represents a difference between two databases."""

    category: str  # "entry" | "group"
    change: str  # "add" | "remove" | "modify"
    left: object | None  # item from db1
    right: object | None  # item from db2
    path: str
    label: str
    left_modified: Optional[datetime]
    right_modified: Optional[datetime]

    def recommendation(self) -> bool:
        """Return True if we recommend applying the change."""
        if self.change == "add":
            return True
        if self.change == "remove":
            return False
        if self.left_modified and self.right_modified:
            return self.right_modified >= self.left_modified
        if self.right_modified:
            return True
        return False

    def sort_key(self) -> Tuple[int, str]:
        order = {
            ("group", "add"): 0,
            ("group", "modify"): 1,
            ("entry", "add"): 2,
            ("entry", "modify"): 3,
        }
        return (order.get((self.category, self.change), 99), self.path)


def ensure_pykeepass():
    if PyKeePass is None:
        raise SystemExit(
            "pykeepass is required to run this tool. "
            "Install with `pip install keepass2-merger[dev]` or `pip install pykeepass`."
        )


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Interactively merge two KeePass2 databases.",
    )
    parser.add_argument("database_one", help="Path to the base KeePass database.")
    parser.add_argument("database_two", help="Path to the KeePass database to merge from.")
    parser.add_argument("output", help="Where to save the merged KeePass database.")
    parser.add_argument(
        "--no-curses",
        action="store_true",
        help="Disable full-screen UI and fall back to line-by-line prompts.",
    )
    return parser.parse_args(argv)


def prompt_for_password(label: str) -> str:
    while True:
        pw = getpass.getpass(f"Password for {label}: ")
        if pw:
            return pw
        print("Password cannot be empty. Please try again.")


def load_database(path: str, label: str) -> "PyKeePass":
    ensure_pykeepass()
    password = prompt_for_password(label)
    try:
        return PyKeePass(path, password=password)
    except Exception as exc:  # pragma: no cover - depends on runtime failures
        raise SystemExit(f"Failed to open {label} ({path}): {exc}")


def group_path_parts(group) -> List[str]:
    names = []
    current = group
    while current is not None:
        names.append(getattr(current, "name", ""))
        parent = getattr(current, "parent", None)
        if parent is None or parent == current:
            break
        current = parent
    names.reverse()
    return names


def group_path(group) -> str:
    return "/" + "/".join([p for p in group_path_parts(group) if p])


def last_modified(obj) -> Optional[datetime]:
    for attr in (
        "last_modification_time",
        "last_modified",
        "last_mod_time",
        "mtime",
        "updated",
    ):
        value = getattr(obj, attr, None)
        if callable(value):
            try:
                value = value()
            except Exception:
                value = None
        if isinstance(value, datetime):
            return value
    return None


def summarize_entry(entry) -> dict:
    def clean(value):
        return "" if value is None else value

    return {
        "title": clean(getattr(entry, "title", "")),
        "username": clean(getattr(entry, "username", "")),
        "password": clean(getattr(entry, "password", "")),
        "url": clean(getattr(entry, "url", "")),
        "notes": clean(getattr(entry, "notes", "")),
        "group": group_path(getattr(entry, "group", None)) if getattr(entry, "group", None) else "",
    }


def summarize_group(group) -> dict:
    def clean(value):
        return "" if value is None else value

    return {
        "name": clean(getattr(group, "name", "")),
        "notes": clean(getattr(group, "notes", "")),
        "group": group_path(group),
    }


def iter_groups(kp) -> Iterable:
    queue = [kp.root_group]
    seen = set()
    while queue:
        current = queue.pop(0)
        if current in seen:
            continue
        seen.add(current)
        yield current
        for subgroup in getattr(current, "subgroups", []) or getattr(current, "groups", []):
            queue.append(subgroup)


def is_recycle_bin_group(group, kp) -> bool:
    bin_candidates = []
    for attr in ("recyclebin", "recycle_bin", "trash", "deleted_objects"):
        candidate = getattr(kp, attr, None)
        if candidate is not None:
            bin_candidates.append(candidate)
    return any(candidate is group for candidate in bin_candidates) or getattr(group, "name", "").lower() == "recycle bin"


def is_in_recycle_bin(group, kp) -> bool:
    current = group
    while current is not None:
        if is_recycle_bin_group(current, kp):
            return True
        parent = getattr(current, "parent", None)
        if parent is None or parent == current:
            break
        current = parent
    return False


def build_group_map(kp) -> dict:
    return {
        getattr(g, "uuid", None): g
        for g in iter_groups(kp)
        if getattr(g, "uuid", None) and not is_in_recycle_bin(g, kp)
    }


def build_entry_map(kp) -> dict:
    return {
        getattr(e, "uuid", None): e
        for e in getattr(kp, "entries", [])
        if getattr(e, "uuid", None) and not is_in_recycle_bin(getattr(e, "group", None), kp)
    }


def groups_differ(left, right) -> bool:
    return summarize_group(left) != summarize_group(right)


def entries_differ(left, right) -> bool:
    return summarize_entry(left) != summarize_entry(right)


def diff_databases(kp1, kp2) -> List[DiffItem]:
    diffs: List[DiffItem] = []

    groups1 = build_group_map(kp1)
    groups2 = build_group_map(kp2)
    for uuid in sorted(set(groups1) | set(groups2)):
        g1 = groups1.get(uuid)
        g2 = groups2.get(uuid)
        if g2 and not g1:
            diffs.append(
                DiffItem(
                    category="group",
                    change="add",
                    left=None,
                    right=g2,
                    path=group_path(g2),
                    label=getattr(g2, "name", ""),
                    left_modified=None,
                    right_modified=last_modified(g2),
                )
            )
        elif g1 and g2 and groups_differ(g1, g2):
            diffs.append(
                DiffItem(
                    category="group",
                    change="modify",
                    left=g1,
                    right=g2,
                    path=group_path(g1),
                    label=getattr(g1, "name", ""),
                    left_modified=last_modified(g1),
                    right_modified=last_modified(g2),
                )
            )

    entries1 = build_entry_map(kp1)
    entries2 = build_entry_map(kp2)
    for uuid in sorted(set(entries1) | set(entries2)):
        e1 = entries1.get(uuid)
        e2 = entries2.get(uuid)
        if e2 and not e1:
            diffs.append(
                DiffItem(
                    category="entry",
                    change="add",
                    left=None,
                    right=e2,
                    path=group_path(getattr(e2, "group", None)) if getattr(e2, "group", None) else "",
                    label=getattr(e2, "title", ""),
                    left_modified=None,
                    right_modified=last_modified(e2),
                )
            )
        elif e1 and e2 and entries_differ(e1, e2):
            diffs.append(
                DiffItem(
                    category="entry",
                    change="modify",
                    left=e1,
                    right=e2,
                    path=group_path(getattr(e1, "group", None)) if getattr(e1, "group", None) else "",
                    label=getattr(e1, "title", ""),
                    left_modified=last_modified(e1),
                    right_modified=last_modified(e2),
                )
            )

    diffs.sort(key=lambda d: d.sort_key())
    return diffs


def ask_yes_no(prompt: str, default: bool) -> bool:
    suffix = "Y/n" if default else "y/N"
    while True:
        response = input(f"{prompt} [{suffix}]: ").strip().lower()
        if not response:
            return default
        if response in {"y", "yes"}:
            return True
        if response in {"n", "no"}:
            return False
        print("Please answer yes or no.")


def ask_use_db2(default_to_db2: bool, left_hint: str = "", right_hint: str = "") -> bool:
    default_label = "2" if default_to_db2 else "1"
    prompt = (
        f"Choose version: [1] keep database #1{left_hint}, "
        f"[2] use database #2{right_hint} (default {default_label}): "
    )
    while True:
        response = input(prompt).strip()
        if not response:
            return default_to_db2
        if response in {"1", "db1", "left"}:
            return False
        if response in {"2", "db2", "right"}:
            return True
        print("Please enter 1 or 2.")


def version_hints(diff: DiffItem) -> Tuple[str, str]:
    left = diff.left_modified
    right = diff.right_modified
    if left and right:
        if left > right:
            return " (Newer)", " (Older)"
        if right > left:
            return " (Older)", " (Newer)"
        return " (Same age)", " (Same age)"
    if left and not right:
        return " (Newer)", " (Unknown age)"
    if right and not left:
        return " (Unknown age)", " (Newer)"
    return "", ""


@contextmanager
def alternate_screen(enabled: bool):
    if not enabled:
        yield
        return
    try:
        sys.stdout.write("\x1b[?1049h")
        sys.stdout.flush()
        yield
    finally:
        sys.stdout.write("\x1b[?1049l")
        sys.stdout.flush()


def format_metadata(label: str, data: dict, modified: Optional[datetime]) -> str:
    lines = [f"{label} (last modified: {modified.isoformat() if modified else 'unknown'})"]
    for key in ("group", "title", "username", "password", "url", "notes", "name"):
        if key in data:
            lines.append(f"  {key}: {data[key]}")
    return "\n".join(lines)


def display_diff(diff: DiffItem) -> None:
    print("-" * 60)
    print(f"{diff.category.upper()} {diff.change.upper()}: {diff.path} :: {diff.label}")
    if diff.category == "entry":
        left_data = summarize_entry(diff.left) if diff.left else {}
        right_data = summarize_entry(diff.right) if diff.right else {}
    else:
        left_data = summarize_group(diff.left) if diff.left else {}
        right_data = summarize_group(diff.right) if diff.right else {}

    if diff.change == "add":
        print(format_metadata("DB2 value", right_data, diff.right_modified))
    elif diff.change == "remove":
        print(format_metadata("DB1 value", left_data, diff.left_modified))
    else:
        left_hint, right_hint = version_hints(diff)
        print(format_metadata(f"DB1 value{left_hint}", left_data, diff.left_modified))
        print()
        print(format_metadata(f"DB2 value{right_hint}", right_data, diff.right_modified))
    if diff.change != "modify":
        print(f"Recommendation: {'accept' if diff.recommendation() else 'reject'}")


def render_lines(stdscr, lines: List[str], start_y: int = 0):
    height, width = stdscr.getmaxyx()
    y = start_y
    for line in lines:
        if y >= height:
            break
        for sub in line.splitlines() or [""]:
            if y >= height:
                break
            if len(sub) > width:
                for chunk in textwrap.wrap(sub, width):
                    if y >= height:
                        break
                    stdscr.addstr(y, 0, chunk)
                    y += 1
            else:
                stdscr.addstr(y, 0, sub)
                y += 1


def display_diff_curses(stdscr, diff: DiffItem, index: int, total: int):
    stdscr.clear()
    header = f"Change {index}/{total} :: {diff.category.upper()} {diff.change.upper()}"
    location = f"{diff.path} :: {diff.label}"
    divider = "-" * max(len(header), len(location))
    lines: List[str] = [header, location, divider]
    if diff.category == "entry":
        left_data = summarize_entry(diff.left) if diff.left else {}
        right_data = summarize_entry(diff.right) if diff.right else {}
    else:
        left_data = summarize_group(diff.left) if diff.left else {}
        right_data = summarize_group(diff.right) if diff.right else {}

    if diff.change == "add":
        lines.append(format_metadata("DB2 value", right_data, diff.right_modified))
    else:
        left_hint, right_hint = version_hints(diff)
        lines.append(format_metadata(f"DB1 value{left_hint}", left_data, diff.left_modified))
        lines.append("")
        lines.append(format_metadata(f"DB2 value{right_hint}", right_data, diff.right_modified))

    render_lines(stdscr, lines, start_y=0)


def run_curses_merge(kp1, diffs: List[DiffItem]):
    def handle_add(stdscr, diff: DiffItem, index: int, total: int):
        while True:
            display_diff_curses(stdscr, diff, index, total)
            height, width = stdscr.getmaxyx()
            default_apply = diff.recommendation()
            default_label = "Yes" if default_apply else "No"
            instructions = f"Apply this change? [Y]es / [N]o / [Q]uit (Enter defaults to {default_label})"
            wrapped = textwrap.wrap(instructions, max(10, width - 1)) or [instructions]
            start_row = max(0, height - len(wrapped) - 1)
            for i, chunk in enumerate(wrapped):
                if start_row + i < height:
                    stdscr.addstr(start_row + i, 0, chunk[: width - 1])
            ch = stdscr.getch()
            if ch in (ord("q"), ord("Q")):
                return "quit"
            if ch in (ord("n"), ord("N")):
                return "skip"
            if ch in (ord("\n"), ord("\r")):
                return "apply" if default_apply else "skip"
            if ch in (ord("y"), ord("Y")):
                return "apply"

    def handle_modify(stdscr, diff: DiffItem, index: int, total: int):
        left_hint, right_hint = version_hints(diff)
        default_db = 2 if diff.recommendation() else 1
        while True:
            display_diff_curses(stdscr, diff, index, total)
            height, width = stdscr.getmaxyx()
            prompt = (
                f"Choose version: [1] keep database #1{left_hint}, "
                f"[2] use database #2{right_hint} (Enter defaults to {default_db}, Q to quit)"
            )
            wrapped = textwrap.wrap(prompt, max(10, width - 1)) or [prompt]
            start_row = max(0, height - len(wrapped) - 1)
            for i, chunk in enumerate(wrapped):
                if start_row + i < height:
                    stdscr.addstr(start_row + i, 0, chunk[: width - 1])
            ch = stdscr.getch()
            if ch in (ord("q"), ord("Q")):
                return "quit"
            if ch in (ord("1"),):
                return "keep_left"
            if ch in (ord("2"),):
                return "use_right"
            if ch in (ord("\n"), ord("\r")):
                return "use_right" if default_db == 2 else "keep_left"

    result = {"status": "ok"}

    def session(stdscr):
        curses.curs_set(0)
        stdscr.keypad(True)
        for index, diff in enumerate(diffs, start=1):
            if diff.change == "modify":
                action = handle_modify(stdscr, diff, index, len(diffs))
                if action == "quit":
                    result["status"] = "aborted"
                    return
                if action == "use_right":
                    apply_diff(kp1, diff)
            else:
                action = handle_add(stdscr, diff, index, len(diffs))
                if action == "quit":
                    result["status"] = "aborted"
                    return
                if action == "apply":
                    apply_diff(kp1, diff)

    with alternate_screen(sys.stdout.isatty()):
        curses.wrapper(session)
    return result["status"]


def ensure_group(kp, path_parts: Sequence[str]):
    group = kp.root_group
    # Skip the root name because we start from root_group already.
    for name in path_parts[1:]:
        existing = next((g for g in getattr(group, "subgroups", []) if getattr(g, "name", "") == name), None)
        if not existing:
            existing = kp.add_group(group, name)
        group = existing
    return group


def move_group(kp, group, destination):
    if hasattr(kp, "move_group"):
        kp.move_group(group, destination)
        return group
    group.parent = destination  # pragma: no cover - fallback path
    return group


def move_entry(kp, entry, destination):
    if hasattr(kp, "move_entry"):
        moved = kp.move_entry(entry, destination)
        return moved if moved is not None else entry
    else:  # pragma: no cover - fallback path
        entry.group = destination
        return entry


def copy_entry(kp, source_entry):
    target_group = ensure_group(kp, group_path_parts(getattr(source_entry, "group", None)))
    return kp.add_entry(
        target_group,
        getattr(source_entry, "title", "") or "",
        getattr(source_entry, "username", "") or "",
        getattr(source_entry, "password", "") or "",
        url=getattr(source_entry, "url", "") or "",
        notes=getattr(source_entry, "notes", "") or "",
    )


def apply_entry_change(kp, diff: DiffItem):
    def clean(value):
        return "" if value is None else value

    if diff.change == "add":
        copy_entry(kp, diff.right)
    elif diff.change == "modify" and diff.left and diff.right:
        target_group = ensure_group(kp, group_path_parts(getattr(diff.right, "group", None)))
        target_entry = move_entry(kp, diff.left, target_group) or diff.left
        target_entry.title = clean(getattr(diff.right, "title", ""))
        target_entry.username = clean(getattr(diff.right, "username", ""))
        target_entry.password = clean(getattr(diff.right, "password", ""))
        target_entry.url = clean(getattr(diff.right, "url", ""))
        target_entry.notes = clean(getattr(diff.right, "notes", ""))


def apply_group_change(kp, diff: DiffItem):
    if diff.change == "add" and diff.right:
        ensure_group(kp, group_path_parts(diff.right))
    elif diff.change == "modify" and diff.left and diff.right:
        desired_parts = group_path_parts(diff.right)
        target_parent = ensure_group(kp, desired_parts[:-1] if len(desired_parts) > 1 else desired_parts)
        move_group(kp, diff.left, target_parent)
        diff.left.name = getattr(diff.right, "name", diff.left.name)
        if hasattr(diff.left, "notes"):
            right_notes = getattr(diff.right, "notes", getattr(diff.left, "notes", ""))
            diff.left.notes = "" if right_notes is None else right_notes


def apply_diff(kp, diff: DiffItem):
    if diff.category == "entry":
        apply_entry_change(kp, diff)
    else:
        apply_group_change(kp, diff)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    kp1 = load_database(args.database_one, "database #1")
    kp2 = load_database(args.database_two, "database #2")

    if args.output == args.database_one or args.output == args.database_two:
        print("Output path must be different from source databases to avoid overwriting.")
        return 1

    diffs = diff_databases(kp1, kp2)
    if not diffs:
        print("No differences detected. Saving copy of database #1.")
        kp1.save(args.output)
        return 0

    use_curses = not args.no_curses and curses is not None and sys.stdout.isatty()
    if use_curses:
        result = run_curses_merge(kp1, diffs)
        if result == "aborted":
            return 1
    else:
        for index, diff in enumerate(diffs, start=1):
            print(f"\nChange {index}/{len(diffs)}")
            display_diff(diff)
            if diff.change == "modify":
                left_hint, right_hint = version_hints(diff)
                use_db2 = ask_use_db2(diff.recommendation(), left_hint, right_hint)
                if use_db2:
                    try:
                        apply_diff(kp1, diff)
                    except Exception as exc:  # pragma: no cover - runtime path
                        print(f"Failed to apply change ({diff.category} {diff.change}): {exc}")
                else:
                    print("Kept database #1 version.")
            else:
                apply_change = ask_yes_no("Apply this change?", diff.recommendation())
                if apply_change:
                    try:
                        apply_diff(kp1, diff)
                    except Exception as exc:  # pragma: no cover - runtime path
                        print(f"Failed to apply change ({diff.category} {diff.change}): {exc}")
                else:
                    print("Skipped.")

    kp1.save(args.output)
    print(f"Merged database saved to {args.output}")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
