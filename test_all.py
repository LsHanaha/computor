import pytest
import rpn
from parse_token import Token
from computor import evaluate


class TestRPN:

    stack = rpn.Stack()

    @pytest.mark.parametrize("op, size",
                             [('*', 1), ('/', 2), ('*', 3)])
    def test_stack_push(self, op, size):
        self.stack.push(Token(op, 0))
        assert self.stack.size == size

    @pytest.mark.parametrize("op, res", [
        ('*', True),
        ('/', True),
        ('-', True),
        ('^', False),
    ])
    def test_precedence(self, op, res):
        res_ = self.stack.check_precedence(Token(op, 0))
        assert res == res_

    @pytest.mark.parametrize("op, size",
                             [('*', 2), ('/', 1), ('*', 0)])
    def test_stack_pop(self, op, size):
        assert self.stack.pop().text == op
        assert self.stack.size == size

    @pytest.mark.parametrize(
        "tokens, res",
        [(['(', '4', 'x', '^', '0', ' ', '-', ' ', '1', ')', '*', '(', '3', 'x', ' ', '+', ' ', '7', ')', ' ', '=', ' ', '9'], "4 x 0 ^ * 1 - 3 x * 7 + * 9 -"),
         (['9', 'x', ' ', '=', ' ', '1'], "9 x * 1 -"),
         (['(', 'X', '^', '2', '^', '4', ' ', '+', ' ', 'x', '^', '1', ' ', '+', ' ', '9', ')', ' ', '/', ' ', '(', '6', 'x', '^', '1', ')'], "X 2 ^ 4 ^ x 1 ^ + 9 + 6 x 1 ^ * /"),
         (['x', '^', '2', '/', 'x'], 'x 2 ^ x /'),
         (['x', '/', 'x'], 'x x /'),
         (['5', ' ', 'x', ' ', '^', ' ', '0', ' ', '=', ' ', '5', ' ', 'x', ' ', '^', ' ', '0'], '5 x 0 ^ * 5 x 0 ^ * -'),
         (['5', ' ', '*', ' ', 'x', '^', '0', ' ', '=', ' ', '4', ' ', '*', ' ', 'x', ' ', '^', ' ', '0', ' ', '+', ' ', '7', ' ', '*', ' ', 'x', ' ', '^', ' ', '1'], '5 x 0 ^ * 4 x 0 ^ * 7 x 1 ^ * + -'),
         (['5', '*', 'x', '^', '0', ' ', '+', ' ', '13', '*', 'x', '^', '1', ' ', '+', ' ', '3', '*', 'x', '^', '2', ' ', '=', ' ', '1', '*', 'x', '^', '0', ' ', '+', ' ', '1', '*', 'x', '^', '1'], '5 x 0 ^ * 13 x 1 ^ * + 3 x 2 ^ * + 1 x 0 ^ * 1 x 1 ^ * + -')])
    def test_rpn(self, tokens, res):
        array = (Token(val, 0) for val in tokens)
        res_ = rpn.ShuntingYard(array).convert()
        assert ' '.join([val.text for val in res_]) == res


class TestSystem:

    @pytest.mark.parametrize("equation,result", [
        ("5 * x^0 - 4 * x ^ 0 + 7 * x ^ 1", "Результат:\n\tX = -0.14"),
        ("5*x^0 + 13*x^1 + 3*x^2 = 1*x^0 + 1*x^1", "Результат:\n\tX1 = -3.63, X2 = -0.37"),
        ("6*x^0 + 11*x^1 + 5 * x^2 = 1 * x^0 + 1 * X ^ 1", "Результат:\n\tX = -1"),
        ("11*x^1 - 5 * x^1 = 1 * x^0 + 1 * X ^ 1", "Результат:\n\tX = -0.20"),
        ("(11*x^4 + 5 * x^3) / x^2 = -6 * x^-1 * x - 1 * X ^ 1", "Результат:\n\tX1 = -1.06, X2 = 0.51"),
        ("x +2x^2 + 1 = 0", "Результат:\n\tX1 = -0.25 - 0.66i, X2 = -0.25 + 0.66i"),
        ("-x^2 + x = 0", "Результат:\n\tX1 = -1, X2 = 0"),
        ("xx = 5^-3", "Результат:\n\tX1 = -0.09, X2 = 0.09"),
        ("(x^(2 +  5 - 4) 4) /x/x = 5 x ^ 0", "Результат:\n\tX = 1.25")
    ])
    def test_solvability(self, equation, result):
        res = evaluate(equation)
        assert res == result

