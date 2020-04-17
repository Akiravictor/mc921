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
        last_cr = p.lexer.lexdata.rfind('\n', 0, p.lexpos(token_idx))
        if last_cr < 0:
            last_cr = -1
        column = (p.lexpos(token_idx) - (last_cr))
        return Coord(p.lineno(token_idx), column).__str__()

    def _type_modify_decl(self, decl, modifier):
        print("Inside _type_modify_decl:")
        print(decl)
        print('End')
        modifier_head = modifier
        modifier_tail = modifier

        while modifier_tail.type:
            modifier_tail = modifier_tail.type

        if isinstance(decl, VarDecl):
            modifier_tail.type = decl
            return modifier
        else:
            decl_tail = decl

            while not isinstance(decl_tail.type, VarDecl):
                decl_tail = decl_tail.type

            modifier_tail.type = decl_tail.type
            decl_tail.type = modifier_head
            return decl



    def p_error(self, p):
        if p:
            print("Error near the symbol %s" % p.value)
        else:
            print("Error at the end of input")

    def _build_function_definition(self, spec, decl, param_decls, body):
        print("Inside _build_function_definition:")
        print(spec)
        print(decl)
        print(param_decls)
        print(body)
        print('End')
        declaration = self._build_declarations(spec=spec, decls=[dict(decl=decl, init=None)])[0]

        return FuncDef(spec=spec, decl=declaration, param_decls=param_decls, body=body, coord=decl.coord)

    def _build_declarations(self, spec, decls):
        print("Inside _build_declarations:")
        for decl in decls:
            print(decl)
        print(spec)
        print('End')
        declarations = []

        for decl in decls:
            print(decl)
            assert decl['decl'] is not None
            declaration = Decl(name=None, type=decl['decl'], init=decl.get('init'), coord=decl.get('coord'))

            if isinstance(declaration.type, Type):
                fixed_decl = declaration
            else:
                fixed_decl = self._fix_decl_name_type(declaration, spec)

            declarations.append(fixed_decl)

        return declarations

    def _fix_decl_name_type(self, decl, typename):
        print("Inside _fix_decl_name_type:")
        print(decl)
        print("typename")
        print(typename)
        print('End')
        type = decl
        while not isinstance(type, VarDecl):
            print("no while")
            print(type)
            type = type.type

        decl.name = type.declname
        type.type = typename
        print("after while")
        print(decl)
        print('End')
        return decl


    def p_program(self, p):
        ''' program : global_declaration_list
        '''
        if self.debug:
            print("Inside p_program:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = Program(p[1])

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_global_declaration_list(self, p):
        ''' global_declaration_list : global_declaration
                                    | global_declaration_list global_declaration
        '''
        if self.debug:
            print("Inside p_global_declaration_list:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        if len(p) == 2:
            p[0] = DeclList([p[1]])
        else:
            p[0] = DeclList([p[1]]+[p[2]])

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_global_declaration_1(self, p):
        ''' global_declaration : function_definition
        '''
        if self.debug:
            print("Inside p_global_declaration:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_global_declaration_2(self, p):
        ''' global_declaration : declaration
        '''
        if self.debug:
            print("Inside p_global_declaration:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = GlobalDecl(p[1])

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_block_item_list_opt(self, p):
        ''' block_item_list_opt : block_item_list
                                | empty
        '''
        if self.debug:
            print("Inside p_block_item_list_opt:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_block_item_list(self, p):
        ''' block_item_list : block_item
                            | block_item_list block_item
        '''
        if self.debug:
            print("Inside p_block_item_list:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        if len(p) == 2 or p[2] == [None]:
            p[0] = p[1]
        else:
            p[0] = p[1] + p[2]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_block_item(self, p):
        ''' block_item : statement
                       | declaration
        '''
        if self.debug:
            print("Inside p_block_item:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        if isinstance(p[1], list):
            p[0] = p[1]
        else:
            p[0] = [p[1]]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_function_definition_1(self, p):
        ''' function_definition : type_specifier declarator declaration_list_opt compound_statement
        '''
        if self.debug:
            print("Inside p_function_definition_1:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = self._build_function_definition(spec=p[1], decl=p[2], param_decls=p[3], body=p[4])

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_function_definition_2(self, p):
        ''' function_definition : declarator declaration_list_opt compound_statement
        '''
        if self.debug:
            print("Inside p_function_definition_2:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = self._build_function_definition(spec=dict(type=[Type(['void'], coord=self._token_coord(p, 1))], function=[]),
                                               decl=p[1], param_decls=p[2], body=p[3])

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_init_declarator_list_opt(self, p):
        ''' init_declarator_list_opt : init_declarator_list
                                     | empty
        '''
        if self.debug:
            print("Inside p_init_declarator_list_opt:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_init_declarator_list_1(self, p):
        ''' init_declarator_list : init_declarator
        '''
        if self.debug:
            print("Inside p_init_declarator_list_1:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = [p[1]]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_init_declarator_list_2(self, p):
        ''' init_declarator_list : init_declarator_list COMMA init_declarator
        '''
        if self.debug:
            print("Inside p_init_declarator_list_2:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = p[1] + [p[3]]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_init_declarator(self, p):
        ''' init_declarator : declarator
                            | declarator EQUALS initializer
        '''
        if self.debug:
            print("Inside p_init_declarator:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        if len(p) == 2:
            p[0] = dict(decl=p[1], init=None)
        else:
            p[0] = dict(decl=p[1], init=p[3])

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')


    def p_initializer_1(self, p):
        ''' initializer : assignment_expression
        '''
        if self.debug:
            print("Inside p_initializer:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_initializer_2(self, p):
        ''' initializer : LBRACE initializer_list RBRACE
                        | LBRACE initializer_list COMMA RBRACE
        '''
        if self.debug:
            print("Inside p_initializer:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        if p[2] is None:
            p[0] = InitList([], self._token_coord(p, 1))
        else:
            p[0] = p[2]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_initializer_list_1(self, p):
        ''' initializer_list : initializer
        '''
        if self.debug:
            print("Inside p_initializer_list:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        if len(p) == 2:
            p[0] = InitList([p[1]], p[1].coord)

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_initializer_list_2(self, p):
        ''' initializer_list : initializer_list COMMA initializer
        '''
        if self.debug:
            print("Inside p_initializer_list:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[1].exprs.append(p[3])
        p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_declaration(self, p):
        ''' declaration :  decl_body SEMI
        '''
        if self.debug:
            print("Inside p_declaration:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_decl_body(self, p):
        ''' decl_body : type_specifier init_declarator_list_opt
        '''
        if self.debug:
            print("Inside p_decl_body:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        spec = p[1]
        if p[2] is not None:
            decls = self._build_declarations(spec=spec, decls=p[2])
        p[0] = decls

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_declaration_list_opt(self, p):
        ''' declaration_list_opt : declaration_list
                                 | empty
        '''
        if self.debug:
            print("Inside p_declaration_list_opt:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_declaration_list(self, p):
        ''' declaration_list : declaration
                            | declaration_list declaration
        '''
        if self.debug:
            print("Inside p_declaration_list:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        if len(p) == 2:
            p[0] = DeclList(p[1])
        else:
            p[0] = DeclList(p[1]+p[2])

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_declarator(self, p):
        ''' declarator : pointer direct_declarator
                       | direct_declarator
        '''
        if self.debug:
            print("Inside p_declarator:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = self._type_modify_decl(decl=p[2], modifier=p[1])

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_parameter_list_1(self, p):
        ''' parameter_list : parameter_declaration
        '''
        if self.debug:
            print("Inside p_parameter_list_1:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = ParamList([p[1]], coord=self._token_coord(p, 1))

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_parameter_list_2(self, p):
        ''' parameter_list : parameter_list COMMA parameter_declaration
        '''
        if self.debug:
            print("Inside p_parameter_list_2:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[1].params.append(p[3])
        p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_parameter_declaration(self, p):
        ''' parameter_declaration : type_specifier declarator
        '''
        if self.debug:
            print("Inside p_parameter_declaration:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        spec = p[1]

        p[0] = self._build_declarations(spec=spec, decls=[dict(decl=p[2])])[0]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_compound_statement(self, p):
        ''' compound_statement : LBRACE block_item_list_opt RBRACE
        '''
        if self.debug:
            print("Inside p_compound_statement:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = Compound(block_items=p[2], coord=self._token_coord(p, 1))

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_expression_statement(self, p):
        ''' expression_statement : expression_opt SEMI
        '''
        if self.debug:
            print("Inside p_expression_statement:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        if p[1] is None:
            p[0] = EmptyStatement(self._token_coord(p, 2))
        else:
            p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_expression_opt(self, p):
        ''' expression_opt : expression
                           | empty
        '''
        if self.debug:
            print("Inside p_expression_opt:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_expression_1(self, p):
        ''' expression : assignment_expression
        '''
        if self.debug:
            print("Inside p_expression_1:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        if len(p) == 2:
            p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_expression_2(self, p):
        ''' expression : expression COMMA assignment_expression
        '''
        if self.debug:
            print("Inside p_expression_2:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        if not isinstance(p[1], ExprList):
            p[1] = ExprList([p[1]], p[1].coord)

        p[1].exprs.append(p[3])
        p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_selection_statement(self, p):
        ''' selection_statement : IF LPAREN expression RPAREN statement
                                | IF LPAREN expression RPAREN statement ELSE statement
        '''
        if self.debug:
            print("Inside p_selection_statement:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        if len(p) == 6:
            p[0] = If(p[3], p[5], None, self._token_coord(p, 1))
        elif len(p) == 8:
            p[0] = If(p[3], p[5], p[7], self._token_coord(p, 1))

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_iteration_statement_1(self, p):
        ''' iteration_statement : WHILE LPAREN expression RPAREN statement
        '''
        if self.debug:
            print("Inside p_iteration_statement:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = While(p[3], p[5], self._token_coord(p, 1))

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_iteration_statement_2(self, p):
        ''' iteration_statement : FOR LPAREN expression_opt SEMI expression_opt SEMI expression_opt RPAREN statement
        '''
        if self.debug:
            print("Inside p_iteration_statement:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = For(p[3], p[5], p[7], p[9], self._token_coord(p, 1))

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_iteration_statement_3(self, p):
        ''' iteration_statement : FOR LPAREN declaration expression_opt SEMI expression_opt RPAREN statement
        '''
        if self.debug:
            print("Inside p_iteration_statement:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = For(DeclList(p[3], self._token_coord(p, 1)), p[4], p[6], p[8], self._token_coord(p, 1))

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_jump_statement_1(self, p):
        ''' jump_statement : BREAK SEMI
        '''
        if self.debug:
            print("Inside p_jump_statement:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = Break(self._token_coord(p, 1))

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_jump_statement_2(self, p):
        ''' jump_statement : RETURN expression SEMI
        '''
        if self.debug:
            print("Inside p_jump_statement:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = Return(p[2], self._token_coord(p, 1))

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_jump_statement_3(self, p):
        ''' jump_statement : RETURN SEMI
        '''
        if self.debug:
            print("Inside p_jump_statement:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = Return(None, self._token_coord(p, 1))

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_assert_statement(self, p):
        ''' assert_statement : ASSERT expression SEMI
        '''
        if self.debug:
            print("Inside p_assert_statement:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = Assert(p[2], self._token_coord(p, 1))

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_print_statement(self, p):
        ''' print_statement : PRINT LPAREN expression_opt RPAREN SEMI
        '''
        if self.debug:
            print("Inside p_print_statement:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        exprs = None
        if len(p) == 6:
            exprs = [p[3]]
        p[0] = Print(exprs, self._token_coord(p, 1))

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_read_statement(self, p):
        ''' read_statement : READ LPAREN argument_expression_list RPAREN SEMI
        '''
        if self.debug:
            print("Inside p_read_statement:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = Read([p[3]], self._token_coord(p, 1))

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

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
        if self.debug:
            print("Inside p_statement:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_assignment_expression_1(self, p):
        ''' assignment_expression : binary_expression
        '''
        if self.debug:
            print("Inside p_assignment_expression:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_assignment_expression_2(self, p):
        ''' assignment_expression : unary_expression assignment_operator assignment_expression
        '''
        if self.debug:
            print("Inside p_assignment_expression:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = Assignment(p[2], p[1], p[3], p[1].coord)

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_binary_expression_1(self, p):
        ''' binary_expression : cast_expression
        '''
        if self.debug:
            print("Inside p_binary_expression:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

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
        if self.debug:
            print("Inside p_binary_expression:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_unary_expression_1(self, p):
        ''' unary_expression : postfix_expression
        '''
        if self.debug:
            print("Inside p_unary_expression:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_unary_expression_2(self, p):
        ''' unary_expression : INCREASE unary_expression
                             | DECREASE unary_expression
                             | unary_operator cast_expression
        '''
        if self.debug:
            print("Inside p_unary_expression:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = UnaryOp(p[1], p[2], p[2].coord)

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_postfix_expression_1(self, p):
        ''' postfix_expression : primary_expression
        '''
        if self.debug:
            print("Inside p_postfix_expression:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_postfix_expression_2(self, p):
        ''' postfix_expression : postfix_expression INCREASE
                               | postfix_expression DECREASE
        '''
        if self.debug:
            print("Inside p_postfix_expression:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = UnaryOp('p' + p[2], p[1], p[1].coord)

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_postfix_expression_3(self, p):
        ''' postfix_expression : postfix_expression LBRACKET expression RBRACKET
        '''
        if self.debug:
            print("Inside p_postfix_expression:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = ArrayRef(p[1], p[3], p[1].coord)

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_postfix_expression_4(self, p):
        ''' postfix_expression : postfix_expression LPAREN argument_expression_opt RPAREN
        '''
        if self.debug:
            print("Inside p_postfix_expression:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = FuncCall(p[1], p[3], p[1].coord)

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_cast_expression_1(self, p):
        ''' cast_expression : unary_expression
        '''
        if self.debug:
            print("Inside p_cast_expression:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_cast_expression_2(self, p):
        ''' cast_expression : LPAREN type_specifier RPAREN cast_expression
        '''
        if self.debug:
            print("Inside p_cast_expression:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = Cast(p[2], p[4], self._token_coord(p, 1))

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_string_literal(self, p):
        ''' string_literal : STRING
        '''
        if self.debug:
            print("Inside p_constant:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = Constant('string', p[1], self._token_coord(p, 1))

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_primary_expression_1(self, p):
        ''' primary_expression : identifier
                               | constant
                               | string_literal
        '''
        if self.debug:
            print("Inside p_primary_expression:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_primary_expression_2(self, p):
        ''' primary_expression : LPAREN expression RPAREN
        '''
        if self.debug:
            print("Inside p_primary_expression:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = p[2]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_argument_expression_opt(self, p):
        ''' argument_expression_opt : argument_expression_list
                                    | empty
        '''
        if self.debug:
            print("Inside p_argument_expression_opt:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        if p[1] is not None:
            p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_argument_expression_list(self, p):
        ''' argument_expression_list : assignment_expression
                                     | argument_expression_list COMMA assignment_expression
        '''
        if self.debug:
            print("Inside p_argument_expression_list:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        if len(p) == 2:
            p[0] = p[1]
        else:
            if not isinstance(p[1], ExprList):
                p[1] = ExprList([p[1]], p[1].coord)

            p[1].exprs.append(p[3])
            p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_constant_expression_opt(self, p):
        ''' constant_expression_opt : constant_expression
                                    | empty
        '''
        if self.debug:
            print("Inside p_constant_expression_opt:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_constant_expression(self, p):
        ''' constant_expression : binary_expression
        '''
        if self.debug:
            print("Inside p_constant_expression:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_assignment_operator(self, p):
        ''' assignment_operator : EQUALS
                               | EQTIMES
                               | EQDIV
                               | EQMOD
                               | EQPLUS
                               | EQMINUS
        '''
        if self.debug:
            print("Inside p_assignment_operator:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_unary_operator(self, p):
        ''' unary_operator : ADDRESS
                           | TIMES
                           | PLUS
                           | UMINUS
                           | NOT
        '''
        if self.debug:
            print("Inside p_unary_operator:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_constant_1(self, p):
        ''' constant : INT_CONST
        '''
        if self.debug:
            print("Inside p_constant:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = Constant('int', p[1], self._token_coord(p, 1))

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_constant_2(self, p):
        ''' constant : FLOAT_CONST
        '''
        if self.debug:
            print("Inside p_constant:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = Constant('float', p[1], self._token_coord(p, 1))

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_constant_3(self, p):
        ''' constant : CHAR_CONST
        '''
        if self.debug:
            print("Inside p_constant:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = Constant('char', p[1], self._token_coord(p, 1))

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_pointer_1(self, p):
        ''' pointer : TIMES pointer
        '''
        if self.debug:
            print("Inside p_pointer:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        tail_type = p[3]
        while tail_type.type is not None:
            tail_type = tail_type.type
        tail_type.type = PtrDecl(type=None, coord=self._token_coord(p, 1))
        p[0] = p[2]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_pointer_2(self, p):
        ''' pointer : TIMES
        '''
        if self.debug:
            print("Inside p_pointer:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = PtrDecl(type=None, coord=self._token_coord(p, 1))

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_direct_declarator_1(self, p):
        ''' direct_declarator : identifier
        '''
        if self.debug:
            print("Inside p_direct_declarator_1:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = VarDecl(p[1], type=None, coord=self._token_coord(p, 1))

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_direct_declarator_2(self, p):
        ''' direct_declarator : LPAREN declarator RPAREN
        '''
        if self.debug:
            print("Inside p_direct_declarator_2:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = p[2]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_direct_declarator_3(self, p):
        ''' direct_declarator : direct_declarator LPAREN parameter_list RPAREN
        '''
        if self.debug:
            print("Inside p_direct_declarator_3:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        func = FuncDecl(args=p[3], type=None, coord=p[1].coord)

        p[0] = self._type_modify_decl(decl=p[1], modifier=func)

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_direct_declarator_4(self, p):
        ''' direct_declarator : direct_declarator LBRACKET constant_expression_opt RBRACKET
        '''
        if self.debug:
            print("Inside p_direct_declarator_4:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        arr = ArrayDecl(type=None, dim=p[3], coord=p[1].coord)
        p[0] = self._type_modify_decl(decl=p[1], modifier=arr)

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_direct_declarator_5(self, p):
        ''' direct_declarator : direct_declarator LPAREN id_list_opt RPAREN
        '''
        if self.debug:
            print("Inside p_direct_declarator_5:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        func = FuncDecl(args=p[3], type=None, coord=p[1].coord)
        p[0] = self._type_modify_decl(decl=p[1], modifier=func)

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_id_list_opt(self, p):
        ''' id_list_opt : id_list
                        | empty
        '''
        if self.debug:
            print("Inside p_id_list_opt:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()
        p[0] = p[1]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_id_list(self, p):
        ''' id_list : identifier
                    | id_list identifier
        '''
        if self.debug:
            print("Inside p_id_list:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_identifier(self, p):
        ''' identifier : ID
        '''
        if self.debug:
            print("Inside p_identifier:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = ID(p[1], coord=self._token_coord(p, 1))

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_type_specifier(self, p):
        ''' type_specifier : VOID
                           | INT
                           | FLOAT
                           | CHAR
        '''
        if self.debug:
            print("Inside p_type_specifier:")
            for i in range(len(p)):
                print("p[{0}] = {1}".format(i, p[i]))
            print()

        p[0] = Type([p[1]], coord=self._token_coord(p, 1))

        if self.debug:
            print("p[0] = {0}".format(p[0]))
            print('End')

    def p_empty(self, p):
        ''' empty :'''
        # print("Inside p_empty:")
        # for i in range(len(p)):
        #     print("p[{0}] = {1}".format(i, p[i]))
        # print('End')
        pass

    def parse(self, code, filename='', debug=0):
        # self.debug = debug

        if debug:
            print("Code: {0}".format(code))
            print("Filename: {0}".format(filename))

        self.debug = True

        print("I'm on parser! :D")

        self.lexer = UCLexer(self.print_error)
        self.lexer.build()
        # lexer.input(code)

        self.tokens = self.lexer.tokens
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