#!/usr/bin/env python

"""
Wrap Java packages, converting the skeleton Java classes to Python modules which
connect to concrete Python implementation classes.
"""

import javaclass.classfile
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
    f.write("import java.lang\n")

    # Process each class file.

    for filename in glob.glob(os.path.join(directory, "*.class")):
        print "Processing", filename
        cf = open(filename, "rb")
        c = javaclass.classfile.ClassFile(cf.read())
        cf.close()

        # Write the class into the source file.

        full_name = c.this_class.get_python_name()
        class_name = full_name.split(".")[-1]
        f.write("class %s(%s.%s, java.lang.Object):\n" % (class_name, package, class_name))

        # Process methods in the class, writing wrapper code.

        method_names = []
        for method in c.methods:
            wrapped_method_name = method.get_unqualified_python_name()

            # Find out more about the parameters, introducing special
            # conversions where appropriate.

            parameter_names = ["self"]
            parameter_index = 1
            conversions = []

            for parameter in method.get_descriptor()[0]:
                parameter_name = "p" + str(parameter_index)
                base_type, object_type, array_type = parameter

                # Special cases.

                if object_type == "java/lang/String":
                    conversions.append("%s = unicode(%s)" % (parameter_name, parameter_name))
                # elif object_type == "java/util/Map":
                    # NOTE: Using special private interface.
                    # conversions.append("%s = %s.as_dict()" % (parameter_name, parameter_name))

                parameter_names.append(parameter_name)
                parameter_index += 1

            # Write the signature.

            f.write("    def %s(%s):\n" % (wrapped_method_name, ", ".join(parameter_names)))

            # Write any conversions.

            for conversion in conversions:
                f.write("        %s\n" % conversion)

            # Write the call to the wrapped method.

            f.write("        return %s.%s.%s(%s)\n" % (package, class_name, wrapped_method_name, ", ".join(parameter_names)))

            # Record the correspondence between the Java-accessible and wrapped
            # method names.

            method_name = method.get_python_name()
            method_names.append((method_name, wrapped_method_name))

        # Produce method entries for the specially named methods.

        for method_name, wrapped_method_name in method_names:
            f.write("setattr(%s, '%s', %s.%s)\n" % (class_name, method_name, class_name, wrapped_method_name))

        # Remove the original class.

        print "Removing", filename
        os.remove(filename)

    f.close()

# vim: tabstop=4 expandtab shiftwidth=4
