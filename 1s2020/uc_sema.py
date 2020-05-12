from uc_type import UCType
from uc_ast import *

class UCSemantic:
    def analyse(ast):
        print("Hello!")
        # print("Received AST:\n{0}".format(ast))

        nodeVisitor = NodeVisitor()
        visitor = Visitor()
        # nodeVisitor.generic_visit(ast)
        visitor.visit_Program(ast)
        # visitor.visit_Assignment(ast)

        # Visitor.visit_Program(ast)


class Environment(object):
    '''
    Class representing a symbol table.  It should provide functionality
    for adding and looking up nodes associated with identifiers.
    '''
    def __init__(self):
        self.symtab = {}

    def lookup(self, a):
        return self.symtab.get(a)

    def add(self, a, v):
        self.symtab[a] = v


class NodeVisitor(object):
    """ A base NodeVisitor class for visiting uc_ast nodes.
        Subclass it and define your own visit_XXX methods, where
        XXX is the class name you want to visit with these
        methods.

        For example:

        class ConstantVisitor(NodeVisitor):
            def __init__(self):
                self.values = []

            def visit_Constant(self, node):
                self.values.append(node.value)

        Creates a list of values of all the constant nodes
        encountered below the given node. To use it:

        cv = ConstantVisitor()
        cv.visit(node)

        Notes:

        *   generic_visit() will be called for AST nodes for which
            no visit_XXX method was defined.
        *   The children of nodes for which a visit_XXX was
            defined will not be visited - if you need this, call
            generic_visit() on the node.
            You can use:
                NodeVisitor.generic_visit(self, node)
        *   Modeled after Python's own AST visiting facilities
            (the ast module of Python 3.0)
    """

    _method_cache = None

    def visit(self, node):
        """ Visit a node.
        """
        print("@visit")
        # print(f"@ {node.coord.line}:{node.coord.column}")
        if self._method_cache is None:
            self._method_cache = {}

        visitor = self._method_cache.get(node.__class__.__name__, None)
        if visitor is None:
            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            self._method_cache[node.__class__.__name__] = visitor

        return visitor(node)

    def generic_visit(self, node):
        print("@generic_visit")
        # print(f"@ {node.coord.line}:{node.coord.column}")
        """ Called if no explicit visitor function exists for a
            node. Implements preorder visiting of the node.
        """
        for c in node:
            print("Generic_visit: {0}".format(c))
            self.visit(c)


class Visitor(NodeVisitor):
    '''
    Program visitor class. This class uses the visitor pattern. You need to define methods
    of the form visit_NodeName() for each kind of AST node that you want to process.
    Note: You will need to adjust the names of the AST nodes if you picked different names.
    '''
    def __init__(self, debug):
        # Initialize the symbol table
        self.environment = Environment()

        # Create specific instances of types. You will need to add
        # appropriate arguments depending on your definition of uCType
        IntType = UCType("int",
                         unary_ops={"-", "+", "--", "++", "p--", "p++", "*", "&"},
                         binary_ops={"+", "-", "*", "/", "%"},
                         rel_ops={"==", "!=", "<", ">", "<=", ">="},
                         assign_ops={"=", "+=", "-=", "*=", "/=", "%="}
                         )

        FloatType = UCType("float"
                           )
        CharType = UCType("char"
                          )
        ArrayType = UCType("array",
                           unary_ops={"*", "&"},
                           rel_ops={"==", "!="}
                           )

        StringType = UCType("string")

        BoolType = UCType("bool")

        PtrType = UCType("ptr")

        VoidType = UCType("void")

        self.typemap = {
            'int': IntType,
            'float': FloatType,
            'char': CharType,
            'array': ArrayType,
            'string': StringType,
            'bool': BoolType,
            'ptr': PtrType,
            'void': VoidType
        }
        self.debug = debug

        # Add built-in type names (int, float, char) to the symbol table
        # self.symtab.add("int", uctype.IntType)
        # self.symtab.add("float", uctype.FloatType)
        # self.symtab.add("char", uctype.CharType)

    def visit_Program(self, node):
        # 1. Visit all of the global declarations
        # 2. Record the associated symbol table
        print("@visit_Program")
        # print(f"@ {node.coord.line}:{node.coord.column}")
        for _decl in node.gdecls:
            self.visit(_decl)

    def visit_BinaryOp(self, node):
        coord = f"@{node.coord.line}:{node.coord.column}"
        # 1. Make sure left and right operands have the same type
        # 2. Make sure the operation is supported
        # 3. Assign the result type
        print("@visit_BinaryOp")
        print(coord)
        self.visit(node.left)
        ltype = node.left.type.names[-1]
        self.visit(node.right)
        rtype = node.right.type.names[-1]
        if ltype != rtype:
            print(f"Cannot assign {rtype} to {ltype} {coord}")
        if node.op in ltype.binary_ops:
            node.type = Type([ltype], node.coord)
        elif node.op in ltype.rel_ops:
            node.type = Type([self.typemap["bool"]], node.coord)
        else:
            print(f"Assign operator {node.op} is not supported by {ltype} {coord}")

    def visit_Assignment(self, node):
        coord = f"@{node.coord.line}:{node.coord.column}"
        print("@visit_Assignment")
        print(coord)
        self.visit(node.rvalue)
        rtype = node.rvalue.type.names
        val = node.lvalue
        self.visit(node.lvalue)
        if isinstance(val, ID):
            if val.scope is None:
                print(f"{val} is not defined {coord}")
        ltype = node.lvalue.types.names
        if ltype != rtype:
            print(f"Cannot assign {rtype} to {ltype} {coord}")
        if node.op not in ltype[-1].assign_ops:
            print(f"Assign operator {node.op} not supported by {ltype[-1]}")

        # ## 1. Make sure the location of the assignment is defined
        # sym = self.symtab.lookup(node.location)
        # assert sym, "Assigning to unknown sym"
        # ## 2. Check that the types match
        # self.visit(node.value)
        # assert sym.type == node.value.type, "Type mismatch in assignment"

    def visit_Assert(self, node):
        coord = f"@{node.expr.coord.line}:{node.expr.coord.column}"
        print("@visit_Assert")
        print(coord)
        self.visit(node.expr)
        if hasattr(node.expr, "type"):
            if node.expr.type.names[0] != self.typemap["bool"]:
                print(f"Expression must be boolean {coord}")
        else:
            print(f"Expression must be boolean {coord}")

    def visit_ArrayRef(self, node):
        coord = f"@{node.subscript.coord.line}:{node.subscript.coord.column}"
        print("@visit_ArrayRef")
        print(coord)
        self.visit(node.subscript)
        if isinstance(node.subscript, ID):
            if node.subscript.scope is None:
                print(f"{node.subscript.name} is not defined {coord}")
        if node.subscript.type.names[-1] != IntType:
            print(f"{node.subscript.type.names[-1]} must be of type Int {coord}")
        self.visit(node.name)
        arrayType = node.name.type.names[1:]
        node.type = Type(arrayType, node.coord)

    def visit_ArrayDecl(self, node):
        print("@visit_ArrayDecl")
        arrayType = node.type
        while not isinstance(arrayType, VarDecl):
            arrayType = arrayType.type
        arrayId = arrayType.declname
        arrayId.type.names.insert(0, self.typemap["array"])
        if node.dim is not None:
            self.visit(node.dim)

    # def visit_Break(self, node):
    #     coord = f"@{node.coord.line}:{node.coord.column}"
    #     print("@visit_Break")
    #     print(coord)
    #     if self.environment.cur_loop == []:
    #         print(f"Break statement must be inside a loop block {coord}")
    #     node.bind = self.environment.cur_loop[-1]

    def visit_Cast(self, node):
        print("@visit_Cast")
        self.visit(node.expr)
        self.visit(node.to_type)
        node.type = Type(node.to_type.names, node.coord)

    def visit_Compound(self, node):
        print("@visit_Compound")
        for item in node.block_items:
            self.visit(item)

    def visit_Constant(self, node):
        print("@visit_Compound")
        if not isinstance(node.type, UCType):
            consType = self.typemap(node.rawtype)
            node.type = Type([consType], node.coord)
            if consType.typename == 'int':
                node.value = int(node.value)
            elif consType.typename == 'float':
                node.value = float(node.value)

    def setDim(self, _type, length, line, var):
        print("@setDim")
        if type.dim is None:
            type.dim = Constant('int', length)
            self.visit_Constant(type.dim)
        else:
            if type.dim.value != length:
                print(f"Size mismatch on {var}")

    def checkInit(self, _type, init, var, line):
        print("@checkInit")
        self.visit(init)
        if isinstance(init, Constant):
            if init.rawtype == 'string':
                if _type.type.type.names != self.typemap["array"]:
                    print(f"Initialization type mismatch {line}")
                self.setDim(_type, len(init.value), line, var)
            else:
                if _type.type.names[0] != init.type.names[0]:
                    print(f"Initialization type mismatch {line}")
        elif isinstance(init, InitList):
            length = len(init.exprs)
            exprs = init.exprs
            if isinstance(_type, VarDecl):
                if length != 1:
                    print(f"Initialization must be a single element {line}")
                if _type.type != exprs[0].type:
                    print(f"Initialization type missing {line}")
            elif isinstance(_type, ArrayDecl):
                size = length
                head = exprs
                decl = _type
                while isinstance(_type.type, ArrayDecl):
                    _type = _type.type
                    length = len(exprs[0].exprs)
                    for i in range(len(exprs)):
                        if len(exprs[i].exprs) != length:
                            print(f"List have a different length {line}")
                    exprs = exprs[0].exprs
                    if isinstance(type, ArrayDecl):
                        self.setDim(type, length, line, var)
                        size += length
                    else:
                        if exprs[0].type != _type.type.type.names[-1]:
                            print(f"{var} Initialization type mismatch {line}")
                _type = decl
                exprs = head
                length = size
                if _type.dim is None:
                    _type.dim = Constant('int', size)
                    self.visit_Constant(type.dim)
                else:
                    if _type.dim.value != length:
                        print(f"Size mismatch {var} initialization {line}")
        elif isinstance(init, ArrayRef):
            id = self.environment.lookup(init.name.name)
            if isinstance(init.subscript, Constant):
                rtype = id.type.names[1]
                if _type.type.names[0] != rtype:
                    print(f"Initialization type mismatch {var} {line}")
        elif isinstance(init, ID):
            if isinstance(_type, ArrayDecl):
                anotherType = _type.type
                while not isinstance(anotherType, VarDecl):
                    anotherType = anotherType.type
                if anotherType.type.names != init.type.names:
                    print(f"Initialization type mismatch {line}")
                self.setDim(_type, init.bind.dim.value, line, var)
            else:
                if _type.type.names[-1] != init.type.names[-1]:
                    print(f"Initialization type mismatch {line}")

    def visit_Decl(self, node):
        coord = f"{node.name.coord}"
        print("@visit_Assert")
        print(coord)
        declType = node.type
        self.visit(declType)
        node.name.bind = declType
        declVar = node.name.name
        if isinstance(declType, PtrDecl):
            while isinstance(declType, PtrDecl):
                declType = declType.type
        if isinstance(declType, FuncDecl):
            if self.environment.lookup(declVar) is None:
                print(f"{declVar} is not defined {coord}")
        else:
            if self.environment.find(declVar) is None:
                print(f"{declVar} is not defined")
            if node.init is not None:
                self.checkInit(declType, node.init, declVar, coord)

    def visit_DeclList(self, node):
        print("@visit_DeclList")
        for decl in node.decls:
            self.visit(decl)
            self.environment.funcdef.decls.append(decl)

    def visit_EmptyStatement(self, node):
        print("@visit_EmptyStatement")
        pass

    def visit_ExprList(self, node):
        print("@visit_ExprList")
        for expr in node.exprs:
            self.visit(expr)
            if isinstance(expr, ID):
                coord = f"@{expr.coord.line}:{expr.coord.column}"
                if expr.scope is None:
                    print(f"{expr.name} is not defined {coord}")

    def visit_For(self, node):
        print("@visit_For")
        if isinstance(node.init, DeclList):
            self.environment.push(node)
        self.envitonment.cur_loop.append(node)
        self.visit(node.init)
        self.visit(node.cond)
        self.visit(node.next)
        self.visit(node.stmt)
        self.environment.cur_loop.pop()
        if isinstance(node.init, DeclList):
            self.environment.pop()

    def visit_FuncCall(self, node):
        print("@visit_FuncCall")
        coord = f"@{node.coord.line}:{node.coord.column}"
        funcLabel = self.environment.lookup(node.name.name)
        if funcLabel.kind != "func":
            print(f"{funcLabel} is not a function {coord}")
        node.type = funcLabel.type
        if node.args is not None:
            sig = funcLabel.bind
            if isinstance(node.args, ExprList):
                if len(sig.args.params) != len(node.args.exprs):
                    print(f"Number of arguments mismatch {coord}")
                for(arg, fpar) in zip(node.args.exprs, sig.args.params):
                    self.visit(arg)
                    coord = f"@{arg.coord.line}:{arg.coord.column}"
                    if isinstance(arg, ID):
                        if not self.environment.find(arg.name):
                            print(f"{arg.name} is not defined {coord}")
                    if arg.type.names != fpar.type.type.names:
                        print(f"Type mismatch for {fpar.type.declname.name} {coord}")
            else:
                self.visit(node.args)
                if len(sig.args.params) != 1:
                    print(f"Number of arguments mismatch {coord}")
                argType = sig.args.params[0].type
                while not isinstance(argType, VarDecl):
                    argType = argType.type
                if node.args.type.names != argType.type.names:
                    print(f"Type mismatch for {sig.args.params[0].name.name} {coord}")

    def visit_FuncDecl(self, node):
        print("@visit_FuncDecl")
        self.visit(node.type)
        func = self.environment.lookup(node.type.declname.name)
        func.kind = 'func'
        func.bind = node.args
        self.environment.push(node)
        if node.args is not None:
            for arg in node.args:
                self.visit(arg)

    def visit_FuncDef(self, node):
        print("@visit_FuncDef")
        node.decls = []
        self.environment.funcdef = node
        self.visit(node.spec)
        self.visit(node.decl)
        if node.param_decls is not None:
            for par in node.param_decls:
                self.visit(par)
        if node.body is not None:
            for body in node.body:
                self.visit(body)
        self.environment.pop()
        func = self.environment.lookup(node.decls.name.name)
        node.spec = func.type

    def visit_GlobalDecl(self, node):
        print("@visit_GlobalDecl")
        for decl in node.decls:
            self.visit(decl)

    def visit_ID(self, node):
        print("@visit_ID")
        varId = self.environment.lookup(node.name)
        if varId is not None:
            node.type = varId.type
            node.kind = varId.kind
            node.scope = varId.scope
            node.bind = varId.bind

    def visit_If(self, node):
        coord = f"@ {node.cond.coord.line}:{node.cond.coord.column}"
        print("@visit_If")
        print(coord)
        self.visit(node.cond)
        if hasattr(node.cond, 'type'):
            if node.cond.type.names[0] != self.typemap["bool"]:
                print(f"The condition must be a boolean type {coord}")
        else:
            print(f"The condition must be a boolean type {coord}")
        self.visit(node.iftrue)
        if node.iffalse is not None:
            self.visit(node.iffalse)

    def visit_InitList(self, node):
        print("@visit_InitList")
        for expr in node.exprs:
            self.visit(expr)

    def visit_ParamList(self, node):
        print("@visit_ParamList")
        for par in node.params:
            self.visit(par)

    def visit_Print(self, node):
        print("@visit_Print")
        if node.expr is not None:
            for expr in node.exprs:
                self.visit(expr)

    def visit_PtrDecl(self, node):
        print("@visit_PtrDecl")
        self.visit(node.type)
        ptrType = node.type
        while not isinstance(ptrType, VarDecl):
            ptrType = ptrType.type
        ptrType.type.names.insert(0, self.typemap["ptr"])

    def checkLocation(self, var):
        print("@checkLocation")
        coord = f"@ {var.coord.line}:{var.coord.column}"
        test = (isinstance(var, ArrayRef) and len(var.type.names) == 1) or isinstance(var, ID)
        name = var.name
        if isinstance(name, ArrayRef):
            name = name.name.name + f"[{name.subscript.name}][{var.subscript.name}]"
        elif hasattr(var, 'subscript'):
            name = name.name + f"[{var.subscript.name}]"
        if not test:
            print(f"{name} is not a simple variable {coord}")
        if isinstance(var, ID):
            if var.scope is None:
                print(f"{name} is not defined {coord}")
        if len(var.type.names) != 1:
            print(f"Type of {name} is not a primitive type")

    def visit_Read(self, node):
        print("@visit_Read")
        for loc in node.names:
            self.visit(loc)
            if isinstance(loc, ID) or isinstance(loc, ArrayRef):
                self.checkLocation(loc)
            elif isinstance(loc, ExprList):
                for var in loc.exprs:
                    if isinstance(var, ID) or isinstance(var, ArrayRef):
                        self.checkLocation(var)
                    else:
                        coord = f"@ {var.coord.line}:{var.coord.column}"
                        print(f"{var} is not a variable {coord}")
            else:
                coord = f"@ {loc.coord.line}:{loc.coord.column}"
                print(f"{loc} is not a variable {coord}")

    def visit_Return(self, node):
        if node.expr is not None:
            self.visit(node.expr)
            returnType = node.expr.type.names
        else:
            returnType = [self.typemap['void']]
        rtype = self.environment.cur_rtype
        coord = f"@ {node.coord.line}:{node.coord.column}"
        if returnType != rtype:
            print(f"Return type {returnType} is not compatible with {rtype} {coord}")

    def visit_Type(self, node):
        for i, name in enumerate(node.names or []):
            if not isinstance(name, UCType):
                node.names[i] = self.typemap[name]

    def visit_VarDecl(self, node):
        self.visit(node.type)
        var = node.declname
        self.visit(var)
        if isinstance(var, ID):
            coord = f"@ {var.coord}"
            if self.environment.find(var.name):
                print(f"{var.name} already defined in this scope")
            self.environment.add_local(var, 'var')
            var.type = node.type

    def visit_UnaryOp(self, node):
        self.visit(node.expr)
        unaryType = node.expr.type.names[-1]
        coord = f"@ {node.coord.line}:{node.coord.column}"
        if node.op not in unaryType.unary_ops:
            print(f"Unary operator {node.op} not supported {coord}")
        node.type = Type(list(node.expr.type.names), node.coord)
        if node.op == "*":
            node.type.names.pop(0)
        elif node.op == "&":
            node.type.names.insert(0, self.typemap["ptr"])

    def visit_While(self, node):
        self.visit(node.cond)
        ctype = node.cond.type.names[0]
        coord = f"@ {node.coord.line}:{node.coord.column}"
        if ctype != BoolType:
            print(f"Conditional expression must be a Boolean type {coord}")
        if node.stmt is not None:
            self.visit(node.stmt)


