#!/usr/bin/env python
"""
tvcli

This is a command line program to manage your favourite TV programs and output air times/program names.
This is the first project I've created in python, feedback is welcome.

Copyright (c) Adam tonks 2011
"""

import getopt, urllib, sys
from xml.dom.minidom import parse, parseString


def search(program):
    sock = urllib.urlopen("http://www.thetvdb.com/api/GetSeries.php?seriesname="+program)
    f = sock.read()
    sock.close()
    dom = parseString(f)
    
    if len(dom.getElementsByTagName('Series')) == 0:
        print "No episodes found with that name."
        return 1;
    
    for series in dom.getElementsByTagName('Series'):
        name = series.getElementsByTagName('SeriesName')
        ID = series.getElementsByTagName('seriesid')
        fa = series.getElementsByTagName('FirstAired')
        overview = series.getElementsByTagName('Overview')

        if len(name) < 0:
            break

        print "\n"+ID[0].childNodes[0].data+" - "+name[0].childNodes[0].data
        if len(fa) > 0:
            print "   First Aired:\t"+fa[0].childNodes[0].data
        if len(overview) > 0:
            print "   Overview:\t"+overview[0].childNodes[0].data[:60].rsplit(' ',1)[0]+"..."

def main(argv):

    if len(argv) == 0:
        usage()
        sys.exit(1)

    try:
        opts, args = getopt.getopt(argv, "s:a:d:tT", ["search=","add=","days=","today","tomorrow"])

    except getopt.GetoptError:
        usage()
        sys.exit(2) 

    for o, a in opts:
        if o in ("-s", "--search"):
            search(a)

def usage():
    print "Usage: tvcli <action>"
    print "   -s,\t--search=PROGRAM\tSearch for a PROGRAM's ID in the TVDB."
    print "   -a,\t--add=ID\t\tAdd program ID to favourites list."
    print "   -d,\t--days=NUM\t\tList programs airing in the next NUM days."
    print "   -t,\t--today\t\t\tList programs airing today."
    print "   -T,\t--tomorrow\t\tList programs airing tomorrow."
main(sys.argv[1:])
