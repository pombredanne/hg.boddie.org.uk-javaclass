#!/usr/bin/env python

import ihooks
import os, glob
from imp import PY_SOURCE, PKG_DIRECTORY, C_BUILTIN
import classfile, bytecode
import new

class ClassHooks(ihooks.Hooks):

    "A filesystem hooks class providing information about supported files."

    def get_suffixes(self):

        "Return the recognised suffixes."

        return ihooks.Hooks.get_suffixes(self) + [(os.extsep + "class", "r", PY_SOURCE)]

class ClassLoader(ihooks.ModuleLoader):

    "A class providing support for searching directories for supported files."

    """
    def find_module(self, name, path=None):
        print "find_module", name, path
        return ihooks.ModuleLoader.find_module(self, name, path)
    """

    def find_module_in_dir(self, name, dir):

        """
        Find the module with the given 'name' in the given directory 'dir'.
        Since Java packages/modules are directories containing class files,
        return the required information tuple only when the path constructed
        from 'dir' and 'name' refers to a directory containing class files.
        """

        dir = dir or "."

        # Provide a special name for the current directory.

        if name == "__this__":
            path = dir
        else:
            path = os.path.join(dir, name)

        print "Processing name", name, "in", dir, "producing", path

        if self._find_module_at_path(path):
            return (None, path, ("", "", PKG_DIRECTORY))
        else:
            return None

    def _find_module_at_path(self, path):
        if os.path.isdir(path):

            # Look for classes in the directory.

            if len(glob.glob(os.path.join(path, "*" + os.extsep + "class"))) != 0:
                return 1

            # Otherwise permit importing where directories containing classes exist.

            for filename in os.listdir(path):
                pathname = os.path.join(path, filename)
                result = self._find_module_at_path(pathname)
                if result is not None:
                    return result

        return None

    def load_module(self, name, stuff):

        """
        Load the module with the given 'name', whose 'stuff' which describes the
        location of the module is a tuple of the form (file, filename, (suffix,
        mode, data type)). Return a module object or raise an ImportError if a
        problem occurred in the import operation.
        """

        # Just go into the directory and find the class files.

        file, filename, info = stuff
        print "*", file, filename, info

        # Prepare a dictionary of globals.

        global_names = {}
        global_names.update(__builtins__.__dict__)
        module = self.hooks.add_module(name)

        # Process each class file, producing a genuine Python class.

        class_files = []
        for class_filename in glob.glob(os.path.join(filename, "*" + os.extsep + "class")):
            print "Importing class", class_filename
            f = open(class_filename, "rb")
            s = f.read()
            f.close()
            class_file = classfile.ClassFile(s)
            translator = bytecode.ClassTranslator(class_file)
            cls = translator.process(global_names)
            module.__dict__[cls.__name__] = cls

        module.__path__ = [filename]
        return module

"""
class ClassImporter(ihooks.ModuleImporter):

    def find_head_package(self, parent, name):
        print "find_head_package", parent, name
        return ihooks.ModuleImporter.find_head_package(self, parent, name)

    def import_it(self, partname, fqname, parent, force_load=0):
        print "import_it", partname, fqname, parent, force_load
        print "modules", self.modules
        try:
            return parent.__dict__[partname]

        except (KeyError, AttributeError):
            return ihooks.ModuleImporter.import_it(
                self, partname, fqname, parent, force_load
                )
"""

importer = ihooks.ModuleImporter(loader=ClassLoader(hooks=ClassHooks()))
importer.install()

# vim: tabstop=4 expandtab shiftwidth=4
