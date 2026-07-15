import ast
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class UiContractTests(unittest.TestCase):
    def test_every_qml_backend_reference_exists(self):
        tree = ast.parse((ROOT / "src" / "backend.py").read_text(encoding="utf-8"))
        methods = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
        references = set()
        for path in (ROOT / "src" / "qml").rglob("*.qml"):
            references.update(re.findall(r"backend\.([A-Za-z_]\w*)", path.read_text(encoding="utf-8")))
        self.assertEqual(sorted(references - methods), [])

    def test_every_catalogue_application_has_help(self):
        applications = json.loads((ROOT / "data" / "applications.json").read_text(encoding="utf-8"))
        for app in applications:
            filename = "APP-" + "".join(c if c.isalnum() else "-" for c in app["name"].upper()).strip("-") + ".md"
            self.assertTrue((ROOT / "docs" / filename).is_file(), filename)

    def test_no_unwired_inline_buttons(self):
        offenders = []
        pattern = re.compile(r"Button\s*\{([^{}]*)\}", re.DOTALL)
        for path in (ROOT / "src" / "qml").rglob("*.qml"):
            for block in pattern.findall(path.read_text(encoding="utf-8")):
                if "text:" in block and "onClicked:" not in block and "onAccepted:" not in block:
                    # Repeater delegates and dialog standard buttons have indirect actions.
                    if "delegate" not in block:
                        offenders.append(f"{path.name}: {block[:80]}")
        self.assertEqual(offenders, [])
