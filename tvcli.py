#!/usr/bin/env python
"""
tvcli

This is a command line program to manage your favourite TV programs and output air times/program names.
This is the first project I've created in python, feedback is welcome.

Copyright (c) Adam Tonks 2011
"""

import getopt, os.path, pickle, urllib, sys
from xml.dom.minidom import parse, parseString

APIKEY = 'AB4A43DCDF3A99B5'

def getData():
    if not os.path.isfile('data/favourites.pk'):
        return 0
    f = open('tvcli.pk','rb')
    data = pickle.load(f)
    f.close()
    return data

def listProgs(favs):
    if not favs:
        print "Your favourites list is empty :("
        return 1
    for i in range(len(favs)):
        print `i+1`+': '+favs[i]['SeriesName']
    return 0

def search(program):
    sock = urllib.urlopen("http://www.thetvdb.com/api/GetSeries.php?seriesname="+program)
    f = sock.read()
    sock.close()
    dom = parseString(f)
    
    if len(dom.getElementsByTagName('Series')) == 0:
        print "No episodes found with that name."
        return 1
    
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

def updateEpisodes(pID):
    url = "http://www.thetvdb.com/api/"+APIKEY+"/series/"+pID+"/all"
    sock = urllib.urlopen(url)
    if sock.getcode() == 200:
        f = sock.read()
    else:
        return 1
    sock.close()
    dom = parseString(f)

    episode = {}
    episodes = []

    for episode in dom.getElementsByTagName('Episode'):
        for tag in episode.childNodes:
            if tag.nodeName != "#text" and tag.nodeValue !="\n":
                if len(tag.childNodex) > 0:
                    episode[tag.nodeName] = tag.childNodes[0].data
        episodes.append(episode)

    f = open('data/episodes/'+pID+'.pk')
    pickle.dump(episodes,f)
    f.close

def add(pID):
    url = "http://www.thetvdb.com/api/"+APIKEY+"/series/"+pID+"/all"
    sock = urllib.urlopen(url)
    if sock.getcode() == 200:
        f = sock.read()
    else:
        print "Error: Series not found or API key incorrect."
        return 1
    sock.close()
    dom = parseString(f)
    
    prog = {}
    progs = []

    for sInfo in dom.getElementsByTagName('Series'):
        for tag in sInfo.childNodes:
            if tag.nodeName != "#text" and tag.nodeValue != "\n":
                if len(tag.childNodes) > 0:
                    prog[tag.nodeName] = tag.childNodes[0].data
    
    if os.path.isfile('data/favourites.pk'):
        current = getData()
        current.append(prog)
        progs = current
    else:
        progs = [ prog ]

    f = open('data/favourites.pk','w')
    pickle.dump(progs,f)
    f.close()

    print "Added "+prog['SeriesName']+" to favourites."
 

def usage():
    print "Usage: tvcli <action>"
    print "   -s,\t--search=PROGRAM\tSearch for PROGRAM's ID in the TVDB."
    print "   -i,\t--info=PID\t\tRetrive info for program using PID (from --list)"
    print "   -a,\t--add=ID\t\tAdd program ID to favourites list."
    print "   -d,\t--days=NUM\t\tList programs airing in the next NUM days."
    print "   -t,\t--today\t\t\tList programs airing today."
    print "   -T,\t--tomorrow\t\tList programs airing tomorrow."
    print "   -u,\t--update\t\tUpdate cache."
    print "   -l,\t--list\t\t\tList the programs being tracked."

def main(argv):

    if len(argv) == 0:
        usage()
        sys.exit(1)

    try:
        opts, args = getopt.getopt(argv, "s:i:a:d:tTul", ["search=","info=","add=","days=","today","tomorrow","update","list"])

    except getopt.GetoptError:
        usage()
        sys.exit(2) 

    for o, a in opts:
        if o in ("-l", "--list"):
            listProgs(getData())
        if o in ("-s", "--search"):
            search(a)
        if o in ("-a", "--add"):
            add(a)

main(sys.argv[1:])
