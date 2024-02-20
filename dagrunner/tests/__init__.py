# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'pp_systems_framework' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import difflib
import os

_RESULT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def expand_results_path(path):
    if "results" not in path:
        path = os.path.join(os.path.dirname(__file__), "results", path)
    return os.path.realpath(os.path.expandvars(os.path.expanduser(path)))


def assert_text_file_equal(result_text_file, ref_text_file, ignore_patterns=None):
    """
    Compare text files.

    Where a reference file doesn't exist, it will be created and an exception
    will be raised, telling the user that they must commit this file.
    Running the test again will cause the test to succeed.
    """

    def filter_patterns(cont):
        if not ignore_patterns:
            return cont
        for pattern in ignore_patterns:
            cont = filter(lambda line: pattern not in line, cont)
        return list(cont)

    assert os.path.isfile(result_text_file), "No input file found"
    with open(result_text_file, "r") as res_fh:
        res_cont = res_fh.readlines()
    ref_text_file = expand_results_path(ref_text_file)

    if not os.path.exists(ref_text_file):
        with open(ref_text_file, "w") as ref_fh:
            ref_fh.writelines(res_cont)
        msg = (
            f"Reference '{ref_text_file}' did not exist.  Reference file "
            "generated.  Commit this new file to include it."
        )
        raise RuntimeError(msg)
    else:
        with open(ref_text_file, "r") as ref_fh:
            ref_cont = ref_fh.readlines()
            ref_cont = filter_patterns(ref_cont)
            res_cont = filter_patterns(res_cont)
            diff = list(difflib.context_diff(res_cont, ref_cont))

        if diff:
            diff = "".join(diff)
            msg = "files {} and {} differ:\n\n{}"
            raise RuntimeError(msg.format(result_text_file, ref_text_file, diff))
