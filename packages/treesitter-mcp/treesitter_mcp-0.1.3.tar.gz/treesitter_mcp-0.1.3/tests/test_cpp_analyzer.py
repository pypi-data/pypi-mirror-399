import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from treesitter_mcp.core.language_manager import LanguageManager
from treesitter_mcp.languages.cpp import CppAnalyzer


class CppAnalyzerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.language_manager = LanguageManager()
        cls.analyzer = CppAnalyzer(cls.language_manager)

    def _parse_root(self, code: str):
        return self.analyzer.parse(code).root_node

    def test_extract_symbols_functions_and_classes(self):
        code = """
        int foo(int a) { return a; }
        class MyClass { int value; };
        """
        symbols = self.analyzer.extract_symbols(self._parse_root(code), "test.cpp")
        kinds = {(s.name, s.kind) for s in symbols}
        self.assertIn(("foo", "function"), kinds)
        self.assertIn(("MyClass", "class"), kinds)

    def test_call_graph_collects_calls(self):
        code = """
        int foo() { return 0; }
        class MyClass {
        public:
            int bar() { foo(); this->baz(); obj.qux(); return 1; }
            int baz() { return 2; }
        };
        """
        call_graph = self.analyzer.get_call_graph(self._parse_root(code), "test.cpp")
        nodes = {n.name: n.calls for n in call_graph.nodes}

        self.assertIn("foo", nodes)
        self.assertIn("bar", nodes)
        self.assertIn("baz", nodes)
        self.assertEqual(nodes["foo"], [])
        self.assertIn("foo", nodes["bar"])
        self.assertIn("baz", nodes["bar"])
        self.assertIn("qux", nodes["bar"])

    def test_find_function(self):
        code = "int foo() { return 0; }\nclass C { int bar() { return foo(); } };"
        result = self.analyzer.find_function(self._parse_root(code), "test.cpp", "bar")
        names = {m.name for m in result.matches}
        self.assertIn("bar", names)

    def test_find_variable_and_usage(self):
        code = """
        int main() {
            int value = 1;
            value = value + 1;
            int other = value;
            return value;
        }
        """
        root = self._parse_root(code)
        var_result = self.analyzer.find_variable(root, "test.cpp", "value")
        kinds = {m.kind for m in var_result.matches}
        self.assertIn("variable_def", kinds)
        self.assertIn("variable_use", kinds)

        usage_result = self.analyzer.find_usage(root, "test.cpp", "value")
        self.assertGreaterEqual(len(usage_result.matches), 3)

    def test_dependencies_from_includes(self):
        code = """
        #include <vector>
        #include "my_header.hpp"
        """
        deps = self.analyzer.get_dependencies(self._parse_root(code), "test.cpp")
        self.assertEqual(set(deps), {"vector", "my_header.hpp"})


if __name__ == "__main__":
    unittest.main()



