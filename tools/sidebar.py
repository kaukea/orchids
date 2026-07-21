#!/usr/bin/env python3
"""Curses fleet sidebar — renders the tree built by sidebar_model, navigates
via sidebar_nav.

Presentation is deliberately split from curses: `flatten()` turns a Fleet
into a flat list of Row objects, and `render_lines()` turns those into plain
text with NO curses calls at all — that pure function is what tests assert
on. The curses app (`main`, run through `curses.wrapper`) is a thin loop that
polls a background `sidebar_model.watch()` thread, advances the spinner/flash
counters, and draws each line with its status colour.

CLI:
  python3 tools/sidebar.py          run the interactive curses UI
  python3 tools/sidebar.py --dump   print one frame as plain text and exit 0
                                    (headless — no TTY required)

STDLIB ONLY.
"""
from __future__ import annotations

import curses
import os
import sys
import threading
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sidebar_model  # noqa: E402
import sidebar_nav  # noqa: E402

STATUS_EMOJI = {
    "running": "🟢",
    "standby": "🟡",
    "completed": "✅",
    "failed": "❌",
    "waiting": "⏳",
}
SPINNER_FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
NO_ACTIVITY_TEXT = "· no activity ·"

FLASH_TOGGLE_TICKS = 3  # timeout is 150ms; ~3 ticks ≈ 450ms ≈ twice a second


# --------------------------------------------------------------------------
# Presentation model (pure, no curses)
# --------------------------------------------------------------------------

@dataclass
class Row:
    depth: int
    kind: str  # "repo" | "feature" | "subagent"
    nav_key: str
    label: str
    status: str | None
    waiting: bool
    is_subagent: bool
    activity: str = field(default="")


def flatten(fleet: sidebar_model.Fleet) -> list[Row]:
    """Fleet -> flat list of Row, depth-first (repo, its features, their subagents)."""
    rows: list[Row] = []
    for repo in fleet.repos:
        rows.append(Row(
            depth=0, kind="repo", nav_key=repo.name, label=repo.name,
            status=repo.status, waiting=repo.waiting, is_subagent=False,
        ))
        for feature in repo.features:
            rows.append(Row(
                depth=1, kind="feature", nav_key=feature.feature_id, label=feature.name,
                status=feature.status, waiting=feature.waiting, is_subagent=False,
                activity=feature.activity,
            ))
            for sub in feature.subagents:
                rows.append(Row(
                    depth=2, kind="subagent", nav_key=feature.feature_id, label=sub.label,
                    status=None, waiting=False, is_subagent=True,
                ))
    return rows


def _status_emoji(row: Row, flash_on: bool) -> str:
    if row.waiting:
        return STATUS_EMOJI["waiting"] if flash_on else " "
    return STATUS_EMOJI.get(row.status, " ")


def _row_text(row: Row, spinner_frame: int, flash_on: bool) -> str:
    indent = "  " * row.depth
    if row.kind == "subagent":
        spinner = SPINNER_FRAMES[spinner_frame % len(SPINNER_FRAMES)]
        return f"{indent}{spinner} {row.label}"

    text = f"{indent}{_status_emoji(row, flash_on)} {row.label}"
    if row.kind == "feature" and row.activity:
        text = f"{text} {row.activity}"
    return text


def _truncate(text: str, width: int) -> str:
    return text[:width] if width > 0 else text


def render_lines(
    fleet: sidebar_model.Fleet,
    selected: int = -1,
    spinner_frame: int = 0,
    flash_on: bool = True,
    width: int = 32,
) -> list[str]:
    """Pure text rendering of one frame — exactly what gets drawn, no curses."""
    rows = flatten(fleet)
    if not rows:
        return [_truncate(NO_ACTIVITY_TEXT, width)]

    lines = []
    for i, row in enumerate(rows):
        marker = ">" if i == selected else " "
        lines.append(_truncate(marker + _row_text(row, spinner_frame, flash_on), width))
    return lines


# --------------------------------------------------------------------------
# Shared fleet state (written by the watch thread, read by the main loop)
# --------------------------------------------------------------------------

class _SharedFleet:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._fleet = sidebar_model.Fleet()

    def set(self, fleet: sidebar_model.Fleet) -> None:
        with self._lock:
            self._fleet = fleet

    def get(self) -> sidebar_model.Fleet:
        with self._lock:
            return self._fleet


def _watch_thread(shared: _SharedFleet) -> None:
    try:
        sidebar_model.watch(shared.set)
    except Exception:
        pass  # keep the UI alive on the last snapshot even if the watch dies


# --------------------------------------------------------------------------
# Curses drawing
# --------------------------------------------------------------------------

def _init_colours() -> dict[str, int]:
    """Colour-pair attrs per status; empty dict (attr 0 everywhere) if the
    terminal has no colour support."""
    if not curses.has_colors():
        return {}
    curses.start_color()
    try:
        curses.use_default_colors()
        bg = -1
    except curses.error:
        bg = curses.COLOR_BLACK

    curses.init_pair(1, curses.COLOR_GREEN, bg)
    curses.init_pair(2, curses.COLOR_YELLOW, bg)
    curses.init_pair(3, curses.COLOR_GREEN, bg)
    curses.init_pair(4, curses.COLOR_RED, bg)
    curses.init_pair(5, curses.COLOR_MAGENTA, bg)
    return {
        "running": curses.color_pair(1),
        "standby": curses.color_pair(2),
        "completed": curses.color_pair(3) | curses.A_BOLD,
        "failed": curses.color_pair(4),
        "waiting": curses.color_pair(5),
    }


def _safe_addstr(stdscr, y: int, x: int, text: str, attr: int) -> None:
    try:
        stdscr.addstr(y, x, text, attr)
    except curses.error:
        pass  # bottom-right cell write raises; harmless, just skip it


def _draw(stdscr, rows: list[Row], selected: int, spinner_frame: int, flash_on: bool,
          colour_pairs: dict[str, int]) -> None:
    stdscr.erase()
    max_y, max_x = stdscr.getmaxyx()

    if not rows:
        _safe_addstr(stdscr, 0, 0, _truncate(NO_ACTIVITY_TEXT, max_x), curses.A_DIM)
        stdscr.refresh()
        return

    for i, row in enumerate(rows[:max_y]):
        text = _truncate(_row_text(row, spinner_frame, flash_on), max_x)
        attr = colour_pairs.get(row.status, 0)
        if i == selected:
            attr |= curses.A_REVERSE
        _safe_addstr(stdscr, i, 0, text, attr)
    stdscr.refresh()


# --------------------------------------------------------------------------
# Main loop
# --------------------------------------------------------------------------

def _navigate_selected(rows: list[Row], selected: int) -> None:
    if not rows or not (0 <= selected < len(rows)):
        return
    row = rows[selected]
    kind = "feature" if row.kind == "subagent" else row.kind
    sidebar_nav.navigate(kind, row.nav_key)


def _clamp_selected(selected: int, count: int) -> int:
    if count == 0:
        return 0
    return max(0, min(selected, count - 1))


def main(stdscr) -> None:
    curses.curs_set(0)
    stdscr.timeout(150)
    colour_pairs = _init_colours()

    shared = _SharedFleet()
    thread = threading.Thread(target=_watch_thread, args=(shared,), daemon=True)
    thread.start()

    selected = 0
    spinner_frame = 0
    flash_on = True
    tick = 0

    while True:
        rows = flatten(shared.get())
        selected = _clamp_selected(selected, len(rows))
        _draw(stdscr, rows, selected, spinner_frame, flash_on, colour_pairs)

        key = stdscr.getch()
        spinner_frame += 1
        tick += 1
        if tick % FLASH_TOGGLE_TICKS == 0:
            flash_on = not flash_on

        if key in (curses.KEY_UP, ord("k")):
            selected = max(0, selected - 1)
        elif key in (curses.KEY_DOWN, ord("j")):
            selected = min(len(rows) - 1, selected + 1) if rows else 0
        elif key in (10, 13, curses.KEY_ENTER):
            _navigate_selected(rows, selected)
        elif key in (ord("q"), ord("Q")):
            return
        elif key == curses.KEY_RESIZE:
            curses.update_lines_cols()
        # any other key (including -1 on timeout) is ignored


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _run_dump() -> int:
    fleet = sidebar_model.build_model()
    for line in render_lines(fleet):
        print(line)
    return 0


if __name__ == "__main__":
    if "--dump" in sys.argv[1:]:
        sys.exit(_run_dump())
    curses.wrapper(main)
