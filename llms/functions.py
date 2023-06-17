def append_single_parameter_function(
    functions: list,
    function_name,
    function_description,
    parameter_name,
    parameter_type,
    parameter_description,
):
    functions.append(
        {
            "name": function_name,
            "description": function_description,
            "parameters": {
                "type": "object",
                "properties": {
                    parameter_name: {
                        "type": parameter_type,
                        "description": parameter_description,
                    }
                },
                "required": [parameter_name],
            },
        }
    )
