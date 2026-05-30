from __future__ import annotations

import importlib
import sys
import unittest


class FeatureFacadesLazyImportTests(unittest.TestCase):
    def test_lazy_feature_facade_modules_are_listed_without_importing_them(self) -> None:
        module_names = (
            "app.feature_facades",
            "app.feature_facades.appearance",
            "app.feature_facades.blockcheck",
            "app.feature_facades.premium",
            "app.feature_facades.runtime",
        )
        saved_modules = {name: sys.modules.pop(name, None) for name in module_names}
        try:
            facades = importlib.import_module("app.feature_facades")

            self.assertIn(
                "app.feature_facades.blockcheck",
                facades.iter_lazy_feature_facade_modules(),
            )
            self.assertNotIn("app.feature_facades.blockcheck", sys.modules)
            self.assertNotIn("app.feature_facades.appearance", sys.modules)
        finally:
            for name in module_names:
                sys.modules.pop(name, None)
            for name, module in saved_modules.items():
                if module is not None:
                    sys.modules[name] = module

    def test_package_import_does_not_load_all_feature_facades(self) -> None:
        module_names = (
            "app.feature_facades",
            "app.feature_facades.appearance",
            "app.feature_facades.premium",
            "app.feature_facades.presets",
            "app.feature_facades.profile",
            "app.feature_facades.runtime",
        )
        saved_modules = {name: sys.modules.pop(name, None) for name in module_names}
        try:
            facades = importlib.import_module("app.feature_facades")

            self.assertNotIn("app.feature_facades.appearance", sys.modules)
            self.assertNotIn("app.feature_facades.premium", sys.modules)
            self.assertNotIn("app.feature_facades.runtime", sys.modules)

            _ = facades.PresetsFeature

            self.assertIn("app.feature_facades.presets", sys.modules)
            self.assertNotIn("app.feature_facades.appearance", sys.modules)
            self.assertNotIn("app.feature_facades.premium", sys.modules)
        finally:
            for name in module_names:
                sys.modules.pop(name, None)
            for name, module in saved_modules.items():
                if module is not None:
                    sys.modules[name] = module


if __name__ == "__main__":
    unittest.main()
