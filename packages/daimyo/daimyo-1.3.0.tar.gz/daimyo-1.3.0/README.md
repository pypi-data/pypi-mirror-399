# Daimyo - Rules Server for Agents

A Python server providing rules to AI agents through REST and MCP interfaces. Supports scope-based rules with inheritance, categories for filtering, and server federation for distributed rule management.

## Features

- **Multiple Interfaces**: REST API, MCP (Model Context Protocol), and CLI
- **Scope Inheritance**: Single and multiple parent inheritance with priority-based conflict resolution
- **Rule Types**: Commandments (MUST) and Suggestions (SHOULD)
- **Categories**: Organize rules into hierarchical categories for selective retrieval
- **Server Federation**: Distribute scopes across multiple servers with automatic merging
- **Multiple Formats**: Output as YAML, JSON, or Markdown
- **Clean Architecture**: Domain-driven design with clear separation of concerns

## Installation

```bash
pip install daimyo
```

Or install from source:

```bash
git clone https://gitlab.com/Kencho1/daimyo.git
cd daimyo
pip install -e .
```

## Quick Start

### 1. Set Up Your Rules

```bash
cp -r example-daimyo-rules daimyo-rules
```

### 2. Start the Server

```bash
daimyo serve
```

### 3. Access the API

Visit http://localhost:8000/docs for interactive API documentation.

```bash
curl http://localhost:8000/api/v1/scopes/python-general/rules
```

## Core Concepts

### Scopes

Scopes represent organizational contexts (company, team, project). Each scope is a directory containing:

- `metadata.yml` - Scope configuration and parent references
- `commandments.yml` - Mandatory rules (MUST)
- `suggestions.yml` - Recommended rules (SHOULD)

```text
daimyo-rules/
├── python-general/
│   ├── metadata.yml
│   ├── commandments.yml
│   └── suggestions.yml
└── team-backend/
    ├── metadata.yml
    ├── commandments.yml
    └── suggestions.yml
```

### Metadata Format

```yaml
name: scope-name
description: Human-readable description
parents:
  - parent-scope-1
  - parent-scope-2
tags:
  team: backend
  language: python
```

**Fields:**

- `name`: Scope identifier (must match directory name)
- `description`: Human-readable description
- `parents`: List of parent scopes (first = highest priority)
- `tags`: Key-value pairs for categorization

### Categories

Categories are hierarchical subdivisions within rules:

```yaml
python.web.testing:
  when: When testing web interfaces
  ruleset:
    - Use playwright for acceptance tests
    - Use pytest fixtures for test setup
```

### Rule Types

**Commandments (MUST)**: Mandatory rules that accumulate through inheritance

**Suggestions (SHOULD)**: Recommended rules that can be overridden or appended with `+` prefix

### Why not nesting the categories?

While it seems more intuitive, it proved to be confusing and harder to maintain in certain cases, e.g.:

- Appending suggestions: it's confusing to know whether the `+` must be prepended to the innermost category, to the root category, or to a category in between.
- Sharding categories: should it combine the innermost category or every category and subcategory defined?

For that reason it was decided to keep the categories at the root level, using the explicit path notation and nesting them logically using the dot path splitting.

## Usage

### REST API

Start the server:

```bash
daimyo serve
daimyo serve --host 0.0.0.0 --port 8080
```

Get rules:

```bash
curl http://localhost:8000/api/v1/scopes/python-general/rules

curl -H "Accept: application/json" \
  http://localhost:8000/api/v1/scopes/python-general/rules

curl -H "Accept: text/markdown" \
  http://localhost:8000/api/v1/scopes/python-general/rules
```

Filter by categories:

```bash
curl "http://localhost:8000/api/v1/scopes/team-backend/rules?categories=python.web,python.testing"
```

### MCP Server

Start the MCP server:

```bash
# Using stdio transport (default)
daimyo mcp

# Using HTTP transport
daimyo mcp --transport http

# Using HTTP with custom host and port
daimyo mcp --transport http --host 127.0.0.1 --port 8002
```

Available tools:

- `get_rules(scope_name, categories?)` - Get formatted rules for a scope
- `get_category_index(scope_name)` - Get a hierarchical list of all available categories with their descriptions
- `list_scopes()` - List available scopes
- `apply_scope_rules(scope_name, categories?)` - Get prompt template with rules

#### Connecting to the MCP server

Add the running _daimyo_ MCP server instance to your configuration (replace the server name and the URL with your own):

```json
{
  "mcpServers": {
    "daimyo-rules": {
      "type": "http",
      "url": "http://daimyo-mcp-instance/mcp"
    }
  }
}
```

Instruct your agents how to use the tools:

- State the project scope to use.
- Tell it to read the categories index and fetch the rules of the relevant categories before anything else.

For instance, in `CLAUDE.md`:

```markdown
- The current scope name of this project is `project-api`.
- First and foremost, use the `daimyo-rules` MCP server tools.
  - Use `list_scopes()` to see available scopes.
  - Use `get_category_index` passing the current scope name to list available categories and their descriptions in the given scope.
  - Depending on the categories that apply to the current task, use `get_rules` with the current scope name and a comma-separated list of all the categories that apply, to fetch the specific rules for the related categories.
```

Note some less capable models (like local models via Ollama) may need additional or more detailed instructions.

To make the instructions reusable, the scope name can be read from a file (for instance `.project-scope`).

### CLI Commands

```bash
daimyo list-scopes
daimyo show python-general
daimyo --version
```

## Configuration

Configuration is managed via `config/settings.toml` or environment variables.

### Configuration Parameters

All configuration parameters with their defaults and descriptions:

#### Rules Directory

- **`rules_path`** (default: `"./daimyo-rules"`)
  - Path to the directory containing scope definitions
  - Environment variable: `DAIMYO_RULES_PATH`

#### Logging

- **`console_log_level`** (default: `"WARNING"`)
  - Log level for console output: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
  - Environment variable: `DAIMYO_CONSOLE_LOG_LEVEL`

- **`file_log_level`** (default: `"INFO"`)
  - Log level for file output: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
  - Environment variable: `DAIMYO_FILE_LOG_LEVEL`

- **`log_file`** (default: `"logs/daimyo.log"`)
  - Path to the main log file
  - Environment variable: `DAIMYO_LOG_FILE`

- **`log_json_file`** (default: `"logs/daimyo.jsonl"`)
  - Path to the JSON-formatted log file
  - Environment variable: `DAIMYO_LOG_JSON_FILE`

#### Scope Resolution

- **`max_inheritance_depth`** (default: `10`, range: `1-100`)
  - Maximum depth for scope inheritance chain to prevent infinite loops
  - Environment variable: `DAIMYO_MAX_INHERITANCE_DEPTH`

#### Remote Server (Federation)

- **`master_server_url`** (default: `""`)
  - URL of master server for scope federation (e.g., `"http://master.example.com:8000"`)
  - Leave empty to disable federation
  - Environment variable: `DAIMYO_MASTER_SERVER_URL`

- **`remote_timeout_seconds`** (default: `5`, range: `1-60`)
  - Timeout in seconds for remote server requests
  - Environment variable: `DAIMYO_REMOTE_TIMEOUT_SECONDS`

- **`remote_max_retries`** (default: `3`, range: `0-10`)
  - Maximum number of retry attempts for failed remote requests
  - Environment variable: `DAIMYO_REMOTE_MAX_RETRIES`

#### REST API Server

- **`rest_host`** (default: `"0.0.0.0"`)
  - Host address to bind the REST API server
  - Environment variable: `DAIMYO_REST_HOST`

- **`rest_port`** (default: `8000`, range: `1-65535`)
  - Port number for the REST API server
  - Environment variable: `DAIMYO_REST_PORT`

#### MCP Server

- **`mcp_transport`** (default: `"stdio"`, options: `"stdio"`, `"http"`)
  - Transport type for MCP server
  - `stdio`: Standard input/output (for CLI integrations)
  - `http`: HTTP server (for HTTP-based integrations)
  - Environment variable: `DAIMYO_MCP_TRANSPORT`

- **`mcp_host`** (default: `"0.0.0.0"`)
  - Host address to bind the MCP server when using HTTP transport
  - Only applies when `mcp_transport="http"`
  - Environment variable: `DAIMYO_MCP_HOST`

- **`mcp_port`** (default: `8001`, range: `1-65535`)
  - Port number for the MCP server when using HTTP transport
  - Only applies when `mcp_transport="http"`
  - Environment variable: `DAIMYO_MCP_PORT`

### Configuration File Example

```toml
[default]
# Rules directory configuration
rules_path = "./daimyo-rules"

# Logging configuration
console_log_level = "WARNING"
file_log_level = "INFO"
log_file = "logs/daimyo.log"
log_json_file = "logs/daimyo.jsonl"

# Scope resolution configuration
max_inheritance_depth = 10

# Remote server configuration
master_server_url = ""
remote_timeout_seconds = 5
remote_max_retries = 3

# REST API configuration
rest_host = "0.0.0.0"
rest_port = 8000

# MCP configuration
mcp_transport = "stdio"
mcp_host = "0.0.0.0"
mcp_port = 8001

[development]
console_log_level = "DEBUG"
rest_port = 8001

[production]
console_log_level = "WARNING"
```

### Environment Variables

Override any configuration parameter using environment variables with the `DAIMYO_` prefix:

```bash
# Rules path
export DAIMYO_RULES_PATH="/custom/rules/path"

# Logging
export DAIMYO_CONSOLE_LOG_LEVEL="DEBUG"
export DAIMYO_FILE_LOG_LEVEL="INFO"

# Server federation
export DAIMYO_MASTER_SERVER_URL="http://master.example.com:8000"

# REST API
export DAIMYO_REST_HOST="127.0.0.1"
export DAIMYO_REST_PORT="9000"

# MCP Server
export DAIMYO_MCP_TRANSPORT="http"
export DAIMYO_MCP_HOST="0.0.0.0"
export DAIMYO_MCP_PORT="8001"
```

## Examples

The `example-daimyo-rules/` directory contains working examples:

### python-general

Base Python development rules with categories for core practices, testing, security, and documentation.

### python-fastapi

FastAPI framework rules extending `python-general` with routing, async patterns, and performance optimization.

### team-backend

Backend team rules extending `python-general` with REST API patterns, database access, and deployment considerations.

### project-api

Demonstrates multiple parent inheritance with `parents: [team-backend, python-fastapi]`:

- Combines team-specific and technology-specific rules
- Shows priority-based conflict resolution
- Uses `+` prefix to append to parent rules

## Advanced Topics

### Multiple Parent Inheritance

```yaml
parents:
  - high-priority
  - low-priority
```

**Commandments**: All rules from all parents are combined (additive)

**Suggestions**: First parent wins in conflicts; use `+` prefix to append instead of replace

### Server Federation

Configure a master server for distributed scope management:

```bash
export DAIMYO_MASTER_SERVER_URL="http://master.example.com:8000"
```

The system will:

1. Look for scopes locally
2. Look for scopes on the master server
3. Merge both if found in both locations (local extends remote)

### Scope Sharding

The same scope name can exist on both master server and locally. When both exist, they are merged with the remote version as the base and the local version extending it.

### Markdown formatting

Rules are typically rendered in Markdown format. LLMs may take advantage of certain formatting features such as emphasis or code fragments, so feel free to use these when writing rules.

### Jinja2 Templates

Rules and category descriptions support Jinja2 templates for dynamic content based on configuration and scope metadata.

#### Available Template Variables

Templates can access:

- **Configuration**: All `DAIMYO_*` environment variables and settings from `config/settings.toml`
- **Scope metadata**: `scope.name`, `scope.description`, `scope.tags`, `scope.sources`
- **Category info**: `category.key`, `category.when` (in rule text only)

#### Basic Example

**Configuration** (`config/settings.toml`):

```toml
[default]
TEAM_NAME = "Backend Team"
SLACK_CHANNEL = "#backend"
```

**Rules with templates** (`commandments.yml`):

```yaml
python.monitoring:
  when: "When monitoring {{ scope.name }} in {{ scope.tags.env | default('dev') }}"
  ruleset:
    - "Alert {{ TEAM_NAME }} via {{ SLACK_CHANNEL }}"
    - "Log level: {{ LOG_LEVEL }}"
```

**Rendered output** (assuming `scope.tags.env = "production"`):

```markdown
## python.monitoring
*When monitoring my-service in production*
- **MUST**: Alert Backend Team via #backend
- **MUST**: Log level: INFO
```

#### Best Practices

**Always use the `default` filter** for optional variables:

```yaml
- "Use {{ MY_VAR | default('fallback_value') }} for configuration"
```

**Conditionals**:

```yaml
- "{% if scope.tags.env == 'prod' %}Use strict security{% else %}Use standard security{% endif %}"
```

**Multiple variables**:

```yaml
- "Team {{ scope.tags.team }} deploys to {{ scope.tags.region }}"
```

#### Error Handling

If a template references an undefined variable without a default:

**REST API**: Returns 422 Unprocessable Entity

```json
{
  "detail": "Template variable 'UNDEFINED_VAR' is undefined in scope 'my-scope', category 'python.web'\n\nTemplate: Use {{ UNDEFINED_VAR }} here\n\nTip: Use Jinja2 'default' filter: {{ UNDEFINED_VAR | default('fallback') }}"
}
```

**MCP/CLI**: Returns error string with same guidance

#### Use Cases

**Environment-aware rules**:

```yaml
python.deployment:
  when: "When deploying to {{ scope.tags.region }}"
  ruleset:
    - "Deploy to {{ scope.tags.region }} region"
    - "{% if scope.tags.env == 'production' %}Require manual approval{% endif %}"
    - "Notification: {{ SLACK_DEPLOY_CHANNEL | default('#deployments') }}"
```

**Team-specific rules**:

```yaml
code-review:
  when: "When reviewing code for {{ TEAM_NAME }}"
  ruleset:
    - "Review in {{ CODE_REVIEW_TOOL | default('SonarQube') }}"
    - "Require approval from {{ scope.tags.team }} lead"
```

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
pytest --cov=daimyo
```

### Code Quality

```bash
mypy daimyo
ruff check daimyo
ruff format daimyo
```

## License

MIT
