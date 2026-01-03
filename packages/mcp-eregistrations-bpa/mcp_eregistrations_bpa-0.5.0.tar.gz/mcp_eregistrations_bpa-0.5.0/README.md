# MCP eRegistrations BPA

**AI-powered Service Design for Government Digital Transformation**

An MCP server that enables AI assistants like Claude to design, configure, and deploy government services on the eRegistrations BPA platform using natural language.

## What It Does

Design and configure BPA services through conversation:

```
You: Create a "Business License" service
Claude: Created service with registration. Service ID: abc-123

You: Add a reviewer role
Claude: Added "Reviewer" role to the service

You: Set a $50 processing fee
Claude: Created fixed cost of $50 attached to the registration
```

Each step uses the right MCP tool. Full audit trail. Rollback if needed.

## Prerequisites

Install [uv](https://docs.astral.sh/uv/) (includes `uvx`):

```bash
# macOS (recommended)
brew install uv

# Other platforms
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Quick Install

**For Claude Desktop** — add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "BPA-elsalvador-dev": {
      "command": "uvx",
      "args": ["mcp-eregistrations-bpa"],
      "env": {
        "BPA_INSTANCE_URL": "https://bpa.dev.els.eregistrations.org",
        "KEYCLOAK_URL": "https://login.dev.els.eregistrations.org",
        "KEYCLOAK_REALM": "SV"
      }
    }
  }
}
```

> **Troubleshooting:** If you get "command not found: uvx", you installed via curl which puts uvx in `~/.local/bin` (not in GUI app PATH). Fix: either `brew install uv`, or use `"command": "/bin/zsh", "args": ["-c", "$HOME/.local/bin/uvx mcp-eregistrations-bpa"]`

**For Claude Code** — add to `.mcp.json` in your project:

```json
{
  "mcpServers": {
    "BPA-elsalvador-dev": {
      "command": "uvx",
      "args": ["mcp-eregistrations-bpa"],
      "env": {
        "BPA_INSTANCE_URL": "https://bpa.dev.els.eregistrations.org",
        "KEYCLOAK_URL": "https://login.dev.els.eregistrations.org",
        "KEYCLOAK_REALM": "SV"
      }
    }
  }
}
```

That's it. On first use, a browser opens for Keycloak login. Your BPA permissions apply automatically.

> **Tip:** Name each MCP after its instance (e.g., `BPA-elsalvador-dev`, `BPA-kenya-test`) to manage multiple environments.

## 90+ MCP Tools

| Category          | Capabilities                                                    |
| ----------------- | --------------------------------------------------------------- |
| **Services**      | Create, read, update, copy, export, transform to YAML           |
| **Registrations** | Full CRUD with parent service linking                           |
| **Institutions**  | Assign/unassign institutions to registrations                   |
| **Forms**         | Read/write Form.io components with container support            |
| **Roles**         | Create reviewer/approver/processor roles                        |
| **Bots**          | Configure workflow automation                                   |
| **Determinants**  | Text, select, numeric, boolean, date, classification, grid      |
| **Behaviours**    | Component visibility/validation effects with JSONLogic          |
| **Costs**         | Fixed fees and formula-based pricing                            |
| **Documents**     | Link document requirements to registrations                     |
| **Workflows**     | Arazzo-driven intent-based natural language service design      |
| **Audit**         | Complete operation history with rollback                        |
| **Analysis**      | Service inspection and dependency mapping                       |

## Natural Language Workflows

Ask Claude to design services using plain English:

| What you say                            | What happens                                         |
| --------------------------------------- | ---------------------------------------------------- |
| "Create a permit service"               | Creates service + registration with proper structure |
| "Add a reviewer role to this service"   | Adds UserRole with 'processing' assignment           |
| "Set a $75 application fee"             | Creates fixed cost attached to registration          |
| "Add document requirement for ID proof" | Links requirement to the registration                |

The workflow system uses [Arazzo](https://spec.openapis.org/arazzo/latest.html) specifications to orchestrate multi-step operations. It extracts your intent, validates inputs, and executes with full audit trail.

### Workflow Tools

| Tool | Purpose |
|------|---------|
| `workflow_list` | List available workflows by category |
| `workflow_search` | Find workflows matching natural language intent |
| `workflow_describe` | Get workflow details, inputs, and steps |
| `workflow_execute` | Run workflow with provided inputs |
| `workflow_start_interactive` | Begin guided step-by-step execution |
| `workflow_status` | Check execution progress |
| `workflow_rollback` | Undo a completed workflow |

## Key Features

**Audit Trail** — Every operation logged (who, what, when). Query history with `audit_list`.

**Rollback** — Undo any write operation. Restore previous state with `rollback`.

**Export** — Get complete service definitions as clean YAML (~25x smaller than raw JSON) for review or version control.

**Copy** — Clone existing services with selective component inclusion.

**Pagination** — All list endpoints support `limit` and `offset` for large datasets. Responses include `total` and `has_more` for navigation.

## Form MCP Tools

BPA uses Form.io for dynamic forms. These tools provide full CRUD operations on form components.

### Available Tools

| Tool | Purpose |
|------|---------|
| `form_get` | Get form structure with simplified component list |
| `form_component_get` | Get full details of a specific component |
| `form_component_add` | Add new component to form |
| `form_component_update` | Update component properties |
| `form_component_remove` | Remove component from form |
| `form_component_move` | Move component to new position/parent |
| `form_update` | Replace entire form schema |

### Form Types

- `applicant` (default) - Main application form
- `guide` - Guidance/help form
- `send_file` - File submission form
- `payment` - Payment form

### Property Availability

Properties vary by tool. Use `form_get` for overview, `form_component_get` for full details:

| Property | `form_get` | `form_component_get` |
|----------|------------|----------------------|
| key | Yes | Yes |
| type | Yes | Yes |
| label | Yes | Yes |
| path | Yes | Yes |
| is_container | Yes | No |
| children_count | For containers | No |
| required | When present | Yes (in validate) |
| validate | No | Yes |
| registrations | No | Yes |
| determinant_ids | No | Yes (in raw) |
| data | No | Yes |
| default_value | No | Yes |
| raw | No | Yes (complete object) |

### Container Types

Form.io uses containers to organize components. Each has different child accessors:

```
Container Type    Children Accessor
--------------    -----------------
tabs              components[] (tab panes)
panel             components[]
columns           columns[].components[] (2-level)
fieldset          components[]
editgrid          components[] (repeatable)
datagrid          components[]
table             rows[][] (HTML table)
well              components[]
container         components[]
```

### Usage Examples

**Get form overview:**
```
form_get(service_id="abc-123", form_type="applicant")
# Returns: component_count, component_keys, simplified components list
```

**Get specific component details:**
```
form_component_get(service_id="abc-123", component_key="firstName")
# Returns: full component with validate, data, determinant_ids, raw object
```

**Add component to form:**
```
form_component_add(
    service_id="abc-123",
    component={"key": "email", "type": "email", "label": "Email Address"},
    parent_key="personalInfo",  # Optional: nest under panel
    position=0                   # Optional: insert at position
)
```

**Update component:**
```
form_component_update(
    service_id="abc-123",
    component_key="firstName",
    updates={"validate": {"required": True}, "label": "First Name *"}
)
```

**Move component:**
```
form_component_move(
    service_id="abc-123",
    component_key="phoneNumber",
    new_parent_key="contactPanel",
    new_position=1
)
```

All write operations include `audit_id` for rollback capability.

## Determinant & Conditional Logic Tools

Create conditional logic that controls form behavior based on user input.

### Determinant Types

| Type | Use Case | Example |
|------|----------|---------|
| `textdeterminant` | Text field conditions | Show panel if country = "USA" |
| `selectdeterminant` | Dropdown selection | Different fees by business type |
| `numericdeterminant` | Numeric comparisons | Require docs if amount > 10000 |
| `booleandeterminant` | Checkbox conditions | Show section if newsletter = true |
| `datedeterminant` | Date comparisons | Validate expiry > today |
| `classificationdeterminant` | Catalog selections | Requirements by industry code |
| `griddeterminant` | Grid/table row conditions | Validate line items |

### Behaviour Effects

Apply determinants to components to control visibility and validation:

```
effect_create(
    service_id="abc-123",
    determinant_id="det-456",
    component_key="additionalDocs",
    effect_type="visibility"  # or "required", "disabled"
)
```

Use `componentbehaviour_list` and `componentbehaviour_get` to inspect existing effects.

## Example Session

```
You: List all services

Claude: Found 12 services. [displays table with IDs, names, status]

You: Analyze the "Business Registration" service

Claude: [shows registrations, roles, determinants, documents, costs]
        Found 3 potential issues: orphaned determinant, missing cost...

You: Create a copy called "Business Registration v2"

Claude: Created service with ID abc-123. Copied 2 registrations,
        4 roles, 8 determinants. Audit ID: xyz-789
```

## Authentication

Uses Keycloak OIDC with Authorization Code + PKCE:

1. Browser opens automatically on first connection
2. Login with your BPA credentials
3. Tokens managed automatically with refresh
4. Your BPA permissions apply to all operations

## Configuration

| Variable           | Description                 | Required |
| ------------------ | --------------------------- | -------- |
| `BPA_INSTANCE_URL` | BPA server URL              | Yes      |
| `KEYCLOAK_URL`     | Keycloak server URL         | Yes      |
| `KEYCLOAK_REALM`   | Keycloak realm name         | Yes      |
| `LOG_LEVEL`        | DEBUG, INFO, WARNING, ERROR | No       |

Logs: `~/.config/mcp-eregistrations-bpa/server.log`

## Development

```bash
# Clone and install
git clone https://github.com/unctad-ai/mcp-eregistrations-bpa.git
cd mcp-eregistrations-bpa
uv sync

# Run tests (1200+ tests)
uv run pytest

# Lint and format
uv run ruff check . && uv run ruff format .

# Type checking
uv run mypy src/
```

## License

Copyright (c) 2025-2026
UN for Trade & Development (UNCTAD)
Division on Investment and Enterprise (DIAE)
Business Facilitation Section

All rights reserved. See [LICENSE](LICENSE).

---

Part of [eRegistrations](https://businessfacilitation.org)
