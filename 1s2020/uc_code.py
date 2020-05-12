from uc_sema import *
from uc_ast import *


class GenerateCode(NodeVisitor):
    '''
    Node visitor class that creates 3-address encoded instruction sequences.
    '''
    def __init__(self):
        super(GenerateCode, self).__init__()

        # version dictionary for temporaries
        self.fname = 'main'  # We use the function name as a key
        self.versions = {self.fname:0}

        # The generated code (list of tuples)
        self.code = []

    def new_temp(self):
        '''
        Create a new temporary variable of a given scope (function name).
        '''
        if self.fname not in self.versions:
            self.versions[self.fname] = 0
        name = "%" + "%d" % (self.versions[self.fname])
        self.versions[self.fname] += 1
        return name

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        return getattr(self, method, self.generic_visit)(node)

    def generic_visit(self, node):
        #~ print('generic:', type(node))
        if node is None:
            return ''
        else:
            return ''.join(self.visit(c) for c_name, c in node.children())

    def visit_Constant(self, node):
        if node.rawtype == 'string':
            _target = self.new_text()
            inst = ('global_string'. _target, node.value)
            self.text.append(inst)
        else:
            _target = self.new_temp()
            inst = ('literal_' + node.rawtype, node.value, _target)
            self.code.append(inst)
        node.gen_location = _target

    def visit_ID(self, node):
        if node.gen_location is None:
            _type = node.bind
            while not isinstance(_type, VarDecl):
                _type = _type.type
            node.gen_location = _type.declname.gen_location

    def visit_Print(self, node):
        if node.expr is not None:
            for _expr in node.expr:
                self.visit(_expr)
                if isinstance(_expr, ID) or isinstance(_expr, ArrayRef):
                    self._loadLocation(_expr)
                inst = ('print_' + _expr.type.names[-1].typename, _expr.gen_location)
                self.code.append(inst)
        else:
            inst = ('print_void',)
            self.code.append(inst)

    def visit_Program(self, node):
        for _decl in node.gdecls:
            self.visit(_decl)

    def visit_Pragma(self, n):
        ret = '#pragma'
        if n.string:
            ret += ' ' + n.string
        return ret

    def visit_ArrayRef(self, node):
        _subs = node.subscript
        self.visit(_subs)
        if isinstance(_subs, ID) or isinstance(_subs, ArrayRef):
            self._loadLocation(_subs)
        _var = node.name.bind.type.declname.gen_location
        _index = _subs.gen_location
        _target = self.new_temp()
        node.gen_location = _target
        inst = ('elem_' + node.type.names[-1].typename, _var, _index, _target)
        self.code.append(inst)

    def visit_StructRef(self, n):
        sref = self._parenthesize_unless_simple(n.name)
        return sref + n.type + self.visit(n.field)

    def visit_FuncCall(self, node):
        if node.args is not None:
            if isinstance(node.args, ExprList):
                _tcode = []
                for _arg in node.args.exprs:
                    self.visit(_arg)
                    if isinstance(_arg, ID) or isinstance(_arg, ArrayRef):
                        self._loadLocation(_arg)
                    inst = ('param_' + _arg.type.names[-1].typename, _arg.gen_location)
                    _tcode.append(inst)
                for _inst in _tcode:
                    self.code.append(_inst)

            else:
                self.visit(node.args)
                if isinstance(node.args, ID) or isinstance(node.args, ArrayRef):
                    self._loadLocation(node.args)
                inst = ('param_' + node.args.type.names[-1].typename, node.args.gen_location)
                self.code.append(inst)

        node.gen_location = self.new_temp()
        self.visit(node.name)
        inst = ('call', node.name.name, node.gen_location)
        self.code.append(inst)


    def visit_UnaryOp(self, node):
        self.visit(node.expr)
        _source = node.expr.gen_location

        if node.op == '&':
            node.gen_location = node.expr.gen_location
        elif node.op == '*':
            node.gen_location = self.new_temp()
            inst = ('load_' + node.expr.type.names[-1].typename + '_*', node.expr.gen_location, node.gen_location)
            self.code.append(inst)
        else:
            if isinstance(node.expr, ID) or isinstance(node.expr, ArrayRef):
                self._loadLocation(node.expr)
            if node.op == '+':
                node.gen_location = node.expr.gen_location

            elif node.op == '-':
                _typename = node.expr.type.names[-1].typename
                opcode = self.unary_opcodes[node.op] + "_" + _typename
                _aux = self.new_temp()
                self.code.append(('literal_' + _typename, 0, _aux))
                node.gen_location = self.new_temp()
                inst = (opcode, _aux, node.expr.gen_location, node.gen_location)
                self.code.append(inst)

            elif node.op in ["++", "p++", "--", "p--"]:
                if node.op == "++" or node.op == "p++":
                    _val = 1
                else:
                    _val = -1
                _value = self.new_temp()
                self.code.append(('literal_int', _val, _value))
                opcode = self.unary_opcodes[node.op] + "_" + node.expr.type.names[-1].typename
                node.gen_location = self.new_temp()
                inst = (opcode, node.expr.gen_location, _value, node.gen_location)
                self.code.append(inst)
                opcode = 'store_' +  node.expr.type.names[-1].typename
                inst = (opcode, node.gen_location, _source)
                self.code.append(inst)
                if node.op in ["p++", "p--"]:
                    node.gen_location = node.expr.gen_location


    def visit_BinaryOp(self, node):
        self.visit(node.left)
        self.visit(node.right)

        if isinstance(node.left, ID) or isinstance(node.left, ArrayRef):
            self._loadLocation(node.left)
        if isinstance(node.right, ID) or isinstance(node.right, ArrayRef):
            self._loadLocation(node.right)

        target = self.new_temp()

        opcode = self.binary_opcodes[node.op] + "_" + node.left.type.names[-1].typename
        inst = (opcode, node.left.gen_location, node.right.gen_location, target)
        self.code.append(inst)

        node.gen_location = target


    def _readLocation(self, source):
        _typename = self.new_temp()
        _target = source.type.names[-1].typename
        self.code.append(('read_' + _typename, _target))
        self.code.append(('store_' + _typename, _target, source))

    def visit_Assert(self, node):
        _expr = node.expr
        self.visit(_expr)

        true_label = self.new_temp()
        false_label = self.new_temp()
        exit_label = self.new_temp()

        inst = ('cbranch', _expr.gen_location, true_label, false_label)
        self.code.append(inst)

        self.code.append((true_label[1:],))
        self.code.append(('jump', exit_label))
        self.code.append((false_label[1:],))

        _target = self.new_text()
        inst = ('global_string', _target, "assertion_fail on " + ) FALTA PREENCHER AQUI
        self.text.append(inst)

        inst = ('print_string', _target)
        self.code.append(inst)
        self.code.append(('jump', self.ret_label))

        self.code.append((exit_label[1:],))

    def visit_Assignment(self, node):
        self.visit(node.rvalue)
        if isinstance(node.rvalue, ID) or isinstance(node.rvalue, ArrayRef):
            self._loadLocation(node.rvalue)
        _lvar = node.lvalue
        self.visit(_lvar)
        if node.op in self.assign_opcodes:
            _lval = self.new_temp()
            _target = self.new_temp()
            _typename = _lvar.type.names[-1].typename
            if isinstance(node.rvalue, ArrayRef):
                _typename += '_*'
            inst = ('load_' + _typename, _lvar.gen_location, _lval)
            self.code.append(inst)
            inst = (self.assign_opcodes[node.op] + '_' + _lvar.type.names[-1].typename,
                    node.rvalue.gen_location, _lval, _target)
            self.code.append(inst)
            inst = ('store_' + _lvar.type.names[-1].typename, _target, _lvar.gen_location)
            self.code.append(inst)
        else:
            if isinstance(_lvar, ID) or isinstance(_lvar, ArrayRef):
                _typename = _lvar.type.names[-1].typename
                if isinstance(_lvar, ArrayRef):
                    _typename += '_*'
                elif _lvar.type.names[0] == PtrType:
                    if _lvar.kind == 'func':
                        _lvar.bind.type.gen_location = _lvar.gen_location
                    else:
                        _typename += '_*'
                inst = ('store_' + _typename, node.rvalue.gen_location, _lvar.gen_location)
                self.code.append(inst)
            else:
                _typename = _lvar.type.names[-1].typename
                inst = ('store' + _typename, node.rvalue.gen_location, _lvar.gen_location)
                self.code.append()


    def visit_IdentifierType(self, n):
        return ' '.join(n.names)

    def _visit_expr(self, n):
        if isinstance(n, c_ast.InitList):
            return '{' + self.visit(n) + '}'
        elif isinstance(n, c_ast.ExprList):
            return '(' + self.visit(n) + ')'
        else:
            return self.visit(n)

    def visit_Decl(self, node):
        _type = node.type
        _dim = ""
        if isinstance(_type, VarDecl):
            self.visit_VarDecl(_type, node, _dim)
        elif isinstance(_type, ArrayDecl):
            self.visit_ArrayDecl(_type, node, _dim)
        elif isinstance(_type, PrtDecl):
            self.visit_PtrDecl(_type, node, _dim)
        elif isinstance(_type, FuncDecl):
            self.visit_FuncDecl(_type)

    def visit_DeclList(self, node):
        for decl in node.decls:
            self.visit(decl)

    def visit_Typedef(self, n):
        s = ''
        if n.storage: s += ' '.join(n.storage) + ' '
        s += self._generate_type(n.type)
        return s

    def visit_Cast(self, node):
        self.visit(node.expr)
        if isinstance(node.expr, ID) or isinstance(node.expr, ArrayRef):
            self._loadLocation(node.expr)
        _temp = self.new_temp()
        if node.to_type.names[-1].typename == IntType.typename:
            inst = ('fptosi', node.expr.gen_location, _temp)
        else:
            inst = ('sitofp', node.expr.gen_location, _temp)
        self.code.append(inst)
        node.gen_location = _temp

    def visit_ExprList(self, node):
        pass

    def visit_InitList(self, node):
        node.value = []
        for _expr in node.exprs:
            if isinstance(_expr, InitList):
                self.visit(_expr)
            node.value.append(_expr.value)

    def visit_Enum(self, n):
        return self._generate_struct_union_enum(n, name='enum')

    def visit_Enumerator(self, n):
        if not n.value:
            return '{indent}{name},\n'.format(
                indent=self._make_indent(),
                name=n.name,
            )
        else:
            return '{indent}{name} = {value},\n'.format(
                indent=self._make_indent(),
                name=n.name,
                value=self.visit(n.value),
            )

    def visit_FuncDef(self, node):
        self.alloc_phase = None
        self.visit(node.decl)

        if node.param_decls is not None:
            for _par in node.param_decls:
                self.visit(_par)

        if node.body is not None:
            self.alloc_phase = 'var_decl'
            for _body in node.body:
                if isinstance(_body, Decl):
                    self.visit(_body)
            for _decl in node.decls:
                self.visit(_decl)

            self.alloc_phase = 'var_init'
            for _body in node.body:
                self.visit(_body)

        self.code.append((self.ret_label[1:],))
        if node.spec.names[-1].typename == 'void':
            self.code.append(('return_void',))
        else:
            _rvalue = self.new_temp()
            inst = ('load_' + node.spec.names[-1].typename. self.ret_location, _rvalue)
            self.code.append(inst)
            self.code.append(('return_' + node.spec.names[-1].typename, _rvalue))


    def visit_FileAST(self, n):
        s = ''
        for ext in n.ext:
            if isinstance(ext, c_ast.FuncDef):
                s += self.visit(ext)
            elif isinstance(ext, c_ast.Pragma):
                s += self.visit(ext) + '\n'
            else:
                s += self.visit(ext) + ';\n'
        return s

    def visit_Compound(self, node):
        for item in node.block_items:
            self.visit(item)

    def visit_CompoundLiteral(self, n):
        return '(' + self.visit(n.type) + '){' + self.visit(n.init) + '}'


    def visit_EmptyStatement(self, node):
        pass

    def visit_ParamList(self, node):
        for _par in node.params:
            self.visit(_par)

    def visit_Read(self, node):
        _target = self.new_temp()
        for _loc in node.names:
            self.visit(_loc)

            if isinstance(_loc, ID) or isinstance(_loc, ArrayRef):
                self._readLocation(_loc.type.names[-1].typename, _target, _loc.gen_location)

            elif isinstance(_loc, ExprList):
                for _var in _loc.exprs:
                    if isinstance(_var, ID) or isinstance(_var, ArrayRef):
                        self._readLocation(_var.type.names[-1].typename, _target, _var.gen_location)


    def visit_Return(self, node):
        if node.expr is not None:
            self.visit(node.expr)
            if isinstance(node.expr, ID) or isinstance(node.expr, ArrayRef):
                self._loadLocation(node.expr)
            inst = ('store_' + node.expr.type.names[-1].typename, node.expr.gen_location, self.ret_location)
            self.code.append(inst)

        self.code.append(('jump', self.ret_label))

    def visit_Break(self, node):
        self.code.append(('jump', node.bind.exit_label))

    def visit_Continue(self, n):
        return 'continue;'

    def visit_TernaryOp(self, n):
        s  = '(' + self._visit_expr(n.cond) + ') ? '
        s += '(' + self._visit_expr(n.iftrue) + ') : '
        s += '(' + self._visit_expr(n.iffalse) + ')'
        return s

    def visit_If(self, node):
        true_label = self.new_temp()
        false_label = self.new_temp()
        exit_label = self.new_temp()

        self.visit(node.cond)
        inst = ('cbranch', node.cond.gen_location, true_label, false_label)
        self.code.append(inst)

        self.code.append((true_label[1:], ))
        self.visit(node.iftrue)

        if node.iffalse is not None:
            self.code.append(('jump', exit_label))
            self.code.append((false_label[1:], ))
            self.visit(node.iffalse)
            self.code.append((exit_label[1:],))
        else:
            self.code.append((false_label[1:],))

    def visit_For(self, node):
        entry_label = self.new_temp()
        body_label = self.new_temp()
        exit_label = self.new_temp()
        node.exit_label = exit_label

        self.visit(node.init)
        self.code.append((entry_label[1:], ))

        self.visit(node.cond)
        inst = ('cbranch', node.cond.gen_location, body_label, exit_label)
        self.code.append(inst)

        self.code.append((body_label[1:], ))
        self.visit(node.stat)
        self.visit(node.next)
        self.code.append(('jump', entry_label))
        self.code.append((exit_label[1:], ))

    def visit_While(self, node):
        entry_label = self.new_temp()
        true_label = self.new_temp()
        exit_label = self.new_temp()
        node.exit_label = exit_label

        self.code.append((entry_label[1:], ))
        self.visit(node.cond)
        inst = ('cbranch', node.cond.gen_location, true_label, exit_label)
        self.code.append(inst)

        self.code.append((true_label[1:], ))
        if node.stmt is not None:
            self.visit(node.stmt)
        self.code.append(('jump', entry_label))
        self.code.append((exit_label[1:], ))


    def visit_Label(self, n):
        return n.name + ':\n' + self._generate_stmt(n.stmt)

    def visit_Goto(self, n):
        return 'goto ' + n.name + ';'

    def visit_EllipsisParam(self, n):
        return '...'

    def visit_Struct(self, n):
        return self._generate_struct_union_enum(n, 'struct')

    def visit_Type(self, node):
        pass

    def visit_Typename(self, n):
        return self._generate_type(n.type)

    def visit_Union(self, n):
        return self._generate_struct_union_enum(n, 'union')

    def visit_NamedInitializer(self, n):
        s = ''
        for name in n.name:
            if isinstance(name, c_ast.ID):
                s += '.' + name.name
            else:
                s += '[' + self.visit(name) + ']'
        s += ' = ' + self._visit_expr(n.expr)
        return s

    def visit_FuncDecl(self, node):
        self.fname = node.type.declname.name

        inst = ('define', self.fname)
        self.code.append(inst)
        node.type.declname.gen_location = self.fname

        if node.args is not None:
            self.clean()
            for _ in node.args.params:
                self.enqueue(self.new_temp())

        self.ret_location = self.new_temp()
        self.alloc_phase = 'arg_decl'
        if node.args is not None:
            for _arg in node.args:
                self.visit(_arg)

        self.ret_label = self.new_temp()

        self.alloc_phase = 'arg_init'
        if node.args is not None:
            for _arg in node.args:
                self.visit(_arg)

                
    def visit_ArrayDecl(self, node, decl, dim):
        _type = node
        dim += "_" + str(node.dim.value)
        while not isinstance(_type, VarDecl):
            _type = _type.type
            if isinstance(_type, ArrayDecl):
                dim += "_" + _type.dim.vale
            elif isinstance(_type, PtrDecl):
                dim += "_*"
        self.visit_VarDecl(_type, decl, dim)

    def visit_TypeDecl(self, n):
        return self._generate_type(n, emit_declname=False)

    def visit_PtrDecl(self, node, decl, dim):
        _type = node
        dim += "_*"
        while not isinstance(_type, VarDecl):
            _type = _type.type
            if isinstance(_type, PtrDecl):
                dim += "_*"
            elif isinstance(_type, ArrayDecl):
                dim += "_" + str(_type.dim.value)
        self.visit_VarDecl(_type, decl, dim)

    def visit_GlobalDecl(self, node):
        for _decl in node.decls:
            self.visit(_decl)

    def _globalLocation(self, node, decl, dim):
        _type = node.type.names[-1].typename
        if dim is not None:
            _type += dim
        _varname = "@" + node.declname.name
        if decl.init is None:
            self.text.append('global_' + _type, _varname)
        elif isinstance(decl.init, Constant):
            self.text.append(('global_' + _type, _varname, decl.init.value))
        elif isinstance(decl.init, InitList):
            self.visit(decl.init)
            self.text.append(('global_' + _type, _varname, decl.init.value))
        node.declname.gen_location = _varname

    def _loadLocation(self, node):
        _varname = self.new_temp()
        _typename = node.type.names[-1].typename
        if isinstance(node, ArrayRef):
            _typename += '_*'
        inst = ('load_' + _typename, node.gen_location, _varname)
        self.code.append(inst)
        node.gen_location = _varname

    def _storeLocation(self, typename, init, target):
        self.visit(init)
        inst = ('store_' + typename, init.gen_location, target)
        self.code.append(inst)

    def visit_VarDecl(self, node, decl, dim):
        if node.declname.scope == 1:
            self._globalLocation(node, decl, dim)
        else:
            _typename = node.type.names[-1].typename + dim
            if self.alloc_phase == 'arg_decl' or self.alloc_phase == 'var_decl':
                _varname = self.new_temp()
                inst = ('alloc_' + _typename, _varname)
                self.code.append(inst)
                node.declname.gen_location = _varname
                decl.name.gen_location = _varname
            elif self.alloc_phase == 'arg_init':
                inst = ('store_' + _typename, self.dequeue(), node.declname.gen_location)
                self.code.append(inst)
            elif self.alloc_phase == 'var_init':
                if decl.init is not None:
                    self._storeLocation(_typename, decl.init, node.declname.gen_location)


    def _generate_struct_union_enum(self, n, name):
        """ Generates code for structs, unions, and enums. name should be
            'struct', 'union', or 'enum'.
        """
        if name in ('struct', 'union'):
            members = n.decls
            body_function = self._generate_struct_union_body
        else:
            assert name == 'enum'
            members = None if n.values is None else n.values.enumerators
            body_function = self._generate_enum_body
        s = name + ' ' + (n.name or '')
        if members is not None:
            # None means no members
            # Empty sequence means an empty list of members
            s += '\n'
            s += self._make_indent()
            self.indent_level += 2
            s += '{\n'
            s += body_function(members)
            self.indent_level -= 2
            s += self._make_indent() + '}'
        return s

    def _generate_struct_union_body(self, members):
        return ''.join(self._generate_stmt(decl) for decl in members)

    def _generate_enum_body(self, members):
        # `[:-2] + '\n'` removes the final `,` from the enumerator list
        return ''.join(self.visit(value) for value in members)[:-2] + '\n'

    def _generate_stmt(self, n, add_indent=False):
        """ Generation from a statement node. This method exists as a wrapper
            for individual visit_* methods to handle different treatment of
            some statements in this context.
        """
        typ = type(n)
        if add_indent: self.indent_level += 2
        indent = self._make_indent()
        if add_indent: self.indent_level -= 2

        if typ in (
                c_ast.Decl, c_ast.Assignment, c_ast.Cast, c_ast.UnaryOp,
                c_ast.BinaryOp, c_ast.TernaryOp, c_ast.FuncCall, c_ast.ArrayRef,
                c_ast.StructRef, c_ast.Constant, c_ast.ID, c_ast.Typedef,
                c_ast.ExprList):
            # These can also appear in an expression context so no semicolon
            # is added to them automatically
            #
            return indent + self.visit(n) + ';\n'
        elif typ in (c_ast.Compound,):
            # No extra indentation required before the opening brace of a
            # compound - because it consists of multiple lines it has to
            # compute its own indentation.
            #
            return self.visit(n)
        else:
            return indent + self.visit(n) + '\n'

    def _generate_decl(self, n):
        """ Generation from a Decl node.
        """
        s = ''
        if n.funcspec: s = ' '.join(n.funcspec) + ' '
        if n.storage: s += ' '.join(n.storage) + ' '
        s += self._generate_type(n.type)
        return s

    def _generate_type(self, n, modifiers=[], emit_declname = True):
        """ Recursive generation from a type node. n is the type node.
            modifiers collects the PtrDecl, ArrayDecl and FuncDecl modifiers
            encountered on the way down to a TypeDecl, to allow proper
            generation from it.
        """
        typ = type(n)
        #~ print(n, modifiers)

        if typ == c_ast.TypeDecl:
            s = ''
            if n.quals: s += ' '.join(n.quals) + ' '
            s += self.visit(n.type)

            nstr = n.declname if n.declname and emit_declname else ''
            # Resolve modifiers.
            # Wrap in parens to distinguish pointer to array and pointer to
            # function syntax.
            #
            for i, modifier in enumerate(modifiers):
                if isinstance(modifier, c_ast.ArrayDecl):
                    if (i != 0 and
                        isinstance(modifiers[i - 1], c_ast.PtrDecl)):
                            nstr = '(' + nstr + ')'
                    nstr += '['
                    if modifier.dim_quals:
                        nstr += ' '.join(modifier.dim_quals) + ' '
                    nstr += self.visit(modifier.dim) + ']'
                elif isinstance(modifier, c_ast.FuncDecl):
                    if (i != 0 and
                        isinstance(modifiers[i - 1], c_ast.PtrDecl)):
                            nstr = '(' + nstr + ')'
                    nstr += '(' + self.visit(modifier.args) + ')'
                elif isinstance(modifier, c_ast.PtrDecl):
                    if modifier.quals:
                        nstr = '* %s%s' % (' '.join(modifier.quals),
                                           ' ' + nstr if nstr else '')
                    else:
                        nstr = '*' + nstr
            if nstr: s += ' ' + nstr
            return s
        elif typ == c_ast.Decl:
            return self._generate_decl(n.type)
        elif typ == c_ast.Typename:
            return self._generate_type(n.type, emit_declname = emit_declname)
        elif typ == c_ast.IdentifierType:
            return ' '.join(n.names) + ' '
        elif typ in (c_ast.ArrayDecl, c_ast.PtrDecl, c_ast.FuncDecl):
            return self._generate_type(n.type, modifiers + [n],
                                       emit_declname = emit_declname)
        else:
            return self.visit(n)

    def _parenthesize_if(self, n, condition):
        """ Visits 'n' and returns its string representation, parenthesized
            if the condition function applied to the node returns True.
        """
        s = self._visit_expr(n)
        if condition(n):
            return '(' + s + ')'
        else:
            return s

    def _parenthesize_unless_simple(self, n):
        """ Common use case for _parenthesize_if
        """
        return self._parenthesize_if(n, lambda d: not self._is_simple_node(d))

    def _is_simple_node(self, n):
        """ Returns True for nodes that are "simple" - i.e. nodes that always
            have higher precedence than operators.
        """
        return isinstance(n, (c_ast.Constant, c_ast.ID, c_ast.ArrayRef,
                              c_ast.StructRef, c_ast.FuncCall))