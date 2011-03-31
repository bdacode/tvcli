#!/usr/bin/env python2
"""
tvcli

This is a command line program to manage your favourite TV programs and output air times/program names.
This is the first project I've created in python, feedback is welcome.

Copyright (c) Adam Tonks 2011
"""

import copy, getopt, os.path, pickle, urllib, sys, time
from datetime import date, timedelta, datetime
from xml.dom.minidom import parse, parseString
from colorama import init, Fore, Back, Style
init()

os.chdir(sys.path[0])

APIKEY = 'AB4A43DCDF3A99B5'

def updateAll():
    shows = getData()
    if not shows:
        print "You have no favourite TV programs to update!"
        return 1
    for show in shows:
        print "Updating episode list for "+show['SeriesName']+"..."
        updateEpisodes(show['id'])

def getData():
    if not os.path.isfile('data/favourites.pk'):
        return 0
    f = open('data/favourites.pk','r')
    data = pickle.load(f)
    f.close()
    return data

def getEpData(pID):
    if not os.path.isfile('data/episodes/'+pID+'.pk'):
        return 0
    f = open('data/episodes/'+pID+'.pk','r')
    data = pickle.load(f)
    f.close()
    return data

def listProgs(favs):
    if not favs:
        print "Your favourites list is empty :("
        return 1
    for i in range(len(favs)):
        print Fore.CYAN+Style.BRIGHT+`i+1`+': '+Style.RESET_ALL+favs[i]['SeriesName']
    return 0

def getNextEp(pID):
    episodes = getEpData(pID)
    
    now = datetime.now()
    offset = None
    at = None

    for episode in episodes:
        if 'FirstAired' in episode:
            time = datetime.strptime(episode['FirstAired'],'%Y-%m-%d')
            td = time - now + timedelta(1)
            if td > timedelta(0) and (offset == None or td < (offset - now)):
                offset = time
                try:
                    epName = "["+episode['SeasonNumber']+"x"+episode['EpisodeNumber']+"] "+episode['EpisodeName']
                except KeyError:
                    epName = "["+episode['SeasonNumber']+"x"+episode['EpisodeNumber']+"] Episode name unavailable."
    if offset == None:
        return "No data available."
    else:
        return offset.strftime("%d %B %Y")+" - "+epName

def getLastEp(pID):
    episodes = getEpData(pID)
    
    now = datetime.now()
    offset = None
    at = None

    for episode in episodes:
        if 'FirstAired' in episode:
            time = datetime.strptime(episode['FirstAired'],'%Y-%m-%d')
            td = now - time - timedelta(1)
            if td > timedelta(0) and (offset == None or td > (offset - now)):
                offset = time
                try:
                    epName = "["+episode['SeasonNumber']+"x"+episode['EpisodeNumber']+"] "+episode['EpisodeName']
                except KeyError:
                    epName = "["+episode['SeasonNumber']+"x"+episode['EpisodeNumber']+"] Episode name unavailable."
    if offset == None:
        return "No data available."
    else:
        return offset.strftime("%d %B %Y")+" - "+epName

def showInDays(days):
    now = datetime.now()
    d = getData()
    
    days = int(days)

    progs = []

    for i in range(len(d)):
        p = d[i]
        episodes = getEpData(p['id'])
        for episode in episodes:
            if 'FirstAired' in episode:
                time = datetime.strptime(episode['FirstAired'],'%Y-%m-%d')
                td = time - now
                if td > timedelta(0) and td < timedelta(days):
                    p['cid'] = i
                    progs.append(p)
                
    if len(progs)==0:
        print "No programs airing in the next "+`days`+" days."
        return 1
    
    print Fore.CYAN+Style.BRIGHT+"Airing in the next "+`days`+" Days:"+Style.RESET_ALL

    for p in progs:
        info(p['cid']+1)

def showToday():
    today = date.today().strftime("%d %B %Y")
    d = getData()

    programs = []

    for i in range(len(d)):
        p = d[i]
        n = getNextEp(p['id'])
        if n.find(today) > -1:
            p['cid'] = i
            programs.append(p)
    
    if len(programs)==0:
        print "No programs airing today."
        return 1
    
    print Fore.CYAN+Style.BRIGHT+"Airing Today:"+Style.RESET_ALL

    for p in programs:
        info(p['cid']+1)

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

        s = getSeriesData(ID[0].childNodes[0].data)

        print "\n"+Style.BRIGHT+Fore.BLUE+ID[0].childNodes[0].data+" - "+name[0].childNodes[0].data+Style.RESET_ALL
        if len(overview) > 0:
            print Style.BRIGHT+"   Overview:\t"+Style.NORMAL+overview[0].childNodes[0].data[:60].rsplit(' ',1)[0]+"..."
        if len(fa) > 0:
            print Style.BRIGHT+"   First Aired:\t"+Style.NORMAL+date.fromtimestamp(time.mktime(time.strptime(fa[0].childNodes[0].data,"%Y-%m-%d"))).strftime("%d %B %Y")
        if 'Genre' in s:
            genres = s['Genre'].split('|')
            print Style.BRIGHT+"   Genre(s):\t"+Style.NORMAL,
            for i in range(len(genres)):
                genre = genres[i]
                if len(genre.strip()) > 0:
                    sys.stdout.write(genre)
                    if len(genres) != (i+2):
                        print ", ",
            print
        if 'Network' in s:
            print Style.BRIGHT+"   Network:\t"+Style.NORMAL+s['Network']
        if 'Rating' in s:
            print Style.BRIGHT+"   Rating:\t"+Style.NORMAL+s['Rating']
        if 'Status' in s:
            print Style.BRIGHT+"   Status:\t"+Style.NORMAL+s['Status']

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

    for episodeData in dom.getElementsByTagName('Episode'):
        for tag in episodeData.childNodes:
            if tag.nodeName != "#text" and tag.nodeValue !="\n":
                if len(tag.childNodes) > 0:
                    episode[tag.nodeName] = tag.childNodes[0].data
        episodes.append(episode.copy())
        episode.clear()

    f = open('data/episodes/'+pID+'.pk','w')
    pickle.dump(episodes,f)
    f.close()

def delete(pID):
    d = getData()
    print Style.BRIGHT+"Are you sure you want to delete "+d[int(pID)-1]['SeriesName']+"?"+Style.NORMAL
    i = raw_input('(y/n): ')
    if i == "n" or i=="N":
        print "Quitting..."
        sys.exit(1)
    elif i!="y" and i!="Y":
        print "Invalid."
        sys.exit(1)
    del d[int(pID)-1]
    f = open('data/favourites.pk','w')
    pickle.dump(d,f)
    f.close()
    print "Deleted."

def getSeriesData(pID):
    url = "http://www.thetvdb.com/api/"+APIKEY+"/series/"+pID+"/all"
    sock = urllib.urlopen(url)
    if sock.getcode() == 200:
        f = sock.read()
    else:
        print "Error: Series not found or API key incorrect."
        return -1
    sock.close()
    dom = parseString(f)
    
    prog = {}

    for sInfo in dom.getElementsByTagName('Series'):
        for tag in sInfo.childNodes:
            if tag.nodeName != "#text" and tag.nodeValue != "\n":
                if len(tag.childNodes) > 0:
                    prog[tag.nodeName] = tag.childNodes[0].data
    return prog


def add(pID):
    print "Searching for "+pID+" in the TVDB..."
    
    prog = getSeriesData(pID)
    
    if prog < 0:
        return prog

    progs = []
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
    print "Updating episodes..."
    updateEpisodes(pID)
    print "Done"

def info(fID):
    fID = int(fID)-1

    d = getData()

    if len(d) < fID:
        print "Bad program ID. Please use the ID for the program given by the --list option."
        sys.exit(1)

    program = d[fID]

    print Fore.BLUE+Style.BRIGHT+`fID+1`+": "+program['SeriesName']+Style.RESET_ALL
    print Style.BRIGHT+"  Airs: "+Style.NORMAL+program['Airs_DayOfWeek']+"s "+program['Airs_Time']+" (Network's local time)"
    print Style.BRIGHT+"  Latest Episode: "+Style.NORMAL+getLastEp(program['id'])
    print Style.BRIGHT+"  Next Episode: "+Style.NORMAL+getNextEp(program['id'])

def usage():
    print "Usage: tvcli <action>"
    print "   -s,\t--search=PROGRAM\tSearch for a program's ID in the TvDB."
    print "   -i,\t--info=PID\t\tRetrive info for program using ID (from --list)"
    print "   -a,\t--add=TVDBID\t\tAdd program (identified by TvDB ID) to favourites list."
    print "   -d,\t--days=NUM\t\tList programs airing in the next NUM days."
    print "   -t,\t--today\t\t\tList programs airing today."
    print "   -T,\t--tomorrow\t\tList programs airing tomorrow."
    print "   -u,\t--update\t\tUpdate episode lists."
    print "   -l,\t--list\t\t\tList the programs being tracked."
    print "   -D,\t--delete=PID\t\tDelete a program using ID from --list."

def main(argv):

    if len(argv) == 0:
        usage()
        sys.exit(1)

    try:
        opts, args = getopt.getopt(argv, "s:i:a:d:D:tTul", ["search=","info=","add=","days=","delete=","today","tomorrow","update","list"])

    except getopt.GetoptError:
        usage()
        sys.exit(2) 

    for o, a in opts:
        if o in ("-l", "--list"):
            listProgs(getData())
        if o in ("-s", "--search"):
            search(a)
        if o in ("-u", "--update"):
            updateAll()
        if o in ("-a", "--add"):
            add(a)
        if o in ("-i", "--info"):
            info(a)
        if o in ("-D", "--delete"):
            delete(a)
        if o in ("-t", "--today"):
            showToday()
        if o in ("-T", "--tomorrow"):
            showInDays(1)
        if o in ("-d", "--days"):
            showInDays(a)

main(sys.argv[1:])
