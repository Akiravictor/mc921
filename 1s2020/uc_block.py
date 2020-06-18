from uc_sema import NodeVisitor
from graphviz import Digraph


class Block(object):
    def __init__(self, label=""):
        self.instructions = []
        self.predecessors = []
        ea_in = []
        ea_out = []
        rd_in = []
        rd_out = []
        la_in = []
        la_out = []
        ea_gen = []
        ea_kill = []
        rd_gen = []
        rd_kill = []
        la_use = []
        la_def = []
        self.next_block = None
        self.label = label
        self.visited = False
        self.branch = None

    def append(self, instruction):
        self.instructions.append(instruction)

    def __iter__(self):
        return iter(self.instructions)

    def generateJump(self):
        return self.instructions[-1][0] != 'jump'


class BasicBlock(Block):
    def __init(self, label=""):
        super(BasicBlock, self).__init__(label)
        self.branch = None


class ConditionalBlock(Block):
    def __init__(self, label=""):
        super(ConditionalBlock, self).__init__(label)
        self.taken = None
        self.fall = None


class AssertBlock(Block):
    def __init__(self, label=""):
        super(AssertBlock, self).__init__(label)
        self.true = None
        self.false = None
        self.condition = None


class ForBlock(Block):
    def __init__(self, label=""):
        super(ForBlock, self).__init__(label)
        self.condition = None
        self.body = None
        self.increment = None


class IfBlock(Block):
    def __init__(self, label=""):
        super(IfBlock, self).__init__(label)
        self.condition = None
        self.if_branch = None
        self.else_branch = None


class WhileBlock(Block):
    def __init__(self, label=""):
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
    def __init__(self):
        self.code = []

    def visit_BasicBlock(self, block):
        for instruction in block.instructions:
            self.code.append(instruction)

    def visit_ConditionalBlock(self, block):
        for instruction in block.instructions:
            self.code.append(instruction)


class CFG(object):
    def __init__(self, fname):
        self.fname = fname
        self.g = Digraph('g', filename=fname + '.gv', node_attr={'shape': 'record'})

    def visit_BasicBlock(self, block):
        # Get the label as node name
        _name = block.label
        print(block.instructions)
        if _name:
            # get the formatted instructions as node label
            _label = "{" + _name + ":\l\t"
            for _inst in block.instructions[1:]:
                # _label += format_instruction(_inst) + "\l\t"
                _label += _inst[0] + "\l\t"
            _label += "}"
            self.g.node(_name, label=_label)
            if block.branch:
                self.g.edge(_name, block.branch.label)
        else:
            # Function definition. An empty block that connect to the Entry Block
            self.g.node(self.fname, label=None, _attributes={'shape': 'ellipse'})
            self.g.edge(self.fname, block.next_block.label)

    def visit_ConditionBlock(self, block):
        # Get the label as node name
        _name = block.label
        print(block.instructions)
        # get the formatted instructions as node label
        _label = "{" + _name + ":\l\t"
        for _inst in block.instructions[1:]:
            _label += _inst[0] + "\l\t"
        _label += "|{<f0>T|<f1>F}}"
        self.g.node(_name, label=_label)
        self.g.edge(_name + ":f0", block.taken.label)
        self.g.edge(_name + ":f1", block.fall_through.label)

    def view(self, block):
        while isinstance(block, Block):
            name = "visit_%s" % type(block).__name__
            if hasattr(self, name):
                getattr(self, name)(block)
            block = block.next_block
        # You can use the next stmt to see the dot file
        # print(self.g.source)
        self.g.view()

