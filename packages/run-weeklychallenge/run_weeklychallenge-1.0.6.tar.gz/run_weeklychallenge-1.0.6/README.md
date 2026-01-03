Facilitates running a solution to [the Weekly Challenge](https://theweeklychallenge.org) using one or more sets of inputs provided as JSON command line arguments.

Example usage running a "solution" to sum integers:

    def sum_of_ints(ints: list[int]) -> int:
        sum: int = 0
        i: int
        for i in ints:
            sum += i
        return sum
    
    if __name__ == '__main__':
        import run_weeklychallenge as run
        run.run_weekly_challenge(
            run_solution = lambda inputs: str(sum_of_ints(run.as_int_list(inputs, 'ints'))),
            inputs_example = '{"ints":[1,2,3]}',
            inputs_schema_json = '''{
                "type": "object",
                "properties": {
                    "ints": {
                        "type": "array",
                        "items": { "type": "integer" }
                    }
                },
                "required": ["ints"],
                "additionalProperties": false
            }'''
        )

Example output:

    $ python example.py '{"ints":[1,2,3]}' '{"ints":[]}'
    Inputs: {"ints":[1,2,3]}
    Output: 6
    Inputs: {"ints":[]}
    Output: 0

You must provide an example JSON inputs string (used in error messages), a JSON schema for inputs, and a shim function to run the solution given the decoded JSON inputs and reformat the output if desired.  To support type checking, helper functions are provided to extract properties of the JSON input as various types to pass to the solution in the shim function.
