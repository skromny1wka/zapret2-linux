from __future__ import annotations

import ast
from pathlib import Path
import unittest


SRC_ROOT = Path(__file__).resolve().parents[1] / "src"


class UpdaterDownloadContractTests(unittest.TestCase):
    def test_update_module_imports_threading_when_download_code_uses_it(self) -> None:
        tree = ast.parse((SRC_ROOT / "updater" / "update.py").read_text(encoding="utf-8"))

        uses_threading = any(
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "threading"
            for node in ast.walk(tree)
        )
        imports_threading = any(
            (isinstance(node, ast.Import) and any(alias.name == "threading" for alias in node.names))
            or (
                isinstance(node, ast.ImportFrom)
                and node.module == "threading"
            )
            for node in ast.walk(tree)
        )

        self.assertTrue(uses_threading)
        self.assertTrue(
            imports_threading,
            "updater.update использует threading, поэтому модуль должен импортировать его явно",
        )


if __name__ == "__main__":
    unittest.main()
