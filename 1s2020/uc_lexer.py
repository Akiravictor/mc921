from ply.lex import lex


class UCLexer:
    def __init__(self, error_func):
        self.error_func = error_func
        self.filename = ''
        self.last_token = None

    def build(self, **kwargs):
        print("I'm on lexer!")
        self.lexer = lex.lex(object=self, **kwargs)

    def reset_lineno(self):
        """ Resets the internal line number counter of the lexer.
        """
        self.lexer.lineno = 1

    def input(self, text):
        self.lexer.input(text)

    def token(self):
        self.last_token = self.lexer.token()
        return self.last_token

    def find_tok_column(self, token):
        """ Find the column of the token in its line.
        """
        last_cr = self.lexer.lexdata.rfind('\n', 0, token.lexpos)
        return token.lexpos - last_cr

    # Internal auxiliary methods
    def _error(self, msg, token):
        location = self._make_tok_location(token)
        self.error_func(msg, location[0], location[1])
        self.lexer.skip(1)

    def _make_tok_location(self, token):
        return (token.lineno, self.find_tok_column(token))

        tokens = ('ID', 'NUM', 'PLUS', 'MINUS', 'TIMES', 'DIV', 'EQUALS', 'MOD', 'LPAREN', 'RPAREN',
                  'LBRACKET', 'RBRACKET', 'LBRACE', 'RBRACE', 'COMMA', 'SEMI',
                  'LT', 'GT', 'LE', 'GE', 'EQ', 'NQ', 'AND', 'OR', 'INCREASE', 'DECREASE',
                  'ASSERT', 'PRINT', 'READ', 'ASSERT', 'FOR', 'RETURN', 'WHILE', 'SWITCH', 'IF', 'ELSE',
                  'INT', 'FLOAT', 'CHAR', 'DOUBLE', 'LONG',
                  'INT_CONST', 'FLOAT_CONST', 'CHAR_CONST', 'STRING')

