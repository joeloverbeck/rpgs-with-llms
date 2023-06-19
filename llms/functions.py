from typing import List


def append_function(
    functions: List[dict],
    function_name: str,
    function_description: str,
    parameters: dict,
):
    """Appends a function with an arbitrary number of parameters to the expected structure by GPT.

    Args:
        functions (List[dict]): a list of functions, that may be empty.
        function_name (str): the name of the function to append.
        function_description (str): the description of the function to append.
        parameters (dict): the parameters that the function should have.
    """
    function_dict = {
        "name": function_name,
        "description": function_description,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }

    for param in parameters:
        function_dict["parameters"]["properties"][param["name"]] = {
            "type": param["type"],
            "description": param["description"],
        }
        function_dict["parameters"]["required"].append(param["name"])

    functions.append(function_dict)
