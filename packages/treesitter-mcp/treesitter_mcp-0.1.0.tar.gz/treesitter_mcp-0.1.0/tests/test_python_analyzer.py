import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from treesitter_mcp.core.language_manager import LanguageManager
from treesitter_mcp.languages.python import PythonAnalyzer


class PythonAnalyzerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.language_manager = LanguageManager()
        cls.analyzer = PythonAnalyzer(cls.language_manager)

    def _parse_root(self, code: str):
        return self.analyzer.parse(code).root_node

    def test_extract_symbols_functions_and_classes(self):
        code = """
        def foo(x):
            return x

        class MyClass:
            def method(self):
                return foo(1)
        """
        symbols = self.analyzer.extract_symbols(self._parse_root(code), "test.py")
        kinds = {(s.name, s.kind) for s in symbols}
        self.assertIn(("foo", "function"), kinds)
        self.assertIn(("MyClass", "class"), kinds)
        self.assertIn(("method", "function"), kinds)

    def test_call_graph_placeholder_is_empty(self):
        code = "def foo():\n    return 1\n"
        call_graph = self.analyzer.get_call_graph(self._parse_root(code), "test.py")
        self.assertEqual(call_graph.nodes, [])

    def test_find_function_placeholder_returns_empty(self):
        code = "def foo():\n    return 1\n"
        result = self.analyzer.find_function(self._parse_root(code), "test.py", "foo")
        self.assertEqual(result.matches, [])

    def test_find_usage(self):
        code = """
        def foo():
            value = 1
            return value
        """
        root = self._parse_root(code)
        usage_result = self.analyzer.find_usage(root, "test.py", "value")
        self.assertGreaterEqual(len(usage_result.matches), 2)

    def test_dependencies_from_imports(self):
        code = """
        import os
        import pkg.submodule as alias
        from collections import defaultdict
        """
        deps = self.analyzer.get_dependencies(self._parse_root(code), "test.py")
        self.assertEqual(set(deps), {"os", "pkg.submodule", "collections"})


if __name__ == "__main__":
    unittest.main()


