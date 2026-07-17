from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class RepositoryHygieneTests(unittest.TestCase):
    def test_bancos_operacionais_ficam_fora_do_git(self) -> None:
        gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("dados/base/*.db", gitignore.splitlines())


if __name__ == "__main__":
    unittest.main()
