from uc_ast import *
from uc_lexer import UCLexer


class UCParser:
    def __init__(self):
        self.errors = 0
        self.warnings = 0

    def print_error(self, msg, x, y):
        print("Lexical error: %s at %d:%d" % (msg, x, y))

    def parse(self, code, filename='', debug=0):
        if debug:
            print("Code: {0}".format(code))
            print("Filename: {0}".format(filename))

        print("I'm on parser! :D")

        lexer = UCLexer(self.print_error)
        lexer.build()
        lexer.input(code)

        return AST



    def show(self, buf=None, showcoord=True):
        print("I'm on show")

    def p_program(self, p):
        """ program  : global_declaration_list
        """
        p[0] = Program(p[1])

    def p_global_declaration_list(self, p):
        """ global_declaration_list : global_declaration
                                    | global_declaration_list global_declaration
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_identifier(self, p):
        """ identifier : ID """
        p[0] = ID(p[1], lineno=p.lineno(1))

    def p_type_specifier(self, p):
        """ type_specifier : void
                           | char
                           | int
                           | float
        """
        p[0] = p[1]

    def p_pointer(self, p):
        """ pointer : TIMES
                    | TIMES pointer
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]]+p[2]

    def p_declarator(self, p):
        """ declarator : direct_declarator
                       | pointer direct_declarator
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[1]+p[2]

    def p_direct_declarator(self, p):
        """ direct_declarator : identifier
                              | declarator
                              | direct_declarator LBRACKET constant_expression_opt RBRACKET
                              | direct_declarator LPAREN parameter_list RPAREN
                              | direct_declarator LPAREN identifier RPAREN TIMES
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = (p[1], p[3])

    def p_constant_expression_opt(self, p):
        """ constant_expression_opt : constant_expression
                                    | None
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = None

    def p_constant_expression(self, p):
        """ constant_expression : binary_expression
        """
        p[0] = p[1]

    def p_binary_expression(self, p):
        """ binary_expression : cast_expression
                              | binary_expression TIMES binary_expression
                              | binary_expression DIVIDE binary_expression
                              | binary_expression MOD binary_expression
                              | binary_expression PLUS binary_expression
                              | binary_expression MINUS binary_expression
                              | binary_expression LT binary_expression
                              | binary_expression LE binary_expression
                              | binary_expression GT binary_expression
                              | binary_expression GE binary_expression
                              | binary_expression EQ binary_expression
                              | binary_expression NQ binary_expression
                              | binary_expression AND binary_expression
                              | binary_expression OR binary_expression
        """
        if len(p) == 2:
            p[0] = p[1]
        elif p[2] == '*':
            p[0] = p[1] * p[3]

        elif p[2] == '/':
            p[0] = p[1] / p[3]

        elif p[2] == '%':
            p[0] = p[1] & p[3]

        elif p[2] == '+':
            p[0] = p[1] + p[3]

        elif p[2] == '-':
            p[0] = p[1] - p[3]

        elif p[2] == '<':
            p[0] = (p[1] < p[3])

        elif p[2] == '<=':
            p[0] = (p[1] <= p[3])

        elif p[2] == '>':
            p[0] = (p[1] > p[3])

        elif p[2] == '>=':
            p[0] = (p[1] >= p[3])

        elif p[2] == '==':
            p[0] = (p[1] == p[3])

        elif p[2] == '!=':
            p[0] = (p[1] != p[3])

        elif p[2] == '&&':
            p[0] = p[1] and p[3]

        elif p[2] == '||':
            p[0] = p[1] or p[3]

    def p_cast_expression(self, p):
        """ cast_expression : unary_expression
                            | LPAREN type_specifier RPAREN cast_expression
        """

    def p_unary_expression(self, p):
        """ unary_expression : postfix_expression
                             | INCREASE unary_expression
                             | DECREASE unary_expression
                             | unary_operator cast_expression
        """

    def p_postfix_expression(self, p):
        """ postfix_expression : primary_expression
                               | postfix_expression LBRACKET expression RBRACKET
                               | postfix_expression LPAREN argument_expression_opt RPAREN
                               | postfix_expression INCREASE
                               | postfix_expression DECREASE
        """

    def p_argument_expression_opt(self, p):
        """ argument_expression_opt : argument_expression
                                    | None
        """

    def p_primary_expression(self, p):
        """ primary_expression : identifier
                               | constant
                               | string
                               | expression
        """

    def p_constant(self, p):
        """ constant : integer_constant
                     | character_constant
                     | floating_constant
        """

    def p_expression(self, p):
        """ expression : assignment_expression
                       | expression COMMA assignment_expression
        """

    def p_argument_expression(self, p):
        """ argument_expression : assignment_expression
                                | argument_expression COMMA assignment_expression
        """

    def p_assignment_expression(self, p):
        """ assignment_expression : binary_expression
                                  | unary_expression assignment_operator assignment_expression
        """

    def p_assignment_operator(self, p):
        """ assignment_operator : EQ
                                | *=
                                | /=
                                | %=
                                | +=
                                | -=
        """

    def p_unary_operator(self, p):
        """ unary_operator : &
                           | TIMES
                           | PLUS
                           | MINUS
                           | !
        """

    def p_parameter_list(self, p):
        """ parameter_list : parameter_declaration
                           | parameter_list COMMA parameter_declaration
        """

    def p_parameter_declaration(self, p):
        """ parameter_declaration : type_specifier declarator
        """

    def p_declaration(self, p):
        """ declaration : type_specifier init_declarator_list_opt SEMI
        """

    def p_init_declarator_list_opt(self, p):
        """ init_declarator_list_opt : init_declarator_list
                                     | None
        """

    def p_init_declarator_list(self, p):
        """ init_declarator_list : init_declarator
                                 | init_declarator_list COMMA init_declarator
        """

    def p_init_declarator(self, p):
        """ init_declarator : declarator
                            | declarator EQUALS initializer
        """

    def p_initializer(self, p):
        """ initializer : assignment_expression
                     | initializer_list
                     | initializer_list COMMA
        """

    def p_initializer_list(self, p):
        """ initializer_list : initializer
                             | initializer_list COMMA initializer
        """

    def p_compound_statement(self, p):
        """ compound_statement : declaration TIMES statement TIMES
        """

    def p_statement(self, p):
        """ statement : expression_statement
                      | compound_statement
                      | selection_statement
                      | iteration_statement
                      | jump_statement
                      | assert_statement
                      | print_statement
                      | read_statement
        """

    def p_expression_statement(self, p):
        """ expression_statement : expression_opt SEMI
        """

    def p_expression_opt(self, p):
        """ expression_opt : expression
                           | None
        """

    def p_selection_statement(self, p):
        """ selection_statement : IF expression statement
                                | IF expression statement ELSE statement
        """

    def p_iteration_statement(self, p):
        """ iteration_statement : WHILE LPAREN expression RPAREN statement
                                | FOR LPAREN expression_opt SEMI expression_opt SEMI expression_opt RPAREN statement
                                | FOR LPAREN declaration SEMI expression_opt SEMI expression_opt RPAREN statement
        """

    def p_jump_statement(self, p):
        """ jump_statement : BREAK
                           | RETURN expression_opt SEMI
        """

    def p_assert_statement(self, p):
        """ assert_statement : ASSERT expression SEMI
        """

    def p_print_statement(self, p):
        """ print_statement : PRINT LPAREN expression_opt RPAREN SEMI
        """

    def p_read_statement(self, p):
        """ read_statement : READ LPAREN argument_expression RPAREN SEMI
        """
