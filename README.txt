Importing Java Classes and Libraries
------------------------------------

The classhook.py import hook needs to be made available before imports from
Java classes and libraries (.jar files) can take place. This can be done
by either...

  1. Running the classhook.py file directly and then using the interactive
     interpreter:

     python -i classhook.py

  2. Putting classhook.py in sys.path or PYTHONPATH and importing the
     classhook module before any code importing Java classes and packages.

Java classes are located using sys.path or PYTHONPATH in the same way that
they would be located using the Java classpath (or CLASSPATH environment
variable).

  * Directories representing packages and containing Java class files must
    reside within directories specified on the PYTHONPATH. For example, the
    directory mypackage residing within /home/paulb/java would be used as
    follows:

    PYTHONPATH=/home/paulb/java python -i classhook.py

    And within Python:

    import mypackage

    Note that the classes within the directory should be assigned to the
    package mypackage.

  * Free-standing Java class files must reside in the current directory.
    For example, a collection of class files in /home/paulb/classes would be
    used as follows:

    cd /home/paulb/classes
    python -i /home/paulb/python/classhook.py

    And within Python:

    import __this__

    Note that such free-standing classes should not be assigned to any
    package and must therefore appear within the special package __this__
    and be imported under such special conditions.

  * Libraries contained within .jar files must be specified directly on the
    PYTHONPATH as if they were directories containing package hierarchies.
    For example, the library archive.jar, residing within /home/paulb/java
    and containing the package mypackage, would be used as follows:

    PYTHONPATH=/home/paulb/java/archive.jar python -i classhook.py

    And within Python:

    import mypackage

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
     imported and used as described above. The wrapper package needs to
     reside in sys.path or PYTHONPATH, as must the wrapped library.

Issues
------

Investigate better exception raising. Currently, exceptions have to be
derived from object so that object.__new__ can be used upon them. However,
this seems to prevent them from being raised, and they need to be wrapped
within Exception so that the information can be transmitted to the
exception's handler.

Consider nicer ways of writing the method names in Python, perhaps using a
function which takes the individual parameter types as arguments.
