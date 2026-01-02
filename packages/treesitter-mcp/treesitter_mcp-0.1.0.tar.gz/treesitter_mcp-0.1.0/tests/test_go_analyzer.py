import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from treesitter_mcp.core.language_manager import LanguageManager
from treesitter_mcp.languages.go import GoAnalyzer


class GoAnalyzerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.language_manager = LanguageManager()
        cls.analyzer = GoAnalyzer(cls.language_manager)

    def _parse_root(self, code: str):
        tree = self.analyzer.parse(code)
        return tree.root_node

    def test_extract_symbols_functions_methods_struct_interface(self):
        code = """
        package main
        import "fmt"
        func foo(a int) int { return a }
        type MyStruct struct { x int }
        type MyInterface interface { Do() }
        func (m MyStruct) Bar() { foo(m.x) }
        """
        symbols = self.analyzer.extract_symbols(self._parse_root(code), "test.go")
        kinds = {(s.name, s.kind) for s in symbols}
        self.assertIn(("foo", "function"), kinds)
        self.assertIn(("MyStruct", "struct"), kinds)
        self.assertIn(("MyInterface", "interface"), kinds)
        self.assertIn(("Bar", "method"), kinds)

    def test_call_graph_collects_calls(self):
        code = """
        package main
        func foo() {}
        func (m MyStruct) Bar() { foo(); m.Baz(); other.Quux() }
        func (m MyStruct) Baz() {}
        """
        call_graph = self.analyzer.get_call_graph(self._parse_root(code), "test.go")
        nodes = {n.name: n.calls for n in call_graph.nodes}

        self.assertIn("foo", nodes)
        self.assertIn("Bar", nodes)
        self.assertIn("Baz", nodes)
        self.assertEqual(nodes["foo"], [])
        self.assertIn("foo", nodes["Bar"])
        self.assertIn("Baz", nodes["Bar"])
        self.assertIn("Quux", nodes["Bar"] or nodes["Bar"])

    def test_find_function_matches_methods(self):
        code = """
        package main
        func foo() {}
        func (s MyStruct) bar() {}
        """
        result = self.analyzer.find_function(self._parse_root(code), "test.go", "bar")
        names = {m.name for m in result.matches}
        self.assertIn("bar", names)

    def test_find_variable_and_usage(self):
        code = """
        package main
        func main() {
            value := 1
            value = value + 1
            var other = value
        }
        """
        root = self._parse_root(code)
        var_result = self.analyzer.find_variable(root, "test.go", "value")
        kinds = {m.kind for m in var_result.matches}
        self.assertIn("variable_def", kinds)
        self.assertIn("variable_use", kinds)

        usage_result = self.analyzer.find_usage(root, "test.go", "value")
        self.assertGreaterEqual(len(usage_result.matches), 3)

    def test_dependencies_from_imports(self):
        code = """
        package main
        import "fmt"
        import raw `os`
        import (
            "net/http"
            "encoding/json"
        )
        """
        deps = self.analyzer.get_dependencies(self._parse_root(code), "test.go")
        self.assertEqual(set(deps), {"fmt", "os", "net/http", "encoding/json"})


if __name__ == "__main__":
    unittest.main()

