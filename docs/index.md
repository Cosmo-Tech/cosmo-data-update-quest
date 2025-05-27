# Cosmo Data Update Quest Documentation

Welcome to the Cosmo Data Update Quest (CosmoDUQ) documentation. This tool provides a framework for migrating between different versions of Cosmo-Tech APIs.

## Overview

CosmoDUQ is designed to help users and developers manage API version transitions in the Cosmo Tech ecosystem. It provides tools and utilities to ensure smooth data migration between different API versions.

## Getting Started

### Installation

1. Ensure you have Python 3.11 or higher installed
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install the package:
   ```bash
   pip install -e .[all]
   ```

### Development Environment

#### Code Quality Tools

1. **Black Configuration**
   - The project uses Black for code formatting
   - Configuration in `pyproject.toml`:
     ```toml
     [tool.black]
     line-length = 120
     target-version = ["py311"]
     ```
   - Files are automatically formatted on commit

2. **Pre-commit Hooks**
   - Install hooks: `pre-commit install`
   - Configured hooks:
     - trailing-whitespace
     - end-of-file-fixer
     - check-added-large-files
     - black
   - Run manually: `pre-commit run --all-files`

#### Documentation

This documentation is built using MkDocs with the Material theme and several extensions:
- Material theme with light/dark mode
- Code syntax highlighting
- Table of contents generation
- Admonitions and content tabs
- Automatic versioning with mike

To build documentation locally:
```bash
pip install -e .[doc]
mkdocs serve
```

## Project Structure

- `/cosmotech/data_update_quest/`: Core migration framework
- `/docs/migrations/`: Version-specific migration guides
- `/docs/notes/`: Technical notes and analysis
- `/tests/`: Test suite (coming soon)

## Next Steps

- Explore the [Migration Guides](migrations/3.1_to_3.2.md) for version-specific information
- Review the [Technical Notes](notes/kubernetes-redis-migration-solution.md) for implementation details
- Check the [GitHub repository](https://github.com/Cosmo-Tech/cosmo-data-update-quest) for the latest updates
