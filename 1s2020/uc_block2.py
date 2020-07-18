from uc_sema import NodeVisitor
from graphviz import Digraph


class Block(object):
    def __init__(self, label=""):
        self.instructions = []
        self.predecessors = set()
        self.next_block = None
        self.label = label
        self.visited = False
        self.branch = None
        self.scope = None

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

def format_instruction(t):
    # Auxiliary method to pretty print the instructions
    op = t[0]
    if (op == None): return None
    if len(t) > 1:
        if op == "define":
            return f"\n{op} {t[1]}"
        else:
            _str = "" if op.startswith('global') else "  "
            if op == 'jump':
                _str += f"{op} label {t[1]}"
            elif op == 'cbranch':
                _str += f"{op} {t[1]} label {t[2]} label {t[3]}"
            elif op == 'global_string':
                _str += f"{op} {t[1]} \'{t[2]}\'"
            elif op.startswith('return'):
                _str += f"{op} {t[1]}"
            else:
                for _el in t:
                    _str += f"{_el} "
            return _str
    elif op == 'print_void' or op == 'return_void':
        return f"  {op}"
    else:
        return f"{op}"

class CFG(object):
    def __init__(self, fname):
        self.fname = fname
        self.g = Digraph('g', filename=fname + '.gv', node_attr={'shape': 'record'})

    def visit_BasicBlock(self, block):
        # Get the label as node name
        _name = block.label
        if _name:
            # get the formatted instructions as node label
            _label = "{" + _name + ":\l\t"
            for _inst in block.instructions[0:]:
                _label += format_instruction(_inst) + "\l\t"
            _label += "}"
            self.g.node(_name, label=_label)
            if block.branch:
                self.g.edge(_name, block.branch.label)
        else:
            # Function definition. An empty block that connect to the Entry Block
            self.g.node(self.fname, label=None, _attributes={'shape': 'ellipse'})
            self.g.edge(self.fname, block.next_block.label)

    def visit_ConditionalBlock(self, block):
        # Get the label as node name
        _name = block.label
        # get the formatted instructions as node label
        _label = "{" + _name + ":\l\t"
        for _inst in block.instructions[0:]:
            _label += format_instruction(_inst) + "\l\t"
        _label +="|{<f0>T|<f1>F}}"
        self.g.node(_name, label=_label)
        self.g.edge(_name + ":f0", block.taken.label)
        self.g.edge(_name + ":f1", block.fall.label)

    def view(self, block):
        self.deep_view(block)
        self.g.view()

    def deep_view(self, block):
        if not isinstance(block, Block) or block.visited:
            return
        block.visited = True
        name = "visit_%s" % type(block).__name__
        if hasattr(self, name):
            getattr(self, name)(block)
        self.deep_view(block.next_block)
        if isinstance(block, ConditionalBlock):
            self.deep_view(block.taken)

