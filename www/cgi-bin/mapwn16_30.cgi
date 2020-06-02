#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi, urllib
import cgitb; cgitb.enable()  # for troubleshooting
import os
import sys
import re, sqlite3, collections
from collections import defaultdict as dd
import pickle


import datetime

from ntumc_util import placeholders_for
from ntumc_webkit import *
from lang_data_toolkit import *



cginame = "Mapping WN 1.6 to 3.0"

form = cgi.FieldStorage()
sslist = form.getfirst("sslist", "")
sslist = sslist.split()

# mode = form.getfirst("mode")
# postag = form.getfirst("postag") # FOR WORDVIEW
# wordtag = form.getlist("wordtag[]") # FOR WORDVIEW
# wordclemma = form.getlist("wordclemma[]") # FOR WORDVIEW
# searchlang = form.getfirst("searchlang", "eng")



### working wordnet.db 
wndb = "../../omw/wn-multix.db"
maps1630 = pickle.load(open('maps1630'))

ssbag = set()
for synset in sslist:
    try:
        ssbag.add(maps1630[synset])
    except:
        pass


###########################
# Connect to wordnet.db
###########################
con = sqlite3.connect(wndb)
wn = con.cursor()

fetch_ss_bylemma = """
SELECT sense.synset, lemma, def, synset_def.lang, sense.lang
FROM sense 
LEFT JOIN word 
LEFT JOIN synset_def
WHERE sense.wordid = word.wordid 
AND synset_def.synset = sense.synset
AND synset_def.lang in ('eng')
AND sense.lang in ('eng')
AND sense.synset in (%s)""" % placeholders_for(ssbag)

wn.execute(fetch_ss_bylemma, list(ssbag))
rows = wn.fetchall()
ss_dict = dd(lambda: dd(lambda: dd(lambda:set())))
for r in rows:
    (synset, lemma, defs, deflang, senselang) = (r[0], r[1], r[2], r[3], r[4])
    ss_dict[synset][senselang]["lemma"].add(lemma)
    ss_dict[synset][deflang]["def"].add(defs)

print(u"""Content-type: text/html; charset=utf-8\n
     <!DOCTYPE html>
     <html>
       <head>
         <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
         <link href="../tag-wn.css" rel="stylesheet" type="text/css">
         <script src="../tag-wn.js" language="javascript"></script>
         <!-- KICKSTART -->
         <script src="../HTML-KickStart-master/js/kickstart.js"></script> 
         <link rel="stylesheet" media="all"
           href="../HTML-KickStart-master/css/kickstart.css"/>""")
print("""</head><body>""")

# START FORM
print("""<form action="" id="newquery" method="post">""")
print("""<textarea name="sslist" placeholder="Insert a list of WN1.6 synsets separated by (any) whitespace"
style="width:800px; height:80px">
</textarea>""")
print("""<button class="small"> <a href="javascript:{}"
         onclick="document.getElementById('newquery').submit(); 
         return false;"><span title="Search">
         <span style="color: #4D99E0;"><i class='icon-search'></i>
         </span></span></a></button></p>""")
print("""</form>""")


print("""<table>""")
print("""<tr><td>WN16</td><td>WN30</td><td>ENG-LEMMAS</td><td>ENG-DEF</td></tr>""")
for i, synset in enumerate(sslist):
    try:
        print("""<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                 </tr>""" % (sslist[i], 
                             maps1630[synset],  
                             ", ".join("'%s'" % s for s in ss_dict[maps1630[synset]]['eng']["lemma"]), 
                             ", ".join("'%s'" % s for s in ss_dict[maps1630[synset]]['eng']["def"])))
    except:
        print("""<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                 </tr>""" % (sslist[i], "N.A.", "N.A.", "N.A."))


print("""</table>""")
print("</body>")
print("</html>")
sys.exit(0)
