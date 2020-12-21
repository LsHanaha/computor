
from typing import Generator
import argparse
import re

from parse_token import Token
from rpn import ShuntingYard
from expression_tree import ExpressionTree
from solve import SolveEquation
from errors import ValidateError, ExpressionTreeError


# 5 x ^ 0 = 5 x ^ 0
# 4 * x ^ 0 = 8 * x ^ 0
# 5 * x^0 - 4 * x ^ 0 + 7 * x ^ 1
# 5*x^0 + 13*x^1 + 3*x^2 = 1*x^0 + 1*x^1
# 6*x^0 + 11*x^1 + 5 * x^2 = 1 * x^0 + 1 * X ^ 1
# 5 * x^0 + 3 * x^1 + 3 * x^2 = 1 * x^0 + 0 * x^1
# 5 * x^3 + 3 * x^1 + 3 * x^2 = 1 * x^0 + 0 * x^1
# 0 * x ^ 10


# 23*x + 35 = 0  : -1.521739
# 5 * X^0 + 4 * X^1 - 9.3 * X^2 = 1 * X^0 :0.905239   -0.475131
# "5 + 4 * X + X^2= X^2" - ОК: -1.25
# 42 * x^0 = 42*x^0
# 4*x + 3*x^2 = 0 OK: 0, -11.333333
# 34*x = 0  OK
# 4.65*x^2 +3*x - 23.2 = 0-
# -4.65*x^2 +3*x - 23.2 = 0
# 4.65*x^2 +3*x - 23.2 = 0 OK: -2.579415 1.934255
# -4.65*x^2 +3*x - 23.2 = 0123
# 45 = 45
# 35 -35-4 = 0
# 23*x + 35 = 0
# -(4.65+35)*x^2 +3*x - 23.2 = 0123
# 35
# 35 - 45
# 34 - 94 = -
# x = 0
# x = -1
# x = -1 - 23 + 23
# 23 = x - 1 OK
# 24 - x = 0
#!!!!!!!!!!!!!!!!!!!!!!!!! 23 = 34*x^1 +45 : -0.647058
# 23 = 34*x +45
#  95 = x
#  0 = 0
# x -234 = 45* x^1: -5.318181
# X + X + X + X + X = 3545 * X - 2 : 0.000565
# 0*x + 34*0 = 0
# 0*x + 34 = 0
# 0 * x = 34*0
# -56 + x^1 = 98
#  -56*x^0 + x^1 = 98
#  =56
# x - = 56.66666666666666
# X^2 = X^2 +X^2 +X^2- X^2+ X^2+ X^2- X^2+X^2+ X^2
# 4*X^0 = 8*X^0
#   "5 * X^0 = 4 * X^0 + 7 * X^1"
# "5 * X ^ 0 + 13 * X ^ 1 + 3 * X ^ 2 = 1 * X ^ 0 + 1 * X ^ 1 " : -3.632993, -0.367006
# "6 * X ^ 0 + 11 * X ^ 1 + 5 * X ^ 2 = 1 * X ^ 0 + 1 * X ^ 1"
# 5 * X ^ 0 + 3 * X ^ 1 + 3 * X ^ 2 = 1 * X ^0 + 0 * X ^5

def create_tokens(equation: str) -> Generator:

    pattern = re.compile(r"("
                         r"(?:[-+()])"
                         r"|(?:[\d.]+)"
                         r"|(?:[*/])"
                         r"|(?:[xX])"
                         r"|(?:\^)"
                         r"|(?:\s+)"
                         r"|(?:=)"
                         r")"
                         )
    position: int = 0
    while position < len(equation):
        match_obj = pattern.match(equation, position)
        if match_obj is None:
            raise ValidateError("Символ не опознан. Уравнение не валидно.",
                                Token("", position))

        text = match_obj.group(1)
        yield Token(text, match_obj.start(1))
        position = match_obj.end()


def read_input() -> argparse.Namespace:

    parser = argparse.ArgumentParser(
        description="Enter your equation as first argument, put it in double "
                    "quotes. Don't forget a '=' symbol.\nNB! Equation should "
                    "not be like '--x=x'. If it starts with dash, add a space "
                    "in it.")
    parser.add_argument('equation', type=str,
                        help='Input equation. Power in range from 0 to 2.')
    group1 = parser.add_mutually_exclusive_group()

    group1.add_argument('-v', action='store_true',
                        help="Activate verbose mode for all solutions steps."
                             "Forbidden with -q.")
    group1.add_argument('-q', '--quiet', action='store_true',
                        help="Activate quiet mode for program. "
                             "Forbidden with -v")
    args = parser.parse_args()
    return args


def evaluate(equation_src: str, verbose: bool = False, quiet: bool = False) \
        -> str:

    tokens = create_tokens(equation_src)
    rpn = ShuntingYard(tokens).convert()
    tree = ExpressionTree(rpn)
    tree.create()
    equation_simplified = tree.evaluate()
    if verbose:
        print("Обратная польская нотация:", end="\n\t")
        for elem in rpn:
            print(elem, end=' ')
        print("")
    if not quiet:
        print("Упрощенная форма:", end="\n\t")
        size = len(equation_simplified)
        for i, elem in enumerate(equation_simplified):
            print(elem, end="")
            if i + 1 < size:
                print("+" if equation_simplified[i + 1].mult >= 0 else "",
                      end="")
        print(" = 0")
    res = SolveEquation(equation_simplified, quiet).solve()
    return res


def computor():
    data = read_input()
    if not data.quiet:
        print("\nComputor v1\n")
        print("Исходное уравнение:", end="\n")
        print(data.equation, end="")

        if "=" in data.equation:
            print("")
        else:
            print(" = 0")
    try:
        res = evaluate(data.equation, data.v, data.quiet)
        print(res)
    except ValidateError:
        return
    except ExpressionTreeError:
        return


if __name__ == '__main__':
    computor()
