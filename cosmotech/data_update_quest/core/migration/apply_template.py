# Copyright (C) - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import pathlib
import json
import jq


def apply_template(template: str, data: str) -> str:
    """
    Apply a JQ template to the provided data.

    Args:
        template (str): The JQ template to apply.
        data (str): The JSON data to transform.

    Returns:
        str: The transformed JSON data as a string.
    """
    try:
        # Parse the input data
        parsed_data = json.loads(data)

        # Apply the JQ template
        result = jq.compile(template).input(parsed_data).first()

        # Convert the result back to JSON string
        return json.dumps(result, indent=2)

    except Exception as e:
        raise ValueError(f"Error applying template: {e}") from e


def apply_template_from_file(template_file: pathlib.Path, data: str) -> str:
    """
    Apply a JQ template from a file to the provided data.

    Args:
        template_file (str): The path to the file containing the JQ template.
        data (str): The JSON data to transform.

    Returns:
        str: The transformed JSON data as a string.
    """
    try:
        # Read the JQ template from the file
        with open(template_file, "r") as file:
            template = file.read()

        # Apply the template
        return apply_template(template, data)

    except FileNotFoundError:
        raise ValueError(f"Template file not found: {template_file}")
    except Exception as e:
        raise ValueError(f"Error applying template from file: {e}") from e


def apply_template_from_file_to_file(
    template_file: pathlib.Path, input_file: pathlib.Path, output_file: pathlib.Path
) -> bool:
    """
    Apply a JQ template from a file to the JSON data in another file and save the result.

    Args:
        template_file (pathlib.Path): The path to the file containing the JQ template.
        input_file (pathlib.Path): The path to the input JSON data file.
        output_file (pathlib.Path): The path to save the transformed JSON data.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    try:
        # Read the input data
        with open(input_file, "r") as infile:
            data = infile.read()

        # Apply the template
        transformed_data = apply_template_from_file(template_file, data)

        # Write the transformed data to the output file
        with open(output_file, "w") as outfile:
            outfile.write(transformed_data)

        return True

    except Exception as e:
        print(f"Error applying template from file to file: {e}")
        return False
