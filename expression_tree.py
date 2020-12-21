from typing import List, Union

from parse_token import Token
from expression_tree_node import Node
from errors import ValidateError, ExpressionTreeError

NODE_NUM = 'num'
NODE_VAR = 'var'
NODE_OP = 'op'
NODE_UNARY = 'unary'

operations = ['^', '*', '/', '+', '-']
unary_op = ['@', '#']


class Stack:

    def __init__(self):
        self._stack: List[Node] = []
        self._size = 0

    def result(self) -> Node:
        return self._stack[0]

    def is_empty(self) -> bool:
        return self._size <= 0

    def push(self, val: Node) -> None:
        self.__return_to_stack(val)
        self._check_node_type()

    def pop(self) -> Node:
        if self.is_empty():
            raise ValidateError("Стак дерева пустой")
        self._size -= 1
        return self._stack.pop()

    def __return_to_stack(self, val: Node):
        self._stack.append(val)
        self._size += 1

    def _check_node_type(self):
        token_type = self._stack[-1].token_type
        if token_type in [NODE_VAR, NODE_NUM]:
            return
        elif token_type == NODE_UNARY:
            op = self.pop()
            left = self.pop()

            if left.token_type == NODE_UNARY and left.text != op.text:
                raise ExpressionTreeError(
                        f"Различные унарные операторы",
                        op)
            op.aleft = left
            self.__return_to_stack(op)
        elif token_type == NODE_OP:
            op = self.pop()
            right = self.pop()
            left = self.pop()
            op.aleft = left
            op.aright = right
            self.__return_to_stack(op)
        else:
            raise ExpressionTreeError("Неопознанный токен", self._stack[-1])


class ExpressionTree:

    def __init__(self, rpn: List[Token]):
        self._rpn = rpn
        self._tree = None
        self._stack = Stack()

    def evaluate(self):
        tree = self.traversal(self._tree)
        res = []
        self._restore_infix(tree, res)
        return res

    def _restore_infix(self, tree: Node, res: List[Node]):
        res.append(tree)
        left = tree.aleft
        right = tree.aright
        tree.aleft = None
        tree.aright = None
        if left:
            self._restore_infix(left, res)
        if right:
            self._restore_infix(right, res)

    def traversal(self, node: Node):
        left = 0
        right = 0
        if node.aleft:
            left = self.traversal(node.aleft)
        if node.aright:
            right = self.traversal(node.aright)
        if node.token_type == NODE_VAR:
            return node
        elif node.token_type == NODE_NUM:
            node.mult = float(node.text)
            node.power = 0
            node.update_node('x', 'var')
            return node
        elif node.token_type == NODE_OP:
            res = Operations().evaluate(node, left, right)
            return res
        elif node.token_type == NODE_UNARY:
            res = self._evaluate_unary(node, left)
            return res
        return 0

    @staticmethod
    def _evaluate_unary(node: Node, left: Node) \
            -> Node:

        if left.token_type == NODE_VAR:
            if node.text == '@':
                left.mult = -left.mult
        else:
            if node.text == '@':
                data = -1 * float(left.text)
            else:
                data = float(left.text)
            left.update_node(data)
        return left

    def create(self):
        for token in self._rpn:
            self._add_token(token)
        self._tree = self._stack.result()

    def _add_token(self, token: Token) -> None:
        if token.text in operations:
            token = Node(token, NODE_OP)
        elif token.text in unary_op:
            token = Node(token, NODE_UNARY)
        elif token.text in ['x', 'X']:
            token = Node(token, NODE_VAR)
        elif token.isdigit():
            token = Node(token, NODE_NUM)
        else:
            raise ValidateError("Undefined token", token)
        self._stack.push(token)


class Operations:

    def evaluate(self, op: Node, left: Node, right: Node) -> Node:
        if op.text == '*':
            return self._multiplication(left, right)
        elif op.text == '/':
            return self._division(left, right)
        elif op.text == '+':
            return self._addition(left, right)
        elif op.text == '-':
            return self._subtraction(left, right)
        elif op.text == '^':
            return self._power(left, right)
        else:
            raise ExpressionTreeError(f"Что ты мне подсунул? Что это: "
                                      f"'{op.text}'", op)

    def _multiplication(self, left: Node, right: Node) -> Node:

        if right.aleft and (left.power or left.aleft):
            raise ExpressionTreeError(
                "Сценарий вида (a1 * X + b1) * (a2 * X ^n + x ^ n-1) "
                "ожидается в следующем проекте", right)
        if right.power > left.power:
            left, right = right, left

        left.mult *= right.mult
        left.power += right.power
        tmp = left.aleft
        while tmp:
            tmp.mult *= right.mult
            tmp.power += right.power
            tmp = tmp.aleft
        return left

    def _division(self, left: Node, right: Node) -> Node:

        if left.num_coef or right.num_coef or right.aleft:
            raise ExpressionTreeError("Сценарий группы (a1 * X + b1) "
                                      "/ (a2 * X + b2) запрещен",
                                      right)

        left.mult /= right.mult
        left.power -= right.power
        tmp = left.aleft
        while tmp:
            tmp.mult /= right.mult
            tmp.power -= right.power
            tmp = tmp.aleft
        return left

    def _subtraction(self, left: Node, right: Node, sign=True) -> Node:

        if sign:
            right.mult = -right.mult
        if left.power < right.power:
            left, right = right, left

        if left.power != right.power:
            left.num_coef -= right.num_coef
            right.num_coef = 0

            if left.aleft and left.aleft.power >= right.power:
                self._subtraction(left.aleft, right, sign=False)
                return left

            if left.aleft and left.aleft.power < right.power:
                aleft = left.aleft
                left.aleft = right
                self._subtraction(right, aleft)
                return left

            if not left.aleft:
                left.aleft = right
                return left

            if right.aleft:
                if left.aleft:
                    self._subtraction(left.aleft, right.aleft)
                else:
                    left.aleft = right.aleft
                    right.aleft = None

            return left

        left.num_coef -= right.num_coef
        left_mult = left.mult + right.mult
        left.mult = left_mult

        if right.aleft:
            if left.aleft:
                self._subtraction(left.aleft, right.aleft)
            else:
                left.aleft = right.aleft
                right.aleft = None
        return left

    def _addition(self, left: Node, right: Node) -> Node:
        if left.power < right.power:
            left, right = right, left

        if left.power != right.power:
            left.num_coef += right.num_coef
            right.num_coef = 0
            if left.aleft and left.aleft.power >= right.power:
                self._addition(left.aleft, right)
                return left

            if left.aleft and left.aleft.power < right.power:
                aleft = left.aleft
                left.aleft = right
                self._addition(right, aleft)
                return left

            if not left.aleft:
                left.aleft = right
                return left

            if right.aleft:
                if left.aleft:
                    self._addition(left.aleft, right.aleft)
                else:
                    left.aleft = right.aleft
                    right.aleft = None
            return left

        left.num_coef += right.num_coef
        left_mult = left.mult + right.mult
        left.mult = left_mult

        if right.aleft:
            if left.aleft:
                self._addition(left.aleft, right.aleft)
            else:
                left.aleft = right.aleft
                right.aleft = None
        return left

    def _power(self, left: Node, right: Node) -> Node:
        if right.token_type == NODE_VAR and right.power:
            raise ExpressionTreeError("Степень икса? Ушел решать.", right)

        right_val = float(right.mult)
        if not right_val.is_integer():
            raise ExpressionTreeError("Запрещена дробная степень.", right)

        if not left.power:
            left.mult **= right_val
            return left

        if left.num_coef != 0 or left.aleft:
            raise ExpressionTreeError("Степень для уравнения вида (ax + b) "
                                      "запрещена.", right)

        left.power *= right_val
        left.mult **= right_val

        return left
