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
        self.symtab = SymbolTable()
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
        if not isinstance(node.type, UCType):
            consType = self.typemap(node.rawtype)
            node.type = Type([consType], node.coord)
            if consType.typename == 'int':
                node.value = int(node.value)
            elif consType.typename == 'float':
                node.value = float(node.value)

    def setDim(self, _type, length, line, var):
        if type.dim is None:
            type.dim = Constant('int', length)
            self.visit_Constant(type.dim)
        else:
            if type.dim.value != length:
                print(f"Size mismatch on {var}")

    def checkInit(self, _type, init, var, line):
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
            