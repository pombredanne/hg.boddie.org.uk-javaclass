#!/usr/bin/env python

"""
Java bytecode conversion. Specification found at the following URL:
http://java.sun.com/docs/books/vmspec/2nd-edition/html/Instructions2.doc.html

NOTE: Synchronized constructs are not actually supported.
"""

from dis import opmap, cmp_op # for access to Python bytecode values and operators
from UserDict import UserDict

# Bytecode production classes.

class BytecodeWriter:

    "A Python bytecode writer."

    def __init__(self):
        # A stack of loop block or exception block start positions.
        self.blocks = []

        # A stack of exception block handler pointers.
        self.exception_handlers = []

        # A dictionary mapping labels to jump instructions referencing such labels.
        self.jumps = {}

        # The output values, including "lazy" subvalues which will need evaluating.
        self.output = []

        # The current Python bytecode instruction position.
        self.position = 0

        # Stack depth estimation.
        self.stack_depth = 0
        self.max_stack_depth = 0

        # Local variable estimation.
        self.max_locals = 0

        # Mapping from values to indexes.
        self.constants = {}

        # Mapping from names to indexes.
        # NOTE: This may be acquired from elsewhere.
        #self.globals = {}

        # Mapping from names to indexes.
        self.names = {}

        # A list of constants used as exception handler return addresses.
        self.constants_for_exceptions = []

    def get_output(self):
        output = []
        for element in self.output:
            if isinstance(element, LazySubValue):
                value = element.value
            else:
                value = element
            output.append(chr(value))
        return "".join(output)

    def get_constants(self):
        l = self._get_list(self._invert(self.constants))
        result = []
        for i in l:
            if isinstance(i, LazyValue):
                result.append(i.get_value())
            else:
                result.append(i)
        return result

    #def get_globals(self):
    #    return self._get_list(self._invert(self.globals))

    def get_names(self):
        return self._get_list(self._invert(self.names))

    def _invert(self, d):
        inverted = {}
        for k, v in d.items():
            inverted[v] = k
        return inverted

    def _get_list(self, d):
        l = []
        for i in range(0, len(d.keys())):
            l.append(d[i])
        return l

    # Administrative methods.

    def update_stack_depth(self, change):
        self.stack_depth += change
        if self.stack_depth > self.max_stack_depth:
            self.max_stack_depth = self.stack_depth

    def update_locals(self, index):
        if index > self.max_locals:
            self.max_locals = index

    # Special methods.

    def _write_value(self, value):
        if isinstance(value, LazyValue):
            # NOTE: Assume a 16-bit value.
            self.output.append(value.values[0])
            self.output.append(value.values[1])
            self.position += 2
        elif value <= 0xffff:
            self.output.append(value & 0xff)
            self.output.append((value & 0xff00) >> 8)
            self.position += 2
        else:
            # NOTE: EXTENDED_ARG not yet supported.
            raise ValueError, value

    def setup_loop(self):
        self.blocks.append(self.position)
        self.output.append(opmap["SETUP_LOOP"])
        self.position += 1
        self._write_value(0) # To be filled in later

    def end_loop(self):
        current_loop_start = self.blocks.pop()
        self.jump_absolute(current_loop_start)
        # NOTE: Using 3 as the assumed length of the SETUP_LOOP instruction.
        # NOTE: 8-bit limit.
        self.output[current_loop_start + 1] = self.position - current_loop_start - 3
        self.output[current_loop_start + 2] = 0
        self.pop_block()

    def jump_to_label(self, status, name):
        # Record the instruction using the jump.
        jump_instruction = self.position
        if status is None:
            self.jump_forward()
        elif status:
            self.jump_if_true()
        else:
            self.jump_if_false()
        # Record the following instruction, too.
        if not self.jumps.has_key(name):
            self.jumps[name] = []
        self.jumps[name].append((jump_instruction, self.position))

    def start_label(self, name):
        # Fill in all jump instructions.
        for jump_instruction, following_instruction in self.jumps[name]:
            # NOTE: 8-bit limit.
            self.output[jump_instruction + 1] = self.position - following_instruction
            self.output[jump_instruction + 2] = 0
        del self.jumps[name]

    def load_const_ret(self, value):
        self.constants_for_exceptions.append(value)
        self.load_const(value)

    def ret(self, index):
        self.load_fast(index)
        # Previously, the constant stored on the stack by jsr/jsr_w was stored
        # in a local variable. In the JVM, extracting the value from the local
        # variable and jumping can be done at runtime. In the Python VM, any
        # jump target must be known in advance and written into the bytecode.
        for constant in self.constants_for_exceptions:
            self.dup_top()              # Stack: actual-address, actual-address
            self.load_const(constant)   # Stack: actual-address, actual-address, suggested-address
            self.compare_op("==")       # Stack: actual-address, result
            self.jump_to_label(0, "const")
            self.pop_top()              # Stack: actual-address
            self.pop_top()              # Stack:
            self.jump_absolute(constant)
            self.start_label("const")
            self.pop_top()              # Stack: actual-address
        # NOTE: If we get here, something is really wrong.
        self.pop_top()              # Stack:

    def setup_except(self, target):
        self.blocks.append(self.position)
        self.exception_handlers.append(target)
        #print "-", self.position, target
        self.output.append(opmap["SETUP_EXCEPT"])
        self.position += 1
        self._write_value(0) # To be filled in later

    def setup_finally(self, target):
        self.blocks.append(self.position)
        self.exception_handlers.append(target)
        #print "-", self.position, target
        self.output.append(opmap["SETUP_FINALLY"])
        self.position += 1
        self._write_value(0) # To be filled in later

    def end_exception(self):
        current_exception_start = self.blocks.pop()
        # Convert the "lazy" absolute value.
        current_exception_target = self.exception_handlers.pop()
        target = current_exception_target.get_value()
        #print "*", current_exception_start, target
        # NOTE: Using 3 as the assumed length of the SETUP_* instruction.
        # NOTE: 8-bit limit.
        self.output[current_exception_start + 1] = target - current_exception_start - 3
        self.output[current_exception_start + 2] = 0

    def start_handler(self, exc_name):
        # Where handlers are begun, produce bytecode to test the type of
        # the exception.
        self.dup_top()                      # Stack: exception, exception
        self.load_global(str(exc_name))     # Stack: exception, exception, handled-exception
        self.compare_op("exception match")  # Stack: exception, result
        self.jump_to_label(1, "handler")
        self.pop_top()
        self.end_finally()
        self.start_label("handler")
        self.pop_top()

    # Complicated methods.

    def load_const(self, value):
        self.output.append(opmap["LOAD_CONST"])
        if not self.constants.has_key(value):
            self.constants[value] = len(self.constants.keys())
        self.position += 1
        self._write_value(self.constants[value])
        self.update_stack_depth(1)

    def load_global(self, name):
        self.output.append(opmap["LOAD_GLOBAL"])
        if not self.names.has_key(name):
            self.names[name] = len(self.names.keys())
        self.position += 1
        self._write_value(self.names[name])
        self.update_stack_depth(1)

    def load_attr(self, name):
        self.output.append(opmap["LOAD_ATTR"])
        if not self.names.has_key(name):
            self.names[name] = len(self.names.keys())
        self.position += 1
        self._write_value(self.names[name])

    def load_name(self, name):
        self.output.append(opmap["LOAD_NAME"])
        if not self.names.has_key(name):
            self.names[name] = len(self.names.keys())
        self.position += 1
        self._write_value(self.names[name])
        self.update_stack_depth(1)

    def load_fast(self, index):
        self.output.append(opmap["LOAD_FAST"])
        self.position += 1
        self._write_value(index)
        self.update_stack_depth(1)
        self.update_locals(index)

    def store_attr(self, name):
        self.output.append(opmap["STORE_ATTR"])
        if not self.names.has_key(name):
            self.names[name] = len(self.names.keys())
        self.position += 1
        self._write_value(self.names[name])
        self.update_stack_depth(-1)

    def store_fast(self, index):
        self.output.append(opmap["STORE_FAST"])
        self.position += 1
        self._write_value(index)
        self.update_stack_depth(-1)
        self.update_locals(index)

    # Normal bytecode generators.

    def for_iter(self):
        self.blocks.append(self.position)
        self.output.append(opmap["FOR_ITER"])
        self.position += 1
        self._write_value(0) # To be filled in later
        self.update_stack_depth(1)

    def jump_if_false(self, offset=0):
        self.output.append(opmap["JUMP_IF_FALSE"])
        self.position += 1
        self._write_value(offset) # May be filled in later

    def jump_if_true(self, offset=0):
        self.output.append(opmap["JUMP_IF_TRUE"])
        self.position += 1
        self._write_value(offset) # May be filled in later

    def jump_forward(self, offset=0):
        self.output.append(opmap["JUMP_FORWARD"])
        self.position += 1
        self._write_value(offset) # May be filled in later

    def jump_absolute(self, address=0):
        self.output.append(opmap["JUMP_ABSOLUTE"])
        self.position += 1
        self._write_value(address) # May be filled in later

    def build_tuple(self, count):
        self.output.append(opmap["BUILD_TUPLE"])
        self.position += 1
        self._write_value(count)
        self.update_stack_depth(-(count - 1))

    def build_list(self, count):
        self.output.append(opmap["BUILD_LIST"])
        self.position += 1
        self._write_value(count)
        self.update_stack_depth(-(count - 1))

    def pop_top(self):
        self.output.append(opmap["POP_TOP"])
        self.position += 1
        self.update_stack_depth(-1)

    def dup_top(self):
        self.output.append(opmap["DUP_TOP"])
        self.position += 1
        self.update_stack_depth(1)

    def rot_two(self):
        self.output.append(opmap["ROT_TWO"])
        self.position += 1

    def rot_three(self):
        self.output.append(opmap["ROT_THREE"])
        self.position += 1

    def rot_four(self):
        self.output.append(opmap["ROT_FOUR"])
        self.position += 1

    def call_function(self, count):
        self.output.append(opmap["CALL_FUNCTION"])
        self.position += 1
        self._write_value(count)
        self.update_stack_depth(-count)

    def binary_subscr(self):
        self.output.append(opmap["BINARY_SUBSCR"])
        self.position += 1
        self.update_stack_depth(-1)

    def binary_add(self):
        self.output.append(opmap["BINARY_ADD"])
        self.position += 1
        self.update_stack_depth(-1)

    def binary_divide(self):
        self.output.append(opmap["BINARY_DIVIDE"])
        self.position += 1
        self.update_stack_depth(-1)

    def binary_multiply(self):
        self.output.append(opmap["BINARY_MULTIPLY"])
        self.position += 1
        self.update_stack_depth(-1)

    def binary_modulo(self):
        self.output.append(opmap["BINARY_MODULO"])
        self.position += 1
        self.update_stack_depth(-1)

    def binary_subtract(self):
        self.output.append(opmap["BINARY_SUBTRACT"])
        self.position += 1
        self.update_stack_depth(-1)

    def binary_and(self):
        self.output.append(opmap["BINARY_AND"])
        self.position += 1
        self.update_stack_depth(-1)

    def binary_or(self):
        self.output.append(opmap["BINARY_XOR"])
        self.position += 1
        self.update_stack_depth(-1)

    def binary_lshift(self):
        self.output.append(opmap["BINARY_LSHIFT"])
        self.position += 1
        self.update_stack_depth(-1)

    def binary_rshift(self):
        self.output.append(opmap["BINARY_RSHIFT"])
        self.position += 1
        self.update_stack_depth(-1)

    def binary_xor(self):
        self.output.append(opmap["BINARY_XOR"])
        self.position += 1
        self.update_stack_depth(-1)

    def compare_op(self, op):
        self.output.append(opmap["COMPARE_OP"])
        self.position += 1
        self._write_value(list(cmp_op).index(op))
        self.update_stack_depth(-1)

    def return_value(self):
        self.output.append(opmap["RETURN_VALUE"])
        self.position += 1
        self.update_stack_depth(-1)

    def raise_varargs(self, count):
        self.output.append(opmap["RAISE_VARARGS"])
        self.position += 1
        self._write_value(count)

    def pop_block(self):
        self.output.append(opmap["POP_BLOCK"])
        self.position += 1

    def end_finally(self):
        self.output.append(opmap["END_FINALLY"])
        self.position += 1

# Utility classes and functions.

class LazyDict(UserDict):
    def __getitem__(self, key):
        if not self.data.has_key(key):
            # NOTE: Assume 16-bit value.
            self.data[key] = LazyValue(2)
        return self.data[key]
    def __setitem__(self, key, value):
        if self.data.has_key(key):
            existing_value = self.data[key]
            if isinstance(existing_value, LazyValue):
                existing_value.set_value(value)
                return
        self.data[key] = value

class LazyValue:
    def __init__(self, nvalues):
        self.values = []
        for i in range(0, nvalues):
            self.values.append(LazySubValue())
    def set_value(self, value):
        # NOTE: Assume at least 16-bit value. No "filling" performed.
        if value <= 0xffff:
            self.values[0].set_value(value & 0xff)
            self.values[1].set_value((value & 0xff00) >> 8)
        else:
            # NOTE: EXTENDED_ARG not yet supported.
            raise ValueError, value
    def get_value(self):
        value = 0
        values = self.values[:]
        for i in range(0, len(values)):
            value = (value << 8) + values.pop().value
        return value

class LazySubValue:
    def __init__(self):
        self.value = 0
    def set_value(self, value):
        self.value = value

def signed(value, limit):

    """
    Return the signed integer from the unsigned 'value', where 'limit' (a value
    one greater than the highest possible positive integer) is used to determine
    whether a negative or positive result is produced.
    """

    d, r = divmod(value, limit)
    if d == 1:
        mask = limit * 2 - 1
        return -1 - (value ^ mask)
    else:
        return value

def signed2(value):
    return signed(value, 0x8000)

def signed4(value):
    return signed(value, 0x80000000)

# Bytecode conversion.

class BytecodeReader:

    "A generic Java bytecode reader."

    def __init__(self, class_file):
        self.class_file = class_file
        self.position_mapping = LazyDict()

    def process(self, method, program):
        self.java_position = 0
        self.in_finally = 0
        self.method = method

        # NOTE: Not guaranteed.
        attribute = method.attributes[0]
        code, exception_table = attribute.code, attribute.exception_table

        # Produce a structure which permits fast access to exception details.
        exception_block_start = {}
        exception_block_end = {}
        exception_block_handler = {}
        reversed_exception_table = exception_table[:]
        reversed_exception_table.reverse()

        # Later entries have wider coverage than earlier entries.
        for exception in reversed_exception_table:
            # Index start positions.
            if not exception_block_start.has_key(exception.start_pc):
                exception_block_start[exception.start_pc] = []
            exception_block_start[exception.start_pc].append(exception)
            # Index end positions.
            if not exception_block_end.has_key(exception.end_pc):
                exception_block_end[exception.end_pc] = []
            exception_block_end[exception.end_pc].append(exception)
            # Index handler positions.
            if not exception_block_handler.has_key(exception.handler_pc):
                exception_block_handler[exception.handler_pc] = []
            exception_block_handler[exception.handler_pc].append(exception)

        # Process each instruction in the code.
        while self.java_position < len(code):
            self.position_mapping[self.java_position] = program.position

            # Insert exception handling constructs.
            block_starts = exception_block_start.get(self.java_position, [])
            for exception in block_starts:
                # Note that the absolute position is used.
                if exception.catch_type == 0:
                    program.setup_finally(self.position_mapping[exception.handler_pc])
                else:
                    program.setup_except(self.position_mapping[exception.handler_pc])
            if block_starts:
                self.in_finally = 0

            # Insert exception handler details.
            # NOTE: Ensure that pop_block is reachable by possibly inserting it at the start of finally handlers.
            # NOTE: Insert a check for the correct exception at the start of each handler.
            for exception in exception_block_handler.get(self.java_position, []):
                program.end_exception()
                if exception.catch_type == 0:
                    self.in_finally = 1
                else:
                    program.start_handler(self.class_file.constants[exception.catch_type - 1].get_python_name())

            # Process the bytecode at the current position.
            bytecode = ord(code[self.java_position])
            mnemonic, number_of_arguments = self.java_bytecodes[bytecode]
            number_of_arguments = self.process_bytecode(mnemonic, number_of_arguments, code, program)
            next_java_position = self.java_position + 1 + number_of_arguments

            # Insert exception block end details.
            for exception in exception_block_end.get(next_java_position, []):
                # NOTE: Insert jump beyond handlers.
                # NOTE: program.jump_forward/absolute(...)
                # NOTE: Insert end finally at end of handlers as well as where "ret" occurs.
                if exception.catch_type != 0:
                    program.pop_block()

            # Only advance the JVM position after sneaking in extra Python
            # instructions.
            self.java_position = next_java_position

    def process_bytecode(self, mnemonic, number_of_arguments, code, program):
        if number_of_arguments is not None:
            arguments = []
            for j in range(0, number_of_arguments):
                arguments.append(ord(code[self.java_position + 1 + j]))

            # Call the handler.
            getattr(self, mnemonic)(arguments, program)
            return number_of_arguments
        else:
            # Call the handler.
            return getattr(self, mnemonic)(code[self.java_position+1:], program)

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
        177 : ("return_", 0),
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

class BytecodeDisassembler(BytecodeReader):

    "A Java bytecode disassembler."

    bytecode_methods = [spec[0] for spec in BytecodeReader.java_bytecodes.values()]

    def __getattr__(self, name):
        if name in self.bytecode_methods:
            print "%5s %s" % (self.java_position, name),
            return self.generic
        else:
            raise AttributeError, name

    def generic(self, arguments, program):
        print arguments

class BytecodeDisassemblerProgram:
    position = 0
    def setup_except(self, target):
        print "(setup_except %s)" % target
    def setup_finally(self, target):
        print "(setup_finally %s)" % target
    def end_exception(self):
        print "(end_exception)"
    def start_handler(self, exc_name):
        print "(start_handler %s)" % exc_name
    def pop_block(self):
        print "(pop_block)"

class BytecodeTranslator(BytecodeReader):

    "A Java bytecode translator which uses a Python bytecode writer."

    def aaload(self, arguments, program):
        # NOTE: No type checking performed.
        program.binary_subscr()

    def aastore(self, arguments, program):
        # NOTE: No type checking performed.
        # Stack: arrayref, index, value
        program.rot_three() # Stack: value, arrayref, index
        program.store_subscr()

    def aconst_null(self, arguments, program):
        program.load_const(None)

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
        index = (arguments[0] << 8) + arguments[1]
        self._newarray(program)

    def _newarray(self, program):
        program.build_list()        # Stack: count, list
        program.rot_two()           # Stack: list, count
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
        program.load_const(None)    # Stack: iter, list, append, None
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
        # If this instruction appears in a finally handler, use end_finally instead.
        if self.in_finally:
            program.end_finally()
        else:
            program.dup_top()
            program.raise_varargs(1)

    baload = aaload
    bastore = aastore

    def bipush(self, arguments, program):
        program.load_const(arguments[0])

    caload = aaload
    castore = aastore

    def checkcast(self, arguments, program):
        index = (arguments[0] << 8) + arguments[1]
        target_name = self.class_file.constants[index - 1].get_python_name()
        # NOTE: Using the string version of the name which may contain incompatible characters.
        target_components = str(target_name).split("/")

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
        index = (arguments[0] << 8) + arguments[1]
        target_name = self.class_file.constants[index - 1].get_python_name()
        # NOTE: Using the string version of the name which may contain incompatible characters.
        program.load_attr(str(target_name))

    def getstatic(self, arguments, program):
        index = (arguments[0] << 8) + arguments[1]
        target_name = self.class_file.constants[index - 1].get_python_name()
        program.load_name("self")
        program.load_attr("__class__")
        # NOTE: Using the string version of the name which may contain incompatible characters.
        program.load_attr(str(target_name))

    def goto(self, arguments, program):
        offset = signed2((arguments[0] << 8) + arguments[1])
        java_absolute = self.java_position + offset
        program.jump_absolute(self.position_mapping[java_absolute])

    def goto_w(self, arguments, program):
        offset = signed4((arguments[0] << 24) + (arguments[1] << 16) + (arguments[2] << 8) + arguments[3])
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
        offset = signed2((arguments[0] << 8) + arguments[1])
        java_absolute = self.java_position + offset
        program.compare_op(op)
        program.jump_to_label(0, "next") # skip if false
        program.pop_top()
        program.jump_absolute(self.position_mapping[java_absolute])
        program.start_label("next")
        program.pop_top()

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
        program.store_fast(arguments[0])

    iload = fload
    iload_0 = fload_0
    iload_1 = fload_1
    iload_2 = fload_2
    iload_3 = fload_3
    imul = fmul
    ineg = fneg

    def instanceof(self, arguments, program):
        index = (arguments[0] << 8) + arguments[1]
        target_name = self.class_file.constants[index - 1].get_python_name()
        # NOTE: Using the string version of the name which may contain incompatible characters.
        target_components = str(target_name).split("/")

        program.load_global("isinstance")   # Stack: objectref, isinstance
        program.rot_two()                   # Stack: isinstance, objectref
        program.load_global(target_components[0])
        for target_component in target_components[1:]:
            program.load_attr(target_component)
        program.call_function(2)            # Stack: result

    def _invoke(self, target_name, program):
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
        index = (arguments[0] << 8) + arguments[1]
        count = arguments[2]
        target_name = self.class_file.constants[index - 1].get_python_name()
        # Stack: objectref, arg1, arg2, ...
        program.build_tuple(count)          # Stack: objectref, tuple
        program.rot_two()                   # Stack: tuple, objectref
        self._invoke(target_name, program)

    def invokespecial(self, arguments, program):
        # NOTE: This implementation does not perform the necessary checks for
        # NOTE: signature-based polymorphism.
        # NOTE: Java rules not specifically obeyed.
        index = (arguments[0] << 8) + arguments[1]
        target = self.class_file.constants[index - 1]
        target_name = target.get_python_name()
        # Get the number of parameters from the descriptor.
        count = len(target.get_descriptor()[0])

        # Check for the method name and invoke superclasses where appropriate.
        if str(self.method.get_python_name()) == "__init__":
            program.build_tuple(count + 1)  # Stack: tuple
            # Must use the actual class.
            # NOTE: Verify this.
            program.load_global(str(self.class_file.this_class.get_python_name()))
                                            # Stack: tuple, classref
            program.load_attr("__bases__")  # Stack: tuple, bases
            program.dup_top()               # Stack: tuple, bases, bases
            program.load_global("len")      # Stack: tuple, bases, bases, len
            program.rot_two()               # Stack: tuple, bases, len, bases
            program.call_function(1)        # Stack: tuple, bases, #bases
            program.load_const(0)           # Stack: tuple, bases, #bases, 0
            program.compare_op("==")        # Stack: tuple, bases, result
            program.jump_to_label(1, "next")
            program.pop_top()               # Stack: tuple, bases
            program.load_const(0)           # Stack: tuple, bases, 0
            program.binary_subscr()         # Stack: tuple, bases[0]
            self._invoke(target_name, program)
            program.jump_to_label(None, "next2")
            program.start_label("next")
            program.pop_top()               # Stack: tuple, bases
            program.pop_top()               # Stack: tuple
            program.pop_top()               # Stack:
            program.start_label("next2")

        elif str(target_name) == "__init__":
            # NOTE: Due to changes with the new instruction's implementation, the
            # NOTE: stack differs from that stated: objectref, arg1, arg2, ...
            # Stack: classref, arg1, arg2, ...
            program.build_tuple(count)          # Stack: classref, tuple
                                                # NOTE: Stack: objectref, tuple
            program.load_global("apply")        # Stack: classref, tuple, apply
            program.rot_three()                 # Stack: apply, classref, tuple
            program.call_function(2)

        else:
            program.build_tuple(count)          # Stack: objectref, tuple
            program.rot_two()                   # Stack: tuple, objectref
            self._invoke(target_name, program)

    """
    def invokespecial(self, arguments, program):
        # NOTE: This implementation does not perform the necessary checks for
        # NOTE: signature-based polymorphism.
        # NOTE: Java rules not specifically obeyed.
        index = (arguments[0] << 8) + arguments[1]
        target = self.class_file.constants[index - 1]
        target_name = target.get_python_name()
        # Get the number of parameters from the descriptor.
        count = len(target.get_descriptor()[0])
        # Stack: objectref, arg1, arg2, ...
        program.build_tuple(count + 1)  # Stack: tuple
        # Use the class to provide access to static methods.
        program.load_name("self")       # Stack: tuple, self
        program.load_attr("__class__")  # Stack: tuple, class
        program.load_attr("__bases__")  # Stack: tuple, base-classes
        program.dup_top()               # Stack: tuple, base-classes, base-classes
        program.load_global("len")      # Stack: tuple, base-classes, base-classes, len
        program.rot_two()               # Stack: tuple, base-classes, len, base-classes
        program.call_function(1)        # Stack: tuple, base-classes, count
        program.load_const(0)           # Stack: tuple, base-classes, count, 0
        program.compare_op("==")        # Stack: tuple, base-classes, result
        program.jump_to_label(1, "next")
        program.pop_top()               # Stack: tuple, base-classes
        program.load_const(0)           # Stack: tuple, base-classes, 0
        program.binary_subscr()         # Stack: tuple, superclass
        self._invoke(target_name, program)
        program.jump_to_label(None, "next2")
        program.start_label("next")
        program.pop_top()               # Stack: tuple, base-classes
        program.pop_top()               # Stack: tuple
        program.pop_top()               # Stack:
        program.start_label("next2")
    """

    def invokestatic(self, arguments, program):
        # NOTE: This implementation does not perform the necessary checks for
        # NOTE: signature-based polymorphism.
        # NOTE: Java rules not specifically obeyed.
        index = (arguments[0] << 8) + arguments[1]
        target = self.class_file.constants[index - 1]
        target_name = target.get_python_name()
        # Get the number of parameters from the descriptor.
        count = len(target.get_descriptor()[0])
        # Stack: arg1, arg2, ...
        program.build_tuple(count)      # Stack: tuple
        # Use the class to provide access to static methods.
        program.load_name("self")       # Stack: tuple, self
        program.load_attr("__class__")  # Stack: tuple, class
        self._invoke(target_name, program)

    def invokevirtual (self, arguments, program):
        # NOTE: This implementation does not perform the necessary checks for
        # NOTE: signature-based polymorphism.
        # NOTE: Java rules not specifically obeyed.
        index = (arguments[0] << 8) + arguments[1]
        target = self.class_file.constants[index - 1]
        target_name = target.get_python_name()
        # Get the number of parameters from the descriptor.
        count = len(target.get_descriptor()[0])
        # Stack: objectref, arg1, arg2, ...
        program.build_tuple(count)          # Stack: objectref, tuple
        program.rot_two()                   # Stack: tuple, objectref
        self._invoke(target_name, program)

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

    def ixor(self, arguments, program):
        # NOTE: No type checking performed.
        program.binary_xor()

    def jsr(self, arguments, program):
        offset = signed2((arguments[0] << 8) + arguments[1])
        java_absolute = self.java_position + offset
        # Store the address of the next instruction.
        program.load_const_ret(self.position_mapping[self.java_position + 3])
        program.jump_absolute(self.position_mapping[java_absolute])

    def jsr_w(self, arguments, program):
        offset = signed4((arguments[0] << 24) + (arguments[1] << 16) + (arguments[2] << 8) + arguments[3])
        java_absolute = self.java_position + offset
        # Store the address of the next instruction.
        program.load_const_ret(self.position_mapping[self.java_position + 5])
        program.jump_absolute(self.position_mapping[java_absolute])

    l2d = i2d
    l2f = i2f

    def l2i(self, arguments, program):
        pass # Preserving Java semantics

    ladd = iadd
    laload = iaload
    land = iand
    lastore = iastore

    def lcmp(self, arguments, program):
        # NOTE: No type checking performed.
        program.dup_topx(2)                 # Stack: value1, value2, value1, value2
        program.compare_op(">")             # Stack: value1, value2, result
        program.jump_to_label(0, "equals")
        # True - produce result and branch.
        program.pop_top()                   # Stack: value1, value2
        program.pop_top()                   # Stack: value1
        program.pop_top()                   # Stack:
        program.load_const(1)               # Stack: 1
        program.jump_to_label(None, "next")
        # False - test equality.
        program.start_label("equals")
        program.pop_top()                   # Stack: value1, value2
        program.dup_topx(2)                 # Stack: value1, value2, value1, value2
        program.compare_op("==")            # Stack: value1, value2, result
        program.jump_to_label(0, "less")
        # True - produce result and branch.
        program.pop_top()                   # Stack: value1, value2
        program.pop_top()                   # Stack: value1
        program.pop_top()                   # Stack:
        program.load_const(0)               # Stack: 0
        program.jump_to_label(None, "next")
        # False - produce result.
        program.start_label("less")
        program.pop_top()                   # Stack: value1, value2
        program.pop_top()                   # Stack: value1
        program.pop_top()                   # Stack:
        program.load_const(-1)              # Stack: -1
        program.start_label("next")

    lconst_0 = iconst_0
    lconst_1 = iconst_1

    def ldc(self, arguments, program):
        program.load_const(self.class_file.constants[arguments[0] - 1])

    def ldc_w(self, arguments, program):
        program.load_const(self.class_file.constants[(arguments[0] << 8) + arguments[1] - 1])

    ldc2_w = ldc_w
    ldiv = idiv
    lload = iload
    lload_0 = iload_0
    lload_1 = iload_1
    lload_2 = iload_2
    lload_3 = iload_3
    lmul = imul
    lneg = ineg

    def lookupswitch(self, arguments, program):
        # Find the offset to the next 4 byte boundary in the code.
        d, r = divmod(self.java_position, 4)
        to_boundary = (4 - r) % 4
        # Get the pertinent arguments.
        arguments = arguments[to_boundary:]
        default = (arguments[0] << 24) + (arguments[1] << 16) + (arguments[2] << 8) + arguments[3]
        npairs = (arguments[4] << 24) + (arguments[5] << 16) + (arguments[6] << 8) + arguments[7]
        # Process the pairs.
        # NOTE: This is not the most optimal implementation.
        pair_index = 8
        for pair in range(0, npairs):
            match = ((arguments[pair_index] << 24) + (arguments[pair_index + 1] << 16) +
                (arguments[pair_index + 2] << 8) + arguments[pair_index + 3])
            offset = signed4((arguments[pair_index + 4] << 24) + (arguments[pair_index + 5] << 16) +
                (arguments[pair_index + 6] << 8) + arguments[pair_index + 7])
            # Calculate the branch target.
            java_absolute = self.java_position + offset
            # Generate branching code.
            program.dup_top()                                           # Stack: key, key
            program.load_const(match)                                   # Stack: key, key, match
            program.compare_op("==")                                    # Stack: key, result
            program.jump_to_label(0, "end")
            program.pop_top()                                           # Stack: key
            program.pop_top()                                           # Stack:
            program.jump_absolute(self.position_mapping[java_absolute])
            # Generate the label for the end of the branching code.
            program.start_label("end")
            program.pop_top()                                           # Stack: key
            # Update the index.
            pair_index += 8
        # Generate the default.
        java_absolute = self.java_position + default
        program.jump_absolute(self.position_mapping[java_absolute])

    lor = ior
    lrem = irem
    lreturn = ireturn
    lshl = ishl
    lshr = ishr
    lstore = istore
    lstore_0 = istore_0
    lstore_1 = istore_1
    lstore_2 = istore_2
    lstore_3 = istore_3
    lsub = isub
    lushr = iushr
    lxor = ixor

    def monitorenter(self, arguments, program):
        # NOTE: To be implemented.
        pass

    def monitorexit(self, arguments, program):
        # NOTE: To be implemented.
        pass

    def multianewarray(self, arguments, program):
        # NOTE: To be implemented.
        pass

    def new(self, arguments, program):
        # This operation is considered to be the same as the calling of the
        # initialisation method of the given class with no arguments.
        index = (arguments[0] << 8) + arguments[1]
        target_name = self.class_file.constants[index - 1].get_python_name()
        # NOTE: Using the string version of the name which may contain incompatible characters.
        program.load_global(str(target_name))
        # NOTE: Unlike Java, we do not provide an object reference. Instead, a
        # NOTE: class reference is provided, and the invokespecial method's
        # NOTE: behaviour is changed.
        #program.call_function(0)

    def newarray(self, arguments, program):
        # NOTE: Does not raise NegativeArraySizeException.
        # NOTE: Not using the arguments to type the list/array.
        self._newarray(program)

    def nop(self, arguments, program):
        pass

    def pop(self, arguments, program):
        program.pop_top()

    pop2 = pop # ignoring Java stack value distinctions

    def putfield(self, arguments, program):
        index = (arguments[0] << 8) + arguments[1]
        target_name = self.class_file.constants[index - 1].get_python_name()
        program.rot_two()
        # NOTE: Using the string version of the name which may contain incompatible characters.
        program.store_attr(str(target_name))

    def putstatic(self, arguments, program):
        index = (arguments[0] << 8) + arguments[1]
        target_name = self.class_file.constants[index - 1].get_python_name()
        program.load_name("self")
        program.load_attr("__class__")
        # NOTE: Using the string version of the name which may contain incompatible characters.
        program.store_attr(str(target_name))

    def ret(self, arguments, program):
        program.ret(arguments[0])
        # Indicate that the finally handler is probably over.
        # NOTE: This is seemingly not guaranteed.
        self.in_finally = 0

    def return_(self, arguments, program):
        program.load_const(None)
        program.return_value()

    saload = laload
    sastore = lastore

    def sipush(self, arguments, program):
        program.load_const((arguments[0] << 8) + arguments[1])

    def swap(self, arguments, program):
        program.rot_two()

    def tableswitch(self, arguments, program):
        # Find the offset to the next 4 byte boundary in the code.
        d, r = divmod(self.java_position, 4)
        to_boundary = (4 - r) % 4
        # Get the pertinent arguments.
        arguments = arguments[to_boundary:]
        default = (arguments[0] << 24) + (arguments[1] << 16) + (arguments[2] << 8) + arguments[3]
        low = (arguments[4] << 24) + (arguments[5] << 16) + (arguments[6] << 8) + arguments[7]
        high = (arguments[8] << 24) + (arguments[9] << 16) + (arguments[10] << 8) + arguments[11]
        # Process the jump entries.
        # NOTE: This is not the most optimal implementation.
        jump_index = 8
        for jump in range(low, high + 1):
            offset = signed4((arguments[jump_index] << 24) + (arguments[jump_index + 1] << 16) +
                (arguments[jump_index + 2] << 8) + arguments[jump_index + 3])
            # Calculate the branch target.
            java_absolute = self.java_position + offset
            # Generate branching code.
            program.dup_top()                                           # Stack: key, key
            program.load_const(jump)                                    # Stack: key, key, jump
            program.compare_op("==")                                    # Stack: key, result
            program.jump_to_label(0, "end")
            program.pop_top()                                           # Stack: key
            program.pop_top()                                           # Stack:
            program.jump_absolute(self.position_mapping[java_absolute])
            # Generate the label for the end of the branching code.
            program.start_label("end")
            program.pop_top()                                           # Stack: key
            # Update the index.
            jump_index += 8
        # Generate the default.
        java_absolute = self.java_position + default
        program.jump_absolute(self.position_mapping[java_absolute])

    def wide(self, code, program):
        # NOTE: To be implemented.
        return number_of_arguments

def disassemble(class_file, method):
    disassembler = BytecodeDisassembler(class_file)
    disassembler.process(method, BytecodeDisassemblerProgram())

def translate(class_file, method):
    translator = BytecodeTranslator(class_file)
    writer = BytecodeWriter()
    translator.process(method, writer)
    return translator, writer

def make_varnames(nlocals):
    l = ["self"]
    for i in range(1, nlocals):
        l.append("_l%s" % i)
    return l[:nlocals]

if __name__ == "__main__":
    import sys
    from classfile import ClassFile
    global_names = {}
    global_names.update(__builtins__.__dict__)
    for filename in sys.argv[1:]:
        f = open(filename, "rb")
        c = ClassFile(f.read())
        import dis, new
        namespace = {}
        for method in c.methods:
            nargs = len(method.get_descriptor()[0]) + 1
            t, w = translate(c, method)
            nlocals = w.max_locals + 1
            filename = str(c.attributes[0].get_name())
            method_name = str(method.get_python_name())
            code = new.code(nargs, nlocals, w.max_stack_depth, 67, w.get_output(), tuple(w.get_constants()), tuple(w.get_names()),
                tuple(make_varnames(nlocals)), filename, method_name, 0, "")
            # NOTE: May need more globals.
            fn = new.function(code, global_names)
            namespace[method_name] = fn
        # NOTE: Define superclasses properly.
        if str(c.super_class.get_name()) not in ("java/lang/Object", "java/lang/Exception"):
            bases = (global_names[str(c.super_class.get_python_name())],)
        else:
            bases = ()
        cls = new.classobj(str(c.this_class.get_python_name()), bases, namespace)
        global_names[cls.__name__] = cls

# vim: tabstop=4 expandtab shiftwidth=4
