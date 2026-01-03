import sys
import traceback
from colorama import Fore, Style, init
# from .ai import get_ai_explanation

init(autoreset=True)

ERROR_HINTS = {
    "NameError": "You probably used a variable before defining it.",
    "TypeError": "You may be using wrong data types together.",
    "IndexError": "You tried to access a list index that doesn't exist.",
    "KeyError": "You tried to access a missing dictionary key.",
    "ValueError": "You passed an invalid value to a function.",
}

def _exception_handler(exc_type, exc_value, tb):
    tb_info = traceback.extract_tb(tb)
    last_call = tb_info[-1]
    error_name = exc_type.__name__
    hint = ERROR_HINTS.get(error_name, "Check your code logic.")
    # ai_expl = get_ai_explanation(error_name, last_call.line, exc_value)

    print(
        f"\n❌ {Fore.MAGENTA}(line {last_call.lineno}) {Fore.RED}{error_name} in {last_call.filename}"
    )

    print(f"{Fore.YELLOW}💡 Hint: {hint}")

    print(f"{Fore.CYAN}📝 Message: {exc_value}\n")

    # if ai_expl:
    #     print(f"\n{Fore.CYAN}🧠 AI Explanation:{Style.RESET_ALL}")
    #     print(f"{Fore.CYAN}{ai_expl}{Style.RESET_ALL}\n")


def enable():
    sys.excepthook = _exception_handler