# src/core/dev_tracker.py
"""Development tracking utilities for GemShot.

- Logs every major development action to `logs/dev.log`.
- Provides `update_roadmap()` that reads the log, extracts tasks and
  automatically updates `PROJECT_ROADMAP.md` with a "## Next Steps"
  section and a "## Bucket List" of possible applications.
- The module is deliberately lightweight and has no external
  dependencies beyond the Python standard library.
"""

import os
import datetime
from pathlib import Path
import re

# -------------------------------------------------------------------
# Configuration (absolute paths – adjust if the project layout changes)
# -------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # points to c:/GemShot_Release_v3.8.0_Estable
LOG_FILE = PROJECT_ROOT / "logs" / "dev.log"
ROADMAP_FILE = PROJECT_ROOT / "PROJECT_ROADMAP.md"
BUCKET_FILE = PROJECT_ROOT / "docs" / "bucket_list.md"

# Ensure the logs directory exists
os.makedirs(LOG_FILE.parent, exist_ok=True)


def log_action(message: str) -> None:
    """Append a timestamped message to the development log.

    Example::
        log_action("Implemented QuantumKeyManager stub")
    """
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} - {message}\n")


def _extract_tasks_from_log() -> list[str]:
    """Return a list of unique task‑like sentences from the log.

    We consider a line a *task* if it starts with a verb in infinitive form
    (e.g. "Implement", "Add", "Create", "Refactor", "Test").
    """
    tasks: set[str] = set()
    verb_pattern = re.compile(r"^(Implement|Add|Create|Refactor|Test|Update|Fix|Generate|Design)", re.IGNORECASE)
    if LOG_FILE.exists():
        with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                # Strip timestamp part
                parts = line.split(" - ", 1)
                if len(parts) != 2:
                    continue
                _, msg = parts
                msg = msg.strip()
                if verb_pattern.match(msg):
                    tasks.add(msg)
    return sorted(tasks)


def _ensure_section(header: str, content: list[str]) -> None:
    """Insert or replace a markdown section in the roadmap.

    *header* must be the exact markdown header (e.g. "## Next Steps").
    *content* is a list of lines (without trailing newlines).
    """
    if not ROADMAP_FILE.exists():
        # Create a minimal roadmap if missing
        with open(ROADMAP_FILE, "w", encoding="utf-8") as f:
            f.write("# Project Roadmap\n\n")
    with open(ROADMAP_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find existing section
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if line.strip() == header:
            start_idx = i
            # Section ends at the next header of same or higher level
            for j in range(i + 1, len(lines)):
                if re.match(r"^##? ", lines[j]):
                    end_idx = j
                    break
            if end_idx is None:
                end_idx = len(lines)
            break

    new_section = [header + "\n", "\n"] + [c + "\n" for c in content] + ["\n"]
    if start_idx is not None:
        # Replace existing section
        lines = lines[:start_idx] + new_section + lines[end_idx:]
    else:
        # Append at the end of the file
        if not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        lines.extend(new_section)

    with open(ROADMAP_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)


def update_roadmap() -> None:
    """Read the development log, generate *Next Steps* and *Bucket List*.

    * Next Steps – a checklist derived from recent log entries.
    * Bucket List – a static list of possible applications for the
      GemShot platform (can be edited manually later).
    """
    tasks = _extract_tasks_from_log()
    if tasks:
        next_steps = ["- [ ] " + t for t in tasks]
    else:
        next_steps = ["- No pending tasks recorded."]
    _ensure_section("## Next Steps", next_steps)

    # Bucket list – we keep a static template but ensure the file exists.
    bucket_items = [
        "- Real‑time collaborative annotation (cloud sync).",
        "- AI‑driven screenshot summarisation for meeting minutes.",
        "- Integration with project‑management tools (Jira, Notion).",
        "- Mobile companion app for quick capture.",
        "- Quantum‑ready backend for future AI acceleration.",
    ]
    # Write bucket list file (used as reference, also inserted in roadmap)
    os.makedirs(BUCKET_FILE.parent, exist_ok=True)
    with open(BUCKET_FILE, "w", encoding="utf-8") as f:
        f.write("# Bucket List – Possible Applications\n\n")
        for item in bucket_items:
            f.write(item + "\n")
    # Insert a reference in the roadmap
    bucket_section = ["- See `docs/bucket_list.md` for a curated list of possible applications."]
    _ensure_section("## Bucket List", bucket_section)

# -------------------------------------------------------------------
# Convenience: run update automatically when this module is executed.
# -------------------------------------------------------------------
if __name__ == "__main__":
    update_roadmap()
    print(f"Roadmap updated: {ROADMAP_FILE}")
    print(f"Bucket list written: {BUCKET_FILE}")
