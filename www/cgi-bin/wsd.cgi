#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# This cgi script is a very basic wordnet ambiguator.
# Given a string, separated by whitespace, and a language, 
# it produces a list of possible synsets for every word.

import cgi, urllib
import cgitb; cgitb.enable()  # for troubleshooting
from os import environ  # for cookies
import re, sqlite3, collections
from collections import defaultdict as dd

import datetime
import sys, codecs

from ntumc_webkit import *
from ntumc_util import *
from lang_data_toolkit import *



cginame = "NTU WN Ambiguator"
url = "http://compling.hss.ntu.edu.sg/"


form = cgi.FieldStorage()

searchlang = form.getfirst("searchlang", "eng")
segmentedtext = form.getfirst("segmentedtext", "")

### working wordnet.db 
wndb = "../../omw/wn-multix.db"

lemmalst = []
lemmalst = segmentedtext.split()


wncgi_lemma = "wn-gridx.cgi?gridmode=ntumcgrid&lang=%s&lemma=" % (searchlang)
wncgi_ss = "wn-gridx.cgi?gridmode=ntumcgrid&lang=%s&synset=" % (searchlang)

###########################
# Connect to wordnet.db
###########################
con = sqlite3.connect(wndb)
wn = con.cursor()


fetch_ss_bylemma = """
SELECT sense.synset, lemma
FROM sense 
LEFT JOIN word 
WHERE sense.wordid = word.wordid 
AND word.lang = "%s" 
AND lemma in (%s)""" % (searchlang,
                        ",".join("'%s'" % sql_escape(s) for s in lemmalst))

wn.execute(fetch_ss_bylemma)
rows = wn.fetchall()
synsets = set()
ss_bylemmas = dd(lambda: set())
for r in rows:
    (synset, lemma) = (r[0], r[1])
    ss_bylemmas[lemma].add(synset)
    synsets.add(synset)

print(u"""Content-type: text/html; charset=utf-8\n
     <!DOCTYPE html>
     <html>
       <head>
         <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
         <link href="../tag-wn.css" rel="stylesheet" type="text/css">
         <script src="../tag-wn.js" language="javascript"></script>
         <!-- KICKSTART -->
         <script 
         src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js">
         </script>
         <script src="../HTML-KickStart-master/js/kickstart.js"></script> 
         <link rel="stylesheet" media="all"
           href="../HTML-KickStart-master/css/kickstart.css"/>""")


print(u"""<!-- Add fancyBox main JS and CSS files -->
	<script type="text/javascript" 
         src="../fancybox/source/jquery.fancybox.js?v=2.1.5"></script>
	<link rel="stylesheet" type="text/css" 
         href="../fancybox/source/jquery.fancybox.css?v=2.1.5" 
         media="screen" />
	<script type="text/javascript" 
         src="../fancybox-ready.js"></script>""")

print("""</head><body>""")



# START FORM
print("""<form action="" id="newquery" method="post">""")
print("""<textarea name="segmentedtext" placeholder="Type here any text separated by (any) whitespace"
style="width:800px; height:80px">
</textarea>""")
print("""<input name="searchlang" placeholder="Type here the iso lang code"/>""")
print("""<button class="small"> <a href="javascript:{}"
         onclick="document.getElementById('newquery').submit(); 
         return false;"><span title="Search">
         <span style="color: #4D99E0;"><i class='icon-search'></i>
         </span></span></a></button></p>""")
print("""</form>""")



print("""<table>""")
print("""<tr><td>Lemmas</td><td>Synsets</td></tr>""")

for i, lemma in enumerate(lemmalst):
    # if len(ss_set) == 1:
        # print("""<tr><td>%s</td>
        # <td>%s</td></tr>""" % (lemma, list(ss_set)))
    ssstring = ""
    for ss in ss_bylemmas[lemma]:
        # ssstring += ss + "; "        
        ssstring += """<a class='fancybox fancybox.iframe' href='%s%s' 
        style='color:black;text-decoration:none;'>%s</a>; """ % (wncgi_ss,
                                                               ss, ss)

    print("""<tr><td><a class='fancybox fancybox.iframe' href='%s%s' 
    style='color:black;text-decoration:none;'>%s</a></td>
    <td>%s
    </td></tr>""" % (wncgi_lemma, lemmalst[i], lemmalst[i], 
                     ssstring))




print("""</table>""")
print("</body>")
print("</html>")
sys.exit(0)
