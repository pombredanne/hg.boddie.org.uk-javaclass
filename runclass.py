#!/usr/bin/env python

"A program to run Java class files."

import classhook

def load_class(class_name):

    "Load the class with the given 'class_name'."

    class_name_parts = class_name.split(".")
    if len(class_name_parts) == 1:
        module = __import__("__this__", globals(), locals(), [class_name])
        obj = getattr(module, class_name)
    else:
        class_module = ".".join(class_name_parts[:-1])
        obj = __import__(class_module, globals(), locals())
        for part in class_name_parts[1:]:
            obj = getattr(obj, part)

    return obj

def run_class(cls, args):
    cls.main(args)

if __name__ == "__main__":
    import sys
    cls = load_class(sys.argv[1])
    run_class(cls, sys.argv[2:])

# vim: tabstop=4 expandtab shiftwidth=4
