# SkillHub CLI

> Command-line interface for the SkillHub registry of AI agent workflows

[![PyPI version](https://img.shields.io/pypi/v/skillhub.svg)](https://pypi.org/project/skillhub/)
[![Python versions](https://img.shields.io/pypi/pyversions/skillhub.svg)](https://pypi.org/project/skillhub/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is SkillHub CLI?

SkillHub CLI is a package manager for AI agent workflows. It allows you to search, download, and manage reusable AI agent task sequences from the [SkillHub Registry](https://github.com/v1k22/skillhub-registry).

Think of it like:
- **Homebrew** for AI agent workflows
- **npm** for coding tasks
- **pip** for automation recipes

## Architecture

![SkillHub Architecture](skillhub.png)

## Installation

### From PyPI (Coming Soon)

```bash
pip install skillhub
```

### From Source

```bash
git clone https://github.com/v1k22/skillhub-cli.git
cd skillhub-cli
pip install -e .
```

## Quick Start

```bash
# Search for skills
skillhub search "react"

# List all available skills
skillhub list

# Download a skill
skillhub pull react-app-setup

# Show skill details
skillhub show benchmark-qwen

# Validate a skill file
skillhub validate my-skill.md

# Show configuration and stats
skillhub info
```

## Commands

### `skillhub search <query>`

Search for skills by name, description, tags, or category.

```bash
# Search for React-related skills
skillhub search "react"

# Search for benchmarking skills
skillhub search "benchmark"

# Limit results
skillhub search "python" --limit 5

# Filter by category
skillhub search "model" --category ml-ops
```

### `skillhub list`

List all available skills in the registry.

```bash
# List all skills
skillhub list

# Filter by category
skillhub list --category web-development

# Refresh index from registry
skillhub list --refresh
```

### `skillhub pull <skill-name>`

Download a skill to your local directory.

```bash
# Pull to current directory
skillhub pull benchmark-qwen

# Pull to specific directory
skillhub pull react-app-setup --output ~/skills
```

### `skillhub show <skill-name>`

Show detailed information about a skill.

```bash
skillhub show model-deployment
```

### `skillhub validate <file>`

Validate a skill file format (useful when creating new skills).

```bash
skillhub validate my-new-skill.md
```

### `skillhub info`

Show SkillHub configuration and registry statistics.

```bash
skillhub info
```

## Configuration

SkillHub stores its configuration in `~/.skillhub/config.json`.

Default configuration:
```json
{
  "registry_url": "https://github.com/v1k22/skillhub-registry",
  "registry_raw_url": "https://raw.githubusercontent.com/v1k22/skillhub-registry/main",
  "cache_dir": "~/.skillhub/cache",
  "skills_dir": "~/.skillhub/skills",
  "index_url": "https://raw.githubusercontent.com/v1k22/skillhub-registry/main/index.json",
  "cache_ttl": 3600
}
```

You can manually edit this file to customize URLs or cache settings.

## Examples

### Finding and Using a Skill

```bash
# 1. Search for what you need
$ skillhub search "benchmark model"

Found 2 skill(s)
┌─────────────────┬──────────────┬─────────────────────────────┬────────────────┐
│ Name            │ Category     │ Description                 │ Tags           │
├─────────────────┼──────────────┼─────────────────────────────┼────────────────┤
│ benchmark-qwen  │ benchmarking │ Benchmark Qwen 3B model...  │ llm, benchmark │
└─────────────────┴──────────────┴─────────────────────────────┴────────────────┘

# 2. Get more details
$ skillhub show benchmark-qwen

# 3. Pull the skill
$ skillhub pull benchmark-qwen

✓ Skill downloaded successfully!
Location: ./benchmark-qwen.md

# 4. Follow the steps in the file
$ cat benchmark-qwen.md
```

### Listing Skills by Category

```bash
$ skillhub list --category ml-ops

📚 Available Skills: 1 total

ML-OPS (1 skills)
  model-deployment v1.0.0
    Deploy ML model as REST API using FastAPI with Docker...
```

### Creating and Validating a New Skill

```bash
# Create a skill using the template
$ curl -O https://raw.githubusercontent.com/v1k22/skillhub-registry/main/templates/skill-template.md

# Edit the template
$ vim skill-template.md

# Validate it
$ skillhub validate skill-template.md

✅ Perfect! No issues found.
```

## Use Cases

### 1. **Reproducible Development Environments**

```bash
# Set up a React development environment
skillhub pull react-app-setup
cat react-app-setup.md  # Follow the steps
```

### 2. **Model Benchmarking**

```bash
# Benchmark a model on different hardware
skillhub pull benchmark-qwen
# Run on machine A, save results
# Run on machine B, compare
```

### 3. **Team Onboarding**

```bash
# New developer joining the team
skillhub pull etl-pipeline
# Everyone uses the same setup process
```

### 4. **Learning Best Practices**

```bash
# Learn how to deploy ML models
skillhub pull model-deployment
# See production-ready setup
```

## Features

- 🔍 **Search**: Find skills by keywords, tags, or categories
- 📥 **Download**: Pull skills to local directory for use
- ✅ **Validate**: Check skill files for proper format
- 📊 **Stats**: View registry statistics and info
- 💾 **Cache**: Local caching for fast repeated access
- 🎨 **Beautiful Output**: Rich terminal formatting with colors and tables

## Development

### Running from Source

```bash
# Clone the repository
git clone https://github.com/v1k22/skillhub-cli.git
cd skillhub-cli

# Install in development mode
pip install -e .

# Run CLI
skillhub --help
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=skillhub
```

## Contributing

We welcome contributions! Please see the main [SkillHub Registry CONTRIBUTING.md](https://github.com/v1k22/skillhub-registry/blob/main/CONTRIBUTING.md) for guidelines.

### Reporting Bugs

Open an issue on [GitHub Issues](https://github.com/v1k22/skillhub-cli/issues) with:
- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- CLI version (`skillhub --version`)
- OS and Python version

## Roadmap

- [x] Basic CLI commands (search, list, pull)
- [x] Skill validation
- [x] Local caching
- [ ] Vector search for semantic matching
- [ ] Skill execution engine (`skillhub run`)
- [ ] Shell completions (bash, zsh, fish)
- [ ] Offline mode
- [ ] Skill updates notification
- [ ] Interactive mode

## Troubleshooting

### Command not found after installation

Make sure your Python scripts directory is in PATH:
```bash
export PATH="$PATH:$HOME/.local/bin"
```

### SSL Certificate errors

If you get SSL errors:
```bash
pip install --upgrade certifi
```

### Cache issues

Clear the cache:
```bash
rm -rf ~/.skillhub/cache
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- [SkillHub Registry](https://github.com/v1k22/skillhub-registry) - The skill repository
- [PyPI Package](https://pypi.org/project/skillhub/) - Install via pip
- [GitHub Issues](https://github.com/v1k22/skillhub-cli/issues) - Report bugs
- [Documentation](https://skillhub.dev) - Full documentation (coming soon)

---

**Made with ❤️ by the SkillHub community**
