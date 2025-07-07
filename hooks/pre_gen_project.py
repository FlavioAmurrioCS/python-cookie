import re
import sys


MODULE_REGEX = re.compile(r"^[_a-zA-Z][_a-zA-Z0-9]+$")

module_name = "{{ cookiecutter.module_name }}"

if not MODULE_REGEX.match(module_name):
    print("ERROR: %s is not a valid Python module name!" % module_name)

    # exits with status 1 to indicate failure
    sys.exit(1)
