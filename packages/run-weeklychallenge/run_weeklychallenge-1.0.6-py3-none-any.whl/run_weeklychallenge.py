import sys
import json
import jsonschema

from collections.abc import Callable
from typing import cast, Any


def run_weekly_challenge(
    run_solution: Callable[[object], str], inputs_example: str, inputs_schema_json: str
) -> None:
    """
    Runs a solution to https://theweeklychallenge.org using one or more sets of inputs provided as JSON command line arguments.

    Parameters:
    run_solution: callable taking one set of decoded inputs as an object and returning the stringified result
    inputs_example (str): example json input to specify on the command line, for use in error messages when inputs are incorrect
    inputs_schema_json (str): JSON schema (draft 2020-12) specifying each set of inputs
    """
    inputs: list[str] = sys.argv[1:]

    validator = jsonschema.Draft202012Validator(json.loads(inputs_schema_json))

    # inputs were incorrectly formatted and we should complain at the end
    inputs_error = False

    for inputs_json in inputs:
        # show the inputs
        print(f"Inputs: {inputs_json}")

        # decode the json
        try:
            inputs = json.loads(inputs_json)
        except Exception as inst:
            print(f"Error: invalid json: {inst}")
            inputs_error = True
            continue
        # validate inputs contains what we expect
        try:
            validator.validate(inputs)
        except jsonschema.ValidationError as inst:
            print(f"Error: invalid input: {inst.message}")
            inputs_error = True
            continue

        # run it and show the results
        try:
            result = run_solution(inputs)
            print(f"Output: {result}")
        except Exception as inst:
            print(f"Exception: {inst}")

    if inputs_error:
        print(f"Expected inputs arguments like {inputs_example}")


# some helper functions to allow for type checking of caller


def as_str(inputs: object, key: str) -> str:
    """
    Extract an attribute as a str.
    """
    return cast(str, cast(dict, inputs).get(key))


def as_int(inputs: object, key: str) -> int:
    """
    Extract an attribute as an int.
    """
    return cast(int, cast(dict, inputs).get(key))


def as_str_list(inputs: object, key: str) -> list[str]:
    """
    Extract an attribute as a list of str.
    """
    return cast(list[str], cast(dict, inputs).get(key))


def as_int_list(inputs: object, key: str) -> list[int]:
    """
    Extract an attribute as a list of int.
    """
    return cast(list[int], cast(dict, inputs).get(key))

def as_list_list(inputs: object, key: str) -> list[list[Any]]:
    """
    Extract an attribute as a list of list of any.
    """
    return cast(list[list[Any]], cast(dict, inputs).get(key))

def dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=True, separators=(',',':'), sort_keys=True)
