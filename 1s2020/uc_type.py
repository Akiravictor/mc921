class UCType(object):
    '''
    Class that represents a type in the uC language.  Types
    are declared as singleton instances of this type.
    '''

    def __init__(self, typename, binary_ops=set(), unary_ops=set(), rel_ops=set(), assign_ops=set()):
        '''
        You must implement yourself and figure out what to store.
        '''
        self.typename = typename
        self.unary_ops = unary_ops or set()
        self.binary_ops = binary_ops or set()
        self.rel_ops = rel_ops or set()
        self.assign_ops = assign_ops or set()

    def __str__(self):
        return str(self.typename)

IntType = UCType("int",
                 unary_ops={"-", "+", "--", "++", "p--", "p++", "*", "&"},
                 binary_ops={"+", "-", "*", "/", "%"},
                 rel_ops={"==", "!=", "<", ">", "<=", ">="},
                 assign_ops={"=", "+=", "-=", "*=", "/=", "%="}
                 )

FloatType = UCType("float",
                   unary_ops={"-", "*", "&"},
                   binary_ops={"+", "-", "*", "/", "%"},
                   rel_ops={"==", "!=", "<", ">", "<=", ">="},
                   assign_ops={"=", "+=", "-=", "*=", "/=", "%="}
                   )
CharType = UCType("char",
                  unary_ops={"*", "&"},
                  binary_ops={"+"},
                  rel_ops={"==", "!=", "<", ">", "<=", ">="},
                  assign_ops={"="}
                  )
ArrayType = UCType("array",
                   unary_ops={"*", "&"},
                   rel_ops={"==", "!="},
                   assign_ops={"="}
                   )

StringType = UCType("string",
                    binary_ops={"+"},
                    rel_ops={"==", "!="},
                    assign_ops={"="}
                    )

BoolType = UCType("bool",
                  unary_ops={"!"},
                  binary_ops={"||", "&&"},
                  rel_ops={"==", "!="},
                  assign_ops={"="}
                  )

VoidType = UCType("void")

PtrType = UCType("ptr")

