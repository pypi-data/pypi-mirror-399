#!/usr/bin/env python
#     Copyright 2025, QutaYba, nasr2python@gmail.com find license text at end of file


""" Tool to compare reference counting behavior of CPython and OxN.

"""

import os
import sys
from optparse import OptionParser

from JACK.PythonVersions import isDebugPython
from JACK.tools.testing.Common import checkReferenceCount, getTempDir
from JACK.Tracing import my_print
from JACK.utils.Execution import check_call
from JACK.utils.Importing import importFileAsModule


def main():
    parser = OptionParser()

    parser.add_option(
        "--checked-module",
        action="store",
        dest="checked_module",
        default=None,
        help="""\
Module with main() function to be checked for reference count stability.""",
    )

    parser.add_option(
        "--explain",
        action="store_true",
        dest="explain",
        default=False,
        help="""\
Try to explain the differences by comparing object counts.""",
    )

    options, positional_args = parser.parse_args()

    if positional_args and options.checked_module is None:
        options.checked_module = positional_args.pop()

    if options.checked_module is None:
        sys.exit("\nNeed to provide checked module filename.")

    if positional_args and options.checked_module:
        parser.print_help()

        sys.exit("\nError, no positional argument allowed.")

    # First with pure Python.
    checked_module = importFileAsModule(options.checked_module)
    my_print("Using %s" % checked_module.main, style="blue")
    checkReferenceCount(checked_module.main, explain=options.explain)

    temp_dir = getTempDir()
    command = [
        sys.executable,
        "-m",
        "JACK",
        "--mode=module",
        options.checked_module,
        "--output-dir=%s" % temp_dir,
    ]

    if isDebugPython():
        command.append("--python-debug")

    check_call(command)

    module_name = os.path.basename(options.checked_module).split(".")[0]

    sys.path.insert(0, temp_dir)
    checked_module = __import__(module_name)

    my_print("Using %s" % checked_module.main, style="blue")
    checkReferenceCount(checked_module.main)


if __name__ == "__main__":
    JACK_package_dir = os.path.normpath(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    )

    # Unchanged, running from checkout, use the parent directory, the JACK
    # package ought be there.
    sys.path.insert(0, JACK_package_dir)

    main()


