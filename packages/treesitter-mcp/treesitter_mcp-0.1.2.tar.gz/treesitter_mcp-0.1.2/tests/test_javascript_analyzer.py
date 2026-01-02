import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from treesitter_mcp.core.language_manager import LanguageManager
from treesitter_mcp.languages.javascript import JavaScriptAnalyzer


class JavaScriptAnalyzerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.language_manager = LanguageManager()
        cls.analyzer = JavaScriptAnalyzer(cls.language_manager)

    def _parse_root(self, code: str):
        tree = self.analyzer.parse(code)
        return tree.root_node

    def test_extract_symbols_functions_classes_methods(self):
        code = """
        function foo(a) { return a; }
        class MyClass {
            bar() { return foo(); }
        }
        """
        symbols = self.analyzer.extract_symbols(self._parse_root(code), "test.js")
        kinds = {(s.name, s.kind) for s in symbols}
        self.assertIn(("foo", "function"), kinds)
        self.assertIn(("MyClass", "class"), kinds)
        self.assertIn(("bar", "method"), kinds)

    def test_call_graph_collects_calls(self):
        code = """
        function foo() {}
        class C {
            bar() { foo(); this.baz(); }
            baz() { return 1; }
        }
        """
        call_graph = self.analyzer.get_call_graph(self._parse_root(code), "test.js")
        nodes = {n.name: n.calls for n in call_graph.nodes}

        self.assertIn("foo", nodes)
        self.assertIn("bar", nodes)
        self.assertIn("baz", nodes)
        self.assertEqual(nodes["foo"], [])
        self.assertIn("foo", nodes["bar"])
        self.assertIn("baz", nodes["bar"])

    def test_find_function_matches_methods(self):
        code = """
        function foo() {}
        class C { bar() {} }
        """
        result = self.analyzer.find_function(self._parse_root(code), "test.js", "bar")
        names = {m.name for m in result.matches}
        self.assertIn("bar", names)

    def test_find_variable_and_usage(self):
        code = """
        let value = 1;
        value = value + 1;
        const other = value;
        """
        root = self._parse_root(code)
        var_result = self.analyzer.find_variable(root, "test.js", "value")
        kinds = {m.kind for m in var_result.matches}
        self.assertIn("variable_def", kinds)
        self.assertIn("variable_use", kinds)

        usage_result = self.analyzer.find_usage(root, "test.js", "value")
        self.assertGreaterEqual(len(usage_result.matches), 3)

    def test_dependencies_from_import_export_and_require(self):
        code = """
        import x from './mod.js';
        import { y as z } from "lib";
        export * from "other";
        const mod = require('pkg');
        """
        deps = self.analyzer.get_dependencies(self._parse_root(code), "test.js")
        self.assertEqual(set(deps), {"./mod.js", "lib", "other", "pkg"})


if __name__ == "__main__":
    unittest.main()

