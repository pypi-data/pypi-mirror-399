import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from treesitter_mcp.core.language_manager import LanguageManager
from treesitter_mcp.languages.rust import RustAnalyzer


class RustAnalyzerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.language_manager = LanguageManager()
        cls.analyzer = RustAnalyzer(cls.language_manager)

    def _parse_root(self, code: str):
        tree = self.analyzer.parse(code)
        return tree.root_node

    def test_extract_symbols_functions_struct_enum_trait(self):
        code = """
        fn foo(x: i32) -> i32 { x }
        struct S { x: i32 }
        enum E { A, B }
        trait T { fn t(&self); }
        impl T for S { fn t(&self) {} }
        """
        symbols = self.analyzer.extract_symbols(self._parse_root(code), "test.rs")
        kinds = {(s.name, s.kind) for s in symbols}
        self.assertIn(("foo", "function"), kinds)
        self.assertIn(("S", "struct"), kinds)
        self.assertIn(("E", "enum"), kinds)
        self.assertIn(("T", "trait"), kinds)

    def test_call_graph_collects_calls(self):
        code = """
        fn foo() {}
        fn bar() { foo(); baz.qux(); self.m(); Q::staticm(); }
        """
        call_graph = self.analyzer.get_call_graph(self._parse_root(code), "test.rs")
        nodes = {n.name: n.calls for n in call_graph.nodes}

        self.assertIn("foo", nodes)
        self.assertIn("bar", nodes)
        self.assertEqual(nodes["foo"], [])
        for expected in ("foo", "qux", "m", "staticm"):
            self.assertTrue(any(expected == call or expected in call for call in nodes["bar"]))

    def test_find_function(self):
        code = """
        fn target() {}
        """
        result = self.analyzer.find_function(self._parse_root(code), "test.rs", "target")
        names = {m.name for m in result.matches}
        self.assertIn("target", names)

    def test_find_variable_and_usage(self):
        code = """
        fn main() {
            let value = 1;
            let other = value;
            let value = value + 1;
        }
        """
        root = self._parse_root(code)
        var_result = self.analyzer.find_variable(root, "test.rs", "value")
        kinds = {m.kind for m in var_result.matches}
        self.assertIn("variable_def", kinds)
        self.assertIn("variable_use", kinds)

        usage_result = self.analyzer.find_usage(root, "test.rs", "value")
        self.assertGreaterEqual(len(usage_result.matches), 3)

    def test_dependencies_use_and_mod(self):
        code = """
        use crate::m::n;
        use std::{fmt, io};
        mod sub;
        extern crate foo;
        """
        deps = self.analyzer.get_dependencies(self._parse_root(code), "test.rs")
        self.assertEqual(set(deps), {"crate::m::n", "std", "fmt", "io", "sub", "foo"})


if __name__ == "__main__":
    unittest.main()


