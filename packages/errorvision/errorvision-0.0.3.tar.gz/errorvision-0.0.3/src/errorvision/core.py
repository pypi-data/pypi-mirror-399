import sys
import traceback
from colorama import Fore, Style, init

init(autoreset=True)

ERROR_HINTS = {
    "NameError": "You probably used a variable before defining it.",
    "TypeError": "You may be using wrong data types together.",
    "IndexError": "You tried to access a list index that doesn't exist.",
    "KeyError": "You tried to access a missing dictionary key.",
    "ValueError": "You passed an invalid value to a function.",
    "AttributeError": "You tried to access an attribute that doesn't exist.",
    "ZeroDivisionError": "You cannot divide a number by zero.",
    "ImportError": "Python couldn't find the module you tried to import.",
    "ModuleNotFoundError": "The module you tried to import doesn't exist.",
    "FileNotFoundError": "The file you tried to access does not exist.",
    "PermissionError": "You don't have permission to perform this operation.",
    "RuntimeError": "A generic runtime error occurred.",
    "OverflowError": "A numerical calculation exceeded the limits.",
    "RecursionError": "Your code recursed too deeply.",
    "StopIteration": "Iteration has no more items.",
    "MemoryError": "The system ran out of memory.",
    "NotImplementedError": "A required method has not been implemented yet.",
    "EOFError": "End-of-file reached while reading input.",
    "FloatingPointError": "An invalid floating point operation occurred.",
    "ArithmeticError": "An error occurred in arithmetic operation.",
    "BufferError": "An error related to buffer occurred.",
    "ConnectionError": "A network connection error occurred.",
    "LookupError": "A lookup operation failed.",
    "EnvironmentError": "An error occurred related to the system environment.",
}

def _exception_handler(exc_type, exc_value, tb):
   
    try:
        error_name = exc_type.__name__ if exc_type else "UnknownError"
        hint = ERROR_HINTS.get(error_name, "Check your code logic carefully.")
        message = exc_value if exc_value else "No additional message."

        tb_info = traceback.extract_tb(tb) if tb else []

        print(f"\n{Fore.RED}❌ Exception: {error_name}")
        print(f"{Fore.YELLOW}💡 Hint: {hint}")
        print(f"{Fore.CYAN}📝 Message: {message}\n")

        if tb_info:
            print(f"{Fore.MAGENTA}--- Full Traceback ---{Style.RESET_ALL}")
            for i, frame in enumerate(tb_info, start=1):
                filename = frame.filename
                lineno = frame.lineno
                func = frame.name
                line = frame.line.strip() if frame.line else ""
                print(f"{Fore.BLUE}Frame {i}: {func} in {filename} (line {lineno})")
                if line:
                    print(f"   {Fore.WHITE}→ {line}")
        else:
            print(f"{Fore.MAGENTA}No traceback available.{Style.RESET_ALL}")

      
        # try:
        #     ai_expl = get_ai_explanation(error_name, tb_info[-1].line if tb_info else "", exc_value)
        #     if ai_expl:
        #         print(f"\n{Fore.CYAN}🧠 AI Explanation:{Style.RESET_ALL}\n{Fore.CYAN}{ai_expl}{Style.RESET_ALL}")
        # except Exception:
        #     pass

        print(f"{Fore.MAGENTA}{'-'*40}{Style.RESET_ALL}\n")

    except Exception as internal_error:
        print(f"{Fore.RED}⚠️ Internal error in exception handler: {internal_error}")
        print("Original exception:")
        traceback.print_exception(exc_type, exc_value, tb)

def enable():
    sys.excepthook = _exception_handler
