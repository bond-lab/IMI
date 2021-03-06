#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###
### This is a simple cgi-script for showing sentences in the corpus
###
### Copyright Francis Bond 2014 <bond@ieee.org>
### This is released under the CC BY license
### (http://creativecommons.org/licenses/by/3.0/)
### bugfixes and enhancements gratefuly received

import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import re, sqlite3, collections
import os 
import operator
import http.cookies
from collections import defaultdict as dd

from ntumc_util import placeholders_for
from ntumc_webkit import HTML
from ntumc_gatekeeper import concurs

selfcgi = "show-sent.cgi"

form = cgi.FieldStorage()
corpus = form.getfirst("corpus", "eng")
corpus2 = form.getfirst("corpus2", "jpn")
sid = int(form.getfirst("sid", 1))
window = int(form.getfirst("window", 7))
if window > 200:
    window = 200
lemma = form.getfirst("lemma", "")
lemma = lemma.strip()


### COOKIES
if 'HTTP_COOKIE' in os.environ:
    C = http.cookies.SimpleCookie(os.environ['HTTP_COOKIE'])
else:
    C = http.cookies.SimpleCookie()
if "UserID" in C:
    userID = C["UserID"].value
else:
    userID = "guest"

con, c = concurs(f"{corpus}.db")
#con = sqlite3.connect(
#c = con.cursor()
##
## get monolingual stuff
##

ss = dd(lambda: dd(str))
c.execute("""SELECT sid, docID, sent 
             FROM sent 
             WHERE sid >= ? AND sid <= ?""", 
          [sid - window, sid + window])
sss = set() ### all the synsets
for (s, d, sent) in c:
    sss.add(s)
    if lemma:
        for l in lemma.split():
            sent = sent.replace(l, f"<font color='green'>{l}</font>")
    ss[d][s] = sent

query = """SELECT corpusID, docid, doc, title, url 
           FROM doc  
           WHERE docid in (%s)""" % placeholders_for(ss.keys())
c.execute(query, list(ss.keys()))

doc = dd(lambda: dd(list))
for (corpusID, docid, docname, title, url) in c:
    if url:
        if not url.startswith('http://'):
            url = 'http://' + url
    else:
        url = ''
    doc[int(corpusID)][int(docid)] = (url, title, docname)

query = """SELECT corpusID, corpus, title 
           FROM corpus 
           WHERE corpusID IN (%s)""" % placeholders_for(doc.keys())
c.execute(query, list(doc.keys()))

corp = dd(list)
for (corpusID, corpuslabel, title) in c:
    #print corpusID, corpus, title
    corp[int(corpusID)] = (title, corpuslabel)

###
### get links 
###
links = dd(set)
ttt = dict()
linkdb= ''
if os.path.isfile(f"../db/{corpus}-{corpus2}.db"):
    linkdb = f"{corpus}-{corpus2}"
    query = """SELECT fsid, tsid FROM slink  
     WHERE fsid IN (%s)""" % placeholders_for(sss)
elif os.path.isfile(f"../db/{corpus2}-{corpus}.db"):
    linkdb = f"{corpus2}-{corpus}"
    query = """SELECT tsid, fsid FROM slink  
    WHERE tsid IN (%s)""" % placeholders_for(sss)

if linkdb:
    lcon = sqlite3.connect(f"../db/{linkdb}.db")
    lc = lcon.cursor()
    lc.execute(query, list(sss))
    for (fsid, tsid) in lc:
        links[int(fsid)].add(int(tsid))
        ttt[tsid] = ''
##
## Get translations
##
if os.path.isfile("../db/%s.db" % corpus2):
    tcon = sqlite3.connect("../db/%s.db" % corpus2)
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
<link href="../tag-wn.css" rel="stylesheet" type="text/css">
</head>""" % (corpus, sid, window))

print("""<body>""")

# 2014-07-14 [Tuan Anh]
# Show/hide translation




          
print(f"""<form id='input' name ='input' method='get' action='{selfcgi}' 
style="display:inline-block;" target='_parent'>""")
#<input type='text' name='corpus' value='{corpus}' style="width:3em">
print("""<span style="display:inline-block;">""")
print(HTML.select_corpus(text='From', field='corpus', value=corpus))
print(HTML.select_corpus(text='to: ', field='corpus2', value=corpus2))
print(f"""sid: <input type='text' name='sid' value='{sid}' size=3/>
window: <input type='text' name='window' value='{window}' style="width:2em" />
</span>
<button class="small"> <a href="javascript:{{}}"
 onclick="document.getElementById('input').submit(); 
 return false;"><span title="Search">
 <span style="color: #4D99E0;">GO
 </span></span></a>
</button>

</form>""")
print("<div><button  style='float:right;' type='button' id='btnTran' name='btnTran'>Toggle Translation</button></div>")


for c in sorted(corp.keys()):
    print(u"<h2>%s (%s)</h2>" % corp[c])
    for d in sorted(doc[c].keys()):
        print(u"<h3><a href='%s'>%s (%s)</a></h3>" % doc[c][d])
        print("<p>" )
        roll_color_alt = ['#ffffff', '#fafafa']
        roll_color = 0
        for s in sorted(ss[d].keys()):
            roll_color = 0 if roll_color == 1 else 1
            print("<div style='background-color: %s'>" % roll_color_alt[roll_color])
            if s ==sid:
                print(f"<span class='sent_match'>{s}&nbsp;&nbsp;&nbsp;&nbsp;{ss[d][s]}</span>")
            else:
                print(f"{s}&nbsp;&nbsp;&nbsp;&nbsp;{ss[d][s]}")
            for t in links[s]:
                print("<br/><font color='#505050' class='trans'>%s&nbsp;&nbsp;&nbsp;&nbsp;%s</font>" % (t, 
                                                                                      ttt[t]) )
            print("</div>")

            
print(HTML.status_bar(userID,text=True))
print("""</body></html>""")
