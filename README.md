# Cosmo Data Update Quest (CosmoDUQ)

A Python-based migration framework for Cosmo-Tech APIs versions, designed to facilitate smooth transitions between different API versions in the Cosmo Tech ecosystem.

## Features

- Automated migration paths between Cosmo-Tech API versions
- Built on the Cosmo Tech Acceleration Library
- Command-line interface via `csm-duq` command
- Extensive documentation and migration guides

## Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- git (for version control and pre-commit hooks)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Cosmo-Tech/cosmo-data-update-quest.git
   cd cosmo-data-update-quest
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the package with all dependencies:
   ```bash
   pip install -e .[all]
   ```

4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development Setup

### Code Formatting

This project uses Black for code formatting with the following configuration:
- Line length: 120 characters
- Target Python version: 3.11
- Configured via `pyproject.toml`

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality:
- trailing-whitespace: Removes trailing whitespace
- end-of-file-fixer: Ensures files end with a newline
- check-added-large-files: Prevents large files from being committed
- black: Formats Python code

### Documentation

The documentation is built using MkDocs with the Material theme. To build and serve locally:

```bash
pip install -e .[doc]  # Install documentation dependencies
mkdocs serve          # Start local documentation server
```

Visit `http://127.0.0.1:8000` to view the documentation.

## Usage

Basic usage of the command-line tool:

```bash
csm-duq --help  # Show available commands
```

For detailed usage instructions and migration guides, please refer to the [official documentation](https://cosmo-tech.github.io/cosmo-data-update-quest).

## License

This project is licensed under the terms included in the LICENSE file.
