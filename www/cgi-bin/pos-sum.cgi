#!/usr/bin/env python
  # -*- coding: utf-8 -*-

import cgi, urllib
import cgitb; cgitb.enable()  # for troubleshooting
from collections import defaultdict as dd
import sys, codecs
from ntumc_webkit import *
from lang_data_toolkit import *

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
reload(sys)  
sys.setdefaultencoding('utf8')

#############################################################################
# This script reads the existing POS data stored in lang_data_toolkit.py
# and connects to each corpus.db to output a table with frequencies and
# examples.
# This includes "real" POS tags and the Universal POS tags mapping.
#############################################################################

selfcgi = "pos-sum.cgi"
cginame = "POS Summary - NTUMC"
ver = "0.1"
url = "http://compling.hss.ntu.edu.sg/"

form = cgi.FieldStorage()
lang = form.getfirst("lang", "eng")
tagset = form.getfirst("tagset", "pos")
sid_from = form.getfirst("sid_from", 0)
try:
    sid_from = int(sid_from)
except:
    sid_from = 0

sid_to = form.getfirst("sid_to", 10000000)
try:
    sid_to = int(sid_to)
except:
    sid_to = 10000000

limit = form.getfirst("limit", 5) # limits the number of examples shown
try:
    limit = int(limit)
except:
    limit = 5

corpusdb = "../db/%s.db" % lang

###########################
# Connect to corpus.db
###########################
conc = sqlite3.connect(corpusdb)
cc = conc.cursor()

cc.execute("""SELECT pos, word, count(word) 
               FROM word
               WHERE sid > %s
               AND sid < %s
               GROUP BY pos, word
               ORDER BY pos, count(word) DESC """ % (sid_from, sid_to))

rows = cc.fetchall()

pos_count = dd(int)
pos_count_word = dd(lambda: dd(list)) 
upos_count_word = dd(lambda: dd(list)) 
for r in rows:
    (pos, word, count) = (r[0], r[1], r[2])

    pos_count[pos] += count # pos > total number of hits
    pos_count_word[pos][count].append(word) # pos > #hits_by_word > list of words

    upos_count_word[pos_tags[lang][pos]['upos']][count].append(word)
    

print(u"""Content-type: text/html; charset=utf-8\n
     <!DOCTYPE html>
     <html>
       <head>
         <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
         <link href="../tag-wn.css" rel="stylesheet" type="text/css">
         <script src="../tag-wn.js" language="javascript"></script>

         <!-- JQUERY -->
         <script src="//code.jquery.com/jquery-1.10.2.js"></script>

         <!-- KICKSTART -->
         <script src="../HTML-KickStart-master/js/kickstart.js"></script> 
         <link rel="stylesheet" media="all"
           href="../HTML-KickStart-master/css/kickstart.css"/>

         <!-- A cool (light) CSS Tooltip! USE:
         class="tooltip-bottom" data-tooltip="I’m the tooltip data!" -->
         <link href="../fancy-tooltip.css" rel="stylesheet" type="text/css">""")


print("""<title>%s</title></head><body>""" % cginame)
print("""<h6>%s's %s</h6>""" % (omwlang.trans(lang, 'eng'), cginame) )


if tagset == "upos":
    print("""<table class="striped sortable">""")
    print("""<thead><tr><th>UPOS</th><th>Definition</th> 
             <th>Count</th>
             <th>Examples (by freq.)</th>
             <th>Mapped POS</th></tr></thead>""")

    for upos in sorted(upos_tags[lang].keys()):
        upos_count = 0
        pos_string = ""
        for pos in sorted(upos_tags[lang][upos]['pos']):
            upos_count += pos_count[pos]
            pos_string += """<span class="tooltip-bottom" 
                 data-tooltip="%s">%s</span>, """ % (pos_tags[lang][pos]['eng_def'],
                        cgi.escape(pos, quote=True))

        print("""<tr>""")
        print("""<td>%s</td>
                 <td>%s</td>
              """ % (upos,upos_tags[lang][upos]['eng_def']))
        print("""<td style="text-align:right" >%s</td>
              """ % (upos_count,))

        word_examples = ""
        examples = 0
        for count, wordlist in sorted(upos_count_word[upos].items(), reverse=True):
            for word in wordlist:
                if examples < limit:
                    word_examples += """%s <sub>%s</sub>, """ % (word,count) 
                    examples += 1
                else:
                    break
        print("""<td>%s</td>""" % word_examples[:-2])
        print("""<td>%s</td>""" % pos_string[:-2])
    print("""</table>""")


else:
    print("""<table class="striped sortable">""")
    print("""<thead><tr><th>POS</th><th>Definition</th> 
             <th>Count</th><th>Examples (by freq.)</th>
             <th>UPOS</th></tr></thead>""")

    for pos in sorted(pos_count.keys()):
        print("""<tr><td>%s</td><td>%s</td>
                  <td style="text-align:right">%s</td>
              """ % (pos,pos_tags[lang][pos]['eng_def'],
                     pos_count[pos]))
        word_examples = ""
        examples = 0
        for count, wordlist in sorted(pos_count_word[pos].items(), reverse=True):
            for word in wordlist:
                if examples < limit:
                    word_examples += """%s <sub>%s</sub>, """ % (word,count) 
                    examples += 1
                else:
                    break
        print("""<td>%s</td>""" % word_examples[:-2])
        print("""<td><span class="tooltip-bottom" 
                 data-tooltip="%s">%s</span></td>
              """ % (upos_tags[lang][pos_tags[lang][pos]['upos']]['eng_def'], 
                     pos_tags[lang][pos]['upos']))
    print("""</table>""")

print "</body>"
print "</html>"
