from cosmotech.data_update_quest.core.migration.apply_template import apply_template_from_file_to_file
import pytest


@pytest.mark.parametrize(
    "input_name,template_name,intended_result,expected_result,expected_equal",
    [
        ("list.json", "root.txt", "list.json", True, True),  # Original test case
        ("first.json", "root.txt", "first.json", True, True),  # Test root template with first.json
        ("list.json", "first_element.txt", "first.json", True, True),  # Test first_element template with list.json
        ("list.json", "first_element.txt", "list.json", True, False),  # Test first_element template with list.json
        (
            "first.json",
            "first_element.txt",
            "first.json",
            False,
            None,
        ),  # Expect failure for first_element on first.json
        (
            "first.json",
            "do_not_exists.txt",
            "first.json",
            False,
            None,
        ),  # Expect failure for first_element on first.json
    ],
)
def test_apply_template(input_name, template_name, intended_result, expected_result, expected_equal, shared_datadir):
    """
    Test applying a JQ template from a file to a JSON data file and saving the result.

    Args:
        input_name: Name of the input JSON file in the source directory
        template_name: Name of the template file in the template directory
        expected_result: Whether the template application should succeed (True) or fail (False)
        expected_equal: Whether the output should equal the input after transformation (True),
                        be different (False), or not checked (None) if expected_result is False
        shared_datadir: pytest fixture for test data directory
    """
    input_file = shared_datadir / f"source/{input_name}"
    template_file = shared_datadir / f"template/{template_name}"
    intended_result_file = shared_datadir / f"source/{intended_result}"
    output_file = shared_datadir / f"test_apply_template_{input_name}_{template_name}.json"

    # Apply the template
    result = apply_template_from_file_to_file(template_file, input_file, output_file)

    # Check if the output file was created with expected result
    assert result is expected_result

    # Only verify content if we expect the operation to succeed
    if expected_result:
        # Verify the content of the output file
        with open(output_file, "r") as output_f, open(intended_result_file, "r") as intended_f:
            intended_data = intended_f.read()
            print(f"Input ({input_name}): {intended_data}")
            output_data = output_f.read()
            print(f"Output (template: {template_name}): {output_data}")

            if expected_equal:
                assert intended_data == output_data  # Check for expected transformation
            else:
                assert intended_data != output_data  # Check for expected transformation
