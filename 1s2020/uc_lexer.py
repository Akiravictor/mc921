import ply.lex as lex


class UCLexer:
    keywords = ('ASSERT', 'PRINT', 'READ', 'FOR', 'RETURN', 'WHILE', 'SWITCH', 'CASE', 'IF', 'ELSE',
                'INT', 'FLOAT', 'CHAR', 'DOUBLE', 'LONG')

    tokens = ('ID', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'EQUALS', 'MOD', 'LPAREN', 'RPAREN',
              'ADDRESS', 'NOT',
              'EQTIMES', 'EQDIV', 'EQMOD', 'EQPLUS', 'EQMINUS',
              'LBRACKET', 'RBRACKET', 'LBRACE', 'RBRACE', 'COMMA', 'SEMI',
              'LT', 'GT', 'LE', 'GE', 'EQ', 'NQ', 'AND', 'OR', 'INCREASE', 'DECREASE',
              'INT_CONST', 'FLOAT_CONST', 'CHAR_CONST', 'STRING') + keywords

    # Regular expression rules for simple tokens
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_EQUALS = r'='
    t_ADDRESS = r'\&'
    t_NOT = r'!'
    t_EQTIMES = r'\*='
    t_EQDIV = r'\/='
    t_EQMOD = r'%='
    t_EQPLUS = r'\+='
    t_EQMINUS = r'-='
    t_MOD = r'%'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_LBRACE = r'{'
    t_RBRACE = r'}'
    t_COMMA = r','
    t_SEMI = r';'
    t_LT = r'<'
    t_GT = r'>'
    t_LE = r'<='
    t_GE = r'>='
    t_EQ = r'=='
    t_NQ = r'!='
    t_AND = r'&&'
    t_OR = r'\|\|'
    t_INCREASE = r'\+\+'
    t_DECREASE = r'--'
    t_ASSERT = r'assert'
    t_PRINT = r'print'
    t_READ = r'read'
    t_FOR = r'for'
    t_WHILE = r'while'
    t_SWITCH = r'switch'
    t_CASE = r'case'
    t_IF = r'if'
    t_ELSE = r'else'
    t_INT = r'int'
    t_FLOAT = r'float'
    t_CHAR = r'char'
    t_DOUBLE = r'double'
    t_LONG = r'long'

    keyword_map = {}
    for keyword in keywords:
        keyword_map[keyword.lower()] = keyword

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

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        t.type = self.keyword_map.get(t.value, "ID")
        return t

    def t_INT_CONST(self, t):
        r'[0-9]+'
        t.type = self.keyword_map.get(t.value, "INT_CONST")
        return t

    def t_FLOAT_CONST(self, t):
        r'[0-9]+\.[0-9]*'
        t.type = self.keyword_map.get(t.value, "FLOAT_CONST")
        return t

    def t_CHAR_CONST(self, t):
        r'\'[a-zA-Z]{1}\''
        t.type = self.keyword_map.get(t.value, "CHAR_CONST")
        return t

    def t_STRING(self, t):
        r'\"[a-zA-Z]*\"'
        t.type = self.keyword_map.get(t.value, "STRING")
        return t

    # A regular expression rule with some action code
    # Note addition of self parameter since we're in a class
    # def t_NUMBER(self, t):
    #     r'\d+'
    #     t.value = int(t.value)
    #     return t

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_comment(self, t):
        r'(\/\*(.|\n)*?\*\/)|(\/\/.*)'
        pass

    # # A string containing ignored characters (spaces and tabs)
    t_ignore = ' \t'

    # Error handling rule
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)
