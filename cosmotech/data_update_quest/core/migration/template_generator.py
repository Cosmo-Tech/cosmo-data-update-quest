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
from datetime import datetime


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

        # Remove description fields before comparison
        source_schema_no_desc = self._remove_descriptions(self.source_schema)
        target_schema_no_desc = self._remove_descriptions(self.target_schema)

        self.schema_diff = DeepDiff(source_schema_no_desc, target_schema_no_desc, ignore_order=True)

    @staticmethod
    def _remove_descriptions(schema: Dict[str, Any]) -> Dict[str, Any]:
        """Remove all description fields from a schema recursively"""
        if not isinstance(schema, dict):
            return schema

        result = {k: v for k, v in schema.items() if k != "description"}

        for key, value in list(result.items()):
            if isinstance(value, dict):
                result[key] = MigrationTemplateGenerator._remove_descriptions(value)
            elif isinstance(value, list):
                result[key] = [
                    MigrationTemplateGenerator._remove_descriptions(item) if isinstance(item, dict) else item
                    for item in value
                ]

        return result

    @staticmethod
    def _resolve_references(
        schema: Dict[str, Any], openapi: Dict[str, Any], resolved_refs: Optional[set] = None
    ) -> Dict[str, Any]:
        """Recursively resolve references in the schema"""
        if resolved_refs is None:
            resolved_refs = set()

        if not isinstance(schema, dict):
            return schema

        # Handle $ref
        if "$ref" in schema:
            ref = schema["$ref"]

            # Avoid circular references
            if ref in resolved_refs:
                return {k: v for k, v in schema.items() if k != "$ref"}

            resolved_refs.add(ref)

            # Extract referenced schema
            ref_schema = MigrationTemplateGenerator._extract_ref_schema(ref, openapi)

            # Recursively resolve references in the referenced schema
            resolved_schema = MigrationTemplateGenerator._resolve_references(ref_schema, openapi, resolved_refs)

            # Merge any additional properties from the original schema, excluding description
            result = {k: v for k, v in schema.items() if k != "$ref" and k != "description"}
            result.update({k: v for k, v in resolved_schema.items() if k != "description"})
            return result

        # Handle allOf - flatten the structure by merging all schemas
        if "allOf" in schema and isinstance(schema["allOf"], list):
            # Create a copy of the schema without allOf
            result = {k: v for k, v in schema.items() if k != "allOf"}

            # Initialize merged properties and required fields
            merged_properties = result.get("properties", {})
            required_fields = set(result.get("required", []))

            # Process each schema in allOf
            for subschema in schema["allOf"]:
                # Resolve references in the subschema
                resolved_subschema = MigrationTemplateGenerator._resolve_references(subschema, openapi, resolved_refs)

                # Merge properties
                if "properties" in resolved_subschema:
                    if "properties" not in result:
                        result["properties"] = {}
                    result["properties"].update(resolved_subschema["properties"])

                # Merge required fields
                if "required" in resolved_subschema:
                    required_fields.update(resolved_subschema["required"])

                # Merge other attributes (type, format, etc.), excluding description
                for key, value in resolved_subschema.items():
                    if key not in ["properties", "required", "description"]:
                        # Special handling for lists - combine them instead of overwriting
                        if key in result and isinstance(result[key], list) and isinstance(value, list):
                            # For enum and examples, deduplicate values
                            if key in ["enum", "examples"]:
                                # For enum and examples, deduplicate values
                                # Convert to tuple for hashability if needed
                                try:
                                    result[key] = list(set(result[key] + value))
                                except TypeError:
                                    # If items aren't hashable (e.g., dicts), just concatenate
                                    combined = result[key].copy()
                                    for item in value:
                                        if item not in combined:
                                            combined.append(item)
                                    result[key] = combined
                            else:
                                # For other lists (like oneOf, anyOf), simply concatenate
                                combined = result[key].copy()
                                for item in value:
                                    if item not in combined:
                                        combined.append(item)
                                result[key] = combined
                        else:
                            # For non-list properties, overwrite as before
                            result[key] = value

            # Update required fields if any were collected
            if required_fields:
                result["required"] = list(required_fields)

            # Continue processing the merged schema
            return MigrationTemplateGenerator._resolve_references(result, openapi, resolved_refs)

        # Recursively process all properties, excluding description
        result = {}
        for key, value in schema.items():
            if key != "description":  # Skip description fields
                if isinstance(value, dict):
                    result[key] = MigrationTemplateGenerator._resolve_references(value, openapi, resolved_refs)
                elif isinstance(value, list):
                    result[key] = [
                        (
                            MigrationTemplateGenerator._resolve_references(item, openapi, resolved_refs)
                            if isinstance(item, dict)
                            else item
                        )
                        for item in value
                    ]
                else:
                    result[key] = value

        return result

    @staticmethod
    def _extract_ref_schema(ref: str, openapi: Dict[str, Any]) -> Dict[str, Any]:
        """Extract schema from a reference"""
        # Handle different reference formats
        if ref.startswith("#/components/schemas/"):
            schema_name = ref.split("/")[-1]
            return openapi["components"]["schemas"][schema_name]
        elif ref.startswith("#/definitions/"):
            schema_name = ref.split("/")[-1]
            return openapi["definitions"][schema_name]
        # Add more reference formats as needed

        raise ValueError(f"Unsupported reference format: {ref}")

    @staticmethod
    def _extract_schema(openapi: Dict[str, Any], model_name: str) -> Dict[str, Any]:
        """Extract schema from OpenAPI definition and resolve all references"""
        # OpenAPI 3.x
        if "components" in openapi and "schemas" in openapi["components"]:
            if model_name in openapi["components"]["schemas"]:
                schema = openapi["components"]["schemas"][model_name]
                return MigrationTemplateGenerator._resolve_references(schema, openapi)

        # OpenAPI/Swagger 2.x
        if "definitions" in openapi:
            if model_name in openapi["definitions"]:
                schema = openapi["definitions"][model_name]
                return MigrationTemplateGenerator._resolve_references(schema, openapi)

        raise ValueError(f"Model {model_name} not found in OpenAPI definition")

    @staticmethod
    def _convert_path_to_dot_notation(path: str) -> str:
        """
        Convert a path from bracket notation to dot notation for jq.

        Example:
        "root['properties']['user']['properties']['address']['properties']['street']"
        becomes "user.address.street"
        """
        # Extract all parts between ['properties'] and the next [ or end of string
        parts = []
        current_pos = 0

        while True:
            # Find the next ['properties'] occurrence
            prop_start = path.find("['properties']", current_pos)
            if prop_start == -1:
                break

            # Move past ['properties']
            current_pos = prop_start + len("['properties']")

            # Find the next property name
            if current_pos < len(path) and path[current_pos:].startswith("['"):
                # Extract the property name between quotes
                name_start = path.find("'", current_pos) + 1
                name_end = path.find("'", name_start)
                if name_start > 0 and name_end > name_start:
                    property_name = path[name_start:name_end]
                    parts.append(property_name)
                    current_pos = name_end + 2  # Move past the closing ']
                else:
                    # If we can't find a proper property name, break
                    break

        # Join parts with dots
        return ".".join(parts)

    def _get_nested_default(self, path: str) -> Optional[Any]:
        """Get default value for a nested property path"""
        # Convert dot notation to a list of property names
        parts = path.split(".")

        # Start from the target schema
        current = self.target_schema

        # Navigate through the properties
        for i, part in enumerate(parts):
            # Check if we're at a properties object
            if "properties" in current and part in current["properties"]:
                current = current["properties"][part]

                # If we're at the last part, return the default if available
                if i == len(parts) - 1:
                    return current.get("default")

            else:
                # Property not found
                return None

        return None

    def _extract_nested_properties(self, schema: Dict[str, Any], parent_path: str = "") -> List[str]:
        """Extract all nested properties from an object schema"""
        properties = []

        if isinstance(schema, dict) and "properties" in schema:
            for prop_name, prop_schema in schema["properties"].items():
                path = f"{parent_path}.{prop_name}" if parent_path else prop_name
                properties.append(path)

                # Recursively extract nested properties
                if isinstance(prop_schema, dict) and "properties" in prop_schema:
                    nested_props = self._extract_nested_properties(prop_schema, path)
                    properties.extend(nested_props)

        return properties

    def analyze_changes(self) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze schema differences and categorize them"""
        changes = {
            "removals": [],
            "additions": [],
            "type_changes": [],
            "moves": [],  # For nested field restructuring
        }

        # Process removed fields
        if "dictionary_item_removed" in self.schema_diff:
            processed_fields = set()  # Track processed fields to avoid duplicates
            for item in self.schema_diff["dictionary_item_removed"]:
                if "['properties']" in item:
                    field = self._convert_path_to_dot_notation(item)
                    if (
                        field and field not in processed_fields
                    ):  # Only add if we extracted a valid field and haven't processed it yet
                        # Add the top-level field
                        changes["removals"].append({"field": field})
                        processed_fields.add(field)

                        # Check if this is an object reference
                        field_schema = self._get_nested_schema_property(self.source_schema, field)
                        if field_schema and isinstance(field_schema, dict) and "properties" in field_schema:
                            # Extract all nested properties
                            nested_props = self._extract_nested_properties(field_schema, field)
                            for nested_prop in nested_props:
                                if nested_prop not in processed_fields:
                                    changes["removals"].append({"field": nested_prop})
                                    processed_fields.add(nested_prop)

        # Process added fields
        if "dictionary_item_added" in self.schema_diff:
            processed_fields = set()  # Track processed fields to avoid duplicates
            for item in self.schema_diff["dictionary_item_added"]:
                if "['properties']" in item:
                    field = self._convert_path_to_dot_notation(item)
                    if (
                        field and field not in processed_fields
                    ):  # Only add if we extracted a valid field and haven't processed it yet
                        # Get default value if available
                        default = self._get_nested_default(field)
                        changes["additions"].append({"field": field, "default": default})
                        processed_fields.add(field)

                        # Check if this is an object reference
                        field_schema = self._get_nested_schema_property(self.target_schema, field)
                        if field_schema and isinstance(field_schema, dict) and "properties" in field_schema:
                            # Extract all nested properties
                            nested_props = self._extract_nested_properties(field_schema, field)
                            for nested_prop in nested_props:
                                if nested_prop not in processed_fields:
                                    nested_default = self._get_nested_default(nested_prop)
                                    changes["additions"].append({"field": nested_prop, "default": nested_default})
                                    processed_fields.add(nested_prop)

        # Process type changes
        if "type_changes" in self.schema_diff:
            for path, change in self.schema_diff["type_changes"].items():
                if "['properties']" in path and "['type']" in path:
                    # Extract the path without the ['type'] part
                    field_path = path.split("['type']")[0]
                    field = self._convert_path_to_dot_notation(field_path)
                    if field:  # Only add if we extracted a valid field
                        changes["type_changes"].append(
                            {"field": field, "old_type": change["old_value"], "new_type": change["new_value"]}
                        )

        return changes

    def _get_nested_schema_property(self, schema: Dict[str, Any], path: str) -> Optional[Dict[str, Any]]:
        """Get a nested property from a schema using a dot-notation path"""
        parts = path.split(".")
        current = schema

        for part in parts:
            if "properties" in current and part in current["properties"]:
                current = current["properties"][part]
            else:
                return None

        return current

    def generate_jq_script(self) -> str:
        """Generate jq transformation script with improved readability"""
        changes = self.analyze_changes()

        jq_parts = []

        # Add header comment
        jq_parts.append(f"# JQ transformation script generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        jq_parts.append("# This script transforms data from the source schema to the target schema")
        jq_parts.append("")

        # Handle removals
        if changes["removals"]:
            jq_parts.append("# Field removals")
            for removal in changes["removals"]:
                jq_parts.append(f"del(.{removal['field']})")
            jq_parts.append("")

        # Handle additions
        if changes["additions"]:
            jq_parts.append("# Field additions")
            for addition in changes["additions"]:
                if addition["default"] is not None:
                    default_json = json.dumps(addition["default"])
                    jq_parts.append(f".{addition['field']} = {default_json}")
                else:
                    jq_parts.append(f".{addition['field']} = null")
            jq_parts.append("")

        # Format as multiline script with pipes
        if len(jq_parts) > 3:  # More than just the header comments
            # Join non-comment lines with pipe
            result = ""
            pipe_needed = False

            for line in jq_parts:
                if line and not line.startswith("#") and line.strip():
                    if pipe_needed:
                        result += "| "
                    result += line + "\n"
                    pipe_needed = True
                else:
                    result += line + "\n"
                    pipe_needed = False

            return result.strip()

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
