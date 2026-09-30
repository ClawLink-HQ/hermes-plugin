"""Keep `hermes plugins install` from blocking this plugin.

Hermes scans every file of a plugin before installing it (tools/plugin_guard.py
in hermes-agent), prose included, and a single critical finding blocks the
install with no override, not even `--force`. One README sentence *explaining*
that we avoid piping a downloaded script into an interpreter matched that
critical pattern and blocked every install (2026-09-30).

The pattern below is assembled from pieces on purpose: Hermes scans this test
file too, and a literal copy here would trip the same rule.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parent.parent

FETCHERS = ["cu" + "rl", "wg" + "et", "irm", "iwr", "Invoke-" + "WebRequest", "Invoke-" + "RestMethod"]
INTERPRETERS = ["pyt" + "hon3?", "sh", "ba" + "sh", "zsh", "iex", "Invoke-" + "Expression", "node"]
PIPE_TO_INTERPRETER = re.compile(
    r"\b(?:" + "|".join(FETCHERS) + r")\b[^\n]*?\|\s*(?:sudo\s+)?(?:" + "|".join(INTERPRETERS) + r")\b",
    re.IGNORECASE,
)

SCANNED_SUFFIXES = {".md", ".txt", ".toml", ".yaml", ".yml", ".py"}


class InstallScanTests(unittest.TestCase):
    def test_no_file_mentions_piping_a_download_into_an_interpreter(self) -> None:
        hits = []
        for path in sorted(PLUGIN_DIR.rglob("*")):
            if not path.is_file() or path.suffix not in SCANNED_SUFFIXES or ".git" in path.parts:
                continue
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if PIPE_TO_INTERPRETER.search(line):
                    hits.append(f"{path.relative_to(PLUGIN_DIR)}:{number}: {line.strip()[:120]}")
        self.assertEqual(
            hits,
            [],
            "Hermes blocks the install on these lines, even in prose; reword them:\n" + "\n".join(hits),
        )


if __name__ == "__main__":
    unittest.main()
