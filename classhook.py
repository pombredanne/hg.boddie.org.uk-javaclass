#!/usr/bin/env python

import ihooks # for the import machinery
import os, glob # for getting suitably-named files
from imp import PY_SOURCE, PKG_DIRECTORY, C_BUILTIN # import machinery magic
import classfile, bytecode # Java class support
import zipfile # for Java archive inspection

# NOTE: Arbitrary constants pulled from thin air.

JAVA_PACKAGE = 20041113
JAVA_CLASS = 20041114
JAVA_ARCHIVE = 20041115

class ClassHooks(ihooks.Hooks):

    "A filesystem hooks class providing information about supported files."

    def get_suffixes(self):

        "Return the recognised suffixes."

        return [("", "", JAVA_PACKAGE), (os.extsep + "jar", "r", JAVA_ARCHIVE)] + ihooks.Hooks.get_suffixes(self)

    def path_isdir(self, x, archive=None):

        "Return whether 'x' is a directory in the given 'archive'."

        if archive is None:
            return ihooks.Hooks.path_isdir(self, x)

        return self._get_dirname(x) in archive.namelist()

    def _get_dirname(self, x):

        """
        Return the directory name for 'x'.
        In zip files, the presence of "/" seems to indicate a directory.
        """

        if x.endswith("/"):
            return x
        else:
            return x + "/"

    def listdir(self, x, archive=None):

        "Return the contents of the directory 'x' in the given 'archive'."

        if archive is None:
            return ihooks.Hooks.listdir(self, x)

        x = self._get_dirname(x)
        l = []
        for path in archive.namelist():

            # Find out if the path is within the given directory.

            if path != x and path.startswith(x):

                # Get the path below the given directory.

                subpath = path[len(x):]

                # Find out whether the path is an object in the current directory.

                if subpath.count("/") == 0 or subpath.count("/") == 1 and subpath.endswith("/"):
                    l.append(subpath)

        return l

    def matching(self, dir, extension, archive=None):

        """
        Return the matching files in the given directory 'dir' having the given
        'extension' within the given 'archive'. Produce a list containing full
        paths as opposed to simple filenames.
        """

        if archive is None:
            return glob.glob(self.path_join(dir, "*" + extension))

        dir = self._get_dirname(dir)
        l = []
        for path in self.listdir(dir, archive):
            if path.endswith(extension):
                l.append(self.path_join(dir, path))
        return l

    def read(self, filename, archive=None):

        """
        Return the contents of the file with the given 'filename' in the given
        'archive'.
        """

        if archive is None:
            f = open(filename, "rb")
            s = f.read()
            f.close()
            return s
        return archive.read(filename)

class ClassLoader(ihooks.ModuleLoader):

    "A class providing support for searching directories for supported files."

    def find_module_in_dir(self, name, dir, allow_packages=1):

        """
        Find the module with the given 'name' in the given directory 'dir'.
        Since Java packages/modules are directories containing class files,
        return the required information tuple only when the path constructed
        from 'dir' and 'name' refers to a directory containing class files.
        """

        result = ihooks.ModuleLoader.find_module_in_dir(self, name, dir, allow_packages)
        if result is not None:
            return result

        # An archive may be opened.

        archive = None

        # Provide a special name for the current directory.

        if name == "__this__":
            path = "."

        # Where no directory is given, return failure immediately.

        elif dir is None:
            return None

        # Detect archives.

        else:
            archive, archive_path, path = self._get_archive_and_path(dir, name)

        #print "Processing name", name, "in", dir, "producing", path, "within archive", archive

        if self._find_module_at_path(path, archive):
            if archive is not None:
                return (archive, archive_path + ":" + path, (os.extsep + "jar", "r", JAVA_ARCHIVE))
            else:
                return (None, path, ("", "", JAVA_PACKAGE))
        else:
            return None

    def _get_archive_and_path(self, dir, name):
        parts = dir.split(":")
        archive_path = parts[0]

        # Archives may include an internal path, but will in any case have
        # a primary part ending in .jar.

        if archive_path.endswith(os.extsep + "jar"):
            archive = zipfile.ZipFile(archive_path, "r")
            path = self.hooks.path_join(":".join(parts[1:]), name)

        # Otherwise, produce a filesystem-based path.

        else:
            archive = None
            path = self.hooks.path_join(dir, name)

        return archive, archive_path, path

    def _get_path_in_archive(self, path):
        parts = path.split(":")
        if len(parts) == 1:
            return parts[0]
        else:
            return ":".join(parts[1:])

    def _find_module_at_path(self, path, archive):
        if self.hooks.path_isdir(path, archive):
            #print "Looking in", path, "using archive", archive

            # Look for classes in the directory.

            if len(self.hooks.matching(path, os.extsep + "class", archive)) != 0:
                return 1

            # Otherwise permit importing where directories containing classes exist.

            #print "Filenames are", self.hooks.listdir(path, archive)
            for filename in self.hooks.listdir(path, archive):
                pathname = self.hooks.path_join(path, filename)
                result = self._find_module_at_path(pathname, archive)
                if result is not None:
                    return result

        return 0

    def load_module(self, name, stuff):

        """
        Load the module with the given 'name', whose 'stuff' which describes the
        location of the module is a tuple of the form (file, filename, (suffix,
        mode, data type)). Return a module object or raise an ImportError if a
        problem occurred in the import operation.
        """

        # Just go into the directory and find the class files.

        archive, filename, info = stuff
        suffix, mode, datatype = info
        if datatype not in (JAVA_PACKAGE, JAVA_ARCHIVE):
            return ihooks.ModuleLoader.load_module(self, name, stuff)

        #print "Loading", archive, filename, info

        # Set up the module.

        module = self.hooks.add_module(name)
        module.__path__ = [filename]

        # Prepare a dictionary of globals.

        global_names = module.__dict__
        global_names["__builtins__"] = __builtins__

        # Process each class file, producing a genuine Python class.

        class_files = []
        classes = []

        # Get the real filename.

        filename = self._get_path_in_archive(filename)
        #print "Real filename", filename

        # Load the class files.

        class_files = {}
        for class_filename in self.hooks.matching(filename, os.extsep + "class", archive):
            #print "Loading class", class_filename
            s = self.hooks.read(class_filename, archive)
            class_file = classfile.ClassFile(s)
            class_files[str(class_file.this_class.get_name())] = class_file

        # Get an index of the class files.

        class_file_index = class_files.keys()

        # NOTE: Unnecessary sorting for test purposes.

        class_file_index.sort()

        # Now go through the classes arranging them in a safe loading order.

        position = 0
        while position < len(class_file_index):
            class_name = class_file_index[position]
            super_class_name = str(class_files[class_name].super_class.get_name())

            # Discover whether the superclass appears later.

            try:
                super_class_position = class_file_index.index(super_class_name)
                if super_class_position > position:

                    # If the superclass appears later, swap this class and the
                    # superclass, then process the superclass.

                    class_file_index[position] = super_class_name
                    class_file_index[super_class_position] = class_name
                    continue

            except ValueError:
                pass

            position += 1

        class_files = [class_files[class_name] for class_name in class_file_index]

        for class_file in class_files:
            translator = bytecode.ClassTranslator(class_file)
            cls, external_names = translator.process(global_names)
            module.__dict__[cls.__name__] = cls
            classes.append((cls, class_file))

            # Import the local names.

            for external_name in external_names:
                external_name_parts = external_name.split(".")
                if len(external_name_parts) > 1:
                    external_module_name = ".".join(external_name_parts[:-1])
                    print "* Importing", external_module_name
                    obj = __import__(external_module_name, global_names, {}, [])
                    global_names[external_name_parts[0]] = obj

        # Finally, call __clinit__ methods for all relevant classes.

        for cls, class_file in classes:
            print "**", cls, class_file
            if hasattr(cls, "__clinit__"):
                eval(cls.__clinit__.func_code, global_names)

        return module

ihooks.ModuleImporter(loader=ClassLoader(hooks=ClassHooks())).install()

# vim: tabstop=4 expandtab shiftwidth=4
