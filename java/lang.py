#!/usr/bin/env python

class Character(object):
    def __init__(self, value):
        raise NotImplementedError, "__init__"
    def charValue(self):
        raise NotImplementedError, "charValue"
    def hashCode(self):
        raise NotImplementedError, "hashCode"
    def equals(self, anObject):
        raise NotImplementedError, "equals"
    def toString(self):
        raise NotImplementedError, "toString"
    def isLowerCase(self, ch):
        raise NotImplementedError, "isLowerCase"
    isLowerCase = staticmethod(isLowerCase)
    def isUpperCase(self, ch):
        raise NotImplementedError, "isUpperCase"
    isUpperCase = staticmethod(isUpperCase)
    def isTitleCase(self, ch):
        raise NotImplementedError, "isTitleCase"
    isTitleCase = staticmethod(isTitleCase)
    def isDigit(self, ch):
        raise NotImplementedError, "isDigit"
    isDigit = staticmethod(isDigit)
    def isDefined(self, ch):
        raise NotImplementedError, "isDefined"
    isDefined = staticmethod(isDefined)
    def isLetter(self, ch):
        raise NotImplementedError, "isLetter"
    isLetter = staticmethod(isLetter)
    def isLetterOrDigit(self, ch):
        raise NotImplementedError, "isLetterOrDigit"
    isLetterOrDigit = staticmethod(isLetterOrDigit)
    def isJavaLetter(self, ch):
        raise NotImplementedError, "isJavaLetter"
    isJavaLetter = staticmethod(isJavaLetter)
    def isJavaLetterOrDigit(self, ch):
        raise NotImplementedError, "isJavaLetterOrDigit"
    isJavaLetterOrDigit = staticmethod(isJavaLetterOrDigit)
    def isJavaIdentifierStart(self, ch):
        raise NotImplementedError, "isJavaIdentifierStart"
    isJavaIdentifierStart = staticmethod(isJavaIdentifierStart)
    def isJavaIdentifierPart(self, ch):
        raise NotImplementedError, "isJavaIdentifierPart"
    isJavaIdentifierPart = staticmethod(isJavaIdentifierPart)
    def isUnicodeIdentifierStart(self, ch):
        raise NotImplementedError, "isUnicodeIdentifierStart"
    isUnicodeIdentifierStart = staticmethod(isUnicodeIdentifierStart)
    def isUnicodeIdentifierPart(self, ch):
        raise NotImplementedError, "isUnicodeIdentifierPart"
    isUnicodeIdentifierPart = staticmethod(isUnicodeIdentifierPart)
    def isIdentifierIgnorable(self, ch):
        raise NotImplementedError, "isIdentifierIgnorable"
    isIdentifierIgnorable = staticmethod(isIdentifierIgnorable)
    def toLowerCase(self, ch):
        raise NotImplementedError, "toLowerCase"
    toLowerCase = staticmethod(toLowerCase)
    def toUpperCase(self, ch):
        raise NotImplementedError, "toUpperCase"
    toUpperCase = staticmethod(toUpperCase)
    def toTitleCase(self, ch):
        raise NotImplementedError, "toTitleCase"
    toTitleCase = staticmethod(toTitleCase)
    def digit(self, ch, radix):
        raise NotImplementedError, "digit"
    digit = staticmethod(digit)
    def getNumericValue(self, ch):
        raise NotImplementedError, "getNumericValue"
    getNumericValue = staticmethod(getNumericValue)
    def isSpace(self, ch):
        raise NotImplementedError, "isSpace"
    isSpace = staticmethod(isSpace)
    def isSpaceChar(self, ch):
        raise NotImplementedError, "isSpaceChar"
    isSpaceChar = staticmethod(isSpaceChar)
    def isWhitespace(self, ch):
        raise NotImplementedError, "isWhitespace"
    isWhitespace = staticmethod(isWhitespace)
    def isISOControl(self, ch):
        raise NotImplementedError, "isISOControl"
    isISOControl = staticmethod(isISOControl)
    def getType(self, ch):
        raise NotImplementedError, "getType"
    getType = staticmethod(getType)
    def forDigit(self, ch, radix):
        raise NotImplementedError, "forDigit"
    forDigit = staticmethod(forDigit)
    def compareTo(self, *args):
        # compareTo(self, anotherCharacter)
        # compareTo(self, o)
        raise NotImplementedError, "compareTo"

# NOTE: Establish a better exception hierarchy.

class IllegalArgumentException(object):
    def __init__(self, *args):
        self.args = args

setattr(IllegalArgumentException, "__init_____", IllegalArgumentException.__init__)
setattr(IllegalArgumentException, "__init_____java__lang__String", IllegalArgumentException.__init__)

class String(object):

    def init__empty(self):
        self.value = u""

    def init__String(self, obj):
        self.value = obj.value

    def __init__(self, *args):
        # Python string initialisation:
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
            self.__init__String(args[0])
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

# vim: tabstop=4 expandtab shiftwidth=4
