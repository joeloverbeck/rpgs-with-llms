from colorama import Fore, init, Style

init()

COLOR_MAP = {
    "red": Fore.RED,
    "green": Fore.GREEN,
    "yellow": Fore.YELLOW,
    "blue": Fore.BLUE,
    "light_blue": Fore.LIGHTBLUE_EX,
    "light_cyan": Fore.LIGHTCYAN_EX,
    "light_green": Fore.LIGHTGREEN_EX,
    "light_magenta": Fore.LIGHTMAGENTA_EX,
    "light_red": Fore.LIGHTRED_EX,
    "light_yellow": Fore.LIGHTYELLOW_EX,
}


def output_colored_message(color: str, message: str):
    if not isinstance(color, str):
        raise ValueError(
            f"The function {output_colored_message.__name__} expected color to be a string, but it was: {color}"
        )

    fore_color = COLOR_MAP.get(color, Fore.RESET)

    print(f"{fore_color}{message}{Style.RESET_ALL}")
