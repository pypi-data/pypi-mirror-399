# JIRA Assistant Skills Library

[![PyPI version](https://badge.fury.io/py/jira-assistant-skills-lib.svg)](https://badge.fury.io/py/jira-assistant-skills-lib)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A shared Python library for JIRA REST API automation, providing HTTP client, configuration management, error handling, and utilities for the [JIRA Assistant Skills](https://github.com/grandcamel/Jira-Assistant-Skills) project.

## Installation

```bash
pip install jira-assistant-skills-lib
```

With optional keyring support for secure credential storage:

```bash
pip install jira-assistant-skills-lib[keyring]
```

## Features

- **JiraClient**: HTTP client with automatic retry logic and exponential backoff
- **ConfigManager**: Multi-source configuration merging (env vars > settings.local.json > settings.json > defaults)
- **Error Handling**: Exception hierarchy mapping HTTP status codes to domain exceptions
- **Validators**: Input validation for issue keys, project keys, JQL queries, URLs, and more
- **Formatters**: Output formatting for tables, JSON, CSV export
- **ADF Helper**: Atlassian Document Format conversion (markdown/text to ADF and back)
- **Time Utils**: JIRA time format parsing and formatting (e.g., '2h', '1d 4h 30m')
- **Cache**: SQLite-based caching with TTL support for API responses
- **Credential Manager**: Secure credential storage via system keychain or JSON fallback

## Quick Start

```python
from jira_assistant_skills_lib import get_jira_client, handle_errors, ValidationError

@handle_errors
def main():
    # Get a configured JIRA client
    client = get_jira_client()

    # Fetch an issue
    issue = client.get_issue('PROJ-123')
    print(f"Summary: {issue['fields']['summary']}")

    # Search issues with JQL
    results = client.search_issues('project = PROJ AND status = Open')
    for issue in results['issues']:
        print(f"{issue['key']}: {issue['fields']['summary']}")

if __name__ == '__main__':
    main()
```

## Configuration

The library supports multiple configuration sources (in priority order):

1. **Environment variables**: `JIRA_API_TOKEN`, `JIRA_EMAIL`, `JIRA_SITE_URL`
2. **Settings files**: `.claude/settings.local.json` (gitignored) and `.claude/settings.json`
3. **Hardcoded defaults**: Fallback values

### Environment Variables

```bash
export JIRA_API_TOKEN="your-api-token"
export JIRA_EMAIL="your-email@company.com"
export JIRA_SITE_URL="https://your-company.atlassian.net"
```

### Profile-based Configuration

```python
# Use a specific profile
client = get_jira_client(profile='development')
```

## Core Components

### JiraClient

```python
from jira_assistant_skills_lib import JiraClient

client = JiraClient(
    base_url="https://your-company.atlassian.net",
    email="your-email@company.com",
    api_token="your-api-token"
)

# Make API calls
issue = client.get_issue('PROJ-123')
client.create_issue(project_key='PROJ', summary='New issue', issue_type='Task')
client.transition_issue('PROJ-123', 'Done')
```

### Error Handling

```python
from jira_assistant_skills_lib import (
    JiraError,
    AuthenticationError,
    PermissionError,
    NotFoundError,
    handle_errors
)

@handle_errors
def main():
    # Exceptions are caught and formatted nicely
    pass

# Or handle manually
try:
    client.get_issue('INVALID-999')
except NotFoundError as e:
    print(f"Issue not found: {e}")
except AuthenticationError as e:
    print(f"Auth failed: {e}")
except JiraError as e:
    print(f"JIRA error: {e}")
```

### Validators

```python
from jira_assistant_skills_lib import (
    validate_issue_key,
    validate_project_key,
    validate_jql,
    validate_url,
    ValidationError
)

try:
    key = validate_issue_key('PROJ-123')  # Returns 'PROJ-123'
    key = validate_issue_key('invalid')   # Raises ValidationError
except ValidationError as e:
    print(f"Invalid input: {e}")
```

### ADF Helper

```python
from jira_assistant_skills_lib import (
    markdown_to_adf,
    text_to_adf,
    adf_to_text
)

# Convert markdown to ADF for JIRA
adf = markdown_to_adf("**Bold** and *italic* text")

# Convert plain text to ADF
adf = text_to_adf("Simple text content")

# Extract text from ADF
text = adf_to_text(adf_document)
```

### Time Utils

```python
from jira_assistant_skills_lib import (
    parse_time_string,
    format_seconds,
    parse_relative_date
)

# Parse JIRA time format to seconds
seconds = parse_time_string('2h 30m')  # 9000

# Format seconds to JIRA time format
time_str = format_seconds(9000)  # '2h 30m'

# Parse relative dates
dt = parse_relative_date('yesterday')
dt = parse_relative_date('2025-01-15')
```

## Development

```bash
# Clone the repository
git clone https://github.com/grandcamel/jira-assistant-skills-lib.git
cd jira-assistant-skills-lib

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src tests
isort src tests
```

## License

MIT License - see [LICENSE](LICENSE) for details.
