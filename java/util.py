#!/usr/bin/env python

class EventObject(object):
    def __init__(self, source):
        self.source = source
    def getSource(self):
        return self.source
    def toString(self):
        # NOTE: Use Python conventions.
        return str(self)

class Hashtable(object):
    def __init__(self, *args):
        # NOTE: To be implemented.
        pass

setattr(Hashtable, "__init_____", Hashtable.__init__)

class ResourceBundle(object):
    def __init__(self, *args):
        # NOTE: To be implemented.
        pass

    def getBundle(self, *args):
        # getBundle(self, baseName)
        # getBundle(self, baseName, locale)
        # getBundle(self, baseName, locale, loader)
        # NOTE: Obviously not the correct implementation.
        return ResourceBundle(args)
    getBundle = staticmethod(getBundle)
    getBundle___java__lang__String = getBundle
    getBundle___java__lang__String___java__util__Locale = getBundle
    getBundle___java__lang__String___java__util__Locale___java__lang__ClassLoader = getBundle

    def getObject(self, key):
        # NOTE: To be implemented.
        return None
    getObject___java__lang__String = getObject

    def getString(self, key):
        # NOTE: To be implemented.
        return None
    getString___java__lang__String = getString

    def getStringArray(self, key):
        # NOTE: To be implemented.
        return None
    getStringArray___java__lang__String = getStringArray

    def getLocale(self, key):
        # NOTE: To be implemented.
        return None
    getLocale___ = getLocale

# vim: tabstop=4 expandtab shiftwidth=4
