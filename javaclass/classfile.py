#!/usr/bin/env python

"""
Java class file decoder. Specification found at the following URL:
http://java.sun.com/docs/books/vmspec/2nd-edition/html/ClassFile.doc.html
"""

import struct # for general decoding of class files

# Utility functions.

def u1(data):
    return struct.unpack(">B", data[0:1])[0]

def u2(data):
    return struct.unpack(">H", data[0:2])[0]

def s2(data):
    return struct.unpack(">h", data[0:2])[0]

def u4(data):
    return struct.unpack(">L", data[0:4])[0]

def s4(data):
    return struct.unpack(">l", data[0:4])[0]

def s8(data):
    return struct.unpack(">q", data[0:8])[0]

def f4(data):
    return struct.unpack(">f", data[0:4])[0]

def f8(data):
    return struct.unpack(">d", data[0:8])[0]

# Useful tables and constants.

descriptor_base_type_mapping = {
    "B" : "int",
    "C" : "str",
    "D" : "float",
    "F" : "float",
    "I" : "int",
    "J" : "int",
    "L" : "object",
    "S" : "int",
    "Z" : "bool",
    "[" : "list"
    }

PUBLIC, PRIVATE, PROTECTED, STATIC, FINAL,  SUPER,  SYNCHRONIZED, VOLATILE, TRANSIENT, NATIVE, INTERFACE, ABSTRACT, STRICT = \
0x0001, 0x0002,  0x0004,    0x0008, 0x0010, 0x0020, 0x0020,       0x0040,   0x0080,    0x0100, 0x0200,    0x0400,   0x0800

def has_flags(flags, desired):
    desired_flags = reduce(lambda a, b: a | b, desired, 0)
    return (flags & desired_flags) == desired_flags

# Useful mix-ins.

class PythonMethodUtils:
    symbol_sep = "___" # was "$"
    type_sep = "__" # replaces "/"
    array_sep = "_array_" # was "[]"
    base_seps = ("_", "_") # was "<" and ">"

    def get_unqualified_python_name(self):
        name = self.get_name()
        if str(name) == "<init>":
            return "__init__"
        elif str(name) == "<clinit>":
            return "__clinit__"
        else:
            return str(name)

    def get_python_name(self):
        name = self.get_unqualified_python_name()
        if name == "__clinit__":
            return name
        return name + self.symbol_sep + self._get_descriptor_as_name()

    def _get_descriptor_as_name(self):
        l = []
        for descriptor_type in self.get_descriptor()[0]:
            l.append(self._get_type_as_name(descriptor_type))
        return self.symbol_sep.join(l)

    def _get_type_as_name(self, descriptor_type, s=""):
        base_type, object_type, array_type = descriptor_type
        if base_type == "L":
            return object_type.replace("/", self.type_sep) + s
        elif base_type == "[":
            return self._get_type_as_name(array_type, s + self.array_sep)
        else:
            return self.base_seps[0] + base_type + self.base_seps[1] + s

class PythonNameUtils:
    def get_python_name(self):
        # NOTE: This may not be comprehensive.
        if not str(self.get_name()).startswith("["):
            return str(self.get_name()).replace("/", ".")
        else:
            return self._get_type_name(
                get_field_descriptor(
                    str(self.get_name())
                    )
                ).replace("/", ".")

    def _get_type_name(self, descriptor_type):
        base_type, object_type, array_type = descriptor_type
        if base_type == "L":
            return object_type
        elif base_type == "[":
            return self._get_type_name(array_type)
        else:
            return descriptor_base_type_mapping[base_type]

class NameUtils:
    def get_name(self):
        if self.name_index != 0:
            return self.class_file.constants[self.name_index - 1]
        else:
            # Some name indexes are zero to indicate special conditions.
            return None

class NameAndTypeUtils:
    def get_name(self):
        if self.name_and_type_index != 0:
            return self.class_file.constants[self.name_and_type_index - 1].get_name()
        else:
            # Some name indexes are zero to indicate special conditions.
            return None

    def get_field_descriptor(self):
        if self.name_and_type_index != 0:
            return self.class_file.constants[self.name_and_type_index - 1].get_field_descriptor()
        else:
            # Some name indexes are zero to indicate special conditions.
            return None

    def get_method_descriptor(self):
        if self.name_and_type_index != 0:
            return self.class_file.constants[self.name_and_type_index - 1].get_method_descriptor()
        else:
            # Some name indexes are zero to indicate special conditions.
            return None

    def get_class(self):
        return self.class_file.constants[self.class_index - 1]

# Symbol parsing.

def get_method_descriptor(s):
    assert s[0] == "("
    params = []
    s = s[1:]
    while s[0] != ")":
        parameter_descriptor, s = _get_parameter_descriptor(s)
        params.append(parameter_descriptor)
    if s[1] != "V":
        return_type, s = _get_field_type(s[1:])
    else:
        return_type, s = None, s[1:]
    return params, return_type

def get_field_descriptor(s):
    return _get_field_type(s)[0]

def _get_parameter_descriptor(s):
    return _get_field_type(s)

def _get_component_type(s):
    return _get_field_type(s)

def _get_field_type(s):
    base_type, s = _get_base_type(s)
    object_type = None
    array_type = None
    if base_type == "L":
        object_type, s = _get_object_type(s)
    elif base_type == "[":
        array_type, s = _get_array_type(s)
    return (base_type, object_type, array_type), s

def _get_base_type(s):
    if len(s) > 0:
        return s[0], s[1:]
    else:
        return None, s

def _get_object_type(s):
    if len(s) > 0:
        s_end = s.find(";")
        assert s_end != -1
        return s[:s_end], s[s_end+1:]
    else:
        return None, s

def _get_array_type(s):
    if len(s) > 0:
        return _get_component_type(s)
    else:
        return None, s

# Constant information.

class ClassInfo(NameUtils, PythonNameUtils):
    def init(self, data, class_file):
        self.class_file = class_file
        self.name_index = u2(data[0:2])
        return data[2:]

class RefInfo(NameAndTypeUtils):
    def init(self, data, class_file):
        self.class_file = class_file
        self.class_index = u2(data[0:2])
        self.name_and_type_index = u2(data[2:4])
        return data[4:]

class FieldRefInfo(RefInfo, PythonNameUtils):
    def get_descriptor(self):
        return RefInfo.get_field_descriptor(self)

class MethodRefInfo(RefInfo, PythonMethodUtils):
    def get_descriptor(self):
        return RefInfo.get_method_descriptor(self)

class InterfaceMethodRefInfo(MethodRefInfo):
    pass

class NameAndTypeInfo(NameUtils, PythonNameUtils):
    def init(self, data, class_file):
        self.class_file = class_file
        self.name_index = u2(data[0:2])
        self.descriptor_index = u2(data[2:4])
        return data[4:]

    def get_field_descriptor(self):
        return get_field_descriptor(unicode(self.class_file.constants[self.descriptor_index - 1]))

    def get_method_descriptor(self):
        return get_method_descriptor(unicode(self.class_file.constants[self.descriptor_index - 1]))

class Utf8Info:
    def init(self, data, class_file):
        self.class_file = class_file
        self.length = u2(data[0:2])
        self.bytes = data[2:2+self.length]
        return data[2+self.length:]

    def __str__(self):
        return self.bytes

    def __unicode__(self):
        return unicode(self.bytes, "utf-8")

    def get_value(self):
        return str(self)

class StringInfo:
    def init(self, data, class_file):
        self.class_file = class_file
        self.string_index = u2(data[0:2])
        return data[2:]

    def __str__(self):
        return str(self.class_file.constants[self.string_index - 1])

    def __unicode__(self):
        return unicode(self.class_file.constants[self.string_index - 1])

    def get_value(self):
        return str(self)

class SmallNumInfo:
    def init(self, data, class_file):
        self.class_file = class_file
        self.bytes = data[0:4]
        return data[4:]

class IntegerInfo(SmallNumInfo):
    def get_value(self):
        return s4(self.bytes)

class FloatInfo(SmallNumInfo):
    def get_value(self):
        return f4(self.bytes)

class LargeNumInfo:
    def init(self, data, class_file):
        self.class_file = class_file
        self.high_bytes = data[0:4]
        self.low_bytes = data[4:8]
        return data[8:]

class LongInfo(LargeNumInfo):
    def get_value(self):
        return s8(self.high_bytes + self.low_bytes)

class DoubleInfo(LargeNumInfo):
    def get_value(self):
        return f8(self.high_bytes + self.low_bytes)

# Other information.
# Objects of these classes are generally aware of the class they reside in.

class ItemInfo(NameUtils):
    def init(self, data, class_file):
        self.class_file = class_file
        self.access_flags = u2(data[0:2])
        self.name_index = u2(data[2:4])
        self.descriptor_index = u2(data[4:6])
        self.attributes, data = self.class_file._get_attributes(data[6:])
        return data

class FieldInfo(ItemInfo, PythonNameUtils):
    def get_descriptor(self):
        return get_field_descriptor(unicode(self.class_file.constants[self.descriptor_index - 1]))

class MethodInfo(ItemInfo, PythonMethodUtils):
    def get_descriptor(self):
        return get_method_descriptor(unicode(self.class_file.constants[self.descriptor_index - 1]))

class AttributeInfo:
    def init(self, data, class_file):
        self.attribute_length = u4(data[0:4])
        self.info = data[4:4+self.attribute_length]
        return data[4+self.attribute_length:]

# NOTE: Decode the different attribute formats.

class SourceFileAttributeInfo(AttributeInfo, NameUtils, PythonNameUtils):
    def init(self, data, class_file):
        self.class_file = class_file
        self.attribute_length = u4(data[0:4])
        # Permit the NameUtils mix-in.
        self.name_index = self.sourcefile_index = u2(data[4:6])
        return data[6:]

class ConstantValueAttributeInfo(AttributeInfo):
    def init(self, data, class_file):
        self.class_file = class_file
        self.attribute_length = u4(data[0:4])
        self.constant_value_index = u2(data[4:6])
        assert 4+self.attribute_length == 6
        return data[4+self.attribute_length:]

    def get_value(self):
        return self.class_file.constants[self.constant_value_index - 1].get_value()

class CodeAttributeInfo(AttributeInfo):
    def init(self, data, class_file):
        self.class_file = class_file
        self.attribute_length = u4(data[0:4])
        self.max_stack = u2(data[4:6])
        self.max_locals = u2(data[6:8])
        self.code_length = u4(data[8:12])
        end_of_code = 12+self.code_length
        self.code = data[12:end_of_code]
        self.exception_table_length = u2(data[end_of_code:end_of_code+2])
        self.exception_table = []
        data = data[end_of_code + 2:]
        for i in range(0, self.exception_table_length):
            exception = ExceptionInfo()
            data = exception.init(data)
            self.exception_table.append(exception)
        self.attributes, data = self.class_file._get_attributes(data)
        return data

class ExceptionsAttributeInfo(AttributeInfo):
    def init(self, data, class_file):
        self.class_file = class_file
        self.attribute_length = u4(data[0:4])
        self.number_of_exceptions = u2(data[4:6])
        self.exception_index_table = []
        index = 6
        for i in range(0, self.number_of_exceptions):
            self.exception_index_table.append(u2(data[index:index+2]))
            index += 2
        return data[index:]

    def get_exception(self, i):
        exception_index = self.exception_index_table[i]
        return self.class_file.constants[exception_index - 1]

class InnerClassesAttributeInfo(AttributeInfo):
    def init(self, data, class_file):
        self.class_file = class_file
        self.attribute_length = u4(data[0:4])
        self.number_of_classes = u2(data[4:6])
        self.classes = []
        data = data[6:]
        for i in range(0, self.number_of_classes):
            inner_class = InnerClassInfo()
            data = inner_class.init(data, self.class_file)
            self.classes.append(inner_class)
        return data

class SyntheticAttributeInfo(AttributeInfo):
    pass

class LineNumberAttributeInfo(AttributeInfo):
    def init(self, data, class_file):
        self.class_file = class_file
        self.attribute_length = u4(data[0:4])
        self.line_number_table_length = u2(data[4:6])
        self.line_number_table = []
        data = data[6:]
        for i in range(0, self.line_number_table_length):
            line_number = LineNumberInfo()
            data = line_number.init(data)
            self.line_number_table.append(line_number)
        return data

class LocalVariableAttributeInfo(AttributeInfo):
    def init(self, data, class_file):
        self.class_file = class_file
        self.attribute_length = u4(data[0:4])
        self.local_variable_table_length = u2(data[4:6])
        self.local_variable_table = []
        data = data[6:]
        for i in range(0, self.local_variable_table_length):
            local_variable = LocalVariableInfo()
            data = local_variable.init(data, self.class_file)
            self.local_variable_table.append(local_variable)
        return data

class DeprecatedAttributeInfo(AttributeInfo):
    pass

# Child classes of the attribute information classes.

class ExceptionInfo:
    def init(self, data):
        self.start_pc = u2(data[0:2])
        self.end_pc = u2(data[2:4])
        self.handler_pc = u2(data[4:6])
        self.catch_type = u2(data[6:8])
        return data[8:]

class InnerClassInfo(NameUtils):
    def init(self, data, class_file):
        self.class_file = class_file
        self.inner_class_info_index = u2(data[0:2])
        self.outer_class_info_index = u2(data[2:4])
        # Permit the NameUtils mix-in.
        self.name_index = self.inner_name_index = u2(data[4:6])
        self.inner_class_access_flags = u2(data[6:8])
        return data[8:]

class LineNumberInfo:
    def init(self, data):
        self.start_pc = u2(data[0:2])
        self.line_number = u2(data[2:4])
        return data[4:]

class LocalVariableInfo(NameUtils, PythonNameUtils):
    def init(self, data, class_file):
        self.class_file = class_file
        self.start_pc = u2(data[0:2])
        self.length = u2(data[2:4])
        self.name_index = u2(data[4:6])
        self.descriptor_index = u2(data[6:8])
        self.index = u2(data[8:10])
        return data[10:]

    def get_descriptor(self):
        return get_field_descriptor(unicode(self.class_file.constants[self.descriptor_index - 1]))

# Exceptions.

class UnknownTag(Exception):
    pass

class UnknownAttribute(Exception):
    pass

# Abstractions for the main structures.

class ClassFile:

    "A class representing a Java class file."

    def __init__(self, s):

        """
        Process the given string 's', populating the object with the class
        file's details.
        """

        self.constants, s = self._get_constants(s[8:])
        self.access_flags, s = self._get_access_flags(s)
        self.this_class, s = self._get_this_class(s)
        self.super_class, s = self._get_super_class(s)
        self.interfaces, s = self._get_interfaces(s)
        self.fields, s = self._get_fields(s)
        self.methods, s = self._get_methods(s)
        self.attributes, s = self._get_attributes(s)

    def _decode_const(self, s):
        tag = u1(s[0:1])
        if tag == 1:
            const = Utf8Info()
        elif tag == 3:
            const = IntegerInfo()
        elif tag == 4:
            const = FloatInfo()
        elif tag == 5:
            const = LongInfo()
        elif tag == 6:
            const = DoubleInfo()
        elif tag == 7:
            const = ClassInfo()
        elif tag == 8:
            const = StringInfo()
        elif tag == 9:
            const = FieldRefInfo()
        elif tag == 10:
            const = MethodRefInfo()
        elif tag == 11:
            const = InterfaceMethodRefInfo()
        elif tag == 12:
            const = NameAndTypeInfo()
        else:
            raise UnknownTag, tag

        # Initialise the constant object.

        s = const.init(s[1:], self)
        return const, s

    def _get_constants_from_table(self, count, s):
        l = []
        # Have to skip certain entries specially.
        i = 1
        while i < count:
            c, s = self._decode_const(s)
            l.append(c)
            # Add a blank entry after "large" entries.
            if isinstance(c, LargeNumInfo):
                l.append(None)
                i += 1
            i += 1
        return l, s

    def _get_items_from_table(self, cls, number, s):
        l = []
        for i in range(0, number):
            f = cls()
            s = f.init(s, self)
            l.append(f)
        return l, s

    def _get_methods_from_table(self, number, s):
        return self._get_items_from_table(MethodInfo, number, s)

    def _get_fields_from_table(self, number, s):
        return self._get_items_from_table(FieldInfo, number, s)

    def _get_attribute_from_table(self, s):
        attribute_name_index = u2(s[0:2])
        constant_name = self.constants[attribute_name_index - 1].bytes
        if constant_name == "SourceFile":
            attribute = SourceFileAttributeInfo()
        elif constant_name == "ConstantValue":
            attribute = ConstantValueAttributeInfo()
        elif constant_name == "Code":
            attribute = CodeAttributeInfo()
        elif constant_name == "Exceptions":
            attribute = ExceptionsAttributeInfo()
        elif constant_name == "InnerClasses":
            attribute = InnerClassesAttributeInfo()
        elif constant_name == "Synthetic":
            attribute = SyntheticAttributeInfo()
        elif constant_name == "LineNumberTable":
            attribute = LineNumberAttributeInfo()
        elif constant_name == "LocalVariableTable":
            attribute = LocalVariableAttributeInfo()
        elif constant_name == "Deprecated":
            attribute = DeprecatedAttributeInfo()
        else:
            raise UnknownAttribute, constant_name
        s = attribute.init(s[2:], self)
        return attribute, s

    def _get_attributes_from_table(self, number, s):
        attributes = []
        for i in range(0, number):
            attribute, s = self._get_attribute_from_table(s)
            attributes.append(attribute)
        return attributes, s

    def _get_constants(self, s):
        count = u2(s[0:2])
        return self._get_constants_from_table(count, s[2:])

    def _get_access_flags(self, s):
        return u2(s[0:2]), s[2:]

    def _get_this_class(self, s):
        index = u2(s[0:2])
        return self.constants[index - 1], s[2:]

    _get_super_class = _get_this_class

    def _get_interfaces(self, s):
        interfaces = []
        number = u2(s[0:2])
        s = s[2:]
        for i in range(0, number):
            index = u2(s[0:2])
            interfaces.append(self.constants[index - 1])
            s = s[2:]
        return interfaces, s

    def _get_fields(self, s):
        number = u2(s[0:2])
        return self._get_fields_from_table(number, s[2:])

    def _get_attributes(self, s):
        number = u2(s[0:2])
        return self._get_attributes_from_table(number, s[2:])

    def _get_methods(self, s):
        number = u2(s[0:2])
        return self._get_methods_from_table(number, s[2:])

if __name__ == "__main__":
    import sys
    f = open(sys.argv[1], "rb")
    c = ClassFile(f.read())
    f.close()

# vim: tabstop=4 expandtab shiftwidth=4