# MuukTest Repair MCP

MCP server for analyzing and repairing E2E test failures (Playwright, Cypress, Selenium, etc).

## Installation

```bash
pip install muuk-test-repair-mcp
```

## Configuration

### VS Code / GitHub Copilot

Open User MCP Configuration (`Cmd+Shift+P` → "MCP: Open User Configuration"):

```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "muuk_api_key",
      "description": "MuukTest API Key",
      "password": true
    }
  ],
  "servers": {
    "muuk-test-repair": {
      "command": "muuk-test-repair-mcp",
      "env": {
        "MUUK_API_KEY": "${input:muuk_api_key}"
      }
    }
  }
}
```

### Claude Desktop

Edit `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "muuk-test-repair": {
      "command": "muuk-test-repair-mcp",
      "env": {
        "MUUK_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Cursor

Similar to VS Code configuration.

## Usage

Ask your AI agent:

```
Analyze the test failure in my project.
- workspace_path: /Users/me/my-project
- test_file_path: ./tests/login.spec.ts
- failure_info_path: ./failure-data/failure_info.json
- dom_elements_path: ./failure-data/dom_elements.json
- screenshot_path: ./failure-data/screenshot.png
```

Or more naturally:

```
Use analyze_test_failure to check the failure in ./failure-data/
The workspace is /Users/me/my-project
```

## Required Parameters

| Parameter | Description |
|-----------|-------------|
| `workspace_path` | **Required**: Absolute path to project root |
| `test_file_path` | Path to test file or directory (relative to workspace) |
| `failure_info_path` | Path to failure info JSON |
| `dom_elements_path` | Path to DOM elements JSON |
| `screenshot_path` | Path to failure screenshot |

## Available AI Presets

- `claude` (default)
- `openai`
- `gemini`
- `deepseek`
- `mistral`

## API Key

Request your `MUUK_API_KEY` from [MuukTest](https://muuktest.com).

## License

MIT