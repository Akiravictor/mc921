from uc_sema import NodeVisitor


class Block(object):
    def __init__(self, label = ""):
        self.instructions = []
        self.predecessors = []
        self.next_block = None
        self.label = label

    def append(self, instruction):
        self.instructions.append(instruction)

    def __iter__(self):
        return iter(self.instructions)


class BasicBlock(Block):
    def __init(self, label = ""):
        super(BasicBlock, self).__init__(label)
        self.branch = None


class ConditionalBlock(Block):
    def __init__(self, label = ""):
        super(ConditionalBlock, self).__init__(label)
        self.taken = None
        self.fall = None


class AssertBlock(Block):
    def __init__(self, label = ""):
        super(AssertBlock, self).__init__(label)
        self.true = None
        self.false = None
        self.condition = None


class ForBlock(Block):
    def __init__(self, label = ""):
        super(ForBlock, self).__init__(label)
        self.condition = None
        self.body = None
        self.increment = None


class IfBlock(Block):
    def __init__(self, label = ""):
        super(IfBlock, self).__init__(label)
        self.condition = None
        self.if_branch = None
        self.else_branch = None


class WhileBlock(Block):
    def __init__(self, label = ""):
        super(WhileBlock, self).__init__(label)
        self.condition = None
        self.body = None


class BlockVisitor(object):
    def visit(self, block):
        while isinstance(block, Block):
            name = "visit_{}".format(type(block).__name__)
            if hasattr(self, name):
                getattr(self, name)(block)
            block = block.next_block


class EmitBlocks(BlockVisitor):
    def visit_BasicBlock(self, block):
        print("Block: [%s]" % block)
        for instruction in block.instructions:
            print("    %s" % (instruction, ))

    def visit_IfBlock(self, block):
        self.visit_BasicBlock(block)
        instruction = ('JUMP_IF_ELSE', block.else_branch if block.else_branch else block.next_block)
        print("    %s" % (instruction,))
        self.visit(block.if_branch)
        if block.else_branch:
            instruction = ('JUMP', block.next_block)
            print("    %s" % (instruction,))
            self.visit(block.else_branch)


class Codegen(NodeVisitor):
    def __init__(self):
        self.current_block = None
        self.fname = "_glob_"
        self.versions = {self.fname: 0}
        self.lbl = Label()

        self.code = []
        self.text =[]

        self.binary_op = {"+": "add", "-": "sub", "*": "mult", "/": "div", "%": "mod",
                            "&&": "and", "||": "or", "==": "eq", "!=": "ne", ">": "gt", ">=": "ge",
                            "<": "lt", "<=": "le"}
