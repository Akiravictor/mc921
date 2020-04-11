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

    def p_global_declaraion(self, p):
        ''' global_declaration : function_definition
                               | declaration
        '''

    def p_function_definition(self, p):
        ''' function_definition : type_specifier declarator declaration_list compound_statement
                                | declarator declaration_list compound_statement
        '''

    def p_declaration(self, p):
        ''' declaration : type_specifier SEMI
                        | type_specifier init_declarator_list SEMI
        '''

    def p_init_declarator_list(self, p):
        ''' init_declarator_list : init_declarator
                                 | init_declarator_list COMMA init_declarator
        '''

    def p_init_declarator(self, p):
        ''' init_declarator : declarator
                            | declarator EQUALS initializer
        '''

    def p_initializer(self, p):
        ''' initializer : assignment_expression
                        | LBRACE initializer_list RBRACE
                        | LBRACE initializer_list COMMA RBRACE
        '''

    def p_initializer_list(self, p):
        ''' initializer_list : initializer
                             | initializer_list COMMA initializer
        '''

    def p_declaration_list(self, p):
        ''' declaration_list : declaration
                             | declaration_list declaration
        '''

    def p_declarator(self, p):
        ''' declarator : pointer direct_declarator
                       | direct_declarator
        '''

    def p_parameter_list(self, p):
        ''' parameter_list : parameter_declaration
                            | parameter_list COMMA parameter_declaration
        '''

    def p_parameter_declaration(self, p):
        ''' parameter_declaration : type_specifier declarator
        '''

    def p_compound_statement(self, p):
        ''' compound_statement : LBRACE declaration_list statement_list RBRACE
        '''

    def p_expression_statement(self, p):
        ''' expression_statement : expression
                                 | empty
        '''

    def p_expression(self, p):
        ''' expression : assignment_expression
                       | expression COMMA assignment_expression
        '''

    def p_selection_statement(self, p):
        ''' selection_statement : IF LPAREN expression RPAREN statement
                                | IF LPAREN expression RPAREN statement ELSE statement
        '''

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

    def p_jump_statement(self, p):
        ''' jump_statement : BREAK SEMI
                           | RETURN expression SEMI
                           | RETURN SEMI
        '''

    def p_assert_statement(self, p):
        ''' assert_statement : ASSERT expression SEMI
                             | ASSERT SEMI
        '''

    def p_print_statement(self, p):
        ''' print_statement : PRINT LPAREN expression RPAREN SEMI
                            | PRINT LPAREN RPAREN SEMI
        '''

    def p_read_statement(self, p):
        ''' read_statement : READ LPAREN argument_expression RPAREN SEMI
        '''

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

    def p_statement_list(self, p):
        ''' statement_list : statement
                           | statement_list statement
        '''

    def p_assignment_expression(self, p):
        ''' assignment_expression : binary_expression
                                  | unary_expression assignment_operator assignment_expression
        '''

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

    def p_unary_expression(self, p):
        ''' unary_expression : postfix_expression
                             | INCREASE unary_expression
                             | DECREASE unary_expression
                             | unary_operator cast_expression
        '''

    def p_postfix_expression(self, p):
        ''' postfix_expression : primary_expression
                               | postfix_expression LBRACKET expression RBRACKET
                               | postfix_expression LPAREN argument_expression RPAREN
                               | postfix_expression LPAREN RPAREN
                               | postfix_expression INCREASE
                               | postfix_expression DECREASE
        '''

    def p_cast_expression(self, p):
        ''' cast_expression : unary_expression
                            | LPAREN type_specifier RPAREN cast_expression
        '''

    def p_primary_expression(self, p):
        ''' primary_expression : ID
                               | constant
                               | STRING
                               | LPAREN expression RPAREN
        '''

    def p_argument_expression(self, p):
        ''' argument_expression : assignment_expression
                                | argument_expression COMMA assignment_expression
        '''

    def p_constant_expression(self, p):
        ''' constant_expression : binary_expression
        '''

    def p_assignment_operator(self, p):
        ''' assignment_operator : EQUALS
                               | EQTIMES
                               | EQDIV
                               | EQMOD
                               | EQPLUS
                               | EQMINUS
        '''

    def p_unary_operator(self, p):
        ''' unary_operator : ADDRESS
                           | TIMES
                           | PLUS
                           | UMINUS
                           | NOT
        '''

    def p_constant(self, p):
        ''' constant : INT_CONST
                     | FLOAT_CONST
                     | CHAR_CONST
        '''

    def p_pointer(self, p):
        ''' pointer : TIMES pointer
                    | TIMES
        '''

    def p_direct_declarator(self, p):
        ''' direct_declarator : ID
                              | LPAREN declarator RPAREN
                              | direct_declarator LBRACKET constant_expression RBRACKET
                              | direct_declarator LBRACKET RBRACKET
                              | direct_declarator LPAREN parameter_list RPAREN
                              | direct_declarator LPAREN id_list RPAREN
        '''

    def p_id_list(self, p):
        ''' id_list : ID
                    | id_list ID
        '''

    def p_type_specifier(self, p):
        ''' type_specifier : VOID
                           | INT
                           | FLOAT
                           | CHAR
        '''



    def p_empty(self, p):
        ''' empty :'''
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
        print(result)


        return AST
