import os
from subprocess import Popen, PIPE
import evaluator
import shutil


def run_and_evaluate(test_name):
    __run(test_name)
    expected_parse_tree, parse_tree = __read_expected_and_actual(
        test_name, "parse_tree")
    expected_errors, errors = __read_expected_and_actual(
        test_name, "syntax_errors")

    score1 = evaluator.calc_parse_tree_score(expected_parse_tree, parse_tree)
    score2 = evaluator.calc_syntax_errors_score(expected_errors, errors)
    print(test_name, "-->", score1, score2)
    return score1, score2


def __run(test_name):
    shutil.copyfile(os.path.join('test/testcases',
                    test_name, 'input.txt'), './input.txt')

    for file_name in ["../parse_tree.txt", "../syntax_errors.txt"]:
        if os.path.exists(file_name):
            os.remove(file_name)
    compiler_process = Popen(
        ['/usr/bin/python3.10', '../compiler.py'], stdout=PIPE, stderr=PIPE)
    out, err = compiler_process.communicate()
    print(out)
    print(err)


def __read_expected_and_actual(test_name: str, filename: str):
    filename = f"{filename}.txt"

    def read(path):
        with open(file=path, mode="r") as f:
            return f.read()

    expected = read(os.path.join('/home/black-titan0/Documents/University/Compiler Design/test/test/testcases',
                    test_name, filename))
    actual = read('/home/black-titan0/Documents/University/Compiler Design/' + filename)

    return expected, actual
