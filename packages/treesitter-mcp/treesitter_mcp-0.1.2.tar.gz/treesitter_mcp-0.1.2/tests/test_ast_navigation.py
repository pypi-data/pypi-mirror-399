import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from treesitter_mcp.core.language_manager import LanguageManager
from treesitter_mcp.languages.python import PythonAnalyzer


class ASTNavigationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.language_manager = LanguageManager()
        cls.analyzer = PythonAnalyzer(cls.language_manager)
        cls.code = "def foo(x):\n    return x\n"

    def _parse_root(self):
        tree = self.analyzer.parse(self.code)
        return tree.root_node

    def test_ast_includes_field_names(self):
        root = self._parse_root()
        ast = self.analyzer._build_ast(root, self.code, max_depth=2)

        func_node = next((c for c in ast.children if c.type == "function_definition"), None)
        self.assertIsNotNone(func_node, "function_definition should be present")

        name_child = next((c for c in func_node.children if c.field_name == "name"), None)
        self.assertIsNotNone(name_child, "function name child should carry field_name")
        self.assertEqual(name_child.text, "foo")

    def test_build_node_at_point_returns_identifier(self):
        node = self.analyzer.build_node_at_point(self.code, row=0, column=4, max_depth=0)
        self.assertEqual(node.type, "identifier")
        self.assertEqual(node.text, "foo")

    def test_build_node_for_range_returns_return_statement(self):
        node = self.analyzer.build_node_for_range(
            self.code,
            start_row=1,
            start_col=4,
            end_row=1,
            end_col=12,
            max_depth=0,
        )
        self.assertEqual(node.type, "return_statement")

    def test_cursor_view_contains_context(self):
        view = self.analyzer.build_cursor_view(self.code, row=1, column=11, max_depth=1)
        self.assertIn("focus", view)
        self.assertIn("ancestors", view)
        self.assertIn("siblings", view)
        self.assertIn("children", view)

        self.assertEqual(view["focus"]["type"], "identifier")
        self.assertTrue(any(a["type"] == "return_statement" for a in view["ancestors"]))


if __name__ == "__main__":
    unittest.main()

