def request_confirmation(question):
    """Requests the user to input either 'yes' or 'no' through the console,
    and continues insisting until the user enters the correct value.

    Args:
        question (str): the text that will be presented to the user before asking for the input.

    Returns:
        bool: either True or False.
    """
    while True:
        user_input = input(f"{question}\nPlease enter 'yes' or 'no': ")
        if user_input.lower() in ["yes", "y"]:
            return True
        elif user_input.lower() in ["no", "n"]:
            return False
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")
