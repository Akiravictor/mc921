class Fila(object):
    def __init__(self):
        self.dados = []

    def insere(self, elemento):
        self.dados.append(elemento)

    def retira(self):
        return self.dados.pop(0)

    def vazia(self):
        return len(self.dados) == 0

class Pilha(object):
    def __init__(self):
        self.dados = []

    def empilha(self, elemento):
        self.dados.append(elemento)

    def desempilha(self):
        if not self.vazia():
            return self.dados.pop(-1)

    def vazia(self):
        return len(self.dados) == 0




class Scope(object):
    '''
    Cada Scope nesse contexto contém:
        -Contém um nome. Se for uma funcão conterá o nome da função. Se for um "For", terá um identificador gerado.
         Vale ressaltar que teremos o escopo global que exerga todos os outros
        -Uma tabela de símbolos relacionando um id a um símbolo temporário forma %n, sendo n>=0 e positivo.
        -Uma tabela de símbolos relacionando um id a um type, como int,float etc.
        -Um conjunto de variáveis temporárias {%0,%1,%2...%n}
        -Um conjunto de variáveis {@.str.1,@.str.2,@.str.3...@.str.n} que tem como propósito tratar heaps
    '''

    def __init__(self, name='global'):

        self.name = name  # Nome do escopo
        self.table = SymbolTable()  # Relaciona id aos aos símbolos %n, n>=0 e inteiro
        self.table_type = SymbolTable()  # Relaciona id aos types
        self.vars = dict()  # Variáveis do escopo
        self.vars[self.name] = 0

        self.name_array = name  # Variavel que trata os heaps
        self.heaps = dict()

    def new_temp(self):
        '''
        Create a new temporary variable of a given scope (function name).
        '''
        if self.name not in self.vars:
            self.vars[self.name] = 0
        name = "%" + "%d" % (self.vars[self.name])
        self.vars[self.name] += 1
        return name

    def new_heap(self):
        '''
        Create a new heap  of a given array .
        '''
        if self.name_array not in self.heaps:
            self.heaps[self.name_array] = 0
        name = "@.str." + "%d" % (self.heaps[self.name_array])
        self.heaps[self.name_array] += 1
        return name

    def set_name(self, name):
        self.name = name

class SymbolTable(dict):
    def __init__(self, decl=None):
        super().__init__()
        self.decl = decl

    def lookup(self, key):
        return self.get(key, None)

    def add(self, k, v):
        self[k] = v


binary=dict()
binary['+']='add'
binary['-']='sub'
binary['*']='mul'
binary['/']='div'
binary['%']='mod'
binary['<']='lt'
binary['<=']='le'
binary['>']='gt'
binary['>=']='gt'
binary['!=']='ne'
binary['&']='and'
binary['||']='or'
binary['!']='not'
binary['==']='eq'

unary=dict()
unary['--']='sub'
unary['++']='add'
unary['p++']='add'
unary['p--']='sub'
assign_op=dict()
assign_op['+=']='+'
assign_op['-=']='-'
assign_op['*=']='*'
assign_op['%=']='%'
assign_op['/=']='/'
rel_ops     = {"==", "!=", "<", ">", "<=", ">=","&&","||","&","|"}