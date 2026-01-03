# Complexipy MCP Server

A Model Context Protocol (MCP) server that wraps `complexipy` to provide cognitive complexity analysis for Python codebases. This server uses the `complexipy` Python API for accurate and robust analysis.

## Features

- **Directory Scanning**: Recursively analyze all `.py` files in a directory and filter by complexity threshold.
- **File Scanning**: Analyze a single Python file.
- **Data Processing**: Uses `pandas` for efficient data filtering and sorting.
- **Clean Output**: Returns JSON formatted results (list of objects).
- **No Emojis**: Pure data output suitable for machine consumption.
- **Stdio Transport**: Uses standard input/output for communication, making it compatible with most MCP clients.

## Installation & Usage

### Quick Start

You can run the server directly using `uvx` (no installation required):

```bash
uvx complexipy-mcp
```

### Configuration for Claude Desktop

Add the following configuration to your MCP client settings (e.g., `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "complexipy": {
      "command": "uvx",
      "args": [
        "complexipy-mcp"
      ]
    }
  }
}
```

### Local Development

1. Clone the repository.
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Run the server locally:
   ```bash
   uv run complexipy-mcp
   ```

#### Local Configuration for Claude Desktop

If you are developing locally, point the configuration to your local setup:

```json
{
  "mcpServers": {
    "complexipy": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/complexipy-mcp",
        "run",
        "complexipy-mcp"
      ]
    }
  }
}
```

## Tools

### `scan_directory`
Scans a directory for files exceeding a cognitive complexity threshold.

- **Arguments**:
  - `directory_path` (string): Absolute path to the directory to scan.
  - `threshold` (integer): Complexity limit (default: 15).
- **Returns**: JSON string containing a list of files that exceed the threshold.
  ```json
  [
    {
      "file_path": "/abs/path/to/file.py",
      "complexity": 25,
      "functions": [
        {
          "name": "function_name",
          "complexity": 10,
          "line_start": 5,
          "line_end": 15
        }
      ],
      "status": "exceeds_threshold"
    }
  ]
  ```

### `scan_file`
Scans a single file for cognitive complexity.

- **Arguments**:
  - `file_path` (string): Absolute path to the file.
  - `threshold` (integer): Complexity limit (default: 15).
- **Returns**: JSON string containing the result if it exceeds the threshold.
