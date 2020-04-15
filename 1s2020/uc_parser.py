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
        ''' program : global_declaration_list
        '''
        print("Inside p_program:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = p[1]

    def p_global_declaration_list(self, p):
        ''' global_declaration_list : global_declaration_list global_declaration
                                    | empty
        '''
        print("Inside p_global_declaration_list:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            if p[1] is None:
                p[0] = []
            else:
                p[0] = [p[1]]
        if len(p) == 3:
            p[0] = p[1] + [p[2]]

    def p_global_declaration(self, p):
        ''' global_declaration : function_definition
                               | declaration
        '''
        print("Inside p_global_declaration:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = p[1]

    def p_function_definition(self, p):
        ''' function_definition : type_specifier declarator compound_statement
                                | declarator declaration_list_opt compound_statement
        '''
        print("Inside p_function_definition:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = (p[1], p[2], p[3])

    def p_init_declarator_list_opt(self, p):
        ''' init_declarator_list_opt : init_declarator_list
                                     | empty
        '''
        print("Inside p_init_declarator_list_opt:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if p[1] is not None:
            p[0] = p[1]

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
        elif len(p) == 4:
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
        elif len(p) == 4:
            p[0] = (p[2], p[1], p[3])

    def p_initializer(self, p):
        ''' initializer : assignment_expression
                        | LBRACE initializer_list RBRACE
                        | LBRACE initializer_list COMMA RBRACE
        '''
        print("Inside p_initializer:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            p[0] = p[2]
        elif len(p) == 5:
            p[0] = p[2]

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
        elif len(p) == 4:
            p[0] = p[1] + [p[3]]

    def p_declaration(self, p):
        ''' declaration :  type_specifier init_declarator_list_opt SEMI
        '''
        print("Inside p_declaration:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = (p[1], p[2])

    def p_declaration_list_opt(self, p):
        ''' declaration_list_opt : declaration_list_opt declaration
                                 | empty
        '''
        print("Inside p_declaration_list_opt:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            if p[1] is None:
                p[0] = []
            else:
                p[0] = p[1]
        if len(p) == 3:
            p[0] = p[1] + [p[2]]

    def p_declarator(self, p):
        ''' declarator : pointer_opt direct_declarator
        '''
        print("Inside p_declarator:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')

        if p[1] is None:
            p[0] = p[2]

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
        elif len(p) == 4:
            p[0] = p[1] + [p[3]]

    def p_parameter_declaration(self, p):
        ''' parameter_declaration : type_specifier declarator
        '''
        print("Inside p_parameter_declaration:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = (p[1], p[2])

    def p_compound_statement(self, p):
        ''' compound_statement : LBRACE declaration_list_opt statement_list_opt RBRACE
        '''
        print("Inside p_compound_statement:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = (p[2], p[3])

    def p_expression_statement(self, p):
        ''' expression_statement : expression_opt SEMI
        '''
        print("Inside p_expression_statement:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = p[1]

    def p_expression_opt(self, p):
        ''' expression_opt : expression
                           | empty
        '''
        print("Inside p_expression_opt:")
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
            p[0] = p[1]
        elif len(p) == 4:
            p[0] = (p[1], p[3])

    def p_selection_statement(self, p):
        ''' selection_statement : IF LPAREN expression RPAREN statement
                                | IF LPAREN expression RPAREN statement ELSE statement
        '''
        print("Inside p_selection_statement:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 6:
            p[0] = (p[1], p[3], p[5])
        elif len(p) == 8:
            p[0] = (p[1], p[3], p[5], p[6], p[7])

    def p_iteration_statement(self, p):
        ''' iteration_statement : WHILE LPAREN expression RPAREN statement
                                | FOR LPAREN init_declarator SEMI expression_opt SEMI expression_opt RPAREN statement
                                | FOR LPAREN type_specifier init_declarator SEMI expression_opt SEMI expression_opt RPAREN statement
        '''
        print("Inside p_iteration_statement:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 6:
            p[0] = (p[1], p[3], p[5])
        elif len(p) == 10:
            p[0] = (p[1], p[3], p[5], p[7], p[9])
        elif len(p) == 11:
            p[0] = (p[1], p[3], p[4], p[6], p[8], [p[10]])

    def p_jump_statement(self, p):
        ''' jump_statement : BREAK SEMI
                           | RETURN expression SEMI
                           | RETURN SEMI
        '''
        print("Inside p_jump_statement:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 4:
            p[0] = p[2]

    def p_assert_statement(self, p):
        ''' assert_statement : ASSERT expression SEMI
        '''
        print("Inside p_assert_statement:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = p[2]

    def p_print_statement(self, p):
        ''' print_statement : PRINT LPAREN expression_opt RPAREN SEMI
        '''
        print("Inside p_print_statement:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = ('print', p[3])

    def p_read_statement(self, p):
        ''' read_statement : READ LPAREN argument_expression RPAREN SEMI
        '''
        print("Inside p_read_statement:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = ('read', p[3])

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

    def p_statement_list_opt(self, p):
        ''' statement_list_opt : statement_list_opt statement
                               | empty
        '''
        print("Inside p_statement_list_opt:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            if p[1] is None:
                p[0] = []
            else:
                p[0] = p[1]
        if len(p) == 3:
            if p[2] is None:
                p[0] = p[1]
            else:
                p[0] = p[1] + [p[2]]
            # if p[1] is not None:
            #     if p[2] is not None:
            #         p[0] = p[1] + [p[2]]
            #     else:
            #         p[0] = [p[1]]
            #
            # elif p[1] is None:
            #     if p[2] is not None:
            #         p[0] = [p[2]]

    def p_assignment_expression(self, p):
        ''' assignment_expression : binary_expression
                                  | unary_expression assignment_operator assignment_expression
        '''
        print("Inside p_assignment_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 4:
            p[0] = (p[2], p[1], p[3])
        elif len(p) == 2:
            p[0] = p[1]

    def p_binary_expression(self, p):
        ''' binary_expression : cast_expression
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
        '''
        print("Inside p_binary_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            p[0] = (p[2], p[1], p[3])

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
        elif len(p) == 3:
            p[0] = (p[1], p[2])

    def p_postfix_expression(self, p):
        ''' postfix_expression : primary_expression
                               | postfix_expression LBRACKET expression RBRACKET
                               | postfix_expression LPAREN argument_expression_opt RPAREN
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
        elif len(p) == 5:
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
        elif len(p) == 5:
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
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            p[0] = p[2]

    def p_argument_expression_opt(self, p):
        ''' argument_expression_opt : argument_expression
                                    | empty
        '''
        print("Inside p_argument_expression_opt:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if p[1] is not None:
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
            p[0] = p[1]
        elif len(p) == 4:
            p[0] = (p[1], p[3])

    def p_constant_expression_opt(self, p):
        ''' constant_expression_opt : constant_expression
                                    | empty
        '''
        print("Inside p_constant_expression_opt:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if p[1] is not None:
            p[0] = p[1]

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

    def p_pointer_opt(self, p):
        ''' pointer_opt : pointer
                        | empty
        '''
        print("Inside p_pointer_opt:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if p[1] is not None:
            p[0] = p[1]

    def p_pointer(self, p):
        ''' pointer : TIMES pointer
                    | TIMES
        '''
        print("Inside p_pointer:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 3:
            p[0] = p[2]

    def p_direct_declarator(self, p):
        ''' direct_declarator : ID
                              | LPAREN declarator RPAREN
                              | direct_declarator LBRACKET constant_expression_opt RBRACKET
                              | direct_declarator LPAREN parameter_list RPAREN
                              | direct_declarator LPAREN id_list RPAREN
        '''
        print("Inside p_direct_declarator:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            p[0] = p[2]
        elif len(p) == 5:
            if p[2] == '[' and p[4] == ']':
                if p[3] is None:
                    p[0] = ('Array', p[1], '')
                else:
                    p[0] = ('Array', p[1], p[3])
            else:
                p[0] = (p[1], p[3])

    def p_id_list(self, p):
        ''' id_list : id_list ID
                    | empty
        '''
        print("Inside p_id_list:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            if p[1] is None:
                p[0] = []
            else:
                p[0] = p[1]
        if len(p) == 3:
            p[0] = p[1] + [p[2]]

    def p_type_specifier(self, p):
        ''' type_specifier : VOID
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
        ''' empty :'''
        # print("Inside p_empty:")
        # for i in range(len(p)):
        #     print("p[{0}] = {1}".format(i, p[i]))
        # print('End')
        pass

    def parse(self, code, filename='', debug=0):
        if debug:
            print("Code: {0}".format(code))
            print("Filename: {0}".format(filename))

        print("I'm on parser! :D")

        lexer = UCLexer(self.print_error)
        lexer.build()
        # lexer.input(code)

        self.tokens = lexer.tokens
        self.precedence = (
             ('nonassoc', 'LT', 'GT', 'LE', 'GE', 'EQ', 'NQ', 'NOT', 'AND', 'OR'),  # Nonassociative operators
             ('left', 'PLUS', 'MINUS'),
             ('left', 'TIMES', 'DIVIDE', 'MOD'),
             ('right', 'UMINUS')
         )

        parser = yacc.yacc(module=self, write_tables=False)
        # print(code)
        result = parser.parse(code)
        # result = parser.parse("int a = 2;")
        print(result)


        return self
