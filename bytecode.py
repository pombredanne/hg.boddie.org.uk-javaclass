#!/usr/bin/env python

"""
Java bytecode conversion. Specification found at the following URL:
http://java.sun.com/docs/books/vmspec/2nd-edition/html/Instructions2.doc.html

NOTE: Synchronized constructs are not actually supported.
"""

import dis # for access to Python bytecode values

# Bytecode production classes.

class BytecodeWriter:
    def __init__(self):
        self.loops = []
        self.jumps = []
        self.output = []
        self.position = 0

    # Special methods.

    def end_loop(self):
        current_loop_start = self.loops.pop()
        self.jump_absolute(current_loop_start)
        self.output[current_loop_start + 1] = self.position
        self.pop_block()

    def jump_to_next(self, status):
        self.jumps.push(self.position)
        if status:
            self.jump_if_true()
        else:
            self.jump_if_false()

    def start_next(self):
        current_jump_start = self.jumps.pop()
        self.output[current_jump_start + 1] = self.position

    # Normal bytecode generators.

    def for_iter(self):
        self.loops.push(self.position)
        self.output.append(opmap["FOR_ITER"])
        self.output.append(None) # To be filled in later
        self.position += 2

    def jump_if_false(self, offset=None):
        self.output.append(opmap["JUMP_IF_FALSE"])
        self.output.append(offset) # May be filled in later
        self.position += 2

    def jump_if_true(self, offset=None):
        self.output.append(opmap["JUMP_IF_TRUE"])
        self.output.append(offset) # May be filled in later
        self.position += 2

# Bytecode conversion.

class BytecodeReader:
    def __init__(self, class_file):
        self.class_file = class_file
        self.position_mapping = {}

    def process(self, code, program):
        self.java_position = 0
        while self.java_position < len(code):
            self.position_mapping[self.java_position] = program.position
            bytecode = ord(code[self.java_position])
            mnemonic, number_of_arguments = self.java_bytecodes[bytecode]
            self.process_bytecode(mnemonic, number_of_arguments)

    def process_bytecode(self, mnemonic, number_of_arguments):
        if number_of_arguments is not None:
            arguments = []
            for j in range(0, number_of_arguments):
                arguments.append(ord(code[self.java_position + 1 + j]))

            # Call the handler.
            getattr(self, mnemonic)(arguments, program)
        else:
            # Call the handler.
            number_of_arguments = getattr(self, mnemonic)(code[self.java_position+1:], program)

        self.java_position = self.java_position + 1 + number_of_arguments

    def nop(self, arguments, program):
        pass

    def aaload(self, arguments, program):
        # NOTE: No type checking performed.
        program.binary_subscr()

    def aastore(self, arguments, program):
        # NOTE: No type checking performed.
        # Stack: arrayref, index, value
        program.rot_three() # Stack: value, arrayref, index
        program.store_subscr()

    def aconst_null(self, arguments, program):
        program.load_global(None)

    def aload(self, arguments, program):
        program.load_fast(arguments[0])

    def aload_0(self, arguments, program):
        program.load_fast(0)

    def aload_1(self, arguments, program):
        program.load_fast(1)

    def aload_2(self, arguments, program):
        program.load_fast(2)

    def aload_3(self, arguments, program):
        program.load_fast(3)

    def anewarray(self, arguments, program):
        # NOTE: Does not raise NegativeArraySizeException.
        # NOTE: Not using the index to type the list/array.
        index = arguments[0] << 8 + arguments[1]

        program.build_list()
        program.setup_loop()
        program.load_global("range")
        program.load_const(0)       # Stack: list, count, range, 0
        program.rot_three()         # Stack: list, 0, count, range
        program.rot_three()         # Stack: list, range, 0, count
        program.call_function(2)    # Stack: list, range_list
        program.get_iter()          # Stack: list, iter
        program.for_iter()          # Stack: list, iter, value
        program.pop_top()           # Stack: list, iter
        program.rot_two()           # Stack: iter, list
        program.dup_top()           # Stack: iter, list, list
        program.load_attr("append") # Stack: iter, list, append
        program.load_global(None)   # Stack: iter, list, append, None
        program.call_function(1)    # Stack: iter, list, None
        program.pop_top()           # Stack: iter, list
        program.rot_two()           # Stack: list, iter
        program.end_loop()          # Back to for_iter above

    def areturn(self, arguments, program):
        program.return_value()

    def arraylength(self, arguments, program):
        program.load_global("len")  # Stack: arrayref, len
        program.rot_two()           # Stack: len, arrayref
        program.call_function(1)

    def astore(self, arguments, program):
        program.store_fast(arguments[0])

    def astore_0(self, arguments, program):
        program.store_fast(0)

    def astore_1(self, arguments, program):
        program.store_fast(1)

    def astore_2(self, arguments, program):
        program.store_fast(2)

    def astore_3(self, arguments, program):
        program.store_fast(3)

    def athrow(self, arguments, program):
        # NOTE: NullPointerException not raised where null/None is found on the stack.
        program.raise_varargs(1)

    baload = aaload
    bastore = aastore

    def bipush(self, arguments, program):
        program.load_const(arguments[0])

    caload = aaload
    castore = aastore

    def checkcast(self, arguments, program):
        index = arguments[0] << 8 + arguments[1]
        target_name = self.class_file.constants[index - 1].get_name()
        target_components = target_name.split("/")

        program.dup_top()                   # Stack: objectref, objectref
        program.load_global("isinstance")   # Stack: objectref, objectref, isinstance
        program.rot_two()                   # Stack: objectref, isinstance, objectref
        program.load_global(target_components[0])
        for target_component in target_components[1:]:
            program.load_attr(target_component)
        program.call_function(2)            # Stack: objectref

    def d2f(self, arguments, program):
        pass

    def d2i(self, arguments, program):
        program.load_global("int")  # Stack: value, int
        program.rot_two()           # Stack: int, value
        program.call_function(1)    # Stack: result

    d2l = d2i # Preserving Java semantics

    def dadd(self, arguments, program):
        # NOTE: No type checking performed.
        program.binary_add()

    daload = aaload
    dastore = aastore

    def dcmpg(self, arguments, program):
        # NOTE: No type checking performed.
        program.compare_op(">")

    def dcmpl(self, arguments, program):
        # NOTE: No type checking performed.
        program.compare_op("<")

    def dconst_0(self, arguments, program):
        program.load_const(0.0)

    def dconst_1(self, arguments, program):
        program.load_const(1.0)

    def ddiv(self, arguments, program):
        # NOTE: No type checking performed.
        program.binary_divide()

    dload = aload
    dload_0 = aload_0
    dload_1 = aload_1
    dload_2 = aload_2
    dload_3 = aload_3

    def dmul(self, arguments, program):
        # NOTE: No type checking performed.
        program.binary_multiply()

    def dneg(self, arguments, program):
        # NOTE: No type checking performed.
        program.unary_negative()

    def drem(self, arguments, program):
        # NOTE: No type checking performed.
        program.binary_modulo()

    dreturn = areturn
    dstore = astore
    dstore_0 = astore_0
    dstore_1 = astore_1
    dstore_2 = astore_2
    dstore_3 = astore_3

    def dsub(self, arguments, program):
        # NOTE: No type checking performed.
        program.binary_subtract()

    def dup(self, arguments, program):
        program.dup_top()

    def dup_x1(self, arguments, program):
        # Ignoring computational type categories.
        program.dup_top()
        program.rot_three()

    def dup_x2(self, arguments, program):
        # Ignoring computational type categories.
        program.dup_top()
        program.rot_four()

    dup2 = dup # Ignoring computational type categories
    dup2_x1 = dup_x1 # Ignoring computational type categories
    dup2_x2 = dup_x2 # Ignoring computational type categories

    def f2d(self, arguments, program):
        pass # Preserving Java semantics

    def f2i(self, arguments, program):
        program.load_global("int")  # Stack: value, int
        program.rot_two()           # Stack: int, value
        program.call_function(1)    # Stack: result

    f2l = f2i # Preserving Java semantics
    fadd = dadd
    faload = daload
    fastore = dastore
    fcmpg = dcmpg
    fcmpl = dcmpl
    fconst_0 = dconst_0
    fconst_1 = dconst_1

    def fconst_2(self, arguments, program):
        program.load_const(2.0)

    fdiv = ddiv
    fload = dload
    fload_0 = dload_0
    fload_1 = dload_1
    fload_2 = dload_2
    fload_3 = dload_3
    fmul = dmul
    fneg = dneg
    frem = drem
    freturn = dreturn
    fstore = dstore
    fstore_0 = dstore_0
    fstore_1 = dstore_1
    fstore_2 = dstore_2
    fstore_3 = dstore_3
    fsub = dsub

    def getfield(self, arguments, program):
        index = arguments[0] << 8 + arguments[1]
        target_name = self.class_file.constants[index - 1].get_name()
        # NOTE: Using the string version of the name which may contain incompatible characters.
        program.load_attr(str(target_name))

    getstatic = getfield # Ignoring Java restrictions

    def goto(self, arguments, program):
        offset = arguments[0] << 8 + arguments[1]
        java_absolute = self.java_position + offset
        program.jump_absolute(self.position_mapping[java_absolute])

    def goto_w(self, arguments, program):
        offset = arguments[0] << 24 + arguments[1] << 16 + arguments[2] << 8 + arguments[3]
        java_absolute = self.java_position + offset
        program.jump_absolute(self.position_mapping[java_absolute])

    def i2b(self, arguments, program):
        pass

    def i2c(self, arguments, program):
        program.load_global("chr")  # Stack: value, chr
        program.rot_two()           # Stack: chr, value
        program.call_function(1)    # Stack: result

    def i2d(self, arguments, program):
        program.load_global("float")    # Stack: value, float
        program.rot_two()               # Stack: float, value
        program.call_function(1)        # Stack: result

    i2f = i2d # Not distinguishing between float and double

    def i2l(self, arguments, program):
        pass # Preserving Java semantics

    def i2s(self, arguments, program):
        pass # Not distinguishing between int and short

    iadd = fadd
    iaload = faload

    def iand(self, arguments, program):
        # NOTE: No type checking performed.
        program.binary_and()

    iastore = fastore

    def iconst_m1(self, arguments, program):
        program.load_const(-1)

    def iconst_0(self, arguments, program):
        program.load_const(0)

    def iconst_1(self, arguments, program):
        program.load_const(1)

    def iconst_2(self, arguments, program):
        program.load_const(2)

    def iconst_3(self, arguments, program):
        program.load_const(3)

    def iconst_4(self, arguments, program):
        program.load_const(4)

    def iconst_5(self, arguments, program):
        program.load_const(5)

    idiv = fdiv

    def _if_xcmpx(self, arguments, program, op):
        offset = arguments[0] << 8 + arguments[1]
        java_absolute = self.java_position + offset
        program.compare_op(op)
        program.jump_to_next(0) # skip if false
        program.goto(offset)
        program.start_next()

    def if_acmpeq(self, arguments, program):
        # NOTE: No type checking performed.
        self._if_xcmpx(arguments, program, "is")

    def if_acmpne(self, arguments, program):
        # NOTE: No type checking performed.
        self._if_xcmpx(arguments, program, "is not")

    def if_icmpeq(self, arguments, program):
        # NOTE: No type checking performed.
        self._if_xcmpx(arguments, program, "==")

    def if_icmpne(self, arguments, program):
        # NOTE: No type checking performed.
        self._if_xcmpx(arguments, program, "!=")

    def if_icmplt(self, arguments, program):
        # NOTE: No type checking performed.
        self._if_xcmpx(arguments, program, "<")

    def if_icmpge(self, arguments, program):
        # NOTE: No type checking performed.
        self._if_xcmpx(arguments, program, ">=")

    def if_icmpgt(self, arguments, program):
        # NOTE: No type checking performed.
        self._if_xcmpx(arguments, program, ">")

    def if_icmple(self, arguments, program):
        # NOTE: No type checking performed.
        self._if_xcmpx(arguments, program, "<=")

    def ifeq(self, arguments, program):
        # NOTE: No type checking performed.
        program.load_const(0)
        self._if_xcmpx(arguments, program, "==")

    def ifne(self, arguments, program):
        # NOTE: No type checking performed.
        program.load_const(0)
        self._if_xcmpx(arguments, program, "!=")

    def iflt(self, arguments, program):
        # NOTE: No type checking performed.
        program.load_const(0)
        self._if_xcmpx(arguments, program, "<")

    def ifge(self, arguments, program):
        # NOTE: No type checking performed.
        program.load_const(0)
        self._if_xcmpx(arguments, program, ">=")

    def ifgt(self, arguments, program):
        # NOTE: No type checking performed.
        program.load_const(0)
        self._if_xcmpx(arguments, program, ">")

    def ifle(self, arguments, program):
        # NOTE: No type checking performed.
        program.load_const(0)
        self._if_xcmpx(arguments, program, "<=")

    def ifnonnull(self, arguments, program):
        # NOTE: No type checking performed.
        program.load_const(None)
        self._if_xcmpx(arguments, program, "is not")

    def ifnull(self, arguments, program):
        # NOTE: No type checking performed.
        program.load_const(None)
        self._if_xcmpx(arguments, program, "is")

    def iinc(self, arguments, program):
        # NOTE: No type checking performed.
        program.load_fast(arguments[0])
        program.load_const(arguments[1])
        program.binary_add()

    iload = fload
    iload_0 = fload_0
    iload_1 = fload_1
    iload_2 = fload_2
    iload_3 = fload_3
    imul = fmul
    ineg = fneg

    def instanceof(self, arguments, program):
        index = arguments[0] << 8 + arguments[1]
        target_name = self.class_file.constants[index - 1].get_name()
        target_components = target_name.split("/")

        program.load_global("isinstance")   # Stack: objectref, isinstance
        program.rot_two()                   # Stack: isinstance, objectref
        program.load_global(target_components[0])
        for target_component in target_components[1:]:
            program.load_attr(target_component)
        program.call_function(2)            # Stack: result

    def _invoke(self, target_name, program):
        program.rot_two()                   # Stack: tuple, objectref
        # NOTE: Using the string version of the name which may contain incompatible characters.
        program.load_attr(str(target_name)) # Stack: tuple, method
        program.rot_two()                   # Stack: method, tuple
        program.load_global("apply")        # Stack: method, tuple, apply
        program.rot_three()                 # Stack: apply, method, tuple
        program.call_function(2)

    def invokeinterface(self, arguments, program):
        # NOTE: This implementation does not perform the necessary checks for
        # NOTE: signature-based polymorphism.
        # NOTE: Java rules not specifically obeyed.
        index = arguments[0] << 8 + arguments[1]
        count = arguments[2]
        target_name = self.class_file.constants[index - 1].get_name()
        # Stack: objectref, arg1, arg2, ...
        program.build_tuple(count)          # Stack: objectref, tuple
        self._invoke(target_name, program)

    def invokespecial(self, arguments, program):
        # NOTE: This implementation does not perform the necessary checks for
        # NOTE: signature-based polymorphism.
        # NOTE: Java rules not specifically obeyed.
        index = arguments[0] << 8 + arguments[1]
        target = self.class_file.constants[index - 1]
        target_name = target.get_name()
        # Get the number of parameters from the descriptor.
        count = len(target.get_descriptor()[0])
        # Stack: objectref, arg1, arg2, ...
        program.build_tuple(count)          # Stack: objectref, tuple
        self._invoke(target_name, program)

    def invokestatic(self, arguments, program):
        # NOTE: This implementation does not perform the necessary checks for
        # NOTE: signature-based polymorphism.
        # NOTE: Java rules not specifically obeyed.
        index = arguments[0] << 8 + arguments[1]
        target = self.class_file.constants[index - 1]
        target_name = target.get_name()
        # Get the number of parameters from the descriptor.
        count = len(target.get_descriptor()[0])
        # Stack: arg1, arg2, ...
        program.build_tuple(count)  # Stack: tuple
        # NOTE: Should probably use Python static methods.
        program.load_name("self")   # Stack: tuple, self
        self._invoke(target_name, program)

    invokevirtual = invokeinterface # Ignoring Java rules

    def ior(self, arguments, program):
        # NOTE: No type checking performed.
        program.binary_or()

    irem = frem
    ireturn = freturn

    def ishl(self, arguments, program):
        # NOTE: No type checking performed.
        # NOTE: Not verified.
        program.binary_lshift()

    def ishr(self, arguments, program):
        # NOTE: No type checking performed.
        # NOTE: Not verified.
        program.binary_rshift()

    istore = fstore
    istore_0 = fstore_0
    istore_1 = fstore_1
    istore_2 = fstore_2
    istore_3 = fstore_3
    isub = fsub
    iushr = ishr # Ignoring distinctions between arithmetic and logical shifts

    def ishr(self, arguments, program):
        # NOTE: No type checking performed.
        program.binary_xor()

    def jsr(self, arguments, program):
        offset = arguments[0] << 8 + arguments[1]
        java_absolute = self.java_position + offset
        # NOTE: To be implemented.

    def wide(self, code, program):
        # NOTE: To be implemented.
        return number_of_arguments

    java_bytecodes = {
        # code : (mnemonic, number of following bytes, change in stack)
        0 : ("nop", 0),
        1 : ("aconst_null", 0),
        2 : ("iconst_m1", 0),
        3 : ("iconst_0", 0),
        4 : ("iconst_1", 0),
        5 : ("iconst_2", 0),
        6 : ("iconst_3", 0),
        7 : ("iconst_4", 0),
        8 : ("iconst_5", 0),
        9 : ("lconst_0", 0),
        10 : ("lconst_1", 0),
        11 : ("fconst_0", 0),
        12 : ("fconst_1", 0),
        13 : ("fconst_2", 0),
        14 : ("dconst_0", 0),
        15 : ("dconst_1", 0),
        16 : ("bipush", 1),
        17 : ("sipush", 2),
        18 : ("ldc", 1),
        19 : ("ldc_w", 2),
        20 : ("ldc2_w", 2),
        21 : ("iload", 1),
        22 : ("lload", 1),
        23 : ("fload", 1),
        24 : ("dload", 1),
        25 : ("aload", 1),
        26 : ("iload_0", 0),
        27 : ("iload_1", 0),
        28 : ("iload_2", 0),
        29 : ("iload_3", 0),
        30 : ("lload_0", 0),
        31 : ("lload_1", 0),
        32 : ("lload_2", 0),
        33 : ("lload_3", 0),
        34 : ("fload_0", 0),
        35 : ("fload_1", 0),
        36 : ("fload_2", 0),
        37 : ("fload_3", 0),
        38 : ("dload_0", 0),
        39 : ("dload_1", 0),
        40 : ("dload_2", 0),
        41 : ("dload_3", 0),
        42 : ("aload_0", 0),
        43 : ("aload_1", 0),
        44 : ("aload_2", 0),
        45 : ("aload_3", 0),
        46 : ("iaload", 0),
        47 : ("laload", 0),
        48 : ("faload", 0),
        49 : ("daload", 0),
        50 : ("aaload", 0),
        51 : ("baload", 0),
        52 : ("caload", 0),
        53 : ("saload", 0),
        54 : ("istore", 1),
        55 : ("lstore", 1),
        56 : ("fstore", 1),
        57 : ("dstore", 1),
        58 : ("astore", 1),
        59 : ("istore_0", 0),
        60 : ("istore_1", 0),
        61 : ("istore_2", 0),
        62 : ("istore_3", 0),
        63 : ("lstore_0", 0),
        64 : ("lstore_1", 0),
        65 : ("lstore_2", 0),
        66 : ("lstore_3", 0),
        67 : ("fstore_0", 0),
        68 : ("fstore_1", 0),
        69 : ("fstore_2", 0),
        70 : ("fstore_3", 0),
        71 : ("dstore_0", 0),
        72 : ("dstore_1", 0),
        73 : ("dstore_2", 0),
        74 : ("dstore_3", 0),
        75 : ("astore_0", 0),
        76 : ("astore_1", 0),
        77 : ("astore_2", 0),
        78 : ("astore_3", 0),
        79 : ("iastore", 0),
        80 : ("lastore", 0),
        81 : ("fastore", 0),
        82 : ("dastore", 0),
        83 : ("aastore", 0),
        84 : ("bastore", 0),
        85 : ("castore", 0),
        86 : ("sastore", 0),
        87 : ("pop", 0),
        88 : ("pop2", 0),
        89 : ("dup", 0),
        90 : ("dup_x1", 0),
        91 : ("dup_x2", 0),
        92 : ("dup2", 0),
        93 : ("dup2_x1", 0),
        94 : ("dup2_x2", 0),
        95 : ("swap", 0),
        96 : ("iadd", 0),
        97 : ("ladd", 0),
        98 : ("fadd", 0),
        99 : ("dadd", 0),
        100 : ("isub", 0),
        101 : ("lsub", 0),
        102 : ("fsub", 0),
        103 : ("dsub", 0),
        104 : ("imul", 0),
        105 : ("lmul", 0),
        106 : ("fmul", 0),
        107 : ("dmul", 0),
        108 : ("idiv", 0),
        109 : ("ldiv", 0),
        110 : ("fdiv", 0),
        111 : ("ddiv", 0),
        112 : ("irem", 0),
        113 : ("lrem", 0),
        114 : ("frem", 0),
        115 : ("drem", 0),
        116 : ("ineg", 0),
        117 : ("lneg", 0),
        118 : ("fneg", 0),
        119 : ("dneg", 0),
        120 : ("ishl", 0),
        121 : ("lshl", 0),
        122 : ("ishr", 0),
        123 : ("lshr", 0),
        124 : ("iushr", 0),
        125 : ("lushr", 0),
        126 : ("iand", 0),
        127 : ("land", 0),
        128 : ("ior", 0),
        129 : ("lor", 0),
        130 : ("ixor", 0),
        131 : ("lxor", 0),
        132 : ("iinc", 2),
        133 : ("i2l", 0),
        134 : ("i2f", 0),
        135 : ("i2d", 0),
        136 : ("l2i", 0),
        137 : ("l2f", 0),
        138 : ("l2d", 0),
        139 : ("f2i", 0),
        140 : ("f2l", 0),
        141 : ("f2d", 0),
        142 : ("d2i", 0),
        143 : ("d2l", 0),
        144 : ("d2f", 0),
        145 : ("i2b", 0),
        146 : ("i2c", 0),
        147 : ("i2s", 0),
        148 : ("lcmp", 0),
        149 : ("fcmpl", 0),
        150 : ("fcmpg", 0),
        151 : ("dcmpl", 0),
        152 : ("dcmpg", 0),
        153 : ("ifeq", 2),
        154 : ("ifne", 2),
        155 : ("iflt", 2),
        156 : ("ifge", 2),
        157 : ("ifgt", 2),
        158 : ("ifle", 2),
        159 : ("if_icmpeq", 2),
        160 : ("if_icmpne", 2),
        161 : ("if_icmplt", 2),
        162 : ("if_icmpge", 2),
        163 : ("if_icmpgt", 2),
        164 : ("if_icmple", 2),
        165 : ("if_acmpeq", 2),
        166 : ("if_acmpne", 2),
        167 : ("goto", 2),
        168 : ("jsr", 2),
        169 : ("ret", 1),
        170 : ("tableswitch", None), # variable number of arguments
        171 : ("lookupswitch", None), # variable number of arguments
        172 : ("ireturn", 0),
        173 : ("lreturn", 0),
        174 : ("freturn", 0),
        175 : ("dreturn", 0),
        176 : ("areturn", 0),
        177 : ("return", 0),
        178 : ("getstatic", 2),
        179 : ("putstatic", 2),
        180 : ("getfield", 2),
        181 : ("putfield", 2),
        182 : ("invokevirtual", 2),
        183 : ("invokespecial", 2),
        184 : ("invokestatic", 2),
        185 : ("invokeinterface", 4),
        187 : ("new", 2),
        188 : ("newarray", 1),
        189 : ("anewarray", 2),
        190 : ("arraylength", 0),
        191 : ("athrow", 0),
        192 : ("checkcast", 2),
        193 : ("instanceof", 2),
        194 : ("monitorenter", 0),
        195 : ("monitorexit", 0),
        196 : ("wide", None), # 3 or 5 arguments, stack changes according to modified element
        197 : ("multianewarray", 3),
        198 : ("ifnull", 2),
        199 : ("ifnonnull", 2),
        200 : ("goto_w", 4),
        201 : ("jsr_w", 4),
        }

if __name__ == "__main__":
    import sys
    from classfile import ClassFile
    f = open(sys.argv[1])
    c = ClassFile(f.read())

# vim: tabstop=4 expandtab shiftwidth=4
