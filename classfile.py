#!/usr/bin/env python

"""
Java class file decoder. Specification found at the following URL:
http://java.sun.com/docs/books/vmspec/2nd-edition/html/ClassFile.doc.html
"""

import struct

# Constant information.

class ClassInfo:
    def init(self, data):
        self.name_index = struct.unpack(">H", data[0:2])[0]
        return data[2:]

class RefInfo:
    def init(self, data):
        self.class_index = struct.unpack(">H", data[0:2])[0]
        self.name_and_type_index = struct.unpack(">H", data[2:4])[0]
        return data[4:]

class FieldRefInfo(RefInfo):
    pass

class MethodRefInfo(RefInfo):
    pass

class InterfaceMethodRefInfo(RefInfo):
    pass

class NameAndTypeInfo:
    def init(self, data):
        self.name_index = struct.unpack(">H", data[0:2])[0]
        self.descriptor_index = struct.unpack(">H", data[2:4])[0]
        return data[4:]

class Utf8Info:
    def init(self, data):
        self.length = struct.unpack(">H", data[0:2])[0]
        self.bytes = data[2:2+self.length]
        return data[2+self.length:]

    def __str__(self):
        return self.bytes

    def __unicode__(self):
        return unicode(self.bytes, "utf-8")

class StringInfo:
    def init(self, data):
        self.string_index = struct.unpack(">H", data[0:2])[0]
        return data[2:]

class SmallNumInfo:
    def init(self, data):
        self.bytes = struct.unpack(">L", data[0:4])[0]
        return data[4:]

class IntegerInfo(SmallNumInfo):
    pass

class FloatInfo(SmallNumInfo):
    pass

class LargeNumInfo:
    def init(self, data):
        self.high_bytes = struct.unpack(">L", data[0:4])[0]
        self.low_bytes = struct.unpack(">L", data[4:8])[0]
        return data[8:]

class LongInfo(LargeNumInfo):
    pass

class DoubleInfo(LargeNumInfo):
    pass

# Other information.

class ItemInfo:
    def init(self, data, class_file):
        self.class_file = class_file
        self.access_flags = struct.unpack(">H", data[0:2])[0]
        self.name_index = struct.unpack(">H", data[2:4])[0]
        self.descriptor_index = struct.unpack(">H", data[4:6])[0]
        self.attributes, data = self.class_file._get_attributes(data[6:])
        return data

    # Symbol parsing.

    def _get_method_descriptor(self, s):
        assert s[0] == "("
        params = []
        s = s[1:]
        while s[0] != ")":
            parameter_descriptor, s = self._get_parameter_descriptor(s)
            params.append(parameter_descriptor)
        if s[1] != "V":
            return_type, s = self._get_field_type(s[1:])
        else:
            return_type, s = None, s[1:]
        return params, return_type

    def _get_parameter_descriptor(self, s):
        return self._get_field_type(s)

    def _get_field_descriptor(self, s):
        return self._get_field_type(s)

    def _get_component_type(self, s):
        return self._get_field_type(s)

    def _get_field_type(self, s):
        base_type, s = self._get_base_type(s)
        object_type = None
        array_type = None
        if base_type == "L":
            object_type, s = self._get_object_type(s)
        elif base_type == "[":
            array_type, s = self._get_array_type(s)
        return (base_type, object_type, array_type), s

    def _get_base_type(self, s):
        if len(s) > 0:
            return s[0], s[1:]
        else:
            return None, s

    def _get_object_type(self, s):
        if len(s) > 0:
            s_end = s.find(";")
            assert s_end != -1
            return s[:s_end], s[s_end+1:]
        else:
            return None, s

    def _get_array_type(self, s):
        if len(s) > 0:
            return self._get_component_type(s[1:])
        else:
            return None, s

    # Processed details.

    def get_name(self):
        return unicode(self.class_file.constants[self.name_index - 1])

class FieldInfo(ItemInfo):
    def get_descriptor(self):
        return self._get_field_descriptor(unicode(self.class_file.constants[self.descriptor_index - 1]))

class MethodInfo(ItemInfo):
    def get_descriptor(self):
        return self._get_method_descriptor(unicode(self.class_file.constants[self.descriptor_index - 1]))

class AttributeInfo:
    def init(self, data, class_file):
        self.attribute_length = struct.unpack(">L", data[0:4])[0]
        self.info = data[4:4+self.attribute_length]
        return data[4+self.attribute_length:]

# NOTE: Decode the different attribute formats.

class SourceFileAttributeInfo(AttributeInfo):
    pass

class ConstantValueAttributeInfo(AttributeInfo):
    def init(self, data, class_file):
        self.attribute_length = struct.unpack(">L", data[0:4])[0]
        self.constant_value_index = struct.unpack(">H", data[4:6])[0]
        assert 4+self.attribute_length == 6
        return data[4+self.attribute_length:]

class CodeAttributeInfo(AttributeInfo):
    def init(self, data, class_file):
        self.class_file = class_file
        self.attribute_length = struct.unpack(">L", data[0:4])[0]
        self.max_stack = struct.unpack(">H", data[4:6])[0]
        self.max_locals = struct.unpack(">H", data[6:8])[0]
        self.code_length = struct.unpack(">L", data[8:12])[0]
        end_of_code = 12+self.code_length
        self.code = data[12:end_of_code]
        self.exception_table_length = struct.unpack(">H", data[end_of_code:end_of_code+2])[0]
        self.exception_table = []
        data = data[end_of_code + 2:]
        for i in range(0, self.exception_table_length):
            exception = ExceptionInfo()
            data = exception.init(data)
        self.attributes, data = self.class_file._get_attributes(data)
        return data

class ExceptionsAttributeInfo(AttributeInfo):
    pass

class InnerClassesAttributeInfo(AttributeInfo):
    pass

class SyntheticAttributeInfo(AttributeInfo):
    pass

class LineNumberAttributeInfo(AttributeInfo):
    pass

class LocalVariableAttributeInfo(AttributeInfo):
    pass

class DeprecatedAttributeInfo(AttributeInfo):
    pass

class ExceptionInfo:
    def __init__(self):
        self.start_pc, self.end_pc, self.handler_pc, self.catch_type = None, None, None, None

    def init(self, data):
        self.start_pc = struct.unpack(">H", data[0:2])[0]
        self.end_pc = struct.unpack(">H", data[2:4])[0]
        self.handler_pc = struct.unpack(">H", data[4:6])[0]
        self.catch_type = struct.unpack(">H", data[6:8])[0]
        return data[8:]

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
        tag = struct.unpack(">B", s[0:1])[0]
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
        s = const.init(s[1:])
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
        attribute_name_index = struct.unpack(">H", s[0:2])[0]
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
        count = struct.unpack(">H", s[0:2])[0]
        return self._get_constants_from_table(count, s[2:])

    def _get_access_flags(self, s):
        return struct.unpack(">H", s[0:2])[0], s[2:]

    def _get_this_class(self, s):
        index = struct.unpack(">H", s[0:2])[0]
        return self.constants[index - 1], s[2:]

    _get_super_class = _get_this_class

    def _get_interfaces(self, s):
        interfaces = []
        number = struct.unpack(">H", s[0:2])[0]
        s = s[2:]
        for i in range(0, number):
            index = struct.unpack(">H", s[0:2])[0]
            interfaces.append(self.constants[index - 1])
            s = s[2:]
        return interfaces, s

    def _get_fields(self, s):
        number = struct.unpack(">H", s[0:2])[0]
        return self._get_fields_from_table(number, s[2:])

    def _get_attributes(self, s):
        number = struct.unpack(">H", s[0:2])[0]
        return self._get_attributes_from_table(number, s[2:])

    def _get_methods(self, s):
        number = struct.unpack(">H", s[0:2])[0]
        return self._get_methods_from_table(number, s[2:])

if __name__ == "__main__":
    import sys
    f = open(sys.argv[1])
    c = ClassFile(f.read())

# vim: tabstop=4 expandtab shiftwidth=4
