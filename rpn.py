from typing import Generator, List
import collections

from parse_token import Token
from errors import ValidateError

RIGHT, LEFT = range(2)


Op = collections.namedtuple('Op',
                            ['precedence', 'associativity'])

OPS = {
    '@': Op(precedence=5, associativity=RIGHT),
    '#': Op(precedence=5, associativity=RIGHT),
    '^': Op(precedence=4, associativity=RIGHT),
    '*': Op(precedence=3, associativity=LEFT),
    '/': Op(precedence=3, associativity=LEFT),
    '+': Op(precedence=2, associativity=LEFT),
    '-': Op(precedence=2, associativity=LEFT)}


class Stack:

    def __init__(self):
        self.stack: List[Token] = []
        self.size = 0

    def push(self, val: Token):
        self.stack.append(val)
        self.size += 1

    def pop(self) -> Token:
        self.size -= 1
        return self.stack.pop()

    def is_empty(self) -> bool:
        return self.size <= 0

    def check_precedence(self, op: Token):
        if self.size == 0 or self.stack[-1].text == '(':
            return False

        if OPS[self.stack[-1].text].precedence == OPS[op.text].precedence and \
                OPS[op.text].precedence == 5:
            return False
        a = OPS[self.stack[-1].text].precedence >= OPS[op.text].precedence
        b = (OPS[self.stack[-1].text].precedence == OPS[op.text].precedence) \
            and OPS[op.text].associativity == LEFT
        return a or b

    def is_bracket(self) -> bool:
        return self.stack[-1].text == '('


class ShuntingYard:

    def __init__(self, tokens: Generator):
        self._res: List[Token] = []
        self._stack = Stack()
        self._tokens: Generator = tokens
        self._moved_left = False
        self._possible_unary = True
        self._position = 0
        self._previous_token: str = ""

    def convert(self) -> List[Token]:
        for val in self._tokens:
            self.select_action(val)
            if not val.text.isspace():
                self._previous_token = val.text
        self._handle_eos()
        self._remove_unary_pluses()
        self._remove_equality()
        self._validate_rpn()
        return self._res

    def select_action(self, val: Token) \
            -> None:
        if val.position >= self._position:
            self._position = val.position
        if val.text in OPS:
            self._handle_operator(val)
        elif val.text.isspace():
            pass
        elif val.isdigit():
            if self._previous_token == ')':
                self.select_action(Token('*', self._position))
            self._res.append(val)
            self._possible_unary = False
        elif val.text in ['x', 'X']:
            if self.__previous_is_digit() or \
                    self._previous_token in ['x', 'X'] or \
                    self._previous_token == ')':
                self.select_action(Token('*', self._position))
            self._res.append(val)
            self._possible_unary = False
        elif val.text == '(':
            self.__increase_stack(val)
            self._possible_unary = True
        elif val.text == ')':
            if self._previous_token in OPS:
                raise ValidateError("Перед закрывающими скобками стоит "
                                    "знак операции", val)
            self._handle_parentheses(val)
            self._possible_unary = False
        elif val.text == '=':
            if self._moved_left:
                raise ValidateError("Not more than one quality sign allowed",
                                    val)
            self._handle_eos()
            self._move_to_left()
            self._possible_unary = True
        else:
            raise ValidateError(f"Unknown token '{val.text}'", val)

    def _handle_operator(self, op: Token) \
            -> None:
        if self._possible_unary and op.text in ['-', '+']:
            op.text = '@' if op.text == '-' else '#'
        while not self._stack.is_empty():
            if not self._stack.check_precedence(op):
                break
            self._stack_to_res()
        self.__increase_stack(op)
        self._possible_unary = True

    def _handle_parentheses(self, val: Token) \
            -> None:
        while not self._stack.is_empty():
            if self._stack.is_bracket():
                self._stack.pop()
                return
            self._stack_to_res()
        raise ValidateError("Brackets not balanced", val)

    def _handle_eos(self) \
            -> None:
        if self._moved_left:
            self._handle_parentheses(Token(')', 0))
        while not self._stack.is_empty():
            val = self._stack_to_res()
            if val.text == '(':
                raise ValidateError("Brackets not balanced", val)

    def __increase_stack(self, val: Token) \
            -> None:
        self._stack.push(val)

    def _stack_to_res(self) \
            -> Token:
        val = self._stack.pop()
        self._res.append(val)
        return val

    def __previous_is_digit(self):
        try:
            float(self._previous_token)
            return True
        except ValueError:
            return False

    def _move_to_left(self) -> None:
        if not len(self._res):
            self.select_action(Token('0', 0))
        self._moved_left = True
        self._possible_unary = False
        self.select_action(Token('-', self._position))
        self.select_action(Token('(', self._position + 1))

    def _remove_unary_pluses(self) -> None:
        plus = False
        size = len(self._res)
        for i, elem in enumerate(self._res[::-1]):
            if elem.text == '#':
                if plus:
                    self._res.pop(size - i)
                plus = True
            else:
                plus = False

    def _remove_equality(self):
        size = len(self._res)
        for i, val in enumerate(self._res[::-1]):
            if val.text == '=':
                self._res.pop(size - i)

    def _validate_rpn(self):
        counter = 0
        for elem in self._res:
            if elem.isdigit() or elem.text in ['x', 'X']:
                counter += 1
            elif elem.text in OPS and elem.text not in ['@', '#']:
                counter -= 2
                if counter < 0:
                    raise ValidateError("Чего-то тут не хватает", elem)
                counter += 1
            elif elem.text in ['@', '#']:
                counter -= 1
                if counter < 0:
                    raise ValidateError("Чего-то тут не хватает", elem)
                counter += 1
        if counter != 1:
            raise ValidateError("Уравнение не корректно!")
