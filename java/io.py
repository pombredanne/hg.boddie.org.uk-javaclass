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
    write___java__lang__String = write
    write___java__lang__String____I_____I_ = write
    def flush(self):
        self.out.flush()
    flush___ = flush
    def close(self):
        self.out.close()
    close___ = close

class InputStream:
    def read(self, *args):
        raise NotImplementedError, "read"
    read___ = read
    def skip(self, n):
        raise NotImplementedError, "skip"
    skip___int = skip
    def available(self):
        raise NotImplementedError, "available"
    available___ = available
    def close(self):
        raise NotImplementedError, "close"
    close___ = close
    def mark(self, readlimit):
        raise NotImplementedError, "mark"
    mark___ = mark
    def reset(self):
        raise NotImplementedError, "reset"
    reset___ = reset
    def markSupported(self):
        raise NotImplementedError, "markSupported"
    markSupported___ = markSupported

class OutputStream:
    def write(self, b, *args):
        raise NotImplementedError, "write"
    write___java__lang__String = write
    def flush(self):
        raise NotImplementedError, "flush"
    flush___ = flush
    def close(self):
        raise NotImplementedError, "close"
    close___ = close

# vim: tabstop=4 expandtab shiftwidth=4
