from uc_ast import AST
from uc_lexer import Lexer


class UCParser:
    def __init__(self):
        self.errors = 0
        self.warnings = 0

    def parse(self, code, filename='', debug=0):
        if debug:
            print("Code: {0}".format(code))
            print("Filename: {0}".format(filename))

        print("I'm on parser! :D")

        Lexer.lexer(self)

        return AST

    def show(self, buf=None, showcoord=True):
        print("I'm on show")
