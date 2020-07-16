from ast import NodeVisitor

from llvmlite import ir, binding
from ctypes import CFUNCTYPE, c_int
from uc_ast2 import *
from uc_block2 import *

int_ty = ir.IntType(32)
i64_ty = ir.IntType(64)
float_ty = ir.DoubleType()
char_ty = ir.IntType(8)
bool_ty = ir.IntType(1)
void_ty = ir.VoidType()

intptr_ty = int_ty.as_pointer()
floatptr_ty = float_ty.as_pointer()
charptr_ty = char_ty.as_pointer()
voidptr_ty = char_ty.as_pointer()

llvm_type = {'int': int_ty,
             'int_*': intptr_ty,
             'float': float_ty,
             'float_*': floatptr_ty,
             'char': char_ty,
             'char_*': charptr_ty,
             'void': void_ty,
             'void_*': voidptr_ty,
             'string': charptr_ty}

llvm_false = ir.Constant(bool_ty, False)
llvm_true = ir.Constant(bool_ty, True)


def get_align(ltype, width):
    if isinstance(ltype, ir.IntType):
        return ltype.width // 8
    elif isinstance(ltype, ir.DoubleType) or isinstance(ltype, ir.PointerType):
        return 8
    elif isinstance(ltype, ir.ArrayType):
        _align = get_align(ltype.element, 1)
        if width < 4:
            width = 1
        else:
            width = 4
        return _align * width


def make_bytearray(buf):
    b = bytearray(buf)
    n = len(b)
    return ir.Constant(ir.ArrayType(char_ty, n), b)


class LLVMFunctionVisitor(BlockVisitor):

    def __init__(self, module):
        self.module = module
        self.func = None
        self.builder = None
        self.phase = None
        self.loc = {}
        self.code = []
        self.params = []
        self.ret_register = None

    def _extract_operation(self, inst):
        _modifier = {}
        _ctype = None
        _aux = inst.split('_')
        _opcode = _aux[0]
        if _opcode not in {'fptosi', 'sitofp', 'jump', 'cbranch', 'define'}:
            _ctype = _aux[1]
            for i, _val in enumerate(_aux[2:]):
                if _val.isdigit():
                    _modifier['dim' + str(i)] = _val
                elif _val == '*':
                    _modifier['prt' + str(i)] = _val
        return _opcode, _ctype, _modifier

    def _get_loc(self, target):
        try:
            if target[0] == '%':
                return self.loc[target]
            elif target[0] == '@':
                return self.module.get_global(target[1:])
        except KeyError:
            return None

    def _global_constant(selfself, builder_or_module, name, value, linkage='internal'):

        if isinstance(builder_or_module, ir.Module):
            mod = builder_or_module
        else:
            mod = builder_or_module.module
        data = ir.GlobalVariable(mod, value.type, name=name)
        data.linkage = linkage
        data.global_constant = True
        data.initializer = value
        data.align = 1
        return data

    def _new_function(self, inst):
        _op, _name, _args = inst
        try:
            self.func = self.module.get_global(_name[1:])
        except KeyError:
            _ctype = _op.split('_')[1]
            _sig = [llvm_type[arg] for arg in [item[0] for item in _args]]
            funty = ir.FunctionType(llvm_type[_ctype], _sig)
            self.func = ir.Function(self.module, funty, name=_name[1:])
        for _idx, _reg in enumerate([item[1] for item in _args]):
            self.loc[_reg] = self.func.args[_idx]

    def _cio(self, fname, format, *target):
        mod = self.builder.module
        fmt_bytes = make_bytearray((format + '\00').encode('ascii'))
        global_fmt = self._global_constant(mod, mod.get_unique_name('.fmt'), fmt_bytes)
        fn = mod.get_global(fname)
        ptr_fmt = self.builder.bitcast(global_fmt, charptr_ty)
        return self.builder.call(fn, [ptr_fmt] + list(target))

    def _build_alloc(self, ctype, target):
        _type = llvm_type[ctype]
        _location = self.builder.alloca(_type, name=target[1:])
        _location.align = get_align(_type, 1)
        self.loc[target] = _location

    def _build_alloc_(self, ctype, target, **kwargs):
        _type = llvm_type[ctype]
        _width = 1
        for arg in reversed(list(kwargs.values())):
            if arg.isdigit():
                _width *= int(arg)
                _type = ir.ArrayType(_type, int(arg))
            else:
                _type = ir.PointerType(_type)
        _location = self.builder.alloca(_type, name=target[1:])
        _location.align = get_align(_type, _width)
        self.loc[target] = _location

    def _build_call(self, ret_type, name, target):
        if name == '%':
            _loc = self.builder.call(self._get_loc(name), self.params)
        else:
            try:
                _fn = self.builder.module.get_global(name[1:])
            except KeyError:
                _type = llvm_type[ret_type]
                _sig = [arg.type for arg in self.params]
                funty = ir.FunctionType(_type, _sig)
                _fn = ir.Function(self.module, funty, name=name[1:])
            _loc = self.builder.call(_fn, self.params)
        self.loc[target] = _loc
        self.params = []

    def _build_elem(self, ctype, source, index, target):
        _source = self._get_loc(source)
        _index = self._get_loc(index)
        _base = ir.Constant(_index.type, 0)
        if isinstance(_source.type.pointee.element, ir.ArrayType):
            col = _source.type.pointee.element.count
            if isinstance(_index, ir.Constant):
                _i = ir.Constant(int_ty, _index.constant // col)
                _j = ir.Constant(int_ty, _index.constant % col)
            else:
                _col = ir.Constant(int_ty, col)
                _i = self.builder.sdiv(_index, _col)
                _j = self.builder.srem(_index, _col)
            _aux = self.builder.gep(_source, [_base, _i])
            _loc = self.builder.gep(_aux, [_base, _j])
        else:
            _loc = self.builder.gep(_source, [_base, _index])
        self.loc[target] = _loc

    def _build_get(self, ctype, source, target):
        pass

    def _build_get_(self, ctype, source, target, **kwargs):
        _source = self._get_loc(source)
        _target = self._get_loc(target)
        _align = get_align(llvm_type[ctype].as_pointer(), 1)
        self.builder.store(_source, _target, align=_align)

    def _build_literal(self, var_type, cte, target):
        _val = llvm_type[var_type](cte)
        _loc = self._get_loc(target)
        if _loc:
            self.builder.store(_val, _loc)
        else:
            self.loc[target] = _val

    def _build_load(self, ctype, source, target):
        _source = self._get_loc(source)
        if isinstance(_source, ir.Constant):
            self.loc[target] = _source
        else:
            _align = get_align(llvm_type[ctype], 1)
            _loc = self.builder.load(_source, align=_align)
            self.loc[target] = _loc

    def _build_load_(self, ctype, source, target, **kwargs):
        _source = self._get_loc(source)
        _type = llvm_type[ctype]
        _pointee = _source.type.pointee
        if isinstance(_pointee, ir.PointerType):
            if isinstance(_pointee.pointee, ir.FunctionType):
                _loc = self.builder.load(_source, align=8)
            else:
                _type = llvm_type[ctype].as_pointer()
                _align = get_align(_type, 1)
                _aux = self.builder.load(_source, align=_align)
                _type = llvm_type[ctype]
                _align = get_align(_type, 1)
                _loc = self.builder.load(_aux, align=_align)
        else:
            _align = get_align(_type, 1)
            _loc = self.builder.load(_source, align=8)
        self.loc[target] = _loc

    def _build_param(self, par_type, source):
        self.params.append(self._get_loc(source))

    def _build_print(self, val_type, target):
        if target:
            _value = self._get_loc(target)
            if val_type == 'int':
                self._cio('printf', '%d', _value)
            elif val_type == 'float':
                self._cio('printf', '%.2f', _value)
            elif val_type == 'char':
                self._cio('printf', '%c', _value)
            elif val_type == 'string':
                self._cio('printf', '%s', _value)
        else:
            self._cio('printf', '\n')

    def _build_read(self, var_type, target):
        _target = self._get_loc(target)
        if var_type == 'int':
            self._cio('scanf', '%d', _target)
        elif var_type == 'float':
            self._cio('scanf', '%lf', _target)
        elif var_type == 'char':
            self._cio('scanf', '%c', _target)

    def _build_read_(self, ctype, target, **kwargs):
        self._build_read_(ctype, target)

    def _build_store(self, ctype, source, target):
        _source = self._get_loc(source)
        _target = self._get_loc(target)
        if _target:
            _align = get_align(llvm_type[ctype], 1)
            self.builder.store(_source, _target, _align)
        else:
            self.loc[target] = _source

    def _build_store_(self, ctype, source, target, **kwargs):
        _source = self._get_loc(source)
        _target = self._get_loc(target)
        if isinstance(_target.type.pointee, ir.ArrayType):
            _size = 1
            for arg in kwargs.values():
                _size *= int(arg)
            if ctype == 'float':
                _size = _size * 8
            elif ctype == 'int':
                _size = _size * int_ty.width // 8
            memcpy = self.module.declare_intrinsic('llvm.memcpy', [charptr_ty, charptr_ty, i64_ty])
            _srcptr = self.builder.bitcast(_source, charptr_ty)
            _tgtptr = self.builder.bitcast(_target, charptr_ty)
            self.builder.call(memcpy, [_tgtptr, _srcptr, ir.Constant(i64_ty, _size), llvm_false])
        elif isinstance(_target.type.pointee, ir.PointerType):
            _align = get_align(ir.PointerType, 1)
            _temp = self.builder.load(_target, align=_align)
            self.builder.store(_source, _temp, _align)
        else:
            _align = get_align(llvm_type[ctype], 1)
            self.builder.store(_source, _target, _align)

    def _build_add(self, expr_type, left, right, target):
        _left = self._get_loc(left)
        _right = self._get_loc(right)
        if expr_type == 'float':
            _loc = self.builder.fadd(_left, _right)
        else:
            _loc = self.builder.add(_left, _right)
        self.loc[target] = _loc

    def _build_sub(self, expr_type, left, right, target):
        _left = self._get_loc(left)
        _right = self._get_loc(right)
        if expr_type == 'float':
            _loc = self.builder.fsub(_left, _right)
        else:
            _loc = self.builder.sub(_left, _right)
        self.loc[target] = _loc

    def _build_mul(self, expr_type, left, right, target):
        _left = self._get_loc(left)
        _right = self._get_loc(right)
        if expr_type == 'float':
            _loc = self.builder.fmul(_left, _right)
        else:
            _loc = self.builder.mul(_left, _right)
        self.loc[target] = _loc

    def _build_div(self, expr_type, left, right, target):
        _left = self._get_loc(left)
        _right = self._get_loc(right)
        if expr_type == 'float':
            _loc = self.builder.fdiv(_left, _right)
        else:
            _loc = self.builder.sdiv(_left, _right)
        self.loc[target] = _loc

    def _build_mod(self, expr_type, left, right, target):
        _left = self._get_loc(left)
        _right = self._get_loc(right)
        if expr_type == 'float':
            _loc = self.builder.frem(_left, _right)
        else:
            _loc = self.builder.srem(_left, _right)
        self.loc[target] = _loc

    def _build_le(self, expr_type, left, right, target):
        _left = self._get_loc(left)
        _right = self._get_loc(right)
        if expr_type == 'float':
            _loc = self.builder.fcnp_signed('<=', _left, _right)
        else:
            _loc = self.builder.icnp_signed('<=', _left, _right)
        self.loc[target] = _loc

    def _build_gt(self, expr_type, left, right, target):
        _left = self._get_loc(left)
        _right = self._get_loc(right)
        if expr_type == 'float':
            _loc = self.builder.fcnp_signed('>', _left, _right)
        else:
            _loc = self.builder.icnp_signed('>', _left, _right)
        self.loc[target] = _loc

    def build_return(self, expr_type, target):
        if expr_type == 'void':
            self.builder.ret_void()
        else:
            _target = self._get_loc(target)
            self.builder.ret(_target)

    def build_jump(self, expr_type, target):
        _target = self._get_loc(target)
        self.builder.branch(_target)

    def _build_cbranch(self, expr_type, expr_test, target, fall_through):
        _expr_test = self._get_loc(expr_test)
        _target = self._get_loc(target)
        _fall_through = self._get_loc(fall_through)
        self.builder.cbranch(_expr_test, _target, _fall_through)

    def build(self, inst):
        opcode, ctype, modifier = self._extract_operation(inst[0])
        if hasattr(self, "_build_" + opcode):
            args = inst[1:] if len(inst) > 1 else (None,)
            if not modifier:
                getattr(self, "_build_" + opcode)(ctype, *args)
            else:
                getattr(self, "_build_" + opcode + "_")(ctype, *inst[1:], **modifier)
        else:
            print("Warning: No _build_" + opcode + "() method", flush=True)

    def visit_BasicBlock(self, block):
        if self.phase == "create_bb":
            if block.label is None:
                assert len(block.instructions) == 1
                self._new_function(block.instructions[0])
            else:
                bb = self.func.append_basic_block(block.label[1:])
                self.loc[block.label] = bb

        elif self.phase == "build_bb":
            if block.label:
                bb = self.loc[block.label]
                self.builder = ir.IRBuilder(bb)
                for inst in block.instructions[1:]:
                    print("INST " + str(inst))
                    self.build(inst)

    def visit_ConditionBlock(self, block):
        if self.phase == "create_bb":
            bb = self.func.append_basic_block(block.label[1:])
            self.loc[block.label] = bb

        elif self.phase == "build_bb":
            bb = self.loc[block.label]
            self.builder = ir.IRBuilder(bb)
            for inst in block.instructions[1:]:
                self.build(inst)


class LLVMCodeGenerator(NodeVisitor):
    def __init__(self, viewcfg):
        self.viewcfg = viewcfg
        self.binding = binding
        self.binding.initialize()
        self.binding.initialize_native_target()
        self.binding.initialize_native_asmprinter()

        self.module = ir.Module(name=__file__)
        self.module.triple = self.binding.get_default_triple()

        self.engine = self._create_execution_engine()

        self._declare_printf_function()
        self._declare_scanf_function()

    def _create_execution_engine(self):
        target = self.binding.Target.from_default_triple()
        target_machine = target.create_target_machine()

        backing_mod = binding.parse_assembly("")
        engine = binding.create_mcjit_compiler(backing_mod, target_machine)
        return engine

    def _declare_printf_function(self):
        printf_ty = ir.FunctionType(int_ty, [voidptr_ty], var_arg=True)
        printf = ir.Function(self.module, printf_ty, name="printf")
        self.printf = printf

    def _declare_scanf_function(self):
        scanf_ty = ir.FunctionType(int_ty, [voidptr_ty], var_arg=True)
        scanf = ir.Function(self.module, scanf_ty, name="scanf")
        self.scanf = scanf

    def compile_ir(self):
        llvm_ir = str(self.module)
        mod = self.binding.parse_assembly(llvm_ir)
        mod.verify()

        self.engine.add_module(mod)
        self.engine.finalize_object()
        self.engine.run_static_constructors()
        return mod

    def save_ir(self, output_file):
        output_file.write(str(self.module))

    def execute_ir(self):
        mod = self.compile_ir()
        main_ptr = self.engine.get_function_address('main')
        main_function = CFUNCTYPE(c_int)(main_ptr)
        res = main_function()
        # print(res)

    def _extract_global_operation(self, source):
        _modifier = {}
        _aux = source.split('_')
        assert _aux[0] == 'global'
        _ctype = _aux[1]
        assert _ctype in ('int', 'float', 'char', 'string')
        if len(_aux) > 2:
            _val = _aux[2]
            if _val.isdigit():
                _modifier['dim_1'] = _val
            elif _val == "*":
                _modifier['ptr_1'] = _val
        if len(_aux) > 3:
            _val = _aux[3]
            if _val.isdigit():
                _modifier['dim_2'] = _val
            elif _val == "*":
                _modifier['ptr_2'] = _val
        return (_ctype, _modifier)

    def _generate_global_instructions(self, glbInst):
        for inst in glbInst:
            _ctype, _modifier = self._extract_global_operation(inst[0])
            _type = llvm_type[_ctype]
            _name = inst[1][1:]
            _value = inst[2]
            fn_sig = isinstance(_value, list)
            if fn_sig:
                for _el in _value:
                    if _el not in list(llvm_type.keys()):
                        fn_sig = False
            if _ctype == "string":
                cte = make_bytearray((_value + "\00").encode('utf-8'))
                gv = ir.GlobalVariable(self.module, cte.type, _name)
                gv.initializer = cte
                gv.align = 1
                gv.global_constant = True
            elif _modifier and not fn_sig:
                _width = 4
                for arg in reversed(list(_modifier.values())):
                    if arg.isdigit():
                        _width = int(arg)
                        _type = ir.ArrayType(_type, int(arg))
                    else:
                        _type = ir.PointerType(_type)
                gv = ir.GlobalVariable(self.module, _type, _name)
                gv.initializer = ir.Constant(_type, _value)
                gv.align = get_align(_type, _width)
                if _name.startswith('.const'):
                    gv.global_constant = True
                elif fn_sig:
                    _sig = [llvm_type[arg] for arg in _value]
                    funty = ir.FunctionType(llvm_type[_ctype], _sig)
                    gv = ir.GlobalVariable(self.module, funty.as_pointer(), _name)
                    gv.linkage = 'common'
                    gv.initializer = ir.Constant(funty.as_pointer(), None)
                    gv.align = 8
                else:
                    gv = ir.GlobalVariable(self.module, _type, _name)
                    gv.align = get_align(_type, 1)
                    if _value:
                        gv.initializer = ir.Constant(_type, _value)

    def visit_Program(self, node):
        self._generate_global_instructions(node.text)
        for _decl in node.gdecls:
            if isinstance(_decl, FuncDef):
                bb = LLVMFunctionVisitor(self.module)
                bb.phase = 'create_bb'
                bb.visit(_decl.cfg)
                bb.phase = 'build_bb'
                bb.visit(_decl.cfg)
                if self.viewcfg:
                    dot = binding.get_function_cfg(bb.func)
                    gv = binding.view_dot_graph(dot, _decl.decl.name.name, False)
                    gv.filename = _decl.decl.name.name + ".ll.gv"
                    gv.view()
