#!/usr/bin/env python
"""
tvcli

This is a command line program to manage your favourite TV programs and output air times/program names.
This is the first project I've created in python, feedback is welcome.

Copyright (c) Adam tonks 2011
"""

import sys, getopt

def main(argv):
    if len(argv) == 1:
        usage()
        sys.exit(1)

    try:
        opts, args = getopt.getopt(argv, "s:a:d:tT", ["search=","add=","days=","today","tomorrow"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

def usage():
    print "Usage: tvcli <action>"
    print "   -s,\t--search=PROGRAM\tSearch for a PROGRAM's ID in the TVDB."
    print "   -a,\t--add=ID\t\tAdd program ID to favourites list."
    print "   -d,\t--days=NUM\t\tList programs airing in the next NUM days."
    print "   -t,\t--today\t\t\tList programs airing today."
    print "   -T,\t--tomorrow\t\tList programs airing tomorrow."
main(sys.argv)