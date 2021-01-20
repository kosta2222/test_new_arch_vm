import sys


# байткоды
push_fl = 0
push_str = 1
add = 2
mul = 3
printt = 4
stop = 5

test_wrong_op = 6

# Операции как классы


class PushFl:
    def __init__(self, stack):
        self._stack = stack

    def ex(self, arg=None):
        self._stack.append(arg)


class PushStr:
    def __init__(self, stack):
        self._stack = stack

    def ex(self, arg=None):
        self._stack.append(arg)


class Add:
    def __init__(self, stack):
        self._stack = stack

    def ex(self, arg=None):
        a = self._stack.pop()
        b = self._stack.pop()
        self._stack.append(a+b)


class Mul:
    def __init__(self, stack):
        self._stack = stack

    def ex(self, arg=None):
        a = self._stack.pop()
        b = self._stack.pop()
        self._stack.append(a*b)


class Printt:
    def __init__(self, stack):
        self._stack = stack

    def ex(self, arg=None):
        a = self._stack.pop()
        print("<print>", a)


class Stop:
    def __init__(self):
       pass
    def ex(self, arg=None):
        sys.exit(0)

# Вм


class Vm:
    def __init__(self, b_c):
        stack = []
        self.ip = 0
        self.b_c = b_c
        self.cmds = [PushFl(stack), PushStr(stack), Add(
            stack), Mul(stack), Printt(stack), Stop()]

    def add_cmd(self, classs):  # можно добавлять новую операцию
        self.cmds.append(classs)

    def vm_ex(self):
        vm_running = True
        i = 0
        while vm_running:
            try:
                # почти нет перебора, операции находятся на соответвующих индексах
                op = self.b_c[i]
                if op in range(0, 2):  # определяем байткоды с параметрами
                    i += 1
                    arg = self.b_c[i]
                    self.cmds[op].ex(arg)
                else:               # байт-коды без параметров
                    self.cmds[op].ex()
                i += 1
            except IndexError:
                print("operation not recognized", op)
                return

# ==========


def main():
    # (10-4)/3 - ?
    code = (push_fl, 1/3, push_fl, 10, push_fl, -4, add, mul, printt, 
    # test_wrong_op,
    stop)

    vm = Vm(code)
    vm.vm_ex()


main()
