#!/usr/bin/env python

"""
Wrap Java packages, converting the skeleton Java classes to Python modules which
connect to concrete Python implementation classes.
"""

import classfile
import glob
import sys
import os

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "wrap.py <package directory> <wrapped package>"
        print "For example:"
        print "wrap.py qtjava qt"
        sys.exit(1)

    # Process all directories in the list, producing for each a Python source
    # file containing the classes found in the given directory.

    directory, package = sys.argv[1:3]
    f = open(os.path.join(directory, "__init__.py"), "w")
    f.write("import %s\n" % package)

    # Process each class file.

    for filename in glob.glob(os.path.join(directory, "*.class")):
        print "Processing", filename
        cf = open(filename, "rb")
        c = classfile.ClassFile(cf.read())
        cf.close()

        # Write the class into the source file.

        full_name = c.this_class.get_python_name()
        class_name = full_name.split(".")[-1]
        f.write("class %s(%s.%s):\n" % (class_name, package, class_name))

        # Process methods in the class, writing wrapper code.

        method_names = []
        for method in c.methods:
            wrapped_method_name = method.get_unqualified_python_name()
            f.write("    def %s(*args):\n" % wrapped_method_name)
            f.write("        return %s.%s.%s(*args)\n" % (package, class_name, wrapped_method_name))
            method_name = method.get_python_name()
            method_names.append((method_name, wrapped_method_name))

        # Produce method entries for the specially named methods.

        for method_name, wrapped_method_name in method_names:
            f.write("setattr(%s, '%s', %s.%s)\n" % (class_name, method_name, class_name, wrapped_method_name))

    f.close()

# vim: tabstop=4 expandtab shiftwidth=4
