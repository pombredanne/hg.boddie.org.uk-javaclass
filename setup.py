#! /usr/bin/env python

from distutils.core import setup

setup(
    name         = "ClassFile",
    description  = "A Java class and package importer and utilities.",
    author       = "Paul Boddie",
    author_email = "paul@boddie.org.uk",
    url          = "http://www.boddie.org.uk/python/ClassFile.html",
    version      = "0.1",
    packages     = ["javaclass", "java", "java.lang", "java.security"],
    scripts      = ["runclass.py"]
    )
