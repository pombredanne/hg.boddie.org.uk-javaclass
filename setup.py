#! /usr/bin/env python

from distutils.core import setup

import javaclass

setup(
    name         = "javaclass",
    description  = "A Java class and package importer with utilities.",
    author       = "Paul Boddie",
    author_email = "paul@boddie.org.uk",
    url          = "http://www.boddie.org.uk/python/javaclass.html",
    version      = javaclass.__version__,
    packages     = ["javaclass", "java", "java.lang", "java.security"],
    scripts      = ["runclass.py"]
    )
