from .console import is_admin
import os
import sys

def reboot_to_admin() -> None | bool:
    if is_admin():
        return False
    module = sys.modules.get("__main__")
    if module:
        file = module.__file__
        if file and os.path.exists(file):
            file = os.path.abspath(file)
            if os.path.isfile(file):
                os.system(f"powershell -Command \"Start-Process wt '\\\"{sys.executable}\\\" \\\"{file}\\\"' -Verb RunAs -WorkingDirectory '{os.getcwd()}'\"")
                return True
    return None