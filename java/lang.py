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

class String(object):
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
            self.value = u""
            return
        # __init__(self, original)
        elif len(args) == 1 and isinstance(args[0], String):
            self.value = args[0].value
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
    def charAt(self, index):
        return self.value[index]
    def getChars(self, srcBegin, srcEnd, dst, dstBegin):
        raise NotImplementedError, "getChars"
    def getBytes(self, *args):
        # void getBytes(self, srcBegin, srcEnd, dst, dstBegin)
        # byte[] getBytes(self, enc)
        # byte[] getBytes(self)
        raise NotImplementedError, "getBytes"
    def equals(self, anObject):
        raise NotImplementedError, "equals"
    def compareTo(self, obj):
        raise NotImplementedError, "compareTo"
    # NOTE: Comparator defined using private classes.
    def compareToIgnoreCase(self, str):
        raise NotImplementedError, "compareToIgnoreCase"
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
    def indexOf(self, *args):
        # indexOf(self, ch)
        # indexOf(self, ch, fromIndex)
        # indexOf(self, str)
        # indexOf(self, str, fromIndex)
        raise NotImplementedError, "indexOf"
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

# vim: tabstop=4 expandtab shiftwidth=4
