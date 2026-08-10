#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###
### This is a simple cgi-script for showing sentences in the corpus
###
### Copyright Francis Bond 2014 <bond@ieee.org>
### This is released under the CC BY license
### (http://creativecommons.org/licenses/by/3.0/)
### bugfixes and enhancements gratefuly received

# FIXME(Wilson): Undefined variables: sid, window, lemma, linkdb, corpus2

import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import re, sqlite3, collections
import os 
import operator
from collections import defaultdict as dd

from ntumc_util import placeholders_for
from ntumc_gatekeeper import connect
from html import escape

showsentcgi = "show-sent.cgi"

form = cgi.FieldStorage()
corpus = form.getfirst("corpus", "eng")
synset = form.getfirst("synset", "00001740-n")
lang=form.getfirst("lang", "eng")

# corpus2 = 'eng'
# linkdb = 'cmn-eng'

try:
    con = connect(corpus)
except FileNotFoundError:
    print("Content-type: text/html; charset=utf-8\n")
    print(f"<p>Unknown corpus: {escape(corpus)}</p>")
    import sys
    sys.exit(0)
c = con.cursor()
##
## get monolingual stuff
##

ss = dd(lambda: dd(str))
c.execute("""SELECT sid, docID, sent FROM sent WHERE sid >= ? AND sid <= ?""", 
          (sid - window, sid + window))
sss =set() ### all the synsets
for (s, d, sent) in c:
    sss.add(s)
    if lemma:
        for l in lemma.split():
            sent = sent.replace(l,"<font color='green'>%s</font>" % l)
    ss[d][s] = sent

query = """SELECT corpusID, docid, doc, title, url FROM doc  
           WHERE docid IN (%s)""" % placeholders_for(ss.keys())
c.execute(query, list( ss.keys()))

doc = dd(lambda: dd(list))
for (corpusID, docid, docname, title, url) in c:
    if url:
        if not url.startswith('http://'):
            url = 'http://' + url
    else:
        url = ''
    doc[int(corpusID)][int(docid)] = (url, title, docname)

query = """SELECT corpusID, corpus, title FROM corpus 
           WHERE corpusID IN (%s)""" % placeholders_for(doc.keys())
c.execute(query, doc.keys())

corp = dd(list)
for (corpusID, corpus, title) in c:
    #print corpusID, corpus, title
    corp[int(corpusID)] = (title, corpus)

###
### get links  ### FIXME -- how to tell which direction programatically?
###
links = dd(set)
ttt = dict()
try:
    lcon = connect(linkdb)
except FileNotFoundError:
    lcon = None
if lcon:
    lc = lcon.cursor()
    query = """SELECT fsid, tsid FROM slink  
               WHERE fsid IN (%s)""" % placeholders_for(sss)
    lc.execute(query, list(sss))
    for (fsid, tsid) in lc:
        links[int(fsid)].add(int(tsid))
        ttt[tsid] = ''
##
## Get translations
##
try:
    tcon = connect(corpus2)
except FileNotFoundError:
    tcon = None
if tcon:
    tc = tcon.cursor()
    query = """SELECT sid, sent FROM sent  
               WHERE sid IN (%s)""" % placeholders_for(ttt.keys())
    tc.execute(query, list(ttt.keys()))
    for (sd, sent) in tc:
        ttt[sd] = sent


# 2014-07-14 [Tuan Anh]
# Add jQuery support & alternate sentence colors
print(u"""Content-type: text/html; charset=utf-8\n
<html>
 <head>
   <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
   <meta http-equiv='content-language' content='zh'>
   <title>%s: %s ± %s</title>
   <script src='../jquery.js' language='javascript'></script>
   <script src='../js/show-sent.js' language='javascript'></script>
   <script>
      $( document ).ready(page_init);
   </script>
</head>""" % (corpus, sid, window))

print("""<body>""")

# 2014-07-14 [Tuan Anh]
# Show/hide translation



for c in sorted(corp.keys()):
    print(u"<h2>%s (%s)</h2>" % corp[c])
    print("<div><button  style='float:right;' type='button' id='btnTran' name='btnTran'>Toggle Translation</button></div>")
    for d in sorted(doc[c].keys()):
        print(u"<h3><a href='%s'>%s (%s)</a></h3>" % doc[c][d])
        print("<p>" )
        roll_color_alt = ['#ffffff', '#fafafa']
        roll_color = 0
        for s in sorted(ss[d].keys()):
            roll_color = 0 if roll_color == 1 else 1
            print("<div style='background-color: %s'>" % roll_color_alt[roll_color])
            if s ==sid:
                print("<span style='color:red'>%d</span>&nbsp;&nbsp;&nbsp;&nbsp;%s" % (s, 
                                                                            ss[d][s]))
            else:
                print("%s&nbsp;&nbsp;&nbsp;&nbsp;%s" % (s, ss[d][s]))
            for t in links[s]:
                print("<br/><font color='#505050' class='trans'>%s&nbsp;&nbsp;&nbsp;&nbsp;%s</font>" % (t, 
                                                                                      ttt[t]))
            print("</div>")

print("""</body></html>""")
