#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi, urllib
import cgitb; cgitb.enable()  # for troubleshooting
from collections import defaultdict as dd
import sys  #, codecs
from ntumc_util import placeholders_for
from ntumc_webkit import *
from lang_data_toolkit import *

#############################################################################
# This script is designed to run a series of tests to the corpora dbs.
#
# Including:
# 1. Common lemmatization mistakes 
# 2.
# 3. 
# 4.
# reads the existing POS data stored in lang_data_toolkit.py
# and connects to each corpus.db to output a table with frequencies and
# examples.
# This includes "real" POS tags and the Universal POS tags mapping.
#############################################################################

cginame = "NTUMC DB Diagnosis"
ver = "0.1"
url = 'https://bond-lab.github.io/'
tagset = 'pos'
limit = 20




if (len(sys.argv) != 5):  # argument: database
    sys.stderr.write('You need to provide the following arguments:')
    sys.stderr.write('1. a path to a database file! \n')
    sys.stderr.write('2. Sid_From ! \n')
    sys.stderr.write('3. Sid_From ! \n')
    sys.stderr.write('4. Sid_To ! \n')
    sys.exit(1)
else:
    corpusdb = sys.argv[1]
    lang = sys.argv[2]
    sid_from = sys.argv[3]
    sid_to = sys.argv[4]

try:
    sid_from = int(sid_from)
    sid_to = int(sid_to)
except:
    sys.stderr.write('The sentence numbers could not be converted to integers! \n')
    sys.exit(1)


fix="""<a href="cgi-bin/fix-corpus.cgi?db_edit=../db/{}.db""".format(lang)
fix+="""&sid_edit={}">{}</a>"""

 



###########################
# Connect to corpus.db
###########################
con = sqlite3.connect(corpusdb)
c = con.cursor()
c2 = con.cursor()

# c.execute("""SELECT wid, pos, word, count(word) 
#              FROM word
#              WHERE sid > %s
#              AND sid < %s
#              GROUP BY pos, word
#              ORDER BY pos, count(word) DESC """ % (sid_from, sid_to))


# rows = c.fetchall()
# pos_count = dd(int)
# pos_count_word = dd(lambda: dd(list))
# upos_count_word = dd(lambda: dd(list))
# for r in rows:
#     (wid, pos, word, count) = (r[0], r[1], r[2],r[3])

#     pos_count[pos] += count # pos > total number of hits
#     pos_count_word[pos][count].append(word) # pos > #hits_by_word > list of words



############

showcorpus  ="""
SELECT cl.sid, cl.cid, cl.tag 
FROM (SELECT c.sid, c.cid, wid, tag 
     FROM (SELECT sid, cid, tag 
           FROM concept WHERE 1 > 0 
           AND sid >= ? 
           AND sid <= ? ) c 
     LEFT JOIN cwl 
     WHERE cwl.sid = c.sid 
     AND c.cid = cwl.cid) cl 
LEFT JOIN word 
WHERE word.sid = cl.sid 
AND word.wid = cl.wid
"""

c.execute(showcorpus, (sid_from, sid_to))
rows = c.fetchall()

sid_cid = dd(lambda: dd(lambda: str))
for r in rows:
    (sid, cid, tag) = (r[0], r[1], r[2])
    sid_cid[sid][cid] = [tag]

sids = ",".join("'%s'" % s for s in sid_cid.keys())



fetch_concept_details = """
SELECT sid, cid, clemma, tag 
FROM concept
WHERE sid >= ?
AND sid <= ?
ORDER BY sid"""


fetch_sent_full_details = """
SELECT w.sid, w.wid, w.word, w.lemma, w.pos, cwl.cid
FROM (SELECT sid, wid, word, lemma, pos
      FROM word
      WHERE sid >= ?
      AND sid <= ? ) w
LEFT JOIN cwl
WHERE w.wid = cwl.wid
AND w.sid = cwl.sid
ORDER BY w.sid"""


fetch_sent = """
SELECT sid, wid, word, lemma, pos
FROM word
WHERE  sid >= ?
AND sid <= ?"""

fetch_fullsent = """
SELECT sid, sent.sent
FROM sent
WHERE  sid >= ?
AND sid <= ?"""


sid_wid = dd(lambda: dd(list))
sid_wid_cid = dd(lambda: dd(list))
sid_wid_lemma = dd(lambda: dd())
sid_wid_wsurface = dd(lambda: dd())
sid_wid_pos = dd(lambda: dd())
sid_wid_tag = dd(lambda: dd(list))
sid_cid_wid = dd(lambda: dd(list))
sid_cid_tag = dd(lambda: dd(str))
sid_cid_clemma = dd(lambda: dd(str))
sid_fullsent = dd(str)

sss = set() # holds the list of all tags (for sentiment)
words_total = 0
concepts_total = 0

c.execute(fetch_concept_details, (sid_from, sid_to))
rows = c.fetchall()
for r in rows:
    (sid, cid, clemma, tag) = (r[0], r[1], r[2], r[3]) 

    concepts_total += 1
    sid_cid_tag[sid][cid] = tag
    sid_cid_clemma[sid][cid] = clemma
    sss.add(tag)


c.execute(fetch_sent_full_details, (sid_from, sid_to))
rows = c.fetchall()
for r in rows:
    (sid, wid, word, 
     lemma, pos, cid) = (r[0], r[1], r[2], 
                         r[3], r[4], r[5])

    words_total += 1
    sid_cid_wid[sid][cid].append(wid) 
    sid_wid_cid[sid][wid].append(cid)
    sid_wid_tag[sid][wid].append(sid_cid_tag[sid][cid])


c.execute(fetch_fullsent, (sid_from, sid_to))
rows = c.fetchall()
for r in rows:
    (sid, fullsent) = (r[0], r[1])
    sid_fullsent[sid] = fullsent



c.execute(fetch_sent, (sid_from, sid_to))
rows = c.fetchall()
for r in rows:
    (sid, wid, word, lemma, pos) = (r[0], r[1], r[2], r[3], r[4])
    pos = "unk" if pos == None else pos
    sid_wid[sid][wid] = [word, lemma, pos]
    sid_wid_wsurface[sid][wid] = word
    sid_wid_lemma[sid][wid] = lemma 
    sid_wid_pos[sid][wid] = pos



##########


print(u"""<!DOCTYPE html>
     <html>
       <head>
         <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
         <link href="tag-wn.css" rel="stylesheet" type="text/css">
         <script src="tag-wn.js" language="javascript"></script>

         <!-- JQUERY -->
         <script src="//code.jquery.com/jquery-1.10.2.js"></script>

         <!-- KICKSTART -->
         <script src="HTML-KickStart-master/js/kickstart.js"></script> 
         <link rel="stylesheet" media="all"
           href="HTML-KickStart-master/css/kickstart.css"/>

         <!-- A cool (light) CSS Tooltip! USE:
         class="tooltip-bottom" data-tooltip="I’m the tooltip data!" -->
         <link href="fancy-tooltip.css" rel="stylesheet" type="text/css">

         <style>
           hr{
             padding: 0px;
             margin: 10px;    
           }
         </style>


    <!-- TO SHOW / HIDE BY ID (FOR DIV)-->
    <script type="text/javascript">
     function toggle_visibility(id) {
         var e = document.getElementById(id);
         if(e.style.display != 'none') {
            e.style.display = 'none';
            e.style.visibility = 'collapse';
         }
         else {
            e.style.display = 'block';
            e.style.visibility = 'visible';
         }
     }
    </script>


""")






print("""<title>%s</title></head><body>""" % cginame)
print("""<h6>%s's %s (sids:%s-%s)</h6>""" % (omwlang.trans(lang, 'eng'), cginame,sid_from, sid_to) )

print("<hr>")
print("<h6> Quick Report </h6>")
print("Number of sentences: {}<br>".format(len( sid_fullsent.keys())))
print("Number of words: {}<br>".format(words_total))
print("Number of concepts: {}<br>".format(concepts_total))
print("<hr><br>")


################################################################################
# CHECK SENTENCE / WORDS SURFACE CONSISTENCY
################################################################################
print("""<button onclick="toggle_visibility('{}')" 
          class="small pull-right">hide/show</button>
         <h6>Sentence - Word Surface Consistency Problems</h6>
         <div id='{}'> 
      """.format('sentword', 'sentword') )

sent_word_inconsistencies = [] 
for sid in sorted(sid_fullsent.keys()):
    fixurl = fix.format(sid, sid)

    fullsent = sid_fullsent[sid]
    ufullsent = fullsent.replace(" ", "")

    wsurfs = []
    uwsurfs = ''
    for wid in sorted(sid_wid_wsurface[sid].keys()):
        uwsurfs += sid_wid_wsurface[sid][wid]
        wsurfs.append(sid_wid_wsurface[sid][wid])

    if uwsurfs != ufullsent:
        sent_word_inconsistencies.append("""<td>{}</td>
                                            <td>{}</td>
                                            <td>{}</td>
                                         """.format(fixurl,fullsent,
                                                    ' '.join(wsurfs)))

if len(sent_word_inconsistencies) > 0:
    print("""<table class="tight striped sortable">""")

    print("<thead><tr>")
    print("""<th>sid</th>
             <th>sent</th>
             <th>words</th>
          """)
    print("</tr></thead>")


    for inc in sent_word_inconsistencies:
        print("<tr>")
        print(inc)
        print("</tr>")

    print("</table>")
else:
    print("No sentence / word surface problems found.")

print("</div>")
print("<hr><br>")


################################################################################
# CHECK LEMMA/CLEMMA CONSISTENCY
################################################################################
print("""<button onclick="toggle_visibility('{}')" 
          class="small pull-right">hide/show</button> 
         <h6>Word Lemma - Concept Lemma Consistency Problems</h6>
         <div id='{}'> 
      """.format('lemmaconcept', 'lemmaconcept') )


word_concept_inconsistencies = [] 
for sid in sorted(sid_cid_clemma.keys()):
    fixurl = fix.format(sid, sid)

    for cid in sorted(sid_cid_wid[sid].keys()):

        
        clemma = sid_cid_clemma[sid][cid]
        try:
            uclemma = clemma.replace(" ", "")
        except:
            sys.stderr.write(str(sid))
            sys.stderr.write('/n')
            sys.stderr.write(str(cid))
            sys.stderr.write('/n')
            sys.stderr.write(clemma)

        wids = sid_cid_wid[sid][cid]
        wlemmas = []
        uwlemmas = ''
        for i in wids:
            uwlemmas += sid_wid_lemma[sid][i]
            wlemmas.append(sid_wid_lemma[sid][i])


        wsurfs = []
        uwsurfs = ''
        for wid in wids:
            uwsurfs += sid_wid_wsurface[sid][wid]
            wsurfs.append(sid_wid_wsurface[sid][wid])


        if uclemma.lower() != uwlemmas.lower():

            if uclemma.lower() == uwsurfs.lower(): # IF MATCHED WORD FORM! (WEIRD MWE)
            
                word_concept_inconsistencies.append("""
                    <td>{}</td><td>{}</td><td>{}</td>
                    <td>{}</td><td>{}</td><td>{}</td>
                     """.format(fixurl,cid,clemma,wids,
                                ' '.join(wlemmas),'Y'))

            else:
                word_concept_inconsistencies.append("""
                    <td>{}</td><td>{}</td><td>{}</td>
                    <td>{}</td><td>{}</td><td>{}</td>
                     """.format(fixurl,cid,clemma,wids,
                                ' '.join(wlemmas), 'N' ))


if len(word_concept_inconsistencies) > 0:
    print("""<table class="tight striped sortable">""")

    print("<thead><tr>")
    print("""<th>sid</th>
             <th>cid</th>
             <th>clemma</th>
             <th>wids</th>
             <th>lemmas</th>
             <th>clem=wsurf</th>
          """)
    print("</tr></thead>")


    for inc in word_concept_inconsistencies:
        print("<tr>")
        print(inc)
        print("</tr>")

    print("</table>")
else:
    print("No word lemma / concept lemmas problems found.")

print("</div>")
print("<hr><br>")




################################################################################
# CHECK TAGS / WORDNET CONSISTENCY
################################################################################
wndb = "../db/wn-ntumc.db"
wn = """SELECT synset, s.lang, lemma, 
               freq, src, confidence 
         FROM ( SELECT synset, lang, wordid, freq, src, confidence 
                FROM sense 
                WHERE synset in (%s) 
                AND lang = ? ) s
         LEFT JOIN word
         WHERE word.wordid = s.wordid
         ORDER BY freq DESC """ % (placeholders_for(sss))

con2 = sqlite3.connect(wndb)
c2 = con2.cursor()

c2.execute(wn, (*sss, lang))
words = dd(lambda: set())
uwords = dd(lambda: set())
for r in c2:
    (synset, l, lemma, 
     freq, src, conf) = (r[0], r[1], r[2], 
                         r[3], r[4], r[5])    
    words[synset].add(lemma.lower())
    ulem= lemma.replace(" ", "")
    ulem= ulem.replace("-", "")
    uwords[synset].add(ulem.lower())


print("""<button onclick="toggle_visibility('{}')" 
          class="small pull-right">hide/show</button> 
         <h6>Tags - Wordnet Consistency Problems</h6>
         <div id='{}'>
      """.format('tagwn', 'tagwn') )


tag_wn_inconsistencies = [] 
for sid in sorted(sid_cid_clemma.keys()):
    fixurl = fix.format(sid, sid)

    for cid in sorted(sid_cid_wid[sid].keys()):

        clemma = sid_cid_clemma[sid][cid]
        tag = sid_cid_tag[sid][cid]
        
     
        exceptions = ['x','e','w','org','loc',
                      'per','dat','oth','num',
                      'dat:year']


        if tag not in exceptions and (clemma.lower() not in words[tag]):

            uclemma = clemma.replace(" ", "")
            uclemma = uclemma.replace("-", "")
            if uclemma.lower() not in uwords[tag]:

                tag_wn_inconsistencies.append("""
                   <td>{}</td><td>{}</td><td>{}</td>
                   <td>{}</td><td>{}</td><td>{}</td>
                    """.format(fixurl,cid,clemma,tag,
                              '; '.join( words[tag]),'N'))

            else:
                tag_wn_inconsistencies.append("""
                   <td>{}</td><td>{}</td><td>{}</td>
                   <td>{}</td><td>{}</td><td>{}</td>
                    """.format(fixurl,cid,clemma,tag,
                              '; '.join( words[tag]),'Y'))


if len(tag_wn_inconsistencies) > 0:
    print("""<table class="tight striped sortable">""")

    print("<thead><tr>")
    print("""<th>sid</th>
             <th>cid</th>
             <th>clemma</th>
             <th>tag</th>
             <th>wn-lemmas</th>
             <th>=No' '/No'-'?</th>
          """)
    print("</tr></thead>")


    for inc in tag_wn_inconsistencies:
        print("<tr>")
        print(inc)
        print("</tr>")

    print("</table>")
else:
    print("No tag / wn lemmas problems found.")

print("</div>")
print("<hr><br>")






################################################################################
# CHECKING FOR NON EMPTY FIELDS CONSISTENCY
################################################################################
print("""<button onclick="toggle_visibility('{}')" 
          class="small pull-right">hide/show</button> 
         <h6>Empty Fields in Word Table Consistency Analysis</h6>
         <div id='{}'>
      """.format('empty', 'empty') )


empty_word_inconsistencies = [] 
empty_lemma_inconsistencies = [] 
empty_pos_inconsistencies = [] 
for sid in sid_wid.keys():
    fixurl = fix.format(sid, sid)

    for wid in sid_wid[sid].keys():
        
        word = sid_wid[sid][wid][0]
        lemma = sid_wid[sid][wid][1]
        pos = sid_wid[sid][wid][2]

        if word == None or word == "":
            empty_word_inconsistencies.append("""
            <td>{}</td><td>{}</td><td>{}</td>""".format(fixurl,wid,'NoWord'))

        if lemma == None or lemma == "":
            empty_word_inconsistencies.append("""
            <td>{}</td><td>{}</td><td>{}</td>""".format(fixurl,wid,'NoLemma'))

        if pos == None or pos == "":
            empty_word_inconsistencies.append("""
            <td>{}</td><td>{}</td><td>{}</td>""".format(fixurl,wid,'NoPOS'))


empty_inconsistencies = empty_word_inconsistencies + empty_lemma_inconsistencies + empty_pos_inconsistencies

if len(empty_inconsistencies) > 0:
    print("""<table class="tight striped sortable">""")

    print("<thead><tr>")
    print("""<th>sid</th>
             <th>wid</th>
             <th>?</th>
          """)
    print("</tr></thead>")

    for inc in empty_inconsistencies:
        print("<tr>")
        print(inc)
        print("</tr>")

    print("</table>")
else:
    print("No empty fields problems found with words.")






print("</div>")
print("<hr><br>")










################################################################################
# CHECK POS CONSISTENCY
################################################################################
print("""<button onclick="toggle_visibility('{}')" 
          class="small pull-right">hide/show</button> 
         <h6>POS Consistency Analysis</h6>
         <div id='{}'>
      """.format('pos', 'pos') )


#pos_count_word[pos][count].append(word) 

    # sid_wid_lemma[sid][wid] = lemma 
    # sid_wid_pos[sid][wid] = pos


pos_inconsistencies = []
for sid in sid_wid.keys():
    fixurl = fix.format(sid, sid)

    for wid in sid_wid_pos[sid].keys():
        
        pos = sid_wid_pos[sid][wid]
        wsurf = sid_wid_wsurface[sid][wid]

        if pos not in pos_tags[lang].keys() or pos == 'unk':
            pos_inconsistencies.append("""
            <td>{}</td><td>{}</td>
            <td>{}</td><td>{}</td>""".format(fixurl,wid,wsurf,pos))


if len(pos_inconsistencies) > 0:
    print("""<table class="tight striped sortable">""")

    print("<thead><tr>")
    print("""<th>sid</th>
             <th>wid</th>
             <th>Word</th>
          """)
    print("</tr></thead>")

    for inc in pos_inconsistencies:
        print("<tr>")
        print(inc)
        print("</tr>")

    print("</table>")
else:
    print("No unknown POS tags were found.")
    






# print("""<table class="striped sortable">""")
# print("""<thead><tr><th>POS</th><th>Definition</th> 
#          <th>Count</th><th>Examples (by freq.)</th>
#          <th>UPOS</th></tr></thead>""")

# for pos in sorted(pos_count.keys()):
#     print("""<tr><td>%s</td><td>%s</td>
#               <td style="text-align:right">%s</td>
#           """ % (pos,pos_tags[lang][pos]['eng_def'],
#                  pos_count[pos]))
#     word_examples = ""
#     examples = 0
#     for count, wordlist in sorted(pos_count_word[pos].items(), reverse=True):
#         for word in wordlist:
#             if examples < limit:
#                 word_examples += """%s <sub>%s</sub>, """ % (word,count) 
#                 examples += 1
#             else:
#                 break
#     print("""<td>%s</td>""" % word_examples[:-2])
#     print("""<td><span class="tooltip-bottom" 
#              data-tooltip="%s">%s</span></td>
#           """ % (upos_tags[lang][pos_tags[lang][pos]['upos']]['eng_def'], 
#                  pos_tags[lang][pos]['upos']))
# print("""</table>""")
print("""</div>""")










print("</body>")
print("</html>")

# N of MWE
# MATCH THE WORD POS WITH THE  WN POS (6 of them)



# CHECK FOR CONCEPTS IN CWL THAT LINK TO DELETED CONCEPTS  


# CHECK REPEATED CONCEPTS (WITH SAME WIDs)
