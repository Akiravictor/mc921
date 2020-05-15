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
        self.versions = {self.fname: 0}

        # The generated code (list of tuples)
        self.text = []
        self.code = []

        self.binary_opcodes = {"+": "add", "-": "sub", "*": "mul", "/": "div", "%": "mod",
                               "==": "eq", "!=": "ne", "<": "lt", ">": "gt", "<=": "le", ">=": "ge", "&&": "and",
                               "||": "or"}
        self.unary_opcodes = {"-": "sub", "+": "", "--": "sub", "++": "add", "p--": "sub", "p++": "add", "!": "not",
                              "*": "", "&": ""}
        self.assign_opcodes = {"+=": "add", "-=": "sub", "*=": "mul", "/=": "div", "%=": "mod"}

        self.alloc_phase = None

        self.items = []

        self.ret_location = None
        self.ret_label = None

    def clean(self):
        self.items = []

    def enqueue(self, item):
        self.items.insert(0, item)

    def dequeue(self):
        return self.items.pop()

    def new_temp(self):
        '''
        Create a new temporary variable of a given scope (function name).
        '''
        if self.fname not in self.versions:
            self.versions[self.fname] = 0
        name = "%" + "%d" % (self.versions[self.fname])
        self.versions[self.fname] += 1
        return name

    def new_text(self):
        name = "@.str." + "%d" % (self.versions['_glob_'])
        self.versions['_glob_'] += 1
        return name

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        return getattr(self, method, self.generic_visit)(node)

    def generic_visit(self, node):
        # ~ print('generic:', type(node))
        if node is None:
            return ''
        else:
            return ''.join(self.visit(c) for c_name, c in node.children())

    def visit_Constant(self, node):
        if node.rawtype == 'string':
            _target = self.new_text()
            inst = ('global_string'._target, node.value)
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
            if _type.declname.gen_location is None:
                if node.kind == 'func' and node.scope == 1:
                    node.gen_location = '@' + node.name
            else:
                node.gen_location = _type.declname.gen_location

    def visit_Print(self, node):
        if node.expr is not None:
            if isinstance(node.expr[0], ExprList):
                for _expr in node.expr[0].exprs:
                    self.visit(_expr)
                    if isinstance(_expr, ID) or isinstance(_expr, ArrayRef):
                        self._loadLocation(_expr)
                    inst = ('print_' + _expr.type.names[-1], _expr.gen_location)
                    self.code.append(inst)
        else:
            inst = ('print_void',)
            self.code.append(inst)

    def visit_Program(self, node):
        for _decl in node.gdecls:
            self.visit(_decl)

    def visit_ArrayRef(self, node):
        _subs_a = node.subscript
        self.visit(_subs_a)
        if isinstance(node.name, ArrayRef):
            _subs_b = node.name.subscript
            self.visit(_subs_b)
            _dim = node.name.name.bind.type.dim
            self.visit(_dim)
            if isinstance(_subs_b, ID) or isinstance(_subs_b, ArrayRef):
                self._loadLocation(_subs_b)
            _target = self.new_temp()
            self.code.append(('mul_' + node.type.names[-1], _dim.gen_location,
                              _subs_b.gen_location, _target))
            if isinstance(_subs_a, ID) or isinstance(_subs_a, ArrayRef):
                self._loadLocation(_subs_a)
            _index = self.new_temp()
            self.code.append(('add_' + node.type.names[-1], _target,
                              _subs_a.gen_location, _index))
            _var = node.name.name.bind.type.type.declname.gen_location
            node.gen_location = self.new_temp()
            self.code.append(('elem_' + node.type.names[-1], _var, _index,
                              node.gen_location))

        else:
            if isinstance(_subs_a, ID) or isinstance(_subs_a, ArrayRef):
                self._loadLocation(_subs_a)
            _var = node.name.bind.type.declname.gen_location
            _index = _subs_a.gen_location
            _target = self.new_temp()
            node.gen_location = _target
            inst = ('elem_' + node.type.names[-1], _var, _index, _target)
            self.code.append(inst)

    def visit_FuncCall(self, node):
        if node.args is not None:
            if isinstance(node.args, ExprList):
                _tcode = []
                for _arg in node.args.exprs:
                    self.visit(_arg)
                    if isinstance(_arg, ID) or isinstance(_arg, ArrayRef):
                        self._loadLocation(_arg)
                    inst = ('param_' + _arg.type.names[-1], _arg.gen_location)
                    _tcode.append(inst)
                for _inst in _tcode:
                    self.code.append(_inst)

            else:
                self.visit(node.args)
                if isinstance(node.args, ID) or isinstance(node.args, ArrayRef):
                    self._loadLocation(node.args)
                inst = ('param_' + node.args.type.names[-1], node.args.gen_location)
                self.code.append(inst)

        if isinstance(node.name.bind, PtrDecl):
            _target = self.new_temp()
            self.code.append(('load_' + node.type.names[-1] + '_*',
                              node.name.bind.type.gen_location, _target))
            node.gen_location = self.new_temp()
            self.code.append(('call', _target, node.gen_location))
        else:
            node.gen_location = self.new_temp()
            self.visit(node.name)
            inst = ('call', node.name.name, node.gen_location)
            self.code.append(inst)

    def visit_UnaryOp(self, node):
        self.visit(node.expr)
        _source = node.expr.gen_location

        if node.op == '&' or node.op == '*':
            node.gen_location = node.expr.gen_location
        elif node.op == '!':
            if isinstance(node.expr, ID) or isinstance(node.expr, ArrayRef):
                self._loadLocation(node.expr)
            node.gen_location = self.new_temp()
            self.code.append(('not_bool', _source, node.gen_location))
        else:
            if isinstance(node.expr, ID) or isinstance(node.expr, ArrayRef):
                self._loadLocation(node.expr)
            if node.op == '+':
                node.gen_location = node.expr.gen_location

            elif node.op == '-':
                _typename = node.expr.type.names[-1]
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
                opcode = self.unary_opcodes[node.op] + "_" + node.expr.type.names[-1]
                node.gen_location = self.new_temp()
                inst = (opcode, node.expr.gen_location, _value, node.gen_location)
                self.code.append(inst)
                opcode = 'store_' + node.expr.type.names[-1]
                inst = (opcode, node.gen_location, _source)
                self.code.append(inst)
                if node.op in ["p++", "p--"]:
                    node.gen_location = node.expr.gen_location

    def visit_BinaryOp(self, node):
        self.visit(node.left)
        self.visit(node.right)

        if isinstance(node.left, ID) or isinstance(node.left, ArrayRef):
            self._loadLocation(node.left)
        elif isinstance(node.left, UnaryOp) and node.left.op == '*':
            self._loadReference(node.left)

        if isinstance(node.right, ID) or isinstance(node.right, ArrayRef):
            self._loadLocation(node.right)
        elif isinstance(node.right, UnaryOp) and node.right.op == '*':
            self._loadReference(node.right)

        target = self.new_temp()

        opcode = self.binary_opcodes[node.op] + "_" + node.left.type.names[-1]
        inst = (opcode, node.left.gen_location, node.right.gen_location, target)
        self.code.append(inst)

        node.gen_location = target

    def _loadReference(self, node):
        node.gen_location = self.new_temp()
        inst = ('load_' + node.expr.type.names[-1] + "_*",
                node.expr.gen_location, node.gen_location)
        self.code.append(inst)

    def _readLocation(self, source):
        _typename = self.new_temp()
        _target = source.type.names[-1]
        self.code.append(('read_' + _typename, _target))
        if isinstance(source, ArrayRef):
            _typename += "_*"
        if isinstance(source, UnaryOp) and source.op == "*":
            self._loadReference(source)
        self.code.append(('store_' + _typename, _target, source.gen_location))

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
        inst = ('global_string', _target, "assertion_fail on " + f"{_expr.coord.line}:{_expr.coord.column}")
        self.text.append(inst)

        inst = ('print_string', _target)
        self.code.append(inst)
        self.code.append(('jump', self.ret_label))

        self.code.append((exit_label[1:],))

    def visit_Assignment(self, node):
        _rval = node.rvalue
        self.visit(_rval)
        if isinstance(_rval, ID) or isinstance(_rval, ArrayRef):
            self._loadLocation(_rval)
        elif isinstance(_rval, UnaryOp) and _rval.op == "*":
            self._loadReference(_rval)
        _lvar = node.lvalue
        self.visit(_lvar)
        if node.op in self.assign_opcodes:
            _lval = self.new_temp()
            _target = self.new_temp()
            _typename = _lvar.type.names[-1]
            if isinstance(node.rvalue, ArrayRef):
                _typename += "_*"
            inst = ('load_' + _typename, _lvar.gen_location, _lval)
            self.code.append(inst)
            inst = (self.assign_opcodes[node.op] + '_' + _lvar.type.names[-1],
                    node.rvalue.gen_location, _lval, _target)
            self.code.append(inst)
            inst = ('store_' + _lvar.type.names[-1], _target, _lvar.gen_location)
            self.code.append(inst)
        else:
            if isinstance(_lvar, ID) or isinstance(_lvar, ArrayRef):
                _typename = _lvar.type.names[-1]
                if isinstance(_lvar, ArrayRef):
                    _typename += '_*'
                elif isinstance(_lvar.bind, ArrayDecl):
                    _typename += '_' + str(_lvar.bind.dim.value)
                elif _lvar.type.names[0] == PtrType:
                    if _lvar.kind == 'func':
                        _lvar.bind.type.gen_location = _lvar.gen_location
                    _typename += '_*'
                    inst = ('get_' + _typename, node.rvalue.gen_location, _lvar.gen_location)
                    self.code.append(inst)
                    return
                inst = ('store_' + _typename, node.rvalue.gen_location, _lvar.gen_location)
                self.code.append(inst)
            else:
                _typename = _lvar.type.names[-1]
                if isinstance(_lvar, UnaryOp):
                    if _lvar.op == '*':
                        _typename += '_*'
                    inst = ('store_' + _typename, node.rvalue.gen_location, _lvar.gen_location)
                    self.code.append(inst)


    def visit_Decl(self, node):
        _type = node.type
        _dim = ""
        if isinstance(_type, VarDecl):
            self.visit_VarDecl(_type, node, _dim)
        elif isinstance(_type, ArrayDecl):
            self.visit_ArrayDecl(_type, node, _dim)
        elif isinstance(_type, PtrDecl):
            self.visit_PtrDecl(_type, node, _dim)
        elif isinstance(_type, FuncDecl):
            self.visit_FuncDecl(_type)

    def visit_DeclList(self, node):
        for decl in node.decls:
            self.visit(decl)

    def visit_Cast(self, node):
        self.visit(node.expr)
        if isinstance(node.expr, ID) or isinstance(node.expr, ArrayRef):
            self._loadLocation(node.expr)
        _temp = self.new_temp()
        if node.to_type.names[-1] == IntType.typename:
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
        if node.spec.names[-1] == 'void':
            self.code.append(('return_void',))
        else:
            _rvalue = self.new_temp()
            inst = ('load_' + node.spec.names[-1].self.ret_location, _rvalue)
            self.code.append(inst)
            self.code.append(('return_' + node.spec.names[-1], _rvalue))

    def visit_Compound(self, node):
        for item in node.block_items:
            self.visit(item)

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
                self._readLocation(_loc.type.names[-1])

            elif isinstance(_loc, ExprList):
                for _var in _loc.exprs:
                    if isinstance(_var, ID) or isinstance(_var, ArrayRef):
                        self._readLocation(_var.type.names[-1])

    def visit_Return(self, node):
        if node.expr is not None:
            self.visit(node.expr)
            if isinstance(node.expr, ID) or isinstance(node.expr, ArrayRef):
                self._loadLocation(node.expr)
            inst = ('store_' + node.expr.type.names[-1], node.expr.gen_location, self.ret_location)
            self.code.append(inst)

        self.code.append(('jump', self.ret_label))

    def visit_Break(self, node):
        self.code.append(('jump', node.bind.exit_label))

    def visit_If(self, node):
        true_label = self.new_temp()
        false_label = self.new_temp()
        exit_label = self.new_temp()

        self.visit(node.cond)
        inst = ('cbranch', node.cond.gen_location, true_label, false_label)
        self.code.append(inst)

        self.code.append((true_label[1:],))
        self.visit(node.iftrue)

        if node.iffalse is not None:
            self.code.append(('jump', exit_label))
            self.code.append((false_label[1:],))
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
        self.code.append((entry_label[1:],))

        self.visit(node.cond)
        inst = ('cbranch', node.cond.gen_location, body_label, exit_label)
        self.code.append(inst)

        self.code.append((body_label[1:],))
        self.visit(node.stat)
        self.visit(node.next)
        self.code.append(('jump', entry_label))
        self.code.append((exit_label[1:],))

    def visit_While(self, node):
        entry_label = self.new_temp()
        true_label = self.new_temp()
        exit_label = self.new_temp()
        node.exit_label = exit_label

        self.code.append((entry_label[1:],))
        self.visit(node.cond)
        inst = ('cbranch', node.cond.gen_location, true_label, exit_label)
        self.code.append(inst)

        self.code.append((true_label[1:],))
        if node.stmt is not None:
            self.visit(node.stmt)
        self.code.append(('jump', entry_label))
        self.code.append((exit_label[1:],))

    def visit_Type(self, node):
        pass

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
            if not isinstance(_decl.type, FuncDecl):
                self.visit(_decl)

    def _globalLocation(self, node, decl, dim):
        _type = node.type.names[-1]
        if dim is not None:
            _type += dim
        _varname = "@" + node.declname.name
        if decl.init is None:
            self.text.append(('global_' + _type, _varname))
        elif isinstance(decl.init, Constant):
            self.text.append(('global_' + _type, _varname, decl.init.value))
        elif isinstance(decl.init, InitList):
            self.visit(decl.init)
            self.text.append(('global_' + _type, _varname, decl.init.value))
        node.declname.gen_location = _varname

    def _loadLocation(self, node):
        _varname = self.new_temp()
        _typename = node.type.names[-1]
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
            _typename = node.type.names[-1] + dim
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
