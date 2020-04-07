import ply.lex as lex


class UCLexer:
    tokens = ('ID', 'NUMBER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'EQUALS', 'MOD', 'LPAREN', 'RPAREN',
              'LBRACKET', 'RBRACKET', 'LBRACE', 'RBRACE', 'COMMA', 'SEMI',
              'LT', 'GT', 'LE', 'GE', 'EQ', 'NQ', 'AND', 'OR', 'INCREASE', 'DECREASE',
              'ASSERT', 'PRINT', 'READ', 'FOR', 'RETURN', 'WHILE', 'SWITCH', 'IF', 'ELSE',
              'INT', 'FLOAT', 'CHAR', 'DOUBLE', 'LONG',
              'INT_CONST', 'FLOAT_CONST', 'CHAR_CONST', 'STRING')

    # Regular expression rules for simple tokens
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'

    def __init__(self, error_func):
        self.error_func = error_func
        self.filename = ''
        self.last_token = None

    def build(self, **kwargs):
        print("I'm on lexer!")
        self.lexer = lex.lex(module=self, **kwargs)

    def reset_lineno(self):
        """ Resets the internal line number counter of the lexer.
        """
        self.lexer.lineno = 1

    def input(self, text):
        self.lexer.input(text)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)

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

    # A regular expression rule with some action code
    # Note addition of self parameter since we're in a class
    def t_NUMBER(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # # A string containing ignored characters (spaces and tabs)
    # t_ignore = ' \t'

    # Error handling rule
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)
