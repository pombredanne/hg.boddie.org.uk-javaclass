#!/usr/bin/env python

"""
Java bytecode conversion. Specification found at the following URL:
http://java.sun.com/docs/books/vmspec/2nd-edition/html/Instructions2.doc.html
"""

import dis # for access to Python bytecode values

# Bytecode conversion.

def get_instructions(code):
    global java_bytecodes

    i = 0
    instructions = []
    while i < len(code):
        bytecode = ord(code[i])
        mnemonic, number_of_arguments, stack_change = java_bytecodes[bytecode]

        # NOTE: To be fixed.
        if number_of_arguments is None:
            print "Stop at", mnemonic
            return instructions

        arguments = []
        for j in range(0, number_of_arguments):
            arguments.append(ord(code[i + 1 + j]))

        i = i + 1 + number_of_arguments
        instructions.append((mnemonic, arguments))

    return instructions

java_bytecodes = {
    # code : (mnemonic, number of following bytes, change in stack)
    0 : ("nop", 0, 0),
    1 : ("aconst_null", 0, 1),
    2 : ("iconst_m1", 0, 1),
    3 : ("iconst_0", 0, 1),
    4 : ("iconst_1", 0, 1),
    5 : ("iconst_2", 0, 1),
    6 : ("iconst_3", 0, 1),
    7 : ("iconst_4", 0, 1),
    8 : ("iconst_5", 0, 1),
    9 : ("lconst_0", 0, 1),
    10 : ("lconst_1", 0, 1),
    11 : ("fconst_0", 0, 1),
    12 : ("fconst_1", 0, 1),
    13 : ("fconst_2", 0, 1),
    14 : ("dconst_0", 0, 1),
    15 : ("dconst_1", 0, 1),
    16 : ("bipush", 1, 1),
    17 : ("sipush", 2, 1),
    18 : ("ldc", 1, 1),
    19 : ("ldc_w", 2, 1),
    20 : ("ldc2_w", 2, 1),
    21 : ("iload", 1, 1),
    22 : ("lload", 1, 1),
    23 : ("fload", 1, 1),
    24 : ("dload", 1, 1),
    25 : ("aload", 1, 1),
    26 : ("iload_0", 0, 1),
    27 : ("iload_1", 0, 1),
    28 : ("iload_2", 0, 1),
    29 : ("iload_3", 0, 1),
    30 : ("lload_0", 0, 1),
    31 : ("lload_1", 0, 1),
    32 : ("lload_2", 0, 1),
    33 : ("lload_3", 0, 1),
    34 : ("fload_0", 0, 1),
    35 : ("fload_1", 0, 1),
    36 : ("fload_2", 0, 1),
    37 : ("fload_3", 0, 1),
    38 : ("dload_0", 0, 1),
    39 : ("dload_1", 0, 1),
    40 : ("dload_2", 0, 1),
    41 : ("dload_3", 0, 1),
    42 : ("aload_0", 0, 1),
    43 : ("aload_1", 0, 1),
    44 : ("aload_2", 0, 1),
    45 : ("aload_3", 0, 1),
    46 : ("iaload", 0, -1),
    47 : ("laload", 0, -1),
    48 : ("faload", 0, -1),
    49 : ("daload", 0, -1),
    50 : ("aaload", 0, -1),
    51 : ("baload", 0, -1),
    52 : ("caload", 0, -1),
    53 : ("saload", 0, -1),
    54 : ("istore", 1, -1),
    55 : ("lstore", 1, -1),
    56 : ("fstore", 1, -1),
    57 : ("dstore", 1, -1),
    58 : ("astore", 1, -1),
    59 : ("istore_0", 0, -1),
    60 : ("istore_1", 0, -1),
    61 : ("istore_2", 0, -1),
    62 : ("istore_3", 0, -1),
    63 : ("lstore_0", 0, -1),
    64 : ("lstore_1", 0, -1),
    65 : ("lstore_2", 0, -1),
    66 : ("lstore_3", 0, -1),
    67 : ("fstore_0", 0, -1),
    68 : ("fstore_1", 0, -1),
    69 : ("fstore_2", 0, -1),
    70 : ("fstore_3", 0, -1),
    71 : ("dstore_0", 0, -1),
    72 : ("dstore_1", 0, -1),
    73 : ("dstore_2", 0, -1),
    74 : ("dstore_3", 0, -1),
    75 : ("astore_0", 0, -1),
    76 : ("astore_1", 0, -1),
    77 : ("astore_2", 0, -1),
    78 : ("astore_3", 0, -1),
    79 : ("iastore", 0, -3),
    80 : ("lastore", 0, -3),
    81 : ("fastore", 0, -3),
    82 : ("dastore", 0, -3),
    83 : ("aastore", 0, -3),
    84 : ("bastore", 0, -3),
    85 : ("castore", 0, -3),
    86 : ("sastore", 0, -3),
    87 : ("pop", 0, -1),
    88 : ("pop2", 0, None), # variable number of elements removed
    89 : ("dup", 0, 1),
    90 : ("dup_x1", 0, 1),
    91 : ("dup_x2", 0, 1),
    92 : ("dup2", 0, 2), # or 1 extra stack value
    93 : ("dup2_x1", 0, 2), # or 1 extra stack value
    94 : ("dup2_x2", 0, 2), # or 1 extra stack value
    95 : ("swap", 0, 0),
    96 : ("iadd", 0, -1),
    97 : ("ladd", 0, -1),
    98 : ("fadd", 0, -1),
    99 : ("dadd", 0, -1),
    100 : ("isub", 0, -1),
    101 : ("lsub", 0, -1),
    102 : ("fsub", 0, -1),
    103 : ("dsub", 0, -1),
    104 : ("imul", 0, -1),
    105 : ("lmul", 0, -1),
    106 : ("fmul", 0, -1),
    107 : ("dmul", 0, -1),
    108 : ("idiv", 0, -1),
    109 : ("ldiv", 0, -1),
    110 : ("fdiv", 0, -1),
    111 : ("ddiv", 0, -1),
    112 : ("irem", 0, -1),
    113 : ("lrem", 0, -1),
    114 : ("frem", 0, -1),
    115 : ("drem", 0, -1),
    116 : ("ineg", 0, 0),
    117 : ("lneg", 0, 0),
    118 : ("fneg", 0, 0),
    119 : ("dneg", 0, 0),
    120 : ("ishl", 0, -1),
    121 : ("lshl", 0, -1),
    122 : ("ishr", 0, -1),
    123 : ("lshr", 0, -1),
    124 : ("iushr", 0, -1),
    125 : ("lushr", 0, -1),
    126 : ("iand", 0, -1),
    127 : ("land", 0, -1),
    128 : ("ior", 0, -1),
    129 : ("lor", 0, -1),
    130 : ("ixor", 0, -1),
    131 : ("lxor", 0, -1),
    132 : ("iinc", 2, 0),
    133 : ("i2l", 0, 0),
    134 : ("i2f", 0, 0),
    135 : ("i2d", 0, 0),
    136 : ("l2i", 0, 0),
    137 : ("l2f", 0, 0),
    138 : ("l2d", 0, 0),
    139 : ("f2i", 0, 0),
    140 : ("f2l", 0, 0),
    141 : ("f2d", 0, 0),
    142 : ("d2i", 0, 0),
    143 : ("d2l", 0, 0),
    144 : ("d2f", 0, 0),
    145 : ("i2b", 0, 0),
    146 : ("i2c", 0, 0),
    147 : ("i2s", 0, 0),
    148 : ("lcmp", 0, -1),
    149 : ("fcmpl", 0, -1),
    150 : ("fcmpg", 0, -1),
    151 : ("dcmpl", 0, -1),
    152 : ("dcmpg", 0, -1),
    153 : ("ifeq", 2, -1),
    154 : ("ifne", 2, -1),
    155 : ("iflt", 2, -1),
    156 : ("ifge", 2, -1),
    157 : ("ifgt", 2, -1),
    158 : ("ifle", 2, -1),
    159 : ("if_icmpeq", 2, -2),
    160 : ("if_icmpne", 2, -2),
    161 : ("if_icmplt", 2, -2),
    162 : ("if_icmpge", 2, -2),
    163 : ("if_icmpgt", 2, -2),
    164 : ("if_icmple", 2, -2),
    165 : ("if_acmpeq", 2, -2),
    166 : ("if_acmpne", 2, -2),
    167 : ("goto", 2, 0),
    168 : ("jsr", 2, 1),
    169 : ("ret", 1, 0),
    170 : ("tableswitch", None, -1), # variable number of arguments
    171 : ("lookupswitch", None, -1), # variable number of arguments
    172 : ("ireturn", 0, -1),
    173 : ("lreturn", 0, -1),
    174 : ("freturn", 0, -1),
    175 : ("dreturn", 0, -1),
    176 : ("areturn", 0, -1),
    177 : ("return", 0, 0),
    178 : ("getstatic", 2, 1),
    179 : ("putstatic", 2, -1),
    180 : ("getfield", 2, 0),
    181 : ("putfield", 2, -2),
    182 : ("invokevirtual", 2, None), # variable number of elements removed
    183 : ("invokespecial", 2, None), # variable number of elements removed
    184 : ("invokestatic", 2, None), # variable number of elements removed
    185 : ("invokeinterface", 4, None), # variable number of elements removed
    187 : ("new", 2, 1),
    188 : ("newarray", 1, 0),
    189 : ("anewarray", 2, 0),
    190 : ("arraylength", 0, 0),
    191 : ("athrow", 0, 0),
    192 : ("checkcast", 2, 0),
    193 : ("instanceof", 2, 0),
    194 : ("monitorenter", 0, -1),
    195 : ("monitorexit", 0, -1),
    196 : ("wide", None, None), # 3 or 5 arguments, stack changes according to modified element
    197 : ("multianewarray", 3, None), # variable number of elements removed
    198 : ("ifnull", 2, -1),
    199 : ("ifnonnull", 2, -1),
    200 : ("goto_w", 4, 0),
    201 : ("jsr_w", 4, 1),
    }

# vim: tabstop=4 expandtab shiftwidth=4
