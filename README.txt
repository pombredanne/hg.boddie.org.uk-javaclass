Class Search Paths
------------------

Java classes belonging to packages are located using sys.path or PYTHONPATH
in the same way that they would be located using the Java classpath (or
CLASSPATH environment variable). Thus, the rules for locating package
classes are as follows:

 * Classes residing within plain directories which represent a package
   hierarchy can be accessed by putting the parent directory of the top of
   the package hierarchy on the PYTHONPATH (or sys.path). For example, a
   package called mypackage, represented by a directory of the same name at
   /home/java/classes/mypackage, would be made accessible by adding the
   /home/java/classes directory to the PYTHONPATH.

 * Classes residing within .jar files can be accessed by putting the path to
   each .jar file on the PYTHONPATH. For example, a package called
   mypackage, represented by a file located at /home/java/lib/mypackage.jar,
   would be made accessible by adding the /home/java/lib/mypackage.jar file
   to the PYTHONPATH.

Note that classes not belonging to a package cannot be accessed via such
search paths and are made available using a special module (see "Non-package
Classes" below).

Importing Classes
-----------------

The classhook.py import hook needs to be made available before imports from
Java classes and libraries (.jar files) can take place. This can be done
by either...

  * Running the classhook.py file directly and then using the interactive
    interpreter:

    python -i classhook.py

  * Putting classhook.py in sys.path or PYTHONPATH and importing the
    classhook module before any code importing Java classes and packages.

Importing Non-package Classes
-----------------------------

Classes which do not belong to a package are only accessible when residing
in the current working directory of any program attempting to use them. Such
classes will not be made available automatically, but must be imported from
a special module called __this__.

 * Usage of the "import __this__" statement will cause all classes in the
   current directory to be made available within the __this__ module.

 * Usage of the "from __this__ import" construct will cause all classes in
   the current directory to be processsed, but only named classes will be
   made available in the global namespace unless "*" was specified (which
   will, as usual, result in all such classes being made available).

Running Java Classes
--------------------

Java classes with a public, static main method can be run directly using the
runclass.py program.

  * Free-standing classes (ie. not belonging to packages) can be run from
    the directory in which they reside. For example, suitable classes in the
    tests directory would be run as follows:

    cd tests
    python ../runclass.py MainTest hello world

    If runclass.py is executable and on the PATH, then the following can be
    used instead:

    cd tests
    runclass.py MainTest hello world

  * Classes residing in packages can be run by ensuring that the packages
    are registered on the PYTHONPATH (see "Class Search Paths" above). Then,
    the testpackage.MainTest class (for example) would be run as follows:

    python runclass.py testpackage.MainTest hello world

    If runclass.py is executable and on the PATH, then the following can be
    used instead:

    runclass.py testpackage.MainTest hello world

Accessing Python Libraries from Java
------------------------------------

To wrap Python libraries for use with Java, skeleton classes need to be
compiled corresponding to each of the wrapped classes. Each of the methods
in the skeleton classes can be empty (or return any permissible value) since
the only purpose they serve is to provide the Java compiler with information
about the Python libraries.

  1. Compile the skeleton classes:

     javac examples/Qt/qtjava/QWidget.java

  2. Compile the Java classes which use the wrapped Python libraries:

     javac -classpath examples/Qt examples/Qt/WidgetTest.java

  3. Run the wrap.py tool on the directory where the skeleton class files
     reside, providing the name of the Python package or module being
     wrapped. This converts the directory into a Python package:

     PYTHONPATH=. python tools/wrap.py examples/Qt/qtjava qt

     Since the Java class files, if left in the processed directory, would
     be detected and imported using the classhook.py import hook, and since
     this would result in two conflicting implementations being imported
     (with possibly the non-functional Java classes being made available
     instead of the generated wrapper classes), the wrap.py tool removes all
     processed class files, leaving only Python source files in the
     processed directory.

  4. The Java classes which use the wrapped Python libraries can now be
     imported and used as described above. The wrapper package (qtjava in
     the above example) needs to reside in sys.path or PYTHONPATH, as must
     the wrapped library (qt in the above example).

Issues
------

Investigate better exception raising. Currently, exceptions have to be
derived from object so that object.__new__ can be used upon them. However,
this seems to prevent them from being raised, and they need to be wrapped
within Exception so that the information can be transmitted to the
exception's handler.

Consider nicer ways of writing the method names in Python, perhaps using a
function which takes the individual parameter types as arguments.
