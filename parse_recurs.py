import tokenize
import io 
from tokenize import NUMBER, STRING, NAME, OP, ENDMARKER, NEWLINE
import sys
# import pdb
# pdb.set_trace()


class Node:
    def __init__(self, kind, value=None, op1=None, op2=None, op3=None):
        self.kind = kind
        self.value = value
        self.op1 = op1
        self.op2 = op2
        self.op3 = op3
                  

class Tokenizer:
    def __init__(self, tokengen):
        """Call with tokenize.generate_tokens(...)."""
        self.tokengen = tokengen

    def next_token(self):

        token = next(self.tokengen)
        return token


class ParserBase:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.token = None

    def found(self, arg):
        if self.token.type == arg or self.token.string == arg:
            return True
        return False

    def next_token(self):
        self.token = self.tokenizer.next_token()

    def error(self, msg):
        EXIT_FAIL=1
        print('Parse error:', msg)
        sys.exit(EXIT_FAIL)    


class Parser(ParserBase):
    ADD, SUB, CONST, PROG, VAR, MULT, DIV = range(7)

    def __init__(self, tokenizer):

        super().__init__(tokenizer)
        self.token = None

    def term(self):
        """
        term  = VAR | NUMBER | SUMMA | - NUMBER
        """
        if self.found(NAME):
            n = Node(Parser.VAR, value=self.token.string)
            self.next_token()
            return n
        elif self.found(NUMBER):
            n = Node(Parser.CONST, value=int(self.token.string))
            self.next_token()
            return n
        elif self.found('('):
            self.next_token()
            n = self.summa()
            if not self.found(')'):
                self.error('expected )')
            return n
        elif self.found('-'):
            self.next_token()
            n=Node(Parser.CONST, value=-int(self.token.string))
            self.next_token()
            return n        

    

    def mult(self):
        """
        mult=term ( * | / ) term ( term ( * | / ) term )*
        """
        n = self.term()
        while self.found('*') or self.found('/'):
            if self.found('*'):
                kind = Parser.MULT
            elif self.found('/'):
                kind = Parser.DIV
            self.next_token()
            n = Node(kind, op1=n, op2=self.term())

        return n

    def summa(self):
        """
        summa = mult? ( + | - ) mult? ( mult ( + | - ) mult )*
        """
        n = self.mult()
        while self.found('+') or self.found('-'):
            if self.found('+'):
                kind = Parser.ADD
            elif self.found('-'):
                kind = Parser.SUB
            self.next_token()
            n = Node(kind, op1=n, op2=self.mult())

        return n

    def program(self):
        """
        program=summa
        """
        self.next_token()
        n = Node(Parser.PROG, op1=self.summa())
        return n

# байт-коды
Istop = 0
Ipush = 1
Iadd = 2
Imult = 3
Idiv = 4
Isub = 5


class Compiler:
    b_c = []
    pc = 0

    def gen(self, command):
        self.b_c.append(command)
        self.pc += 1

    def compile(self, node):
        if node.kind == Parser.CONST:
            self.gen(Ipush)
            self.gen(node.value)
        elif node.kind == Parser.ADD:
            self.compile(node.op1)
            self.compile(node.op2)
            self.gen(Iadd)
        elif node.kind == Parser.SUB:
            self.compile(node.op1)
            self.compile(node.op2)
            self.gen(Isub)
        elif node.kind == Parser.MULT:
            self.compile(node.op1)
            self.compile(node.op2)
            self.gen(Imult)
        elif node.kind == Parser.DIV:
            self.compile(node.op1)
            self.compile(node.op2)
            self.gen(Idiv)
        elif node.kind == Parser.PROG:
            self.compile(node.op1)
            self.gen(Istop)

    def get_bc(self):
        return self.b_c

class Object:
    def __init__(self):
       self.ref_count=0
       self.id=0

class ObjectFloat(Object):
    def __init__(self, float_val):
        self.float_val=float_val
    def _add_(self, v):
        self.float_val+=v
    def _sub_(self, v):
        self.float_val-=v 
    def _mult_(self, v):
        self.float_val*=v 
    def _div_(self, v):
        self.float_val/=v                 

class Vm:
    def __init__(self):
        self.vm_instructions = [("Istop", 0),
                                ("Ipush", 1), ("Iadd", 0), ("Imult", 0), ("Idiv", 0),
                                ("Isub", 0)]

    def print_instruction(self, b_c, pc):
        op = b_c[pc]

        n_args = self.vm_instructions[op][1]
        inst_name = self.vm_instructions[op][0]

        if n_args == 0:
            print("{0} {1}".format(pc, inst_name))
        elif n_args == 1:
            print("{0} {1} {2}".format(pc, inst_name, b_c[pc + 1]))
        elif n_args == 2:
            print("{0} {1} {2} {3}".format(pc, inst_name,
                                           b_c[pc + 1],
                                           b_c[pc + 2]))

    def run(self, b_c, trace=True):
        stack = []
        pc = 0
        heap=[0]*10
        heap_cnt=0
        vm_is_running = True
        while vm_is_running:
            if trace:
                self.print_instruction(b_c, pc)
            op = b_c[pc]
            if op == Istop:
                break
            elif op == Ipush:
                pc += 1
                arg = b_c[pc]
                float_val=ObjectFloat(arg)
                float_val.id=heap_cnt
                heap[heap_cnt]=float_val
                stack.append(heap_cnt)
                heap_cnt+=1
            elif op == Iadd:
                b = stack.pop()
                a = stack.pop()
                obj_a=heap[b]
                obj_b=heap[a]
                obj_a._add_(obj_b.float_val)
                stack.append(obj_a.id)
            elif op == Isub:
                b = stack.pop()
                a = stack.pop()
                obj_a=heap[b]
                obj_b=heap[a]
                obj_a._sub_(obj_b.float_val)
                stack.append(obj_a.id)
            elif op == Imult:
                b = stack.pop()
                a = stack.pop()
                obj_a=heap[b]
                obj_b=heap[a]
                obj_a._mult_(obj_b.float_val)
                stack.append(obj_a.id)
            elif op == Idiv:
                b = stack.pop()
                a = stack.pop()
                obj_a=heap[b]
                obj_b=heap[a]
                obj_a._div_(obj_b.float_val)
                stack.append(obj_a.id)
            pc += 1
        print('stack:', stack)
        a=stack.pop()
        obj_a=heap[a]
        val=obj_a.float_val
        print('stack debug:', val)


SRC = 'src.txt'


if __name__ == "__main__":
    def main():
      with tokenize.open(SRC) as f:
        tokens = tokenize.generate_tokens(
                f.readline) # Получили обьект генератор
        
        # lexer=Lexer('src.txt')
        tokenizer = Tokenizer(tokens)
        parser = Parser(tokenizer)
        tree = parser.program()
        compiler = Compiler()
        vm = Vm()
        compiler.compile(tree)
        b_c = compiler.get_bc()
        print(b_c)
        vm.run(b_c)

    main()
