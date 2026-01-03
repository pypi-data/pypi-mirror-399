# actions-latest-mcp

A Model Context Protocol (MCP) server that fetches the latest GitHub Actions versions from [actions-latest](https://github.com/simonw/actions-latest).

## Overview

This MCP server provides a simple tool to fetch the contents of `https://simonw.github.io/actions-latest/versions.txt`, which contains the latest version numbers for popular GitHub Actions. This is useful for keeping your workflows up to date.

## Installation

This package is published to PyPI and can be used directly without manual installation.

### Using with MCP (Recommended)

Add to your MCP client configuration (e.g., Claude Desktop's `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "actions-latest": {
      "command": "uvx",
      "args": ["actions-latest-mcp"]
    }
  }
}
```

The `uvx` command will automatically download and run the package from PyPI when needed.

### Manual Installation (Optional)

If you prefer to install the package manually:

```bash
# Install with uv
uv pip install actions-latest-mcp

# Or with pip
pip install actions-latest-mcp
```

Then configure your MCP client:

```json
{
  "mcpServers": {
    "actions-latest": {
      "command": "actions-latest-mcp"
    }
  }
}
```

### Available Tools

- **latest_github_actions_versions**: Returns a list of latest versions of all actions from the official GitHub Actions organization. This is useful for keeping your workflows up to date with the latest action versions.

### Running Directly

```bash
# Using uvx (recommended - no installation needed)
uvx actions-latest-mcp

# Or if manually installed
actions-latest-mcp

# Or using Python module
python -m actions_latest_mcp.server
```

## About actions-latest

This server fetches data from [simonw/actions-latest](https://github.com/simonw/actions-latest), a project that tracks the latest versions of popular GitHub Actions and makes them available in an easy-to-consume format.

## Publishing to PyPI

For maintainers, to publish a new version to PyPI:

### Automated Publishing (Recommended)

The repository includes a GitHub Actions workflow (`.github/workflows/publish.yml`) that automatically publishes to PyPI when a new release is created.

**Setup:**
1. Configure PyPI trusted publishing in your PyPI project settings
   - Go to https://pypi.org/manage/account/publishing/
   - Add a new pending publisher with:
     - PyPI Project Name: `actions-latest-mcp`
     - Owner: `Hiosdra`
     - Repository name: `actions-latest-mcp`
     - Workflow name: `publish.yml`
     - Environment name: `pypi`
2. Create a new release on GitHub with a version tag (e.g., `v0.1.0`)
3. The workflow will automatically build and publish to PyPI

### Manual Publishing

Alternatively, publish manually:

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Upload to PyPI
python -m twine upload dist/*
```