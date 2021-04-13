# --------------------------------------------------
#   Компилятор
# --------------------------------------------------
"""
   Представлены больше байт-кодов, чем реализованы
"""
from object_ import Object
import re
from struct import pack, unpack
from help_parse_funcs import read, isa
from pyobj import Frame
from opcodes import *
import logging

EXIT_FAIL = 1


def op_prior(str_char_op):
    """
        Приоритет арифметической операции
    """

    if str_char_op == "^":

        return 6
    elif str_char_op == "*":

        return 5
    elif str_char_op == "/":

        return 5
    elif str_char_op == "%":

        return 3
    elif str_char_op == "+":

        return 2
    elif str_char_op == "-":

        return 2


def isOp(c):
    """
        Это арифметическая операция?
    """

    if c == "-" or c == "+" or c == "*" or c == "/" or c == "%" or c == "^":
        return True
    return False


def opn(code_arif):
    """
        Перевод в обратную польскую запись
        @param code_arif список инфиксного выражения
        @return список  постфиксного выражения
    """
    """
       В списке должны быть числа типа float для работы с ними, вообще на этом построен компилятор
    """

    item_i = 0
    # Операндовый стек
    operat_stack = []
    # Выходной список
    resOpn = []

    len_code_arif = len(code_arif)
    while (item_i < len_code_arif):

        # получить следующий член выражения
        v = code_arif[item_i]
        item_i += 1
        # определить тип члена
        if isa(v, float):

            resOpn.append(v)
        elif re.match("[A-Za-z]+", v):

            resOpn.append(v)
        elif isa(v, str) and v[0] == '|':
            resOpn.append(v)
        elif isOp(v):

            while(len(operat_stack) > 0 and
                  operat_stack[-1] != "[" and
                  op_prior(v) <= op_prior(operat_stack[-1])):
                resOpn.append(operat_stack.pop())

            operat_stack.append(v)
        elif v == ']':

            while len(operat_stack) > 0:

                x = operat_stack.pop()
                if x == '[':

                    break
                resOpn.append(x)
        elif v == "[":
            operat_stack.append(v)
    while len(operat_stack) > 0:

        resOpn.append(operat_stack.pop())

    return resOpn
# -----------------------------------
#  Обьекты
#  Objects
# -----------------------------------

# ---------------------------------------------
#  Обьекты для компилятора и виртуальной машины.
#  Это бьекты типов.
#  Objects for compillet and virtual machine.
#  This is objects of data types.
# ---------------------------------------------


class ObjectFloat(Object):
    def __init__(self, v, type_):  # Initialize object by float value
        self.v = v
        self.type = type_

    def _str_(self):
        return self.v


class ObjectStr(Object):
    def __init__(self, v, type_):  # Initialize object by string value
        self.v = v
        self.type = type_

# ------------------------------------------------------------------------------------------------------
#  Кодовый обьект содержит дата-кодовые-обьекты(для згрузки байткодом и например количество аргументов)
#  и другие такие же кодовые обьекты, обязательно содержит байт-код.Должен составлятся компилятором и
#  использован виртуальной машиной.
#  Code object have data-code-objects(for loading by byte-code and for example number of arguments)
#  and other same code objects, and also have byte-code.It must be made by compiller and unboxed by
#  Virtual machine.
# ------------------------------------------------------------------------------------------------------


class Code:
    """
      Minimum code object
    """

    co_name = ""  # name of function, for module it will be "<module>"
    co_argcount = 0  # number of func parameters
    co_consts = []  # diffrent types of consts to load on stack
    co_names = []  # gloabal string names
    co_varnames = []  # local string names
    co_code = []  # byte-code

    def __str__(self):
        co_const_vals = ''
        len_co_consts_vals = len(self.co_consts)
        for i in range(len_co_consts_vals):
            co_const_vals += str(self.co_consts[i].v)+' '
        s = "\nco_name: {}\n co_argcount: {}\nco_consts: {}\nco_names: {}\nco_varnames: {}\nco_code: {}".format(
            self.co_name, self.co_argcount, co_const_vals, self.co_names, self.co_varnames, self.co_code)
        return s


class Compiller:

    def __init__(self):

        self.byte_code = []
        self.startIp = 0
        self.module_co = None  # object for class Code for global scope
        self.co_consts_ind = 0  # pointer to co_consts
        self.co_names_ind = 0  # pointer to co_names

        """
           Для формирования индекса переменной
        """
        self.nglobals = 0

        """
          карта name => index
        """
        self.globals = {}

    def generate(self, int_command):
        """"
          генерация байткода
          @param int_command добавляем число в список
        """

        self.byte_code.append(int_command)

    def varIndexByName(self, name):
        """
            Находит индекс переменной в глобальной карте
            @param _name имя переменной
            @return кортеж индекс и лейбл карты
        """
        """
         Просматриваем карту
        """
        for pair in self.globals.items():

            if pair[0] == name:

                return (pair[1], 'G')
            else:

                print("Undefined var:%s" % name)
                exit(EXIT_FAIL)

    def compille(self, SExp):
        """
           Parse nested and sequensed(maybe nested) lists by first word for generating
           byte-code
        """

        we_in_function = False  # determes if we in global scope or in local function
        print('SExp', SExp)

        if isa(SExp[0], float):  # We got a float value

            if not we_in_function:
                self.module_co.co_code.append(Iload_const)
                self.module_co.co_code.append(self.co_consts_ind)
                self.module_co.co_consts.append(
                    ObjectFloat(SExp[0], "<float>"))
                self.co_consts_ind += 1

        elif isa(SExp[0], str) and SExp[0][0] == '|':  # We got a string value

            if not we_in_function:
                self.module_co.co_code.append(Iload_const)
                self.module_co.co_code.append(self.co_consts_ind)
                self.module_co.co_consts.append(
                    ObjectStr(SExp[0][1:], "<str>"))
                self.co_consts_ind += 1

        elif SExp[0] == '//':  # Это комментарии

            pass

        elif SExp[0] == 'set!':  # Create gloabal var name in module scope or local variable

            (_, var_name, exp) = SExp

            self.compille(exp)
            if not we_in_function:
                self.module_co.co_code.append(Istore_name)
                self.module_co.co_code.append(self.co_names_ind)
                self.module_co.co_names.append(ObjectStr(var_name, "<str>"))
                self.co_names_ind += 1
        elif SExp[0] == '$':
            # Recursivly parse sequensed (maybe they contain nested lists) lists
            # In source text we always begin with this symbol and in the begining of
            # functions

            self.module_co = Code()
            if not we_in_function:
                self.module_co.co_name = '<module>'
            for exp in SExp[1:]:

                self.compille(exp)

        elif SExp[0] == 'arif':  # Это арифметическое выражение

            resOpn = opn(SExp[1:])  # преобразуем из инфиксной записи в ОПЗ
            """
              Заменяем в списке операции и индификаторы переменных(на индексы)
            """
            print('res opn', resOpn)
            for i in resOpn:

                if isOp(i):

                    if i == "+":

                        self.module_co.co_code.append(Iadd)
                    if i == "-":

                        self.module_co.co_code.append(Isub)
                    if i == "*":

                        self.module_co.co_code.append(Imult)
                    if i == "/":

                        self.module_co.co_code.append(Idiv)
                    if i == "%":

                        self.module_co.co_code.append(Irem)
                    if i == "^":

                        self.module_co.co_code.append(Ipow)

                elif isa(i, float):   # We got a float value
                    if not we_in_function:
                        self.module_co.co_code.append(Iload_const)
                        self.module_co.co_code.append(self.co_consts_ind)
                        self.module_co.co_consts.append(
                            ObjectFloat(i, "<float>"))
                        self.co_consts_ind += 1
                elif isa(i, str) and i[0] == '|':  # We got a string value
                    if not we_in_function:
                        self.module_co.co_code.append(Iload_const)
                        self.module_co.co_code.append(self.co_consts_ind)
                        self.module_co.co_consts.append(
                            ObjectStr(i[1:], "<str>"))
                        self.co_consts_ind += 1

        elif SExp[0] == '<':  # сравнить на меньше

            (_, list_arif1, list_arif2) = SExp

            self.compille(list_arif1)
            self.compille(list_arif2)
            self.generate(Ilt)

        elif SExp[0] == '=':  # сравнить на равенство

            (_, list_arif1, list_arif2) = SExp

            self.compille(list_arif1)
            self.compille(list_arif2)
            self.generate(Ieq)

        elif SExp[0] == 'if':  # если

            (_, list_test, list_trueEpr, list_falseExpr) = SExp

            self.compille(list_test)
            self.generate(BRF)
            self.generate(0)
            self.generate(0)
            nAddr0_1 = len(self.byte_code)
            self.compille(list_trueEpr)
            self.generate(BR)
            self.generate(0)
            self.generate(0)
            nAddr1_2 = len(self.byte_code)
            delta1 = nAddr1_2-nAddr0_1
            self.byte_code[nAddr0_1-2] = self.short2bytes(delta1)[0]
            self.byte_code[nAddr0_1-1] = self.short2bytes(delta1)[1]
            self.compille(list_falseExpr)
            nAddr3_4 = len(self.byte_code)
            delta2 = (nAddr3_4-nAddr1_2)+2
            self.byte_code[nAddr1_2-2] = self.short2bytes(delta2)[0]
            self.byte_code[nAddr1_2-1] = self.short2bytes(delta2)[1]

        elif SExp[0] == 'while':  # пока

            (_, list_test, list_whileBody) = SExp

            nAddr1_2 = len(self.byte_code)
            self.compille(list_test)
            self.generate(BRF)
            self.generate(0)
            self.generate(0)
            nAddr0_1 = len(self.byte_code)
            self.compille(list_whileBody)
            self.generate(BR)
            self.generate(0)
            self.generate(0)
            nAddr2_3 = len(self.byte_code)
            delta1 = nAddr2_3-nAddr0_1
            delta2 = (nAddr2_3-nAddr1_2)-2
            self.byte_code[nAddr0_1-2] = self.short2bytes(delta1)[0]
            self.byte_code[nAddr0_1-1] = self.short2bytes(delta1)[1]
            self.byte_code[nAddr2_3-2] = self.short2bytes(-delta2)[0]
            self.byte_code[nAddr2_3-1] = self.short2bytes(-delta2)[1]

        elif SExp[0] == 'pass':  # ничего не делать

            self.generate(Inop)

        else:  # ошибка компиляции

            raise Exception("Unknown function name:%s" % SExp[0])

    def get_module_co_obj(self):
        """
             Возвращает результирующий байт код для ВМ
        """
        self.module_co.co_code.append(Istop)
        return self.module_co


def convert_float2objfloat(v):  # boxing: float_val->obj
    return ObjectFloat(v, "<float>")


def convert_str2objstr(v):  # boxing: float_val->obj
    return ObjectStr(v, "<str>")


def convert_objfloat2float(ob):  # unboxing
    return ob.v


def convert_objstr2str(ob):  # unboxing
    return ob.v


def incref(ob):  # увеличивает счетчик ссылок обьекта
    ob.ref_count += 1


def decref(ob):  # уменьшает счетчик ссылок обьекта
    ob.ref_count -= 1


def ukFloat_add(v, w):  # takes to references, works with them - unbox them, gives object
    v = convert_objfloat2float(v)
    w = convert_objfloat2float(w)
    v = v+w
    return convert_float2objfloat(v)


def ukStr_add(v, w):  # takes to references, works with them - unbox them, gives object
    v = convert_objstr2str(v)
    w = convert_objstr2str(w)
    v = v+w
    return convert_str2objstr(v)


def ukStr_mult(n, w):
    w = convert_objstr2str(w)
    v = w * n
    return convert_str2objstr(v)


def ukFloat_sub(v, w):  # takes to references, works with them - unbox them, gives object
    v = convert_objfloat2float(v)
    w = convert_objfloat2float(w)
    v = v-w
    return convert_float2objfloat(v)


def ukFloat_mult(v, w):  # takes to references, works with them - unbox them, gives object
    v = convert_objfloat2float(v)
    w = convert_objfloat2float(w)
    v = v*w
    return convert_float2objfloat(v)


def ukFloat_div(v, w):  # takes to references, works with them - unbox them, gives object
    v = convert_objfloat2float(v)
    w = convert_objfloat2float(w)
    v = v/w
    return convert_float2objfloat(v)


# -----------------------------
#  ВМ
#  Vm
# -----------------------------


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
h = logging.StreamHandler()
log.addHandler(h)


class Vm:
    def __init__(self):
        self.vm_instructions = ("Istore_name",  # 0
                                "Iload_const",  # 1
                                "Iadd",  # 2
                                "Imult",  # 3
                                "Idiv",  # 4
                                "Isub",  # 5
                                "Inop",  # 6
                                "Irem",  # 7
                                "Ipow",  # 8
                                "BR",  # 9
                                "BRT",  # 10
                                "BRF",  # 11
                                "ICONST",  # 12
                                "LOAD",  # 13
                                "GLOAD",  # 1
                                "Istop")
        self.frames = []
        self.frame = None
        self.return_value = None

    def print_instruction(self, b_c, pc, frame):
        op = b_c[pc]
        consts = frame.f_code.co_consts
        inst_name = self.vm_instructions[op]

        if op == HAVE_ARGUMENT:
            print("{0} {1} {2}".format(pc, inst_name, b_c[pc + 1]))
        elif op == WE_LOAD_CONSTS:
            print("{0} {1} {2}".format(pc, inst_name, consts[b_c[pc + 1]].v))
        else:
            print("{0} {1}".format(pc, inst_name))

    def run_code(self, code: Code):
        frame = Frame()
        frame.f_code = code
        #self.print_objs_arrs(code.co_consts, 'co_consts')
        #self.print_objs_arrs(code.co_names, 'co_names')
        val = self.eval_frame(frame)
        return val

    def print_objs_arrs(self, objs_arr, label):
        print(label, end=' ')
        for i in objs_arr:
            print(i.v, end=' ')
        print()

    def print_locals(self, locals_dict):
        print('locals->', end=' ')
        for pair in locals_dict.items():
            print(pair[0], ':', pair[1].v, end=', ')
        print('.')

    def eval_frame(self, frame: Frame,  trace=True):
        self.frame = frame
        self.stack = []  # Object stack
        pc = 0
        vm_is_running = True
        b_c = self.frame.f_code.co_code
        locals_ = self.frame.f_locals
        consts = self.frame.f_code.co_consts
        names = self.frame.f_code.co_names

        while vm_is_running:
            if trace:
                self.print_instruction(b_c, pc, self.frame)
            op = b_c[pc]
            if op == Istop:
                break
            elif op == Iload_const:
                pc += 1
                arg_ind = b_c[pc]  # we determe index for loading on stack
                ob = consts[arg_ind]
                self.stack.append(ob)
            elif op == Iadd:
                right = self.stack.pop()
                left = self.stack.pop()
                ob = None
                if right.type == '<float>' and left.type == '<float>':
                    ob = ukFloat_add(left, right)  # work with references
                elif right.type == '<str>' and left.type == '<str>':
                    ob = ukStr_add(left, right)  # work with references
                decref(right)  # work with references
                decref(left)   # work with references
                self.stack.append(ob)
            elif op == Isub:
                right = self.stack.pop()
                left = self.stack.pop()
                ob = ukFloat_sub(left, right)  # работаем с обьектами
                decref(right)  # работаем с обьектами
                decref(left)   # работаем с  обьектами
                self.stack.append(ob)
            elif op == Imult:
                ob = None
                right = self.stack.pop()
                left = self.stack.pop()
                if (right.type == '<float>' and left.type == '<float>') or (left.type == '<float>' and right.type == '<float>'):
                    ob = ukFloat_mult(left, right)  # работаем с обьектами
                elif (right.type == '<str>' and left.type == '<float>'):
                    n = convert_objfloat2float(left)
                    n = int(n)
                    ob = ukStr_mult(n, right)
                elif (right.type == '<float>' and left.type == '<str>'):
                    n = convert_objfloat2float(right)
                    n = int(n)
                    ob = ukStr_mult(n, left)
                decref(right)  # работаем с обьектами
                decref(left)   # работаем с обьектами
                self.stack.append(ob)
            elif op == Idiv:
                right = self.stack.pop()
                left = self.stack.pop()
                ob = ukFloat_div(left, right)  # работаем с обьектами
                decref(right)  # работаем с обьектами
                decref(left)   # работаем с обьектами
                self.stack.append(ob)
            elif op == Istore_name:
                pc += 1
                arg_ind = b_c[pc]
                locals_[names[arg_ind].v] = self.stack.pop()
            pc += 1
        if self.stack:
            ob = self.stack.pop()
            print('ob val {0} ob type {1}'.format(ob.v, ob.type))
        self.print_locals(locals_)
        return self.return_value


# **********************Программа********************************
c = None
with open('src.txt', 'r') as f:
    s = f.read()
    c = read(s)

compiller = Compiller()
vm = Vm()
compiller.compille(c)
module_co_obj = compiller.get_module_co_obj()
vm.run_code(module_co_obj)
