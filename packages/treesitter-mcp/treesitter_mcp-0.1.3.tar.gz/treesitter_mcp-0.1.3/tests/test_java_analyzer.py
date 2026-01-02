import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from treesitter_mcp.core.language_manager import LanguageManager
from treesitter_mcp.languages.java import JavaAnalyzer


class JavaAnalyzerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.language_manager = LanguageManager()
        cls.analyzer = JavaAnalyzer(cls.language_manager)

    def _parse_root(self, code: str):
        tree = self.analyzer.parse(code)
        return tree.root_node

    def test_extract_symbols_classes_interfaces_methods_constructors(self):
        code = """
        class Foo {
          Foo(int x) { this.x = x; }
          void bar() {}
        }
        interface I { void doIt(); }
        """
        symbols = self.analyzer.extract_symbols(self._parse_root(code), "test.java")
        kinds = {(s.name, s.kind) for s in symbols}
        self.assertIn(("Foo", "class"), kinds)
        self.assertIn(("I", "interface"), kinds)
        self.assertIn(("bar", "method"), kinds)
        self.assertIn(("Foo", "constructor"), kinds)

    def test_call_graph_collects_calls(self):
        code = """
        class Foo {
          Foo() { bar(); }
          void bar() { baz(); this.qux(); Obj.staticCall(); }
          void baz() {}
        }
        """
        call_graph = self.analyzer.get_call_graph(self._parse_root(code), "test.java")
        nodes = {n.name: n.calls for n in call_graph.nodes}

        self.assertIn("bar", nodes)
        self.assertIn("baz", nodes)
        self.assertIn("Foo", nodes)  # constructor
        self.assertEqual(nodes["baz"], [])
        self.assertIn("bar", nodes["Foo"])
        self.assertTrue(any(call for call in nodes["bar"] if "baz" in call))
        self.assertTrue(any(call for call in nodes["bar"] if "qux" in call))
        self.assertTrue(any(call for call in nodes["bar"] if "staticCall" in call))

    def test_find_function_matches_methods_and_ctors(self):
        code = """
        class Foo { Foo() {} void bar() {} }
        """
        root = self._parse_root(code)
        result_method = self.analyzer.find_function(root, "test.java", "bar")
        names_method = {m.name for m in result_method.matches}
        self.assertIn("bar", names_method)

        result_ctor = self.analyzer.find_function(root, "test.java", "Foo")
        names_ctor = {m.name for m in result_ctor.matches}
        self.assertIn("Foo", names_ctor)

    def test_find_variable_and_usage(self):
        code = """
        class Foo {
          void bar() {
            int value = 1;
            value = value + 1;
            int other = value;
          }
        }
        """
        root = self._parse_root(code)
        var_result = self.analyzer.find_variable(root, "test.java", "value")
        kinds = {m.kind for m in var_result.matches}
        self.assertIn("variable_def", kinds)
        self.assertIn("variable_use", kinds)

        usage_result = self.analyzer.find_usage(root, "test.java", "value")
        self.assertGreaterEqual(len(usage_result.matches), 3)

    def test_dependencies_from_imports(self):
        code = """
        import foo.bar.Baz;
        import java.util.*;
        """
        deps = self.analyzer.get_dependencies(self._parse_root(code), "test.java")
        self.assertEqual(set(deps), {"foo.bar.Baz", "java.util"})


if __name__ == "__main__":
    unittest.main()


