import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from treesitter_mcp.core.language_manager import LanguageManager
from treesitter_mcp.languages.php import PhpAnalyzer


class PhpAnalyzerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.language_manager = LanguageManager()
        cls.analyzer = PhpAnalyzer(cls.language_manager)

    def _parse_root(self, code: str):
        tree = self.analyzer.parse(code)
        return tree.root_node

    def test_extract_symbols_functions_classes_interfaces_traits_methods(self):
        code = """<?php
        function foo($a) { return $a; }
        class MyClass { function bar() { return foo($a); } }
        interface IExample { public function doWork(); }
        trait TExample { public function mixin() {} }
        ?>"""
        symbols = self.analyzer.extract_symbols(self._parse_root(code), "test.php")
        kinds = {(s.name, s.kind) for s in symbols}
        self.assertIn(("foo", "function"), kinds)
        self.assertIn(("MyClass", "class"), kinds)
        self.assertIn(("bar", "method"), kinds)
        self.assertIn(("IExample", "interface"), kinds)
        self.assertIn(("TExample", "trait"), kinds)

    def test_call_graph_collects_calls(self):
        code = """<?php
        function foo() {}
        class C {
            function bar() { foo(); $this->baz(); Baz::qux(); }
            public static function baz() { return 1; }
        }
        ?>"""
        call_graph = self.analyzer.get_call_graph(self._parse_root(code), "test.php")
        nodes = {n.name: n.calls for n in call_graph.nodes}

        self.assertIn("foo", nodes)
        self.assertIn("bar", nodes)
        self.assertIn("baz", nodes)
        self.assertEqual(nodes["foo"], [])
        self.assertIn("foo", nodes["bar"])
        self.assertIn("baz", nodes["bar"])
        self.assertIn("qux", nodes["bar"])

    def test_find_function_matches_methods(self):
        code = """<?php
        function foo() {}
        class C { function bar() {} }
        ?>"""
        result = self.analyzer.find_function(self._parse_root(code), "test.php", "bar")
        names = {m.name for m in result.matches}
        self.assertIn("bar", names)

    def test_find_variable_and_usage(self):
        code = """<?php
        function sample($value) {
            $value = $value + 1;
            $other = $value;
        }
        ?>"""
        root = self._parse_root(code)
        var_result = self.analyzer.find_variable(root, "test.php", "$value")
        kinds = {m.kind for m in var_result.matches}
        self.assertIn("variable_def", kinds)
        self.assertIn("variable_use", kinds)

        usage_result = self.analyzer.find_usage(root, "test.php", "$value")
        self.assertGreaterEqual(len(usage_result.matches), 3)

    def test_dependencies_from_include_require_and_use(self):
        code = """<?php
        include 'file.php';
        require_once "lib.php";
        use Foo\\Bar as Baz, Qux;
        ?>"""
        deps = self.analyzer.get_dependencies(self._parse_root(code), "test.php")
        self.assertEqual(set(deps), {"file.php", "lib.php", "Foo\\Bar", "Baz", "Qux"})


if __name__ == "__main__":
    unittest.main()

