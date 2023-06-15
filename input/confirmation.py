def request_confirmation(question):
    while True:
        user_input = input(f"{question}\nPlease enter 'yes' or 'no': ")
        if user_input.lower() in ["yes", "y"]:
            return True
        elif user_input.lower() in ["no", "n"]:
            return False
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")
