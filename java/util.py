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

setattr(Hashtable, "__init__$", Hashtable.__init__)

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

setattr(ResourceBundle, "getBundle$java/lang/String", staticmethod(ResourceBundle.getBundle))
setattr(ResourceBundle, "getBundle$java/lang/String$java/util/Locale", staticmethod(ResourceBundle.getBundle))
setattr(ResourceBundle, "getBundle$java/lang/String$java/util/Locale$java/lang/ClassLoader", staticmethod(ResourceBundle.getBundle))

# vim: tabstop=4 expandtab shiftwidth=4
