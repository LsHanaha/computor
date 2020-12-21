from typing import Optional, Union
from parse_token import Token

import errors


class Node:

    __slots__ = ['text', 'position', 'aleft', 'aright', 'token_type', 'power',
                 'mult', 'num_coef']

    def __init__(self, val: Token, type_: str):
        self.text: Union[float, str] = val.text
        self.position = val.position
        self.token_type = None
        self.__define_type(type_)
        self.aleft: Optional[Node] = None
        self.aright: Optional[Node] = None

        self.power: float = 1.0
        self.mult: float = 1.0
        self.num_coef: float = 0.0

    def __repr__(self):
        if self.mult == 1.0:
            text_ = ""
        elif self.mult.is_integer():
            text_ = f"{int(self.mult)}"
        else:
            text_ = f"{round(self.mult, 2):.2}"
        return f"{text_}" \
               f"{self.text.upper()}" \
               f"^{int(self.power)}" \
               f"{self.num_coef if self.num_coef else ''}"

    def __define_type(self, type_: str):

        if not self.token_type:
            self.token_type = type_
        elif type_ == 'var' or self.token_type == 'var':
            self.token_type = 'var'
        elif type_ in ['op', 'unary'] and self.token_type in ['op', 'unary']:
            raise errors.ExpressionTreeError(
                "Последовательно несколько операций", self)
        else:
            self.token_type = 'num'
            self.text = float(self.text)

    def update_node(self, text: Union[str, float],
                    type_: Optional[str] = None) \
            -> None:
        self.text = text
        if type:
            self.__define_type(type_)
