#!/usr/bin/env python

class FilterOutputStream:
    def __init__(self, out):
        self.out = out
    def write(self, value, *args):
        if args:
            start, length = args
            self.out.write(value[start:start+length])
        else:
            self.out.write(value)
    def flush(self):
        self.out.flush()
    def close(self):
        self.out.close()

class InputStream:
    def read(self, *args):
        raise NotImplementedError, "read"
    def skip(self, n):
        raise NotImplementedError, "skip"
    def available(self):
        raise NotImplementedError, "available"
    def close(self):
        raise NotImplementedError, "close"
    def mark(self, readlimit):
        raise NotImplementedError, "mark"
    def reset(self):
        raise NotImplementedError, "reset"
    def markSupported(self):
        raise NotImplementedError, "markSupported"

class OutputStream:
    def write(self, b, *args):
        raise NotImplementedError, "write"
    def flush(self):
        raise NotImplementedError, "flush"
    def close(self):
        raise NotImplementedError, "close"

# vim: tabstop=4 expandtab shiftwidth=4
