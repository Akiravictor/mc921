from uc_ast import *
from uc_lexer import UCLexer
import ply.yacc as yacc


class UCParser:
    def __init__(self):
        self.errors = 0
        self.warnings = 0

    def print_error(self, msg, x, y):
        print("Lexical error: %s at %d:%d" % (msg, x, y))

    def show(self, buf=None, showcoord=True):
        print("I'm on show")

    def p_error(self, p):
        if p:
            print("Error near the symbol %s" % p.value)
        else:
            print("Error at the end of input")

    def p_program(self, p):
        ''' program : global_declaration
        '''
        print("Inside p_program:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = p[1]

    def p_global_declaraion(self, p):
        ''' global_declaration : function_definition
                               | declaration
        '''
        print("Inside p_global_declaraion:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = p[1]

    def p_function_definition(self, p):
        ''' function_definition : type_specifier declarator declaration_list compound_statement
                                | declarator declaration_list compound_statement
        '''
        print("Inside p_function_definition:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 4:
            p[0] = (p[1], p[2], p[3])
        else:
            p[0] = (p[1], p[2], p[3], p[4])

    def p_init_declarator_list(self, p):
        ''' init_declarator_list : init_declarator
                                 | init_declarator_list COMMA init_declarator
        '''
        print("Inside p_init_declarator_list:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_init_declarator(self, p):
        ''' init_declarator : declarator
                            | declarator EQUALS initializer
        '''
        print("Inside p_init_declarator:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = (p[1], p[3])

    def p_initializer(self, p):
        ''' initializer : assignment_expression
                        | LBRACE initializer_list RBRACE
                        | LBRACE initializer_list COMMA RBRACE
        '''
        print("Inside p_initializer:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = p[1]

    def p_initializer_list(self, p):
        ''' initializer_list : initializer
                             | initializer_list COMMA initializer
        '''
        print("Inside p_initializer_list:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_declaration(self, p):
        ''' declaration : type_specifier SEMI
                        | type_specifier init_declarator_list SEMI
        '''
        print("Inside p_declaration:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = (p[1], p[2])

    def p_declaration_list(self, p):
        ''' declaration_list : declaration
                             | declaration_list declaration
                             | empty
        '''
        print("Inside p_declaration_list:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_declarator(self, p):
        ''' declarator : pointer direct_declarator
                       | direct_declarator
        '''
        print("Inside p_declarator:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[1]+p[2]

    def p_parameter_list(self, p):
        ''' parameter_list : parameter_declaration
                            | parameter_list COMMA parameter_declaration
        '''
        print("Inside p_parameter_list:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1]+[p[3]]

    def p_parameter_declaration(self, p):
        ''' parameter_declaration : type_specifier declarator
        '''
        print("Inside p_parameter_declaration:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = (p[1], p[2])

    def p_compound_statement(self, p):
        ''' compound_statement : LBRACE declaration_list statement_list RBRACE
        '''
        print("Inside p_compound_statement:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = (p[1], p[2])

    def p_expression_statement(self, p):
        ''' expression_statement : expression
                                 | empty SEMI
        '''
        print("Inside p_expression_statement:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = p[1]

    def p_expression(self, p):
        ''' expression : assignment_expression
                       | expression COMMA assignment_expression
        '''
        print("Inside p_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1]+[p[3]]

    def p_selection_statement(self, p):
        ''' selection_statement : IF LPAREN expression RPAREN statement
                                | IF LPAREN expression RPAREN statement ELSE statement
        '''
        print("Inside p_selection_statement:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 6:
            p[0] = (p[3], p[5])
        else:
            p[0] = (p[3], p[5], p[7])

    def p_iteration_statement(self, p):
        ''' iteration_statement : WHILE LPAREN expression RPAREN statement
                                | FOR LPAREN expression SEMI expression SEMI expression RPAREN statement
                                | FOR LPAREN SEMI expression SEMI expression RPAREN statement
                                | FOR LPAREN expression SEMI SEMI expression RPAREN statement
                                | FOR LPAREN SEMI SEMI expression RPAREN statement
                                | FOR LPAREN expression SEMI expression SEMI RPAREN statement
                                | FOR LPAREN SEMI expression SEMI RPAREN statement
                                | FOR LPAREN expression SEMI SEMI RPAREN statement
                                | FOR LPAREN SEMI SEMI RPAREN statement
                                | FOR LPAREN declaration expression SEMI expression RPAREN statement
                                | FOR LPAREN declaration SEMI expression RPAREN statement
                                | FOR LPAREN declaration expression SEMI RPAREN statement
                                | FOR LPAREN declaration SEMI RPAREN statement
        '''

        if len(p) == 6:
            p[0] = (p[3], p[5])
        elif p[3] == ";":
            if p[4] == ";":
                if p[5] == ")":
                    p[0] = p[6]
                else:
                    p[0] = (p[5], p[7])
            elif p[7] == ")":
                p[0] = (p[4], p[6], p[8])
            else:
                p[0] = (p[4], p[7])
        elif p[4] == ";":
            if p[5] == ")":
                p[0] = (p[3], p[6])
            elif p[6] == ")":
                if p[5] == ";":
                    p[0] = (p[3], p[7])
                else:
                    p[0] = (p[3], p[5], p[7])
            elif p[5] == ";":
                p[0] = (p[3], p[6], p[8])
            elif p[6] == ";":
                if p[7] == ")":
                    p[0] = (p[3], p[5], p[8])
                else:
                    p[0] = (p[3], p[5], p[7], p[9])
        elif p[6] == ")":
            p[0] = (p[3], p[4], p[7])
        else:
            p[0] = (p[3], p[4], p[6], p[8])

    def p_jump_statement(self, p):
        ''' jump_statement : BREAK SEMI
                           | RETURN expression SEMI
                           | RETURN SEMI
        '''
        print("Inside p_jump_statement:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')

    def p_assert_statement(self, p):
        ''' assert_statement : ASSERT expression SEMI
                             | ASSERT SEMI
        '''
        print("Inside p_assert_statement:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 3:
            p[0] = p[2]
        else:
            p[0] = p[1]

    def p_print_statement(self, p):
        ''' print_statement : PRINT LPAREN expression RPAREN SEMI
                            | PRINT LPAREN RPAREN SEMI
        '''
        print("Inside p_print_statement:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = p[3]

    def p_read_statement(self, p):
        ''' read_statement : READ LPAREN argument_expression RPAREN SEMI
        '''
        print("Inside p_read_statement:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = p[3]

    def p_statement(self, p):
        ''' statement : expression_statement
                      | compound_statement
                      | selection_statement
                      | iteration_statement
                      | jump_statement
                      | assert_statement
                      | print_statement
                      | read_statement
        '''
        print("Inside p_statement:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = p[1]

    def p_statement_list(self, p):
        ''' statement_list : statement
                           | statement_list statement
                           | empty
        '''
        print("Inside p_statement_list:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_assignment_expression(self, p):
        ''' assignment_expression : binary_expression
                                  | unary_expression assignment_operator assignment_expression
        '''
        print("Inside p_assignment_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = (p[1], p[2], p[3])

    def p_binary_expression(self, p):
        ''' binary_expression : cast_expression
                              | binary_expression PLUS binary_expression
                              | binary_expression MINUS binary_expression
                              | binary_expression TIMES binary_expression
                              | binary_expression DIVIDE binary_expression
                              | binary_expression MOD binary_expression
                              | binary_expression LT binary_expression
                              | binary_expression LE binary_expression
                              | binary_expression GT binary_expression
                              | binary_expression GE binary_expression
                              | binary_expression EQ binary_expression
                              | binary_expression NQ binary_expression
                              | binary_expression AND binary_expression
                              | binary_expression OR binary_expression
        '''
        print("Inside p_binary_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
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

    def p_unary_expression(self, p):
        ''' unary_expression : postfix_expression
                             | INCREASE unary_expression
                             | DECREASE unary_expression
                             | unary_operator cast_expression
        '''
        print("Inside p_unary_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = (p[1], p[2])

    def p_postfix_expression(self, p):
        ''' postfix_expression : primary_expression
                               | postfix_expression LBRACKET expression RBRACKET
                               | postfix_expression LPAREN argument_expression RPAREN
                               | postfix_expression LPAREN RPAREN
                               | postfix_expression INCREASE
                               | postfix_expression DECREASE
        '''
        print("Inside p_postfix_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = (p[2], p[1])
        else:
            p[0] = (p[1], p[3])

    def p_cast_expression(self, p):
        ''' cast_expression : unary_expression
                            | LPAREN type_specifier RPAREN cast_expression
        '''
        print("Inside p_cast_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = (p[2], p[4])

    def p_primary_expression(self, p):
        ''' primary_expression : ID
                               | constant
                               | STRING
                               | LPAREN expression RPAREN
        '''
        print("Inside p_primary_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = p[1]

    def p_argument_expression(self, p):
        ''' argument_expression : assignment_expression
                                | argument_expression COMMA assignment_expression
        '''
        print("Inside p_argument_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1]+[p[3]]

    def p_constant_expression(self, p):
        ''' constant_expression : binary_expression
        '''
        print("Inside p_constant_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = p[1]

    def p_assignment_operator(self, p):
        ''' assignment_operator : EQUALS
                               | EQTIMES
                               | EQDIV
                               | EQMOD
                               | EQPLUS
                               | EQMINUS
        '''
        print("Inside p_assignment_operator:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = p[1]

    def p_unary_operator(self, p):
        ''' unary_operator : ADDRESS
                           | TIMES
                           | PLUS
                           | UMINUS
                           | NOT
        '''
        print("Inside p_unary_operator:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = p[1]

    def p_constant(self, p):
        ''' constant : INT_CONST
                     | FLOAT_CONST
                     | CHAR_CONST
        '''
        print("Inside p_constant:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = p[1]

    def p_pointer(self, p):
        ''' pointer : TIMES pointer
                    | TIMES
        '''
        print("Inside p_pointer:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')

    def p_direct_declarator(self, p):
        ''' direct_declarator : ID
                              | LPAREN declarator RPAREN
                              | direct_declarator LBRACKET constant_expression RBRACKET
                              | direct_declarator LBRACKET RBRACKET
                              | direct_declarator LPAREN parameter_list RPAREN
                              | direct_declarator LPAREN id_list RPAREN
        '''
        print("Inside p_direct_declarator:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = (p[1], p[3])

    def p_id_list(self, p):
        ''' id_list : ID
                    | id_list ID
                    | empty
        '''
        print("Inside p_id_list:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_type_specifier(self, p):
        '''  type_specifier : VOID
                           | INT
                           | FLOAT
                           | CHAR
        '''
        print("Inside p_type_specifier:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = p[1]

    def p_empty(self, p):
        '''  empty :
        '''
        pass

    def parse(self, code, filename='', debug=0):
        if debug:
            print("Code: {0}".format(code))
            print("Filename: {0}".format(filename))

        print("I'm on parser! :D")

        lexer = UCLexer(self.print_error)
        lexer.build()
        lexer.input(code)

        self.tokens = lexer.tokens
        self.precedence = (
             ('nonassoc', 'LT', 'GT', 'LE', 'GE', 'EQ', 'NQ', 'NOT', 'AND', 'OR'),  # Nonassociative operators
             ('left', 'PLUS', 'MINUS'),
             ('left', 'TIMES', 'DIVIDE', 'MOD'),
             ('right', 'UMINUS')
         )

        parser = yacc.yacc(module=self)
        print(code)
        result = parser.parse(code)
        # result = parser.parse('int main();')
        print(result)


        return AST
