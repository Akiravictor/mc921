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

    def _token_coord(self, p, token_idx):
        last_cr = p.lexer.lexer.lexdata.rfind('\n', 0, p.lexpos(token_idx))
        if last_cr < 0:
            last_cr = -1
        column = (p.lexpos(token_idx) - (last_cr))
        return Coord(p.lineno(token_idx), column)

    def p_error(self, p):
        if p:
            print("Error near the symbol %s" % p.value)
        else:
            print("Error at the end of input")

    def _build_function_definition(self, spec, decl, param_decls, body):
        declaration = self._build_declarations(spec=spec, decls=[dict(decl=decl, init=None)])[0]

        return FuncDef(spec=spec, decl=declaration, param_decls=param_decls, body=body, coord=decl.coord)

    def _build_declarations(self, spec, decls):
        declarations = []

        for decl in decls:
            assert decl['decl'] is not None
            declaration = Decl(name=None, type=decl['decl'], init=decl.get('init'), coord=decl['decl'].coord)

            if isinstance(declaration.type, (Type)):
                fixed_decl = declaration
            else:
                fixed_decl = self._fix_decl_name_type(declaration, spec)

            declarations.append(fixed_decl)

        return declarations

    def _fix_decl_name_type(self, decl, typename):
        type = decl
        while not isinstance(type, VarDecl):
            type = type.type

        decl.name = type.declname

        for tn in typename:
            if not isinstance(tn, Type):
                if len(typename) > 1:
                    self._parse_error("Invalid multiple types specified", tn.coord)

                else:
                    type.type = tn
                    return decl

        if not typename:
            if not isinstance(decl.type, FuncDef):
                self._parse_error("Missing type in declaration", decl.coord)

            type.type = Type(['int'], coord=decl.coord)
        else:
            # At this point, we know that typename is a list of Type
            # nodes. Concatenate all the names into a single list.
            type.type = Type(
                [typename.names[0]],
                coord=typename.coord)
        return decl


    def p_program(self, p):
        ''' program : global_declaration_list
        '''
        print("Inside p_program:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # p[0] = p[1]
        p[0] = Program(p[1])

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

    def p_global_declaration_1(self, p):
        ''' global_declaration : function_definition
        '''
        print("Inside p_global_declaration:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = p[1]

    def p_global_declaration_2(self, p):
        ''' global_declaration : declaration
        '''
        print("Inside p_global_declaration:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[0] = GlobalDecl(p[1])
        # p[0] = p[1]

    def p_function_definition_1(self, p):
        ''' function_definition : type_specifier declarator declaration_list_opt compound_statement
        '''
        print("Inside p_function_definition:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 5:
        #     p[0] = FuncDef(p[1], p[2], p[3], p[4])
        # p[0] = (p[1], p[2], p[3], p[4])
        p[0] = self._build_function_definition(spec=p[1], decl=p[2], param_decls=p[3], body=p[4])

    def p_function_definition_2(self, p):
        ''' function_definition : declarator declaration_list_opt compound_statement
        '''
        print("Inside p_function_definition:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 4:
        #     p[0] = FuncDef('void', p[1], p[2], p[3])
        # p[0] = ('void', p[1], p[2], p[3])
        p[0] = self._build_function_definition(spec=dict(type=[Type(['void'], coord=self._token_coord(p, 1))]),
                                               decl=p[1], param_decls=p[2], body=p[3])


    def p_init_declarator_list_opt(self, p):
        ''' init_declarator_list_opt : init_declarator_list
                                     | empty
        '''
        print("Inside p_init_declarator_list_opt:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if p[1] is not None:
            # p[0] = DeclList(p[1])
            p[0] = p[1]

    def p_init_declarator_list_1(self, p):
        ''' init_declarator_list : init_declarator
        '''
        print("Inside p_init_declarator_list:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 2:
        #     p[0] = [p[1]]
        p[0] = [p[1]]

    def p_init_declarator_list_2(self, p):
        ''' init_declarator_list : init_declarator_list COMMA init_declarator
        '''
        print("Inside p_init_declarator_list:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 4:
        #     p[0] = p[1] + [p[3]]
        p[0] = p[1] + [p[3]]

    def p_init_declarator(self, p):
        ''' init_declarator : declarator
                            | declarator EQUALS initializer
        '''
        print("Inside p_init_declarator:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 2:
        #     p[0] = Decl(p[1])
        p[0] = dict(decl=p[1], init=(p[3] if len(p) > 2 else None))
        pass


    def p_initializer_1(self, p):
        ''' initializer : assignment_expression
        '''
        print("Inside p_initializer:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            p[0] = p[1]

    def p_initializer_2(self, p):
        ''' initializer : LBRACE initializer_list RBRACE
                        | LBRACE initializer_list COMMA RBRACE
        '''
        print("Inside p_initializer:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if p[2] is None:
            p[0] = InitList([], self._token_coord(p, 1))
        else:
            p[0] = p[2]

    def p_initializer_list_1(self, p):
        ''' initializer_list : initializer
        '''
        print("Inside p_initializer_list:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            p[0] = InitList([p[1]], p[1].coord)

    def p_initializer_list_2(self, p):
        ''' initializer_list : initializer_list COMMA initializer
        '''
        print("Inside p_initializer_list:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        p[1].exprs.append(p[3])
        p[0] = p[1]

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

    def p_parameter_list_1(self, p):
        ''' parameter_list : parameter_declaration
        '''
        print("Inside p_parameter_list_1:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            p[0] = [p[1]]

    def p_parameter_list_2(self, p):
        ''' parameter_list : parameter_list COMMA parameter_declaration
        '''
        print("Inside p_parameter_list_2:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 4:
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

    def p_expression_1(self, p):
        ''' expression : assignment_expression
        '''
        print("Inside p_expression_1:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 2:
            p[0] = p[1]

    def p_expression_2(self, p):
        ''' expression : expression COMMA assignment_expression
        '''
        print("Inside p_expression_2:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        if len(p) == 4:
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

    def p_iteration_statement_1(self, p):
        ''' iteration_statement : WHILE LPAREN expression RPAREN statement
        '''
        print("Inside p_iteration_statement:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 6:
        #     p[0] = (p[1], p[3], p[5])
        p[0] = (p[1], p[3], p[5])

    def p_iteration_statement_2(self, p):
        ''' iteration_statement : FOR LPAREN init_declarator SEMI expression_opt SEMI expression_opt RPAREN statement
        '''
        print("Inside p_iteration_statement:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 10:
        #     p[0] = (p[1], p[3], p[5], p[7], p[9])
        p[0] = (p[1], p[3], p[5], p[7], p[9])

    def p_iteration_statement_3(self, p):
        ''' iteration_statement : FOR LPAREN type_specifier init_declarator SEMI expression_opt SEMI expression_opt RPAREN statement
        '''
        print("Inside p_iteration_statement:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 11:
        #     p[0] = (p[1], p[3], p[4], p[6], p[8], p[10])
        p[0] = (p[1], p[3], p[4], p[6], p[8], p[10])

    def p_jump_statement_1(self, p):
        ''' jump_statement : BREAK SEMI
        '''
        print("Inside p_jump_statement:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 3:
        #     p[0] = (p[1])
        p[0] = p[1]

    def p_jump_statement_2(self, p):
        ''' jump_statement : RETURN expression SEMI
        '''
        print("Inside p_jump_statement:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 4:
        #     p[0] = (p[1], p[2])
        p[0] = (p[1], p[2])

    def p_jump_statement_3(self, p):
        ''' jump_statement : RETURN SEMI
        '''
        print("Inside p_jump_statement:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 3:
        #     p[0] = (p[1])
        p[0] = p[1]

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

    def p_assignment_expression_1(self, p):
        ''' assignment_expression : binary_expression
        '''
        print("Inside p_assignment_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 2:
        #     p[0] = p[1]
        p[0] = p[1]

    def p_assignment_expression_2(self, p):
        ''' assignment_expression : unary_expression assignment_operator assignment_expression
        '''
        print("Inside p_assignment_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 4:
        #     p[0] = Assignment(p[2], p[1], p[3])
        p[0] = (p[2], p[1], p[3])

    def p_binary_expression_1(self, p):
        ''' binary_expression : cast_expression
        '''
        print("Inside p_binary_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 2:
        #     if isinstance(p[1], Cast):
        #         p[0] = p[1]
        #     else:
        #         p[0] = p[1]
        p[0] = p[1]

    def p_binary_expression_2(self, p):
        ''' binary_expression : binary_expression TIMES binary_expression
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
        # if len(p) == 4:
        #     p[0] = BinaryOp(p[2], p[1], p[3])
        p[0] = (p[2], p[1], p[3])

    def p_unary_expression_1(self, p):
        ''' unary_expression : postfix_expression
        '''
        print("Inside p_unary_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 2:
        #     p[0] = p[1]
        p[0] = p[1]

    def p_unary_expression_2(self, p):
        ''' unary_expression : INCREASE unary_expression
                             | DECREASE unary_expression
                             | unary_operator cast_expression
        '''
        print("Inside p_unary_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 3:
        #     if isinstance(p[2], Cast):
        #         p[0] = p[2]
        #     else:
        #         p[0] = UnaryOp(p[1], p[2])
        p[0] = (p[1], p[2])

    def p_postfix_expression_1(self, p):
        ''' postfix_expression : primary_expression
        '''
        print("Inside p_postfix_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 2:
        #     p[0] = p[1]
        p[0] = p[1]

    def p_postfix_expression_2(self, p):
        ''' postfix_expression : postfix_expression INCREASE
                               | postfix_expression DECREASE
        '''
        print("Inside p_postfix_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 3:
        #     p[0] = (p[2], p[1])
        p[0] = (p[2], p[1])

    def p_postfix_expression_3(self, p):
        ''' postfix_expression : postfix_expression LBRACKET expression RBRACKET
                               | postfix_expression LPAREN argument_expression_opt RPAREN
        '''
        print("Inside p_postfix_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 5:
        #     p[0] = (p[1], p[3])
        p[0] = (p[1], p[2], p[3], p[4])

    def p_cast_expression_1(self, p):
        ''' cast_expression : unary_expression
        '''
        print("Inside p_cast_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 2:
        #     p[0] = p[1]
        p[0] = p[1]

    def p_cast_expression_2(self, p):
        ''' cast_expression : LPAREN type_specifier RPAREN cast_expression
        '''
        print("Inside p_cast_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 5:
        #     p[0] = Cast(p[1], p[2])
        p[0] = (p[2], p[4])

    def p_primary_expression_1(self, p):
        ''' primary_expression : ID
                               | constant
                               | STRING
        '''
        print("Inside p_primary_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 2:
        #     if isinstance(p[1], ID):
        #         p[0] = p[1]
        #     elif isinstance(p[1], Constant):
        #         p[0] = p[1]
        #     else:
        #         p[0] = Constant('string', p[1])
        p[0] = p[1]

    def p_primary_expression_2(self, p):
        ''' primary_expression : LPAREN expression RPAREN
        '''
        print("Inside p_primary_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 4:
        #     p[0] = p[2]
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

    def p_argument_expression_1(self, p):
        ''' argument_expression : assignment_expression
        '''
        print("Inside p_argument_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 2:
        #     p[0] = p[1]
        p[0] = p[1]

    def p_argument_expression_2(self, p):
        ''' argument_expression : argument_expression COMMA assignment_expression
        '''
        print("Inside p_argument_expression:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 4:
        #     p[0] = (p[1], p[3])
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

        if p.slice[1].type == 'INT_CONST':
            type = 'int'
        elif p.slice[1].type == 'FLOAT_CONST':
            type = 'float'
        elif p.slice[1].type == 'CHAR_CONST':
            type = 'char'

        # p[0] = Constant(type, p[1])
        p[0] = (type, p[1])

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

    def p_pointer_1(self, p):
        ''' pointer : TIMES pointer
        '''
        print("Inside p_pointer:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 3:
        #     p[0] = PtrDecl(p[2])
        p[0] = ('pointer', p[1])

    def p_pointer_2(self, p):
        ''' pointer : TIMES
        '''
        print("Inside p_pointer:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 3:
        #     p[0] = PtrDecl(p[2])
        p[0] = 'pointer'

    def p_direct_declarator_1(self, p):
        ''' direct_declarator : ID
        '''
        print("Inside p_direct_declarator:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 2:
        #     p[0] = p[1]
        p[0] = ('id', p[1])

    def p_direct_declarator_2(self, p):
        ''' direct_declarator : LPAREN declarator RPAREN
        '''
        print("Inside p_direct_declarator:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 4:
        #     p[0] = p[2]
        p[0] = p[2]

    def p_direct_declarator_3(self, p):
        ''' direct_declarator : direct_declarator LBRACKET constant_expression_opt RBRACKET
                              | direct_declarator LPAREN parameter_list RPAREN
                              | direct_declarator LPAREN id_list RPAREN
        '''
        print("Inside p_direct_declarator:")
        for i in range(len(p)):
            print("p[{0}] = {1}".format(i, p[i]))
        print('End')
        # if len(p) == 5:
        #     if p[2] == '[' and p[4] == ']':
        #         p[0] = ArrayDecl('type', p[3])
        #     else:
        #         p[0] = (p[1], p[3])
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
                # p[0] = ID(p[1])
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
        # p[0] = Type(p[1])
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
        result = parser.parse(code, tracking=True)
        # result = parser.parse("int a = 2;")
        result.show()


        return self
