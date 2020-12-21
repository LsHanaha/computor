
class Token:

    __slots__ = ['text', 'position']

    def __init__(self, text: str, position: int):
        self.text = text
        self.position = position

    def __repr__(self):
        return str(self.text)

    def __str__(self):
        return str(self.text)

    def isdigit(self) -> bool:
        try:
            float(self.text)
            return True
        except ValueError:
            return False
