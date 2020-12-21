from typing import Optional

from parse_token import Token
from expression_tree_node import Node


class ValidateError(Exception):

    def __init__(self, message: str, token: Optional[Token] = None):
        self._message = message
        self._token = token
        self.__repr__()

    def __repr__(self):
        msg = ""
        if isinstance(self._token, Token):
            msg = " " * self._token.position + "^ "
        print(msg + self._message)


class ExpressionTreeError(Exception):

    def __init__(self, message: str, node: Node):
        self._message = message
        self._node = node
        self.__repr__()

    def __repr__(self):
        msg = " " * self._node.position + "^ "
        print(msg + self._message)
