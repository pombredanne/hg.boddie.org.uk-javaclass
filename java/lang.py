#!/usr/bin/env python

import java.io
import os
import sys

class Character(object):
    def __init__(self, value):
        raise NotImplementedError, "__init__"

    def charValue(self):
        raise NotImplementedError, "charValue"
    charValue___ = charValue

    def hashCode(self):
        raise NotImplementedError, "hashCode"
    hashCode___ = hashCode

    def equals(self, anObject):
        raise NotImplementedError, "equals"
    equals___java__lang__Object = equals

    def toString(self):
        raise NotImplementedError, "toString"
    toString___ = toString

    def isLowerCase(self, ch):
        raise NotImplementedError, "isLowerCase"
    isLowerCase____C_ = staticmethod(isLowerCase)

    def isUpperCase(self, ch):
        raise NotImplementedError, "isUpperCase"
    isUpperCase____C_ = staticmethod(isUpperCase)

    def isTitleCase(self, ch):
        raise NotImplementedError, "isTitleCase"
    isTitleCase____C_ = staticmethod(isTitleCase)

    def isDigit(self, ch):
        raise NotImplementedError, "isDigit"
    isDigit____C_ = staticmethod(isDigit)

    def isDefined(self, ch):
        raise NotImplementedError, "isDefined"
    isDefined____C_ = staticmethod(isDefined)

    def isLetter(self, ch):
        raise NotImplementedError, "isLetter"
    isLetter____C_ = staticmethod(isLetter)

    def isLetterOrDigit(self, ch):
        raise NotImplementedError, "isLetterOrDigit"
    isLetterOrDigit____C_ = staticmethod(isLetterOrDigit)

    def isJavaLetter(self, ch):
        raise NotImplementedError, "isJavaLetter"
    isJavaLetter____C_ = staticmethod(isJavaLetter)

    def isJavaLetterOrDigit(self, ch):
        raise NotImplementedError, "isJavaLetterOrDigit"
    isJavaLetterOrDigit____C_ = staticmethod(isJavaLetterOrDigit)

    def isJavaIdentifierStart(self, ch):
        raise NotImplementedError, "isJavaIdentifierStart"
    isJavaIdentifierStart____C_ = staticmethod(isJavaIdentifierStart)

    def isJavaIdentifierPart(self, ch):
        raise NotImplementedError, "isJavaIdentifierPart"
    isJavaIdentifierPart____C_ = staticmethod(isJavaIdentifierPart)

    def isUnicodeIdentifierStart(self, ch):
        raise NotImplementedError, "isUnicodeIdentifierStart"
    isUnicodeIdentifierStart____C_ = staticmethod(isUnicodeIdentifierStart)

    def isUnicodeIdentifierPart(self, ch):
        raise NotImplementedError, "isUnicodeIdentifierPart"
    isUnicodeIdentifierPart____C_ = staticmethod(isUnicodeIdentifierPart)

    def isIdentifierIgnorable(self, ch):
        raise NotImplementedError, "isIdentifierIgnorable"
    isIdentifierIgnorable____C_ = staticmethod(isIdentifierIgnorable)

    def toLowerCase(self, ch):
        raise NotImplementedError, "toLowerCase"
    toLowerCase____C_ = staticmethod(toLowerCase)

    def toUpperCase(self, ch):
        raise NotImplementedError, "toUpperCase"
    toUpperCase____C_ = staticmethod(toUpperCase)

    def toTitleCase(self, ch):
        raise NotImplementedError, "toTitleCase"
    toTitleCase____C_ = staticmethod(toTitleCase)

    def digit(self, ch, radix):
        raise NotImplementedError, "digit"
    digit____C_____I_ = staticmethod(digit)

    def getNumericValue(self, ch):
        raise NotImplementedError, "getNumericValue"
    getNumericValue____C_ = staticmethod(getNumericValue)

    def isSpace(self, ch):
        raise NotImplementedError, "isSpace"
    isSpace____C_ = staticmethod(isSpace)

    def isSpaceChar(self, ch):
        raise NotImplementedError, "isSpaceChar"
    isSpaceChar____C_ = staticmethod(isSpaceChar)

    def isWhitespace(self, ch):
        raise NotImplementedError, "isWhitespace"
    isWhitespace____C_ = staticmethod(isWhitespace)

    def isISOControl(self, ch):
        raise NotImplementedError, "isISOControl"
    isISOControl____C_ = staticmethod(isISOControl)

    def getType(self, ch):
        raise NotImplementedError, "getType"
    getType____C_ = staticmethod(getType)

    def forDigit(self, ch, radix):
        raise NotImplementedError, "forDigit"
    forDigit____C_____I_ = staticmethod(forDigit)

    def compareTo(self, *args):
        # compareTo(self, anotherCharacter)
        # compareTo(self, o)
        raise NotImplementedError, "compareTo"
    compareTo____C_ = compareTo
    compareTo___java__lang__Object = compareTo

setattr(Character, "__init____C_", Character.__init__)

class Class(object):
    def forName(className):
        parts = unicode(className).split(".")
        obj = __import__(".".join(parts[:-1]), globals(), {}, [])
        for part in parts[1:]:
            obj = getattr(obj, part)
        return obj

    forName___java__lang__String = staticmethod(forName)
    # NOTE: To be enhanced.
    forName___java__lang__String____Z____java__lang__ClassLoader = staticmethod(forName)

# NOTE: Establish a better exception hierarchy.

class Error(object):
    def __init__(self, *args):
        self.args = args

setattr(Error, "__init_____", Error.__init__)
setattr(Error, "__init_____java__lang__String", Error.__init__)

class Exception(object):
    def __init__(self, *args):
        self.args = args

setattr(Exception, "__init_____", Exception.__init__)
setattr(Exception, "__init_____java__lang__String", Exception.__init__)

class IndexOutOfBoundsException(object):
    def __init__(self, *args):
        self.args = args

setattr(IndexOutOfBoundsException, "__init_____", IndexOutOfBoundsException.__init__)
setattr(IndexOutOfBoundsException, "__init_____java__lang__String", IndexOutOfBoundsException.__init__)

class IllegalArgumentException(Exception):
    def __init__(self, *args):
        self.args = args

setattr(IllegalArgumentException, "__init_____", IllegalArgumentException.__init__)
setattr(IllegalArgumentException, "__init_____java__lang__String", IllegalArgumentException.__init__)

class NullPointerException(object):
    def __init__(self, *args):
        self.args = args

setattr(NullPointerException, "__init_____", NullPointerException.__init__)
setattr(NullPointerException, "__init_____java__lang__String", NullPointerException.__init__)

class SecurityException(Exception):
    def __init__(self, *args):
        self.args = args

setattr(SecurityException, "__init_____", SecurityException.__init__)
setattr(SecurityException, "__init_____java__lang__String", SecurityException.__init__)

class String(object):

    # NOTE: This method should not be needed, really.
    def __str__(self):
        return self.value.encode("utf-8")

    def __unicode__(self):
        return self.value

    def init__empty(self):
        self.value = u""

    def init__String(self, obj):
        self.value = obj.value

    def __init__(self, *args):

        "Python string initialisation only."

        if len(args) == 1 and isinstance(args[0], str):
            self.value = unicode(args[0])
            return
        elif len(args) == 1 and isinstance(args[0], unicode):
            self.value = args[0]
            return
        # __init__(self)
        elif len(args) == 0:
            self.__init__empty()
            return
        # __init__(self, original)
        elif len(args) == 1 and isinstance(args[0], String):
            self.init__String(args[0])
            return
        # __init__(self, value)
        # __init__(self, value, offset, count)
        # __init__(self, ascii, hibyte, offset, count)
        # __init__(self, ascii, hibyte)
        # __init__(self, bytes, offset, length, enc)
        # __init__(self, bytes, enc)
        # __init__(self, bytes, offset, length)
        # __init__(self, bytes)
        elif len(args) >= 1 and isinstance(args[0], list):
            raise NotImplementedError, "__init__"
        # __init__(self, buffer)
        raise NotImplementedError, "__init__"

    def length(self):
        return len(self.value)
    length___ = length

    def charAt(self, index):
        return ord(self.value[index])
    charAt____I_ = charAt

    def getChars(self, srcBegin, srcEnd, dst, dstBegin):
        raise NotImplementedError, "getChars"
    getChars____I_____I_____C__array_____I_ = getChars

    def getBytes(self, *args):
        # void getBytes(self, srcBegin, srcEnd, dst, dstBegin)
        # byte[] getBytes(self, enc)
        # byte[] getBytes(self)
        raise NotImplementedError, "getBytes"
    getBytes___ = getBytes
    getBytes____I_____I_____B__array_____I_ = getBytes

    def equals(self, anObject):
        return isinstance(anObject, self.__class__) and self.value == anObject.value
    equals___java__lang__Object = equals

    def compareTo(self, obj):
        if self.value < obj.value:
            return -1
        elif self.value == obj.value:
            return 0
        else:
            return 1
    compareTo___java__lang__String = compareTo

    # NOTE: Comparator defined using private classes. This implementation just
    # NOTE: uses Python's lower method.
    def compareToIgnoreCase(self, str):
        value = self.value.lower()
        value2 = str.value.lower()
        if value < value2:
            return -1
        elif value == value2:
            return 0
        else:
            return 1
    compareToIgnoreCase___java__lang__String = compareToIgnoreCase

    # NOTE: Comparator defined using private classes. This implementation just
    # NOTE: uses Python's lower method.
    def equalsIgnoreCase(self, anotherString):
        value = self.value.lower()
        value2 = anotherString.value.lower()
        return value == value2
    equalsIgnoreCase___java__lang__String = equalsIgnoreCase

    def regionMatches(self, *args):
        # regionMatches(self, toffset, other, ooffset, len)
        # regionMatches(self, ignoreCase, toffset, other, ooffset, len)
        raise NotImplementedError, "regionMatches"

    def startsWith(self, *args):
        # startsWith(self, prefix, toffset)
        # startsWith(self, prefix)
        raise NotImplementedError, "startsWith"

    def endsWith(self, suffix):
        raise NotImplementedError, "endsWith"

    def hashCode(self):
        raise NotImplementedError, "hashCode"

    def indexOf____I_(self, ch):
        return self.value.find(chr(ch))

    def indexOf____I_____I_(self, ch, fromIndex):
        return self.value.find(chr(ch), fromIndex)

    def indexOf___java__lang__String___(self, str):
        return self.value.find(str.value)

    def indexOf___java__lang__String____I_(self, str, fromIndex):
        return self.value.find(str.value, fromIndex)

    def lastIndexOf(self, *args):
        # lastIndexOf(self, ch)
        # lastIndexOf(self, ch, fromIndex)
        # lastIndexOf(self, str)
        # lastIndexOf(self, str, fromIndex)
        raise NotImplementedError, "lastIndexOf"

    def substring(self, *args):
        # substring(self, beginIndex)
        # substring(self, beginIndex, endIndex)
        raise NotImplementedError, "substring"

    def concat(self, str):
        raise NotImplementedError, "concat"

    def replace(self, oldChar, newChar):
        raise NotImplementedError, "replace"

    def toLowerCase(self, *args):
        # toLowerCase(self, locale)
        # toLowerCase(self)
        raise NotImplementedError, "toLowerCase"

    def toUpperCase(self, *args):
        # toUpperCase(self, locale)
        # toUpperCase(self)
        raise NotImplementedError, "toUpperCase"

    def trim(self):
        raise NotImplementedError, "trim"

    def toString(self):
        return self

    def toCharArray(self):
        raise NotImplementedError, "toCharArray"

    def valueOf(self, *args):
        # valueOf(self, obj)
        # valueOf(self, data)
        # valueOf(self, data, offset, count)
        # valueOf(self, b)
        # valueOf(self, c)
        # valueOf(self, l)
        # valueOf(self, f)
        # valueOf(self, d)
        raise NotImplementedError, "valueOf"
    valueOf = staticmethod(valueOf)

    def copyValueOf(self, *args):
        # copyValueOf(self, data, offset, count)
        # copyValueOf(self, data)
        raise NotImplementedError, "copyValueOf"
    copyValueOf = staticmethod(copyValueOf)

    def intern(self):
        raise NotImplementedError, "intern"

setattr(String, "__init_____", String.init__empty)
setattr(String, "__init_____java__lang__String", String.init__String)

class System(object):
    in_ = java.io.InputStream(sys.stdin)
    out = java.io.PrintStream(sys.stdout)
    err = java.io.PrintStream(sys.stderr)

    def getProperty___java__lang__String(key):
        try:
            return os.environ[key]
        except KeyError:
            return None

    getProperty___java__lang__String = staticmethod(getProperty___java__lang__String)

setattr(System, "in", System.in_)

# vim: tabstop=4 expandtab shiftwidth=4
