# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Tree-sitter MCP Server is a Model Context Protocol server for code analysis using Tree-sitter. It provides AST extraction, symbol analysis, call graphs, and custom query capabilities for multiple programming languages.

## Development Commands

```bash
# Install in editable mode (recommended)
uv pip install -e .

# Or with pip
pip install -e .

# Run directly without installation
uvx treesitter-mcp

# Run MCP server in stdio mode (default, for Claude Desktop)
treesitter-mcp

# Run in HTTP mode for testing/development
treesitter-mcp --http --port 8000 --host 127.0.0.1
```

## Architecture

The codebase follows a **Language-Specific Analyzer** pattern:

### Core Components

1. **`src/treesitter_mcp/core/language_manager.py`** - Manages Tree-sitter language parsers
   - Loads and caches Parser instances for each language
   - Supports: C, C++, JavaScript, PHP, Rust, TypeScript, Go, Java, Python, Ruby

2. **`src/treesitter_mcp/core/analyzer.py`** - Abstract base class `BaseAnalyzer`
   - Defines the interface all language analyzers must implement
   - Provides common functionality: AST building, query execution, point/range navigation
   - Key abstract methods: `extract_symbols()`, `get_call_graph()`, `find_function()`, `find_variable()`, `find_usage()`, `get_dependencies()`

3. **`src/treesitter_mcp/languages/*.py`** - Language-specific analyzers
   - Each analyzer inherits from `BaseAnalyzer`
   - Implements language-specific Tree-sitter queries for symbol extraction
   - Pattern: Use `Query` and `QueryCursor` to capture AST nodes via S-expressions

4. **`src/treesitter_mcp/server.py`** - MCP server using FastMCP
   - Maps file extensions to analyzers in `get_analyzer()`
   - Exposes 12 MCP tools for different analysis operations
   - Entry point: `main()` handles --http, --port, --host arguments

5. **`src/treesitter_mcp/core/models.py`** - Pydantic models for structured data
   - `ASTNode`, `Symbol`, `AnalysisResult`, `CallGraph`, `SearchResult`

### Important: Ruby Analyzer

Ruby has a language module (`languages/ruby.py`) and is loaded in `LanguageManager`, but **is NOT registered in the `analyzers` dict in `server.py`**. This means `.rb` files are not currently supported even though the code exists.

## Adding a New Language

1. Install the tree-sitter binding (e.g., `pip install tree-sitter-<lang>`)
2. Add import and language to `_languages` dict in `core/language_manager.py`
3. Create `languages/<lang>.py` with a class inheriting from `BaseAnalyzer`
4. Implement all abstract methods using Tree-sitter S-expression queries
5. Import and register the analyzer in the `analyzers` dict in `server.py`
6. Add file extension mapping in `get_analyzer()` function

## Tree-sitter Version

The project uses `tree-sitter>=0.22.0` (pinned at minimum version 0.22.0 in pyproject.toml). The `ARCHITECTURE.md` documentation mentions version 0.21.3, which is outdated.

## MCP Tools

The server exposes these tools (decorated with `@mcp.tool()` in `server.py`):
- `treesitter_analyze_file` - Basic symbol extraction
- `treesitter_get_ast` - Full AST (use max_depth parameter for large files)
- `treesitter_get_call_graph` - Function call relationships
- `treesitter_find_function` / `treesitter_find_variable` / `treesitter_find_usage` - Search operations
- `treesitter_get_dependencies` - Import/include extraction
- `treesitter_run_query` - Custom Tree-sitter S-expression queries
- `treesitter_get_node_at_point` / `treesitter_get_node_for_range` - AST navigation
- `treesitter_cursor_walk` - Cursor-style view with context (focus + ancestors + siblings)
- `treesitter_get_supported_languages` - List available analyzers

## Known Limitations

Python analyzer lacks: `get_call_graph()`, `find_function()`, `find_variable()` implementations (returns "not supported" errors). See `FEATURES.md` for full feature matrix.
