from uc_sema import *
from uc_ast2 import *
from uc_block2 import *


class GenerateCode(NodeVisitor):
    '''
    Node visitor class that creates 3-address encoded instruction sequences.
    '''

    def __init__(self, cfg):
        super(GenerateCode, self).__init__()

        self.cfg = cfg

        self.ftype = None
        self.fname = '_glob_'
        self.currentBlock = BasicBlock('global')
        self.currentScope = 0
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
        self.ret_block = None

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

    def changeCurrentBlock(self):
        newBlock = ConditionalBlock(None)
        newBlock.instructions = self.currentBlock.instructions
        newBlock.predecessors = self.currentBlock.predecessors
        newBlock.label = self.currentBlock.label
        for block in self.currentBlock.predecessors:
            if block.next_block == self.currentBlock:
                block.next_block = newBlock
            if isinstance(block, BasicBlock):
                if block.branch == self.currentBlock:
                    block.branch = newBlock
            elif isinstance(block, ConditionalBlock):
                if block.taken == self.currentBlock:
                    block.taken = newBlock
                if block.fall == self.currentBlock:
                    block.fall = newBlock
        self.currentBlock = newBlock

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
        print("Constant")

        if node.rawtype == 'string':
            _target = self.new_text()
            inst = ('global_string', _target, node.value)
            self.text.append(inst)
        else:
            _target = self.new_temp()
            inst = ('literal_' + node.rawtype, node.value, _target)
            self.code.append(inst)
            self.currentBlock.instructions.append(inst)
        node.gen_location = _target

    def visit_ID(self, node):
        print("ID")

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
        print("Print")

        if node.expr is not None:
            if isinstance(node.expr[0], ExprList):
                for _expr in node.expr[0].exprs:
                    self.visit(_expr)
                    if isinstance(_expr, ID) or isinstance(_expr, ArrayRef):
                        self._loadLocation(_expr)
                    elif isinstance(_expr, UnaryOp) and _expr.op == "*":
                        self._loadReference(_expr)
                    inst = ('print_' + _expr.type.names[-1].typename, _expr.gen_location)
                    # self.code.append(inst)
                    self.currentBlock.append(inst)
            else:
                _expr = node.expr[0]
                self.visit(_expr)
                if isinstance(_expr, ID) or isinstance(_expr,ArrayRef):
                    self._loadLocation(_expr)
                elif isinstance(_expr, UnaryOp) and _expr.op == "*":
                    self._loadReference(_expr)
                inst = ('print_' + _expr.type.names[-1].typename, _expr.gen_location)
                self.currentBlock.append(inst)

        else:
            inst = ('print_void',)
            # self.code.append(inst)
            self.currentBlock.append(inst)

    def visit_Program(self, node):
        print("Program")

        for _decl in node.gdecls:
            self.visit(_decl)

        self.code = self.text.copy()
        node.text = self.text.copy()

        for _decl in node.gdecls:
            if isinstance(_decl, FuncDef):
                block = EmitBlocks()
                block.visit(_decl.cfg)
                for _code in block.code:
                    self.code.append(_code)
                    # self.currentBlock.instructions.append(_code)

        if self.cfg:
            for _decl in node.gdecls:
                if isinstance(_decl, FuncDef):
                    _cfg = CFG(_decl.decl.name.name)
                    _cfg.view(_decl.cfg)

    def visit_ArrayRef(self, node):
        print("ArrayRef:")

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
            self.code.append(('mul_' + node.type.names[-1].typename, _dim.gen_location, _subs_b.gen_location, _target))
            self.currentBlock.instructions.append(('mul_' + node.type.names[-1].typename, _dim.gen_location, _subs_b.gen_location, _target))
            if isinstance(_subs_a, ID) or isinstance(_subs_a, ArrayRef):
                self._loadLocation(_subs_a)
            _index = self.new_temp()
            self.code.append(('add_' + node.type.names[-1].typename, _target, _subs_a.gen_location, _index))
            self.currentBlock.instructions.append(('add_' + node.type.names[-1].typename, _target, _subs_a.gen_location, _index))
            _var = node.name.name.bind.type.type.declname.gen_location
            node.gen_location = self.new_temp()
            self.code.append(('elem_' + node.type.names[-1].typename, _var, _index, node.gen_location))
            self.currentBlock.instructions.append(('elem_' + node.type.names[-1].typename, _var, _index, node.gen_location))

        else:
            if isinstance(_subs_a, ID) or isinstance(_subs_a, ArrayRef):
                self._loadLocation(_subs_a)
            _var = node.name.bind.type.declname.gen_location
            _index = _subs_a.gen_location
            _target = self.new_temp()
            node.gen_location = _target
            inst = ('elem_' + node.type.names[-1].typename, _var, _index, _target)
            self.code.append(inst)
            self.currentBlock.instructions.append(inst)

    def visit_FuncCall(self, node):
        print("FuncCall:")

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
                    # self.code.append(_inst)
                    self.currentBlock.append(_inst)

            else:
                self.visit(node.args)
                if isinstance(node.args, ID) or isinstance(node.args, ArrayRef):
                    self._loadLocation(node.args)
                inst = ('param_' + node.args.type.names[-1].typename, node.args.gen_location)
                # self.code.append(inst)
                self.currentBlock.append(inst)

        if isinstance(node.name.bind, PtrDecl):
            _target = self.new_temp()
            # self.code.append(('load_' + node.type.names[-1].typename + '_*', node.name.bind.type.gen_location, _target))
            self.currentBlock.append(('load_' + node.type.names[-1].typename + '_*', node.name.bind.type.gen_location, _target))
            node.gen_location = self.new_temp()
            # self.code.append(('call', _target, node.gen_location))
            self.currentBlock.instructions.append(('call', _target, node.gen_location))
        else:
            node.gen_location = self.new_temp()
            self.visit(node.name)
            inst = ('call', '@' + node.name.gen_location, node.gen_location)
            # self.code.append(inst)
            self.currentBlock.append(inst)

    def visit_UnaryOp(self, node):
        print("UnaryOp:")

        self.visit(node.expr)
        _source = node.expr.gen_location

        if node.op == '&' or node.op == '*':
            node.gen_location = node.expr.gen_location
        elif node.op == '!':
            if isinstance(node.expr, ID) or isinstance(node.expr, ArrayRef):
                self._loadLocation(node.expr)
            node.gen_location = self.new_temp()
            self.code.append(('not_bool', _source, node.gen_location))
            self.currentBlock.instructions.append(('not_bool', _source, node.gen_location))
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
                self.currentBlock.instructions.append(('literal_' + _typename, 0, _aux))
                node.gen_location = self.new_temp()
                inst = (opcode, _aux, node.expr.gen_location, node.gen_location)
                self.code.append(inst)
                self.currentBlock.instructions.append(inst)

            elif node.op in ["++", "p++", "--", "p--"]:
                if node.op == "++" or node.op == "p++":
                    _val = 1
                else:
                    _val = -1
                _value = self.new_temp()
                self.code.append(('literal_int', _val, _value))
                self.currentBlock.instructions.append(('literal_int', _val, _value))
                opcode = self.unary_opcodes[node.op] + "_" + node.expr.type.names[-1].typename
                node.gen_location = self.new_temp()
                inst = (opcode, node.expr.gen_location, _value, node.gen_location)
                self.code.append(inst)
                self.currentBlock.instructions.append(inst)
                opcode = 'store_' + node.expr.type.names[-1].typename
                inst = (opcode, node.gen_location, _source)
                self.code.append(inst)
                self.currentBlock.instructions.append(inst)
                if node.op in ["p++", "p--"]:
                    node.gen_location = node.expr.gen_location

    def visit_BinaryOp(self, node):
        print("BinaryOp:")

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

        opcode = self.binary_opcodes[node.op] + "_" + node.left.type.names[-1].typename
        inst = (opcode, node.left.gen_location, node.right.gen_location, target)
        self.code.append(inst)
        self.currentBlock.instructions.append(inst)

        node.gen_location = target

    def _storeLocation(self, typename, init, target, operation):
        self.visit(init)
        if isinstance(init, ID) or isinstance(init, ArrayRef):
            self._loadLocation(init)
        elif isinstance(init, UnaryOp) and init.op == "*":
            self._loadReference(init)
        inst = (operation + typename, init.gen_location, target)
        self.currentBlock.append(inst)

    def _loadReference(self, node):
        node.gen_location = self.new_temp()
        inst = ('load_' + node.expr.type.names[-1].typename + "_*",
                node.expr.gen_location, node.gen_location)
        # self.code.append(inst)
        self.currentBlock.append(inst)

    def _readLocation(self, source):
        # _target = self.new_temp()
        _typename = source.type.names[-1].typename
        # self.code.append(('read_' + _typename, _target))
        # self.currentBlock.instructions.append(('read_' + _typename, _target))
        if isinstance(source, ArrayRef):
            _typename += "_*"
        if isinstance(source, UnaryOp) and source.op == "*":
            self._loadReference(source)
        # self.code.append(('store_' + _typename, _target, source.gen_location))
        # self.currentBlock.instructions.append(('store_' + _typename, _target, source.gen_location))
        self.currentBlock.append(('read_' + _typename, source.gen_location))

    def visit_Assert(self, node):
        print("Assert:")

        _expr = node.expr
        self.visit(_expr)

        self.changeCurrentBlock()

        true_label = self.new_temp()
        false_label = self.new_temp()

        trueBlock = BasicBlock(true_label)
        falseBlock = BasicBlock(false_label)
        trueBlock.predecessors = self.currentBlock
        falseBlock.predecessors = self.currentBlock

        inst = ('cbranch', _expr.gen_location, trueBlock.label, falseBlock.label)
        self.code.append(inst)
        self.currentBlock.instructions.append(inst)
        self.currentBlock.taken = trueBlock
        self.currentBlock.fall = falseBlock

        self.currentBlock.next_block = falseBlock
        self.currentBlock = falseBlock
        _target = self.new_text()
        _tempExp = _expr.coord.split('@')
        _tempCoord = _tempExp[1].split(':')
        inst = ('global_string', _target, "assertion_fail on " + f"{_tempCoord[0]}:{_tempCoord[1]}")
        self.text.append(inst)
        self.currentBlock.instructions.append(('print_str', _target))
        self.currentBlock.instructions.append(('jump', self.ret_block.label))
        self.currentBlock.next_block = self.ret_block
        self.currentBlock.branch = self.ret_block
        self.ret_block.predecessors.add(self.currentBlock)

        self.currentBlock = trueBlock

    def visit_Assignment(self, node):
        print("Assignment:")

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
            _typename = _lvar.type.names[-1].typename
            if isinstance(node.rvalue, ArrayRef):
                _typename += "_*"
            inst = ('load_' + _typename, _lvar.gen_location, _lval)
            self.code.append(inst)
            self.currentBlock.instructions.append(inst)
            inst = (self.assign_opcodes[node.op] + '_' + _lvar.type.names[-1].typename,
                    node.rvalue.gen_location, _lval, _target)
            self.code.append(inst)
            self.currentBlock.instructions.append(inst)
            inst = ('store_' + _lvar.type.names[-1].typename, _target, _lvar.gen_location)
            self.code.append(inst)
            self.currentBlock.instructions.append(inst)
        else:
            if isinstance(_lvar, ID) or isinstance(_lvar, ArrayRef):
                _typename = _lvar.type.names[-1].typename
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
                    self.currentBlock.instructions.append(inst)
                    return
                inst = ('store_' + _typename, node.rvalue.gen_location, _lvar.gen_location)
                self.currentBlock.instructions.append(inst)
                self.code.append(inst)
            else:
                _typename = _lvar.type.names[-1].typename
                if isinstance(_lvar, UnaryOp):
                    if _lvar.op == '*':
                        _typename += '_*'
                    inst = ('store_' + _typename, node.rvalue.gen_location, _lvar.gen_location)
                    self.code.append(inst)
                    self.currentBlock.instructions.append(inst)

    def visit_Decl(self, node):
        print("Decl:")

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
        print("DeclList:")

        for decl in node.decls:
            self.visit(decl)

    def visit_Cast(self, node):
        print("Cast:")

        self.visit(node.expr)
        if isinstance(node.expr, ID) or isinstance(node.expr, ArrayRef):
            self._loadLocation(node.expr)
        _temp = self.new_temp()
        if node.to_type.names[-1].typename == IntType.typename:
            inst = ('fptosi', node.expr.gen_location, _temp)
        else:
            inst = ('sitofp', node.expr.gen_location, _temp)
        self.code.append(inst)
        self.currentBlock.instructions.append(inst)
        node.gen_location = _temp

    def visit_ExprList(self, node):
        pass

    def visit_InitList(self, node):
        print("InitList:")

        node.value = []
        for _expr in node.exprs:
            if isinstance(_expr, InitList):
                self.visit(_expr)
            node.value.append(_expr.value)

    def visit_FuncDef(self, node):
        print("FuncDef:")

        self.ftype = node.spec.names[-1].typename
        self.fname = node.decl.name.name
        _funcName = self.fname
        _funcType = self.ftype

        self.ret_label = '%exit_' + _funcName
        self.ret_block = BasicBlock(self.ret_label)

        # self.currentBlock = BasicBlock('define_' + _funcName)
        node.cfg = self.currentBlock

        self.alloc_phase = None
        self.visit(node.decl)

        if node.body is not None:
            self.alloc_phase = "var_decl"
            for _body in node.body:
                if isinstance(_body, Decl):
                    self.visit(_body)
            for _decl in node.decls:
                self.visit(_decl)

        if node.decl.type.args is not None:
            self.alloc_phase = 'arg_init'
            for _arg in node.decl.type.args:
                self.visit(_arg)

        if _funcType == 'void':
            self.code.append(('return_void',))
            self.ret_block.append(('return_void',))
            # self.currentBlock.append(('return_void',))
        else:
            _rvalue = self.new_temp()
            inst = ('load_' + node.spec.names[-1].typename, self.ret_location, _rvalue)
            # self.code.append(inst)
            self.currentBlock.append(inst)
            # self.code.append(('return_' + node.spec.names[-1].typename, _rvalue))
            self.ret_block.append(('return_' + node.spec.names[-1].typename, _rvalue))

        if node.body is not None:
            self.alloc_phase = 'var_init'
            for _body in node.body:
               self.visit(_body)


    def visit_Compound(self, node):
        print("Compound:")

        for item in node.block_items:
            self.visit(item)

    def visit_EmptyStatement(self, node):
        pass

    def visit_ParamList(self, node):
        print("ParamList:")

        for _par in node.params:
            self.visit(_par)

    def visit_Read(self, node):
        print("Read:")

        for _loc in node.names:
            self.visit(_loc)

            if isinstance(_loc, ID) or isinstance(_loc, ArrayRef):
                self._readLocation(_loc)
            elif isinstance(_loc, UnaryOp) and _loc.op == "*":
                self._readLocation(_loc)
            elif isinstance(_loc, ExprList):
                for _var in _loc.exprs:
                    self.visit(_var)
                    self._readLocation(_var)

    def visit_Return(self, node):
        print("Return:")

        # if node.expr is not None:
        #     self.visit(node.expr)
        #     if isinstance(node.expr, ID) or isinstance(node.expr, ArrayRef):
        #         self._loadLocation(node.expr)
        #     inst = ('store_' + node.expr.type.names[-1].typename, node.expr.gen_location, self.ret_location)
        #     self.currentBlock.instructions.append(inst)
            # self.code.append(inst)

        # if self.currentBlock.generateJump():
        self.currentBlock.append(('jump', self.ret_block.label))
        self.currentBlock.branch = self.ret_block
        self.currentBlock.next_block = self.ret_block
        self.ret_block.predecessors.add(self.currentBlock)
        self.currentBlock = self.ret_block

    def visit_Break(self, node):
        print("Break:")

        self.code.append(('jump', node.bind.exit_label))
        self.currentBlock.instructions.append(('jump', node.bind.exit_label))

    def visit_If(self, node):
        print("If:")

        true_label = self.new_temp()
        else_label = self.new_temp()
        exit_label = self.new_temp()

        self.changeCurrentBlock()
        self.visit(node.cond)

        trueBlock = BasicBlock('%if.then_' + true_label)
        exitBlock = BasicBlock('%if.end_' + exit_label)
        _dump_exitBlock = False

        if node.iffalse:
            falseBlock = BasicBlock('%if.else_' + else_label)
        else:
            lbl = '%if.else_'
            _dump_exitBlock = True
            falseBlock = exitBlock

        trueBlock.predecessors.add(self.currentBlock)
        falseBlock.predecessors.add(self.currentBlock)
        self.currentBlock.taken = trueBlock
        self.currentBlock.fall = falseBlock

        inst = ('cbranch', node.cond.gen_location, trueBlock.label, falseBlock.label)
        # self.code.append(inst)
        self.currentBlock.append(inst)

        self.currentBlock.next_block = trueBlock
        self.currentBlock = trueBlock

        self.visit(node.iftrue)

        if self.currentBlock.generateJump():
            self.currentBlock.append(('jump', exitBlock.label))
            self.currentBlock.branch = exitBlock
            exitBlock.predecessors.add(self.currentBlock)
            _dump_exitBlock = True

        if node.iffalse is not None:
            self.currentBlock.next_block = falseBlock
            self.currentBlock = falseBlock
            # self.code.append(('jump', exit_label))
            # self.code.append((false_label[1:],))
            self.visit(node.iffalse)
            if self.currentBlock.generateJump():
                self.currentBlock.append(('jump', exitBlock.label))
                self.currentBlock.branch = exitBlock
                exitBlock.predecessors.add(self.currentBlock)
                _dump_exitBlock = True
            # self.code.append((exit_label[1:],))
        if _dump_exitBlock:
            self.currentBlock.next_block = exitBlock
            self.currentBlock = exitBlock
        # else:
        #     self.code.append((false_label[1:],))
        # self.currentBlock.next_block = exitBlock
        # self.currentBlock = exitBlock

    def visit_For(self, node):
        print("For:")

        self.visit(node.init)

        increase_label = self.new_temp()
        body_label = self.new_temp()
        exit_label = self.new_temp()
        cond_label = self.new_temp()

        increaseBlock = BasicBlock(increase_label)
        conditionBlock = ConditionalBlock(cond_label)
        bodyBlock = BasicBlock(body_label)
        exitBlock = BasicBlock(exit_label)

        node.exit_label = exitBlock
        self.currentBlock.append(('jump', cond_label))
        # self.code.append((entry_label[1:],))

        self.currentBlock.next_block = conditionBlock
        self.currentBlock.branch = conditionBlock
        conditionBlock.predecessors.add(self.currentBlock)
        self.currentBlock = conditionBlock
        self.visit(node.cond)
        inst = ('cbranch', node.cond.gen_location, bodyBlock.label, exitBlock.label)
        # self.code.append(inst)
        self.currentBlock.append(inst)

        self.currentBlock.next_block = bodyBlock
        self.currentBlock.taken = bodyBlock
        self.currentBlock.fall = exitBlock
        bodyBlock.predecessors.add(self.currentBlock)
        exitBlock.predecessors.add(self.currentBlock)
        self.currentBlock = bodyBlock

        # self.code.append((body_label[1:],))
        self.visit(node.stmt)
        if len(self.currentBlock.instructions) > 0 and self.currentBlock.instructions[-1][0] != 'jump':
            self.currentBlock.instructions.append(('jump', increaseBlock.label))
            self.currentBlock.branch = increaseBlock
            increaseBlock.predecessors.add(self.currentBlock)

        self.currentBlock.next_block = increaseBlock
        self.currentBlock = increaseBlock
        self.visit(node.next)
        if len(self.currentBlock.instructions) > 0 and  self.currentBlock.instructions[-1][0] != 'jump':
            self.currentBlock.instructions.append(('jump', conditionBlock.label))
            self.currentBlock.branch = conditionBlock
            conditionBlock.predecessors.add(self.currentBlock)

        self.currentBlock.next_block = exitBlock
        exitBlock.predecessors.add(self.currentBlock)
        self.currentBlock = exitBlock
        # self.code.append(('jump', entry_label))
        # self.code.append((exit_label[1:],))

    def visit_While(self, node):
        print("While:")

        while_label = self.new_temp()
        body_label = self.new_temp()
        exit_label = self.new_temp()

        whileBlock = ConditionalBlock(while_label)
        bodyBlock = BasicBlock(body_label)
        exitBlock = BasicBlock(exit_label)

        # self.currentBlock.next_block = whileBlock

        node.exit_label = exitBlock
        self.currentBlock.append(('jump', whileBlock.label))
        self.currentBlock.next_block = whileBlock
        self.currentBlock.branch = whileBlock
        whileBlock.predecessors.add(self.currentBlock)

        self.currentBlock = whileBlock
        self.visit(node.cond)
        inst = ('cbranch', node.cond.gen_location, bodyBlock.label, exitBlock.label)
        # self.code.append(inst)
        self.currentBlock.append(inst)
        self.currentBlock.taken = bodyBlock
        self.currentBlock.fall = exitBlock
        exitBlock.predecessors.add(self.currentBlock)

        # self.code.append((true_label[1:],))
        self.currentBlock.next_block = bodyBlock
        bodyBlock.predecessors.add(self.currentBlock)
        self.currentBlock = bodyBlock

        if node.stmt is not None:
            self.visit(node.stmt)
        if self.currentBlock.generateJump():
            self.currentBlock.instructions.append(('jump', whileBlock.label))
            self.currentBlock.branch = whileBlock
            whileBlock.predecessors.add(self.currentBlock)

        self.currentBlock.next_block = exitBlock
        exitBlock.predecessors.add(self.currentBlock)
        self.currentBlock = exitBlock


    def visit_Type(self, node):
        pass

    def visit_FuncDecl(self, node):
        print("FuncDecl:")

        _args = []

        if node.args is not None:
            self.clean()
            for _param in node.args.params:
                # self.enqueue(self.new_temp())
                _loc = self.new_temp()
                self.enqueue(_loc)
                _args.append((self.getTypeName(_param.type), _loc))

        # self.currentBlock.instructions.append(('define_' + self.ftype, '@ ' + self.fname, _args))
        node.type.declname.gen_location = self.fname

        funcBlock = BasicBlock('define_' + self.ftype + ' ' + self.fname)
        self.currentBlock.next_block = funcBlock
        self.currentBlock.branch = funcBlock
        funcBlock.predecessors.add(self.currentBlock)
        self.currentBlock = funcBlock

        if self.ftype != 'void':
            # self.ret_location = self.new_temp()
            self.ret_location = '@' + self.fname + '_return'
            self.currentBlock.instructions.append(('alloc_' + self.ftype, self.ret_location))

        self.alloc_phase = 'arg_decl'
        if node.args is not None:
            for _arg in node.args:
                self.visit(_arg)

    def visit_ArrayDecl(self, node, decl, dim):
        print("ArrayDecl:")

        _type = node
        dim += "_" + str(node.dim.value)
        while not isinstance(_type, VarDecl):
            _type = _type.type
            if isinstance(_type, ArrayDecl):
                dim += "_" + str(_type.dim.value)
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
        print("GlobalDecl:")

        for _decl in node.decls:
            if not isinstance(_decl.type, FuncDecl):
                self.visit(_decl)

    def _globalLocation(self, node, decl, dim):
        _type = node.type.names[-1].typename
        if dim is not None:
            _type += dim
        _varname = "@" + node.declname.name
        if decl.init is None:
            self.text.append(('global_' + _type, _varname))
            self.currentBlock.instructions.append(('global_' + _type, _varname))
        elif isinstance(decl.init, Constant):
            self.text.append(('global_' + _type, _varname, decl.init.value))
            self.currentBlock.instructions.append(('global_' + _type, _varname, decl.init.value))
        elif isinstance(decl.init, InitList):
            self.visit(decl.init)
            self.text.append(('global_' + _type, _varname, decl.init.value))
            self.currentBlock.instructions.append(('global_' + _type, _varname, decl.init.value))
        node.declname.gen_location = _varname

    def _loadLocation(self, node):
        _varname = self.new_temp()
        _typename = node.type.names[-1].typename
        if isinstance(node, ArrayRef):
            _typename += '_*'
        elif isinstance(node.bind, ArrayDecl):
            _typename += '_' + str(node.bind.dim.value)
        inst = ('load_' + _typename, node.gen_location, _varname)
        self.code.append(inst)
        self.currentBlock.instructions.append(inst)
        node.gen_location = _varname

    def _storeLocation(self, typename, init, target):
        self.visit(init)
        if isinstance(init, ID) or isinstance(init, ArrayRef):
            self._loadLocation(init)
        elif isinstance(init, UnaryOp) and init.op == '*':
            self._loadReference(init)
        inst = ('store_' + typename, init.gen_location, target)
        self.code.append(inst)
        self.currentBlock.instructions.append(inst)

    def visit_VarDecl(self, node, decl, dim):
        print("VarDecl:")

        if node.declname.scope == 1:
            self._globalLocation(node, decl, dim)
        else:
            _typename = node.type.names[-1].typename + dim
            if self.alloc_phase == 'arg_decl' or self.alloc_phase == 'var_decl':
                _varname = ''
                if node.declname.kind == 'var':
                    _varname = '@' + node.declname.name
                else:
                    _varname = self.new_temp()
                inst = ('alloc_' + _typename, _varname)
                self.code.append(inst)
                self.currentBlock.instructions.append(inst)
                node.declname.gen_location = _varname
                decl.name.gen_location = _varname
            elif self.alloc_phase == 'arg_init':
                inst = ('store_' + _typename, self.dequeue(), node.declname.gen_location)
                self.code.append(inst)
                self.currentBlock.instructions.append(inst)
            elif self.alloc_phase == 'var_init':
                if decl.init is not None:
                    self._storeLocation(_typename, decl.init, node.declname.gen_location)
