from typing import List

from expression_tree_node import Node
from parse_token import Token
import errors


class SolveEquation:

    def __init__(self, tree: List[Node], quiet: bool):
        self._terms = tree
        self.size = len(tree)
        self._quiet = quiet

    def solve(self) -> str:
        self._terms = Checker(self._terms).check_all()
        homer_simpson: float = 0
        for val in self._terms:
            if val.power > homer_simpson:
                homer_simpson = val.power
        if homer_simpson == 1:
            return self._first_degree()
        elif homer_simpson == 2:
            return self._second_degree()

    def _first_degree(self) -> str:
        if not self._quiet:
            print("Уравнение первой степени. Возможно только одно решение.")
        if self.size == 1:
            return "Результат:\n\tX = 0"
        left = self._terms[0]
        right = self._terms[1]
        res = -right.mult / left.mult
        if not res.is_integer():
            res = f"{round(res, 2):.2f}"
        return f"Результат:\n\tX = {res}"

    def _second_degree(self) -> str:

        a = Node(Token('x', 0), 'var')
        a.power = 1
        a.mult = 0
        b = Node(Token('x', 0), 'var')
        b.power = 1
        b.mult = 0
        c = Node(Token('x', 0), 'var')
        c.power = 0
        c.mult = 0
        for val in self._terms:
            if val.power == 2:
                a = val
            elif val.power == 1:
                b = val
            else:
                c = val
        disc = self.discriminant(a, b, c)
        if disc < 0:
            print("Значение дискриминанта меньше 0. Действительных "
                  "решений нет.")
            disc = -disc
            res1 = f"{-b.mult / (2 * a.mult):.2} - " \
                   f"{round(sqrt(disc) / (2 * a.mult), 2):.2}i"
            res2 = f"{-b.mult / (2 * a.mult):.2} + " \
                   f"{round(sqrt(disc) / (2 * a.mult), 2):.2}i"
            return f"Результат:\n\tX1 = {res1}, X2 = {res2}"
        if disc == 0:
            if not self._quiet:
                print("Дискриминант равен нулю. Доступно одно решение.")
            res = -b.mult / (2 * a.mult)
            if not round(res, 2).is_integer():
                res = f"{round(res, 2):.2f}"
            else:
                res = int(res)
            return f"Результат:\n\tX = {res}"
        else:
            if not self._quiet:
                print("Дискриминант больше нуля. Доступно два решения.")
            res1 = (-b.mult - sqrt(disc)) / (2 * a.mult)
            res2 = (-b.mult + sqrt(disc)) / (2 * a.mult)
            if not round(res1, 2).is_integer():
                res1 = f"{round(res1, 2):.2f}"
            else:
                res1 = int(res1)
            if not round(res2, 2).is_integer():
                res2 = f"{round(res2, 2):.2f}"
            else:
                res2 = int(res2)
            return f"Результат:\n\tX1 = {res1}, X2 = {res2}"

    @staticmethod
    def discriminant(a: Node, b: Node, c: Node) -> float:

        val = b.mult**2 - 4 * a.mult * c.mult

        return val


class Checker:

    def __init__(self, terms: List[Node]):
        self._terms: List[Node] = terms

    def check_all(self) -> List[Node]:
        self._check_solvability()
        self._check_power()
        return self._check_zero_mult()

    def _check_power(self):
        for elem in self._terms:
            if elem.power < 0 or elem.power > 2:
                raise errors.ValidateError("Разрешены степени от 0 до 2 "
                                           "включительно.")

    def _check_solvability(self):
        if len(self._terms) == 1:
            elem = self._terms[0]
            if elem.power == 0 and elem.mult != 0:
                raise errors.ValidateError("Уравнение вида a * X^0 = 0 "
                                           "решения не имеет.")

            if elem.mult == 0:
                raise errors.ValidateError("В уравнении вида 0 * X^n = 0 "
                                           "любое действительное значение"
                                           " X это решение.")

            if elem.power > 0:
                raise errors.ValidateError("Уравнения вида a * X^n = 0 "
                                           "имеют одно решение:\n\tX = 0.")

    def _check_zero_mult(self):
        for_remove = []
        start_size = len(self._terms)
        for i, val in enumerate(self._terms):
            if val.mult == 0:
                for_remove.append(i)
        for val in for_remove[::-1]:
            self._terms.pop(val)
        end_size = len(self._terms)
        if end_size == 0:
            raise errors.ValidateError("В уравнении вида 0 * X^n = 0 "
                                       "любое действительное значение"
                                       " X это решение.")
        if start_size > end_size:
            self._check_solvability()
        return self._terms


def sqrt(val):
    x = 1
    while True:
        nx = (x + val / x) / 2
        if abs(x - nx) < 1e-10:
            break
        x = nx
    return x
