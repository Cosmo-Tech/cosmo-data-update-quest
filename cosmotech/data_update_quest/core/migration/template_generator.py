# Copyright (C) - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import json
import yaml
from typing import Dict, Any, List, Optional, Union
from deepdiff import DeepDiff
import os


class MigrationTemplateGenerator:
    """
    Analyzes OpenAPI schema differences and generates migration templates
    for standard data transformation tools.
    """

    def __init__(
        self,
        source_openapi: Dict[str, Any],
        target_openapi: Dict[str, Any],
        source_model_name: str,
        target_model_name: str,
    ):
        """Initialize with OpenAPI schemas"""
        # Extract schemas from OpenAPI
        self.source_schema = self._extract_schema(source_openapi, source_model_name)
        self.target_schema = self._extract_schema(target_openapi, target_model_name)
        self.schema_diff = DeepDiff(self.source_schema, self.target_schema, ignore_order=True)

    @staticmethod
    def _extract_schema(openapi: Dict[str, Any], model_name: str) -> Dict[str, Any]:
        """Extract schema from OpenAPI definition"""
        # OpenAPI 3.x
        if "components" in openapi and "schemas" in openapi["components"]:
            if model_name in openapi["components"]["schemas"]:
                return openapi["components"]["schemas"][model_name]

        # OpenAPI/Swagger 2.x
        if "definitions" in openapi:
            if model_name in openapi["definitions"]:
                return openapi["definitions"][model_name]

        raise ValueError(f"Model {model_name} not found in OpenAPI definition")

    def analyze_changes(self) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze schema differences and categorize them"""
        changes = {
            "renames": [],
            "removals": [],
            "additions": [],
            "type_changes": [],
            "moves": [],  # For nested field restructuring
        }

        # Process removed fields
        if "dictionary_item_removed" in self.schema_diff:
            for item in self.schema_diff["dictionary_item_removed"]:
                if "['properties']" in item.path():
                    field = item.path().split("['properties'][")[-1].strip("']")
                    changes["removals"].append({"field": field})

        # Process added fields
        if "dictionary_item_added" in self.schema_diff:
            for item in self.schema_diff["dictionary_item_added"]:
                if "['properties']" in item.path():
                    field = item.path().split("['properties'][")[-1].strip("']")
                    # Get default value if available
                    default = None
                    if field in self.target_schema.get("properties", {}):
                        default = self.target_schema["properties"][field].get("default")
                    changes["additions"].append({"field": field, "default": default})

        # Process type changes
        if "type_changes" in self.schema_diff:
            for path, change in self.schema_diff["type_changes"].items():
                if "['properties']" in path and "['type']" in path:
                    field_path = path.split("['type']")[0]
                    field = field_path.split("['properties'][")[-1].strip("']")
                    changes["type_changes"].append(
                        {"field": field, "old_type": change["old_value"], "new_type": change["new_value"]}
                    )

        # Detect potential renames
        self._detect_renames(changes)

        return changes

    def _detect_renames(self, changes: Dict[str, List[Dict[str, Any]]]):
        """
        Detect likely field renames by analyzing removed and added fields
        """
        removals = changes["removals"].copy()
        additions = changes["additions"].copy()

        for removal in removals:
            old_field = removal["field"]

            # Skip if not in source schema properties
            if old_field not in self.source_schema.get("properties", {}):
                continue

            old_def = self.source_schema["properties"][old_field]

            for addition in additions:
                new_field = addition["field"]

                # Skip if not in target schema properties
                if new_field not in self.target_schema.get("properties", {}):
                    continue

                new_def = self.target_schema["properties"][new_field]

                # Check if definitions are similar enough to suggest a rename
                if old_def.get("type") == new_def.get("type"):
                    # This is a simple heuristic - could be improved
                    changes["renames"].append({"from": old_field, "to": new_field})

                    # Remove from other lists to avoid duplication
                    changes["removals"] = [r for r in changes["removals"] if r["field"] != old_field]
                    changes["additions"] = [a for a in changes["additions"] if a["field"] != new_field]
                    break

    def generate_jq_script(self) -> str:
        """Generate jq transformation script"""
        changes = self.analyze_changes()

        jq_parts = []

        # Handle renames
        for rename in changes["renames"]:
            jq_parts.append(f".{rename['to']} = .{rename['from']}")

        # Handle removals (after renames to avoid conflicts)
        for rename in changes["renames"]:
            jq_parts.append(f"del(.{rename['from']})")

        for removal in changes["removals"]:
            jq_parts.append(f"del(.{removal['field']})")

        # Handle additions with defaults
        for addition in changes["additions"]:
            if addition["default"] is not None:
                # JSON-encode the default value
                default_json = json.dumps(addition["default"])
                jq_parts.append(f".{addition['field']} = {default_json}")
            else:
                # Add null if no default
                jq_parts.append(f".{addition['field']} = null")

        # Combine all parts with pipe
        if jq_parts:
            return " | ".join(jq_parts)
        return "."  # Identity transform if no changes

    @classmethod
    def from_openapi_files(
        cls, source_path: str, target_path: str, source_model: str, target_model: str
    ) -> "MigrationTemplateGenerator":
        """Create generator from OpenAPI files"""
        source_openapi = cls._load_file(source_path)
        target_openapi = cls._load_file(target_path)

        return cls(source_openapi, target_openapi, source_model, target_model)

    @staticmethod
    def _load_file(file_path: str) -> Dict[str, Any]:
        """Load YAML or JSON file"""
        with open(file_path, "r") as f:
            if file_path.endswith(".json"):
                return json.load(f)
            else:  # Assume YAML
                return yaml.safe_load(f)

    def save_all_templates(self, output_dir: str):
        """Generate and save all templates to files"""
        os.makedirs(output_dir, exist_ok=True)

        # Generate and save jq script
        jq_script = self.generate_jq_script()
        with open(os.path.join(output_dir, "transform.jq"), "w") as f:
            f.write(jq_script)

        # Generate README explaining the templates
        readme = self._generate_readme()
        with open(os.path.join(output_dir, "README.md"), "w") as f:
            f.write(readme)

    def _generate_readme(self) -> str:
        """Generate a README explaining how to use the generated templates"""
        changes = self.analyze_changes()

        sections = [
            "# Data Migration Templates",
            "\nThese templates were automatically generated based on schema differences between OpenAPI versions.\n",
            "## Changes Detected\n",
        ]

        # Summarize changes
        if changes["renames"]:
            sections.append("### Field Renames")
            for rename in changes["renames"]:
                sections.append(f"- `{rename['from']}` → `{rename['to']}`")
            sections.append("")

        if changes["removals"]:
            sections.append("### Field Removals")
            for removal in changes["removals"]:
                sections.append(f"- `{removal['field']}`")
            sections.append("")

        if changes["additions"]:
            sections.append("### Field Additions")
            for addition in changes["additions"]:
                default_str = f" (default: `{addition['default']}`)" if addition["default"] is not None else ""
                sections.append(f"- `{addition['field']}`{default_str}")
            sections.append("")

        if changes["type_changes"]:
            sections.append("### Type Changes")
            for change in changes["type_changes"]:
                sections.append(f"- `{change['field']}`: {change['old_type']} → {change['new_type']}")
            sections.append("")

        # Add usage instructions
        sections.append("## Usage Instructions\n")
        sections.append("### jq Script (Command Line)")
        sections.append("```bash")
        sections.append("#!/bin/bash")
        sections.append("# Iterate through Redis keys and apply transformation")
        sections.append('redis-cli --scan --pattern "your-pattern:*" | while read key; do')
        sections.append('  redis-cli GET "$key" | jq -f transform.jq | redis-cli -x SET "$key"')
        sections.append("done")
        sections.append("```\n")

        return "\n".join(sections)
