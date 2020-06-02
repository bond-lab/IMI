#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
import cgitb; cgitb.enable()  # for troubleshooting

import sqlite3, codecs
from collections import defaultdict as dd

from ntumc_webkit import *
from lang_data_toolkit import *


################################################################################
# GET CGI FORM FIELDS / GLOBAL VARIABLES
################################################################################
form = cgi.FieldStorage()

try:
    sid_from = int(form.getfirst("sid_from", 50804))
    sid_to = int(form.getfirst("sid_to", 51464))
except:
    sid_from = 50804
    sid_to = 51464


lang = form.getfirst("lang", "eng")
langs = [('eng','English'), ('eng1','English 1'), ('eng2','English 2'), 
         ('cmn','Chinese'), ('ind','Indonesian'),
         ('jpn','Japanese'), ('ita','Italian')]


dbs = [] # TRIPLET (A/B/..., db_path, corpus_code)
#for i in ['A','B','C','D','E']:
for i in ['A','B','C']:
    if os.path.isfile("../db/%s%s.db" % (lang,i)):
        dbs.append((i, "../db/%s%s.db" % (lang,i),"%s%s" % (lang,i)))

target_db = [('target', "../db/%s.db" % (lang,), "%s" % (lang,))]



wncgi = "wn-gridx.cgi?gridmode=ntumc-noedit&synset="
wncgi_lemma = "wn-gridx.cgi?gridmode=ntumc-noedit&lang=%s&lemma="  % (lang[0:3])
if lang == 'eng2':
    tag_w = "tag-word.cgi?corpus=eng2&lang=eng&gridmode=ntumc-noedit&sid="
else:
    tag_w = "tag-word.cgi?corpus=%s&lang=%s&gridmode=ntumc-noedit&sid=" % (lang[0:3],lang[0:3])




################################################################################
# FETCH WN DATA (DEFINITIONS)
################################################################################
wndb = "../db/wn-ntumc.db"
con = sqlite3.connect(wndb)
c = con.cursor()
c.execute("""SELECT synset, lang, sid, def
             FROM synset_def
             WHERE lang in (?, ?)
          """ , (lang, 'eng'))                                       

defs = dd(lambda: dd(lambda: dd(str)))
for r in c:
    defs[r[0]][r[1]][r[2]] = r[3]

con.close()



################################################################################
# FUNCTIONS
################################################################################
def s_color(num):
    """This functions takes a float number, trims it to n decimals places 
       without rounding it, and assigns color according to it."""
    
    n = 2
    if num < 0.5:
        return ('<span style="color:red">%.*f</span>' % (n + 1, num))[:-1]
    elif num < 0.7:
        return ('<span style="color:orange">%.*f</span>' % (n + 1, num))[:-1]
    elif num < 1:
        return ('<span style="color:blue">%.*f</span>' % (n + 1, num))[:-1]
    elif num == 1:  # #008000 = green
        return ('<span style="color:#008000">%.*f</span>' % (n + 1, num))[:-1]
    else: 
        return ('<span style="color:red">%s</span>' % (num))


def link(tag, ref):
    """This function transforms a tag into a link to the wn-gridx
       It takes a tag (ideally a synset), and a ref (???) as argument"""
    title = """ title='' """;
    href = '';

    if tag and len(tag) == 10:  # Check if tag looks like a synset
        href = " href='%s%s' "  % (wncgi, tag)

        tdf = list()
        for i in sorted(defs[tag][lang].keys()):
            tdf.append(defs[tag][lang][i])
        if len(tdf) > 0:
            tdf = cgi.escape('; '.join(tdf) + ';', True)
        else:
            tdf = ''

        edf = list()
        for i in sorted(defs[tag]['eng'].keys()):
            edf.append(defs[tag]['eng'][i])
        if len(edf) > 0:
            edf = cgi.escape('; '.join(edf)+ ';', True)
        else:
            edf = ''

        title = """ class='tooltip' title="%s %s" """ % (tdf, edf)

    if ref and tag == ref:  # #008000 = green
        return "<a style='color:#008000;'%s %s>%s</a>" % (href, title, tag)  # ref & tag match = Green
    elif ref:
        return "<a style='color:crimson;'%s %s>%s</a>" % (href, title, tag)  # if ref = red
    else:
        return "<a style='color:black;'%s %s >%s</a>" % (href, title, tag)  # else black


def linkw(word):
    """This function turns a word into a link for a lemma search in the wordnet"""
    return """<a style='color:black;text-decoration:none;' target="_blank" 
              href='%s%s'>%s</a>""" % (wncgi_lemma, word, word)








################################################################################
# FETCH DB DATA; IT ASSUMES AT LEAST 1 DB EXISTS
################################################################################
sent = dict()
data = dd(lambda: dd(lambda: dd(lambda: dd(str))))  # agregates data by sentence
data_ag = dd(lambda: dd(lambda: dd(lambda: dd(str))))  # agreegates all data
ag_scores = dd(lambda: dd(int))  # e.g. {sid: {'AvsS' : 0.8} }
tagger = dict()


con = sqlite3.connect(dbs[0][1])
c = con.cursor()

c.execute("""SELECT sid, sent
             FROM  sent
             WHERE sid >= ? 
             AND sid <= ?""", (sid_from, sid_to))
for (sid, sentence) in c:
    sent[sid] = sentence

con.close()



concept_query = """SELECT sid, cid, clemma, tag, tags, 
                          comment, usrname 
                   FROM concept 
                   WHERE sid >= ? AND sid <= ? 
                   ORDER BY sid, cid"""

word_query = """SELECT sid, wid, word, pos, lemma
                FROM word
                WHERE sid >= ? AND sid <= ?"""



for db in dbs + target_db:
    db_ref = db[0].lower()
    con = sqlite3.connect(db[1])
    c = con.cursor()

    # sys.stderr.write('CONNECTING TO DB: ' + db_ref + ' ' + db[1] + '\n') #TEST#
    # sys.stderr.write('RUNNING QUERY: ' + concept_query + '\n') #TEST#

    c.execute(concept_query, (sid_from, sid_to))
    for (sid, cid, clemma, tag, tags, comment, usrname) in c:
        data[sid][cid][db_ref]['tag'] = str(tag).strip()
        data[sid][cid][db_ref]['clem'] = clemma
        data[sid][cid][db_ref]['usr'] = usrname
        if comment:
            data[sid][cid][db_ref]['com'] = comment

        sidcid = str(sid) + '_' + str(cid)

        data_ag['all'][sidcid][db_ref]['tag'] = str(tag).strip()

    con.close()



################################################################################
# CALCULATE SILVER DATA / MAJ TAG
################################################################################
for sid in sent.keys():

    for cid in data[sid].keys():

        tags = [] # LIST OF TAGS USED
        for db in dbs:
            db_ref = db[0].lower()

            if data[sid][cid][db_ref]['tag'] != None and\
               data[sid][cid][db_ref]['tag'] != "None":
                tags.append(data[sid][cid][db_ref]['tag'])

        try:
            mx = max(tags.count(t) for t in tags) # MOST USED TAG
        except:
            mx = 0

        if mx > 1:  # IF THERE WAS A MINIMUM AGREEMENT

            majtags =  list(set([t for t in tags if tags.count(t) == mx]))

            if len(majtags) == 1: # IF THERE IS NO TIE
                majtag = majtags[0]
            else:
                majtag = '?'

            if majtag == "None":
                 majtag = '?'

            data[sid][cid]['s']['tag'] = majtag             

            sidcid = str(sid) + '_' + str(cid)
            data_ag['all'][sidcid]['s']['tag'] = majtag

        else: # NO AGREEMENT
            data[sid][cid]['s']['tag'] = '?'  
            data_ag['all'][sidcid]['s']['tag'] = '?'


    ############################################################################
    # CALCULATE SENTENCE AGREEMENT SCORES
    ############################################################################

    db_refs = []
    for db in dbs:
        db_refs.append(db[0].lower())
    db_refs.append('s') # ADD THE MAJ TAG

    for x in db_refs:
        for y in db_refs:

            ag_ref = '%s%s' % (x, y)
            ag_ref = ag_ref.upper()

            try:
                score = 1.0 * sum([1 for cid in data[sid].keys() \
                if data[sid][cid][x]['tag'] == data[sid][cid][y]['tag'] and \
                data[sid][cid][x]['tag'] != "None"]) / len(data[sid].keys())

                ag_scores[sid][ag_ref] = score
            except:
                ag_scores[sid][ag_ref] = "N.A."
    ############################################################################
                

################################################################################
# CALCULATE GLOBAL AGREEMENT SCORES
################################################################################

db_refs = []
for db in dbs:
    db_refs.append(db[0].lower())
db_refs.append('s') # ADD THE MAJ TAG

for x in db_refs:
    for y in db_refs:

        ag_ref = '%s%s' % (x, y)
        ag_ref = ag_ref.upper()

        try:
            score = 1.0 * sum([1 for sidcid in data_ag['all'].keys() if \
            data_ag['all'][sidcid][x]['tag'] == data_ag['all'][sidcid][y]['tag'] \
            and data_ag['all'][sidcid][x]['tag'] != "None"]) / len(data_ag['all'].keys())

            ag_scores['all'][ag_ref] = score

        except:
            ag_scores['all'][ag_ref] = "N.A."



################################################################################
# GUIDELINES
################################################################################
guidelines = """<div class="info">
<a class="info"><span style="color: #4D99E0;">
<i class="icon-info-sign"></i>ReadMe</a>

<div class="show_info">
<h5>Guidelines:</h5>

<p>Agreement is the percentage of times the tag agreed with the majority.
<br>The majority tag is calculated as the most frequent tag between A, B, C and D.

<p>Clicking on the sentence number (marked by ✎) will jump you to the 
sentence to be tagged (you may have to log in). Clicking on the lemma looks 
it up in wordnet, clicking on the tag looks it up on wordnet, mouse-over on 
the tag gives you the defintion.

</div></div>"""
################################################################################



########
# HTML
########

# Header
print(u"""Content-type: text/html; charset=utf-8\n""")
print(u"""
<!DOCTYPE html>
<html>
  <head>

    <!-- IMPORT FONT AWESOME -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.4.0/css/font-awesome.min.css">

    <!-- KICKSTART -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
    <script src="../HTML-KickStart-master/js/kickstart.js"></script> <!-- KICKSTART -->
    <link rel="stylesheet" href="../HTML-KickStart-master/css/kickstart.css" media="all" /> 

    <!-- IMPORT NTUMC COMMON STYLES -->
    <link href="../ntumc-common.css" rel="stylesheet" type="text/css">

<style>
hr{
  padding: 0px;
  margin: 10px;    
}
</style>

</head>
<body>""")



print("""<div class="col_7"  >""")

print("""<h5>Annotation Agreement: %s-%s </h5>\n """ % (sid_from, sid_to))

################################################################################
# SEARCH FORM
################################################################################
print("""<form id="goto" action="agreement.cgi" method="post" style="display:inline-block">""")
print("""<b>Lang:</b>""")
print("""<select id="lang" name="lang">""")
for l in langs:
    if l[0] == lang:
        print("<option value ='%s' selected>%s</option>" % l)
    else:
        print("<option value ='%s'>%s</option>" % l)
print("""</select>""")

print("""<b>From (sid):</b>""")
print("""<input type="text" name="sid_from" value="%s" size="6"
         pattern="[0-9]{1,}" onfocus="disableKeys();" 
         onblur="enableKeys();"/>""" % sid_from)
print("""<b>To:</b>""")
print("""<input type="text" name="sid_to" value="%s" size="6"
         pattern="[0-9]{1,}" onfocus="disableKeys();" 
         onblur="enableKeys();"/>""" % sid_to)

print("""<button class="small"><a href="javascript:{}"
         onclick="document.getElementById('goto').submit(); 
         return false;"><span style="color: #4D99E0;font-size:15px">
         Go</span></a>
         </button>""")

print("""</form>""")

print("<br><br>")
print(guidelines)
print("</div>")



################################################################################
# PRINT GLOBAL AGREEMENT SCORES (ALL SENTENCES)
################################################################################
db_refs = []
for db in dbs:
    db_refs.append(db[0].lower())

print("""<div class="col_3" style="font-size:90%"> 
         <strong> Global Agreement Scores: </strong>
         <table class="tight">""")

print("""<thead><tr>""")
print("<th></th>")
for x in db_refs + ['M']:
    print("<th><b>%s</b></th>" % x.upper())
print("</tr></thead>")

for x in db_refs:
    print("<tr><td><b>%s</b></td>" % x.upper())
    for y in db_refs + ['s']:
        ag_ref = ('%s%s' % (x, y)).upper()
        print("<td>%s</td>" % s_color(ag_scores['all'][ag_ref]))
print("</table>")
print("</div>")





################################################################################
# PRINT PER-SENTENCE AGREEMENT 
################################################################################
for sid in sorted(data.keys()):  # for sentence in selected range
    print("<hr>")

    print("""<div class="col_9" style="font-size:90%">""") 
    print("""<a href='%s%d' target='_blank' >✎ SID:%s</a>
             <strong>%s</strong> (%d Concepts)
         """ % (tag_w, sid, sid, sent[sid], len(data[sid].keys()) ))

    print("""<table>""")
    # TABLE HEADERS
    print("""<tr><th>cid</th><th>lemma</th>""")
    for db in dbs:
        print("<th>%s</th>" % db[0])
    print("""<th>TargetDB</th><th>MajTag</th><th>Comments</th></tr>""")


    for cid in data[sid].keys():  # for each concept in the sentence

        majtag = str(data[sid][cid]['s']['tag']).strip() # used com compare tags
        db_ref = dbs[0][0].lower()

        print("<tr>")

        # CID
        print("<td><nobr>%s</nobr></td>" % cid)

        # C-LEMMA
        clemma = linkw(data[sid][cid][db_ref]['clem'].strip())
        print("<td><nobr>%s</nobr></td>" % clemma)

        comms = ''
        for db in dbs + target_db:
            db_ref = db[0].lower()

            tag = link(str(data[sid][cid][db_ref]['tag']).strip(), majtag)
            # TAG
            print("<td><nobr>%s</nobr></td>" % tag)
            
            com = data[sid][cid][db_ref]['com']
            if com:
                comms += ("<b>%s:</b>" % (db[0])) + com + '; '

        # MAJTAG
        print("<td><nobr>%s</nobr></td>" % link(majtag, None))

        # COMMENTS
        print(u"""<td>%s</td>""" % comms )

        print("</tr>")


    print("</table>")
    print("""</div>""") 


    ############################################################################
    # PER-SENTENCE AGREEMENT SUMMARY  
    ############################################################################
    print("""<div class="col_3" style="font-size:75%" >""")
    print("""<table class="tight">""")

    print("""<thead><tr>""") 
    print("<th></th>")
    for x in db_refs + ['M']:
        print("<th><b>%s</b></th>" % x.upper())
    print("</tr></thead>")

    for x in db_refs:
        print("<tr><td><b>%s</b></td>" % x.upper())
        for y in db_refs + ['s']:
            ag_ref = ('%s%s' % (x, y)).upper()
            print("<td>%s</td>" % s_color(ag_scores[sid][ag_ref]))
    print("</table>")
    print("</div>")



print("""</body></html>\n""")
