class AST:
    def __init__(self):
        '''Ainda não sei oq colocar aqui...'''

    def show(buf=None, showcoord=True):
        print("I'm on show from AST!")

    def ast(self):
        print("I'm on AST!")


class ArrayDecl:
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)


class ArrayRef:
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)


class Assert:
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)


class Assignment:
    __slots__ = ('op', 'coord')

    def __init__(self, op, coord=None):
        self.op = op
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('op',)


class BinaryOp:
    __slots__ = ('op', 'coord')

    def __init__(self, op, coord=None):
        self.op = op
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('op',)


class Break:
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)


class Cast:
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)


class Compound:
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)


class Constant:
    __slots__ = ('type', 'value', 'coord')

    def __init__(self, type, value, coord=None):
        self.type = type
        self.value = value
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('type', 'value',)


class Decl:
    __slots__ = ('name', 'coord')

    def __init__(self, name, coord=None):
        self.name = name
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('name',)


class DeclList:
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)


class EmptyStatement:
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)


class ExprList:
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)


class For:
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)


class FuncCall:
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)


class FuncDecl:
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)


class FuncDef:
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)


class GlobalDecl:
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)


class ID:
    __slots__ = ('name', 'coord')

    def __init__(self, name, coord=None):
        self.name = name
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('name',)


class If:
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)


class InitList:
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)


class ParamList:
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)


class Print:
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)


class Program:
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)


class PtrDecl:
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)


class Read:
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)


class Return:
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)


class Type:
    __slots__ = ('names', 'coord')

    def __init__(self, names, coord=None):
        self.names = names
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('names',)


class VarDecl:
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)


class UnaryOp:
    __slots__ = ('op', 'coord')

    def __init__(self, op, coord=None):
        self.op = op
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('op',)


class While:
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)
