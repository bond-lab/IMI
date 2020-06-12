#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# KNOWN BUGS:
######################################################################
# There seems to be a bug about ';' in the URI. 
# Our server is accepting any kind of punctuation but ';' or " ' "
# For now, I'm just printing nothing about these in wordviewmode.

######################################################################

import cgi, urllib
import cgitb; cgitb.enable()  # for troubleshooting
from os import environ  # for cookies
import re, sqlite3, collections
from collections import defaultdict as dd
import datetime

from ntumc_util import placeholders_for
from ntumc_webkit import *
from lang_data_toolkit import *
from html import escape

# create the error log for the cgi errors
errlog = open('cgi_err.log', 'w+', encoding="utf-8")
errlog.write("LAST SEARCH LOG:\n")


cginame = "NTU Multilingual Corpus Interface"
ver = "0.1"
url = "http://compling.hss.ntu.edu.sg/"


form = cgi.FieldStorage()

mode = escape(form.getfirst('mode',''))
postag = escape(form.getfirst("postag",'')) # FOR WORDVIEW
# wordtag = form.getlist("wordtag[]") # FOR WORDVIEW
wordtag = [escape(t) for t in form.getlist("wordtag[]")]
# wordclemma = form.getlist("wordclemma[]") # FOR WORDVIEW
wordclemma = [escape(c) for c in form.getlist("wordclemma[]")]

################################################################################
# LANGUAGE CHOICES: it allows the choice of a main
# search language, and as many other languages
# as wanted to show parallel alignment.
# The same language as the search language cannot
# be chosen as a "see also language"
################################################################################
searchlang = escape(form.getfirst("searchlang", "eng"))
# langs2 = form.getlist("langs2")
langs2 = [escape(l) for l in form.getlist("langs2")]
if searchlang in langs2:
    langs2.remove(searchlang)


# senti = form.getlist("senti[]") # receives either 'mlsenticon', 'sentiwn', both or none! 
senti = [escape(s) for s in form.getlist("senti[]")]
if 'mlsenticon' in senti and 'sentiwn' in senti:
    senti = 'comp' # then it will compile both sentiment scores

concept = escape(form.getfirst('concept','')) # receives a synset
ph_concept = concept if concept != None else ""
clemma = escape(form.getfirst('clemma','')) # receives a lemmatized concept 
ph_clemma = clemma if clemma != None else ""
word = escape(form.getfirst('word','')) # receives a surface form
ph_word = word if word != None else ""
lemma = escape(form.getfirst('lemma','')) # receives a lemmatized word
ph_lemma = lemma if lemma != None else ""
limit = escape(form.getfirst("limit", "10")) # limit number os sentences to show


sentlike = escape(form.getfirst('sentlike','')) # try to match pattern to sentence
ph_sentlike = sentlike if sentlike != None else ""



#########################################
# SIDS FROM TO
sid_from = escape(form.getfirst("sid_from", '0'))
try:
    sid_from = int(sid_from)
except:
    sid_from = 0
sid_to = escape(form.getfirst("sid_to", '1000000'))

try:
    sid_to = int(sid_to)
except:
    sid_to = 1000000
#print(sid_from, sid_to)
##########################################

# pos_eng = form.getlist("selectpos-eng")
# pos_cmn = form.getlist("selectpos-cmn")
# pos_jpn = form.getlist("selectpos-jpn")
# pos_ind = form.getlist("selectpos-ind")
# pos_ita = form.getlist("selectpos-ita")
pos_eng = [escape(pos) for pos in form.getlist("selectpos-eng")]
pos_cmn = [escape(pos) for pos in form.getlist("selectpos-cmn")]
pos_jpn = [escape(pos) for pos in form.getlist("selectpos-jpn")]
pos_ind = [escape(pos) for pos in form.getlist("selectpos-ind")]
pos_ita = [escape(pos) for pos in form.getlist("selectpos-ita")]

pos_form = dd(lambda: list())
pos_form['eng'] = pos_eng
pos_form['cmn'] = pos_cmn
pos_form['jpn'] = pos_jpn
pos_form['ind'] = pos_ind
pos_form['ita'] = pos_ita

# corpuslangs = ['eng', 'cmn', 'jpn', 'ind'] # THIS SHOULD GO TO DATA.py
corpusdb = "../db/%s.db" % searchlang



usr = escape(form.getfirst('usr', '')) # should be fetched by cookie!
userid = escape(form.getfirst('userid', 'all')) # defaults to every user
mode = escape(form.getfirst('mode','')) # viewing mode
source = escape(form.getfirst('source[]','')) # choose source, default is ntmuc


### reference to self (.cgi)
selfcgi = "showcorpus.cgi"

### working wordnet.db 
wndb = "../db/wn-ntumc.db"

### reference to wn-grid (search .cgi)
wncgi_lemma = "wn-gridx.cgi?gridmode=ntumc-noedit&lang=%s&lemma=" % searchlang
wncgi_ss = "wn-gridx.cgi?gridmode=ntumc-noedit&lang=%s&synset=" % searchlang


#############################
# SQLITE Query Preparation
#############################
searchquery = ""
# searchquery += "(Language:%s)+" % searchlang



if sentlike:
    searchquery += "(Sentence-Like:%s)+" % sentlike
    # sentlike_q = """ AND sent.sent GLOB '*%s*' """ % sentlike
    sentlike_q = (""" AND sent.sent GLOB ? """, [sentlike])
else:
    sentlike_q = ('', False)

if concept:
    searchquery += "(Concept:%s)+" % concept
    # concept_q = " AND tag='%s' " % concept
    concept_q = (" AND tag = ? ", [concept])
else:
    concept_q = ('', False)

if clemma:
    searchquery += "(C-Lemma:%s)+" % clemma
    # clemma_q = """ AND clemma GLOB '%s' """ % clemma
    clemma_q = (" AND clemma GLOB ? ", [clemma])
else:
    clemma_q = ('', False)

if word:
    searchquery += "(Word:%s)+" % word
    # word_q = """ AND word GLOB '%s' """ % word
    word_q = (" AND word GLOB ? ", [word])
else:
    word_q = ('', False)

if lemma:
    searchquery += "(Lemma:%s)+" % lemma
    # lemma_q = """ AND lemma GLOB '%s' """ % lemma
    lemma_q = (" AND lemma GLOB ? ", [lemma])
else:
    lemma_q =  ('', False)

if len(pos_form[searchlang]) > 0:
    searchquery += "(POS:%s)+" % (" or ".join("'%s'" % s for s in pos_form[searchlang]),)
    # pos_t  = ",".join("'%s'" % s for s in pos_form[searchlang])
    # pos_q = """ AND pos in (%s) """ % pos_t
    pos_t = placeholders_for(pos_form[searchlang])
    pos_q = (" AND pos in (%s) " % pos_t, pos_form[searchlang])
else:
    pos_q =  ('', False)

if sid_from != 0:
    searchquery += "(SID>=%s)+" % sid_from
    # sid_from_q = " AND sent.sid >= %s " % sid_from
    # sid_from_q2 = " AND sid >= %s " % sid_from
    sid_from_q = (" AND sent.sid >= %s ", [sid_from])
    sid_from_q2 = (" AND sid >= %s ", [sid_from])
else:
    sid_from_q =  ('', False)
    sid_from_q2 =  ('', False)

if sid_to != 1000000:
    searchquery += "(SID<=%s)+" % sid_to
    # sid_to_q = " AND sent.sid <= %s " % sid_to
    # sid_to_q2 = " AND sid <= %s " % sid_to
    sid_to_q = (" AND sent.sid <= ? ", [sid_to])
    sid_to_q2 = (" AND sid <= ? ", [sid_to])
else:
    sid_to_q =  ('', False)
    sid_to_q2 =  ('', False)

release_match_style = False
if limit == "all":
    limit_q =  ('', False)
elif (sid_from != 0 or sid_to != 1000000) and (concept_q == "" and 
    clemma_q == "" and word_q == "" and lemma_q == "" and pos_q == ""):
    limit_q = (" LIMIT ? ", [5000]) #HARD CODED LIMIT 500 words
    release_match_style = True
else:
    limit_q = (" LIMIT ? ", [limit])


    
if mode == "wordview":
    # errlog.write("It entered wordview mode!<br>")
    
    # sss = ",".join("'%s'" % s for s in wordtag)
    sss = (",".join("?" for s in wordtag),wordtag)

    ###########################
    # Connect to wordnet.db
    ###########################
    con = sqlite3.connect(wndb)
    wn = con.cursor()
    fetch_ss_name_def = """
        SELECT s.synset, name, src, lang, def, sid
        FROM (SELECT synset, name, src
              FROM synset
              WHERE synset in (%s)) s
        LEFT JOIN synset_def
        WHERE synset_def.synset = s.synset
        AND synset_def.lang in (?, 'eng')
    """ % placeholders_for(sss[0])
    wn.execute(fetch_ss_name_def, sss[0] + sss[1] + [searchlang])
    rows = wn.fetchall()
    ss_defs = dd(lambda: dd(lambda:  dd(lambda: str())))
    ss_names = dd(lambda: dd(lambda:list()))
    for r in rows:
        (synset, name, src,
         lang, ss_def, sid) = (r[0], r[1], r[2],
                               r[3], r[4], r[5])
        ss_names[synset] = [name, src]
        ss_defs[synset][lang][sid] = ss_def
    try:
        html_word = escape(word, quote=True)
    except:
        html_word = '' # The forms fails to read ; as the argument for word!
    try:
        html_lemma = escape(lemma, quote=True)
    except:
        html_lemma = '' # The forms fails to read ; as the argument for lemma!
    html_pos = escape(postag, quote=True)

    lemma_href = """<a class='fancybox fancybox.iframe' 
                    href='%s%s'>%s</a>
                      """ % (wncgi_lemma, html_lemma, html_lemma)
    postag_def = """<span title='%s'>%s</span>""" % (pos_tags[searchlang][postag]['eng_def'], 
                        pos_tags[searchlang][postag]['def'])

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
    print("""<title>%s</title></head><body>""" % cginame)
    print("""<h6>Word Details</h6>""")
    print("""<table>""")
    print("""<tr><td>Word:</td><td>%s</td></tr>""" % html_word)
    print("""<tr><td>POS:</td><td>%s (%s)</td></tr>
          """ % (html_pos, postag_def) )
    print("""<tr><td>Lemma:</td><td>%s</td></tr>""" % lemma_href)
    print("""<tr><td>Concept(s):</td><td>""")

    for i, tag in enumerate(wordtag):
        tag_defs = ""
        for defid in ss_defs[tag][searchlang]:
            tag_defs += ss_defs[tag][searchlang][defid]
            tag_defs += "; "
        if  searchlang != 'eng':
            if tag_defs != "":
                tag_defs = "<br>"
            for defid in ss_defs[tag]['eng']:
                tag_defs += ss_defs[tag]['eng'][defid]
                tag_defs += "; "
        if tag_defs == "":
            tag_defs = "no_definition "

        tag_defs = tag_defs[:-1] # remove the final space
        try:
            print("""<a class='fancybox fancybox.iframe' 
                  href='%s%s'>%s</a> (%s) <br>
                  """ % (wncgi_ss,tag, wordclemma[i], tag_defs))
        except:
            if tag in ['e','None','x','w','loc','org','per','dat','oth']:
                print("""<a class='fancybox fancybox.iframe' 
                  href='%s%s'>%s</a> (%s) <br>
                  """ % (wncgi_ss,tag, tag, tag_defs))
            else:
                print("""<a class='fancybox fancybox.iframe' 
                  href='%s%s'>%s</a> (%s) <br>
                  """ % (wncgi_ss,tag, ss_names[tag][0], tag_defs))

    print("""</td></tr>""")
    print("""</table></div>""")

    print("</body>")
    print("</html>")
    sys.exit(0)




# errlog.write("It did not enter wordviewmode!<br>")
# message = "" #TEST
###########################
# Connect to corpus.db
###########################
if corpusdb != "../db/None.db":
    conc = sqlite3.connect(corpusdb)
    cc = conc.cursor()
    cc2 = conc.cursor()


    ############################################################
    # If nothing is linked to a concept, then the query
    # should not have cwl (because that restricts the 
    # query to ONLY things that have concepts!
    ############################################################
    if concept_q != ('', False) or clemma_q != ('', False):

        # errlog.write("It entered concept_q nor clemma_q =! EMPTY <br>")

        # showcorpus  ="""
        #    SELECT cl.sid, cl.cid, cl.tag 
        #    FROM (SELECT c.sid, c.cid, wid, tag 
        #          FROM (SELECT sid, cid, tag 
        #                FROM concept WHERE 1 > 0 {} {} {} {} ) c 
        #          LEFT JOIN cwl 
        #          WHERE cwl.sid = c.sid 
        #          AND c.cid = cwl.cid) cl 
        #    LEFT JOIN word 
        #    WHERE word.sid = cl.sid 
        #    AND word.wid = cl.wid {} {} {} {} 
        #    """.format(concept_q, clemma_q, sid_from_q2, 
        #               sid_to_q2, word_q, lemma_q, pos_q, limit_q)


        showcorpus  ="""
           SELECT cl.sid, cl.cid, cl.tag 
           FROM (SELECT c.sid, c.cid, wid, tag 
                 FROM (SELECT sid, cid, tag 
                       FROM concept WHERE 1 > 0 {} {} {} {} ) c 
                 LEFT JOIN cwl 
                 WHERE cwl.sid = c.sid 
                 AND c.cid = cwl.cid) cl 
           LEFT JOIN word 
           WHERE word.sid = cl.sid 
           AND word.wid = cl.wid {} {} {} {} 
           """.format(concept_q[0], clemma_q[0], sid_from_q2[0], sid_to_q2[0], word_q[0], lemma_q[0], pos_q[0], limit_q[0])


        # errlog.write("concept(tag): %s\n" % concept_q)
        # errlog.write("conceptlemma: %s\n" % clemma_q)
        # errlog.write("It will try to run the following query: <br>")
        # errlog.write("%s <br>" % showcorpus)
        # errlog.flush()


        params = []
        for p in (concept_q, clemma_q, sid_from_q2, 
                  sid_to_q2, word_q, lemma_q, pos_q, limit_q):
            if p[1]:
                params = params + p[1]

        # concept_q[1] if concept_q[1] else [] +\
        # clemma_q[1] if clemma_q[1] else [] +\
        # sid_from_q2[1] if sid_from_q2[1] else [] +\
        # sid_to_q2[1] if sid_to_q2[1] else [] +\
        # word_q[1] if word_q[1] else [] +\
        # lemma_q[1] if lemma_q[1] else [] +\
        # pos_q[1] if pos_q[1] else [] +\
        # limit_q[1] if limit_q[1] else []

        cc.execute(showcorpus, params)

        rows = cc.fetchall()

        sid_cid = dd(lambda: dd(lambda: str))
        for r in rows:
            (sid, cid, tag) = (r[0], r[1], r[2])
            sid_cid[sid][cid] = [tag]
        sids = ",".join("'%s'" % s for s in sid_cid.keys())
        # errlog.write("Executed ok and now has a list of sids: <br>")
        # errlog.write(" %s <br>" % str(sids))



    elif word_q != ('', False) or lemma_q != ('', False) or pos_q != ('', False) \
         or sid_from_q != ('', False) or sid_to_q != ('', False) or sentlike_q != ('', False):

        # errlog.write("The search was not related to concepts... <br>")

        # showcorpus = """
        # SELECT word.sid, word.wid
        # FROM word
        # LEFT JOIN sent
        # WHERE word.sid = sent.sid
        # %s %s %s %s %s %s %s""" % (word_q, lemma_q, pos_q, 
        #                            sid_from_q, sid_to_q, sentlike_q, limit_q)

        showcorpus = """
        SELECT word.sid, word.wid
        FROM word
        LEFT JOIN sent
        WHERE word.sid = sent.sid
        {} {} {} {} {} {} {}""".format(word_q[0], lemma_q[0], pos_q[0], 
                                       sid_from_q[0], sid_to_q[0], sentlike_q[0], limit_q[0])




        # errlog.write("It will try to run the following query:\n")
        errlog.write("%s\n" % showcorpus)



        params = []
        for p in (word_q, lemma_q, pos_q, 
                  sid_from_q, sid_to_q, sentlike_q, limit_q):
            if p[1]:
                params = params + p[1]

        cc.execute(showcorpus, params)


        rows = cc.fetchall()

        sid_cid = dd(lambda: dd(lambda:list()))
        sid_matched_wid = dd(lambda: list())
        sid_list = list()
        for r in rows:
            sid = r[0]
            wid = r[1]
            sid_list.append(sid)
            sid_matched_wid[sid].append(wid)
        sids = ",".join("'%s'" % s for s in sid_list)

    else:
        sids = ",".join("'%s'" % s for s in [])
    #######################################################################
    # THE sids HAS THE SIDS TO BE PRINTED IN AN SQLITE QUERY;  
    # IF CONCEPTS WERE SEARCHED, THEN THE DICT sid_cid HOLDS THAT INFO TOO
    #######################################################################


    sid_wid = dd(lambda: dd(lambda:list()))
    fetch_sent = """
    SELECT sid, wid, word, lemma, pos
    FROM word
    WHERE sid in (%s)""" % sids
    cc.execute(fetch_sent)
    rows = cc.fetchall()
    for r in rows:
        (sid, wid, word, lemma, pos) = (r[0], r[1], r[2], r[3], r[4])
        pos = "unk" if pos == None else pos
        sid_wid[sid][wid] = [word, lemma, pos]

    #######################################################################
    # THE DICT sid_wid HAS THE FULL LIST OF SIDS BY WIDS;  
    #######################################################################

    fetch_sent_full_details = """
    SELECT w.sid, w.wid, w.word, w.lemma, w.pos, cwl.cid
    FROM (SELECT sid, wid, word, lemma, pos
          FROM word
          WHERE sid in (%s) ) w
    LEFT JOIN cwl
    WHERE w.wid = cwl.wid
    AND w.sid = cwl.sid
    ORDER BY w.sid""" % sids

    fetch_concept_details = """
    SELECT sid, cid, clemma, tag 
    FROM concept
    WHERE sid in (%s)
    ORDER BY sid""" % sids

    sid_cid_wid = dd(lambda: dd(lambda: list()))
    sid_wid_cid = dd(lambda: dd(lambda: list()))
    sid_wid_tag = dd(lambda: dd(lambda: list()))
    sid_cid_tag = dd(lambda: dd(lambda: str))
    sid_cid_clemma = dd(lambda: dd(lambda: str))

    sss = set() # holds the list of all tags (for sentiment)

    cc2.execute(fetch_concept_details)
    rows2 = cc2.fetchall()
    for r in rows2:
        (sid, cid, clemma, tag) = (r[0], r[1], r[2], r[3]) 
        sid_cid_tag[sid][cid] = tag
        sid_cid_clemma[sid][cid] = clemma
        sss.add(tag)

    cc.execute(fetch_sent_full_details)
    rows = cc.fetchall()

    for r in rows:
        (sid, wid, word, 
         lemma, pos, cid) = (r[0], r[1], r[2], 
                             r[3], r[4], r[5])

        # TRY TO USE ONLY THE SECOND DICT
        # (IS IT COMPATIBLE WITH BOTH CASES?) 
        sid_cid_wid[sid][cid].append(wid)  # THIS IS TO COLOR EVERY WID IN CID
        sid_wid_cid[sid][wid].append(cid)
        sid_wid_tag[sid][wid].append(sid_cid_tag[sid][cid])

    conc.close()


    #######################################################################
    # THE DICT sid_cid_wid IDENTIFIES IF A WID BELONGS TO A CID IN SID
    # THE DICT sid_cid_tag HAS THE TAG FOR EACH CONCEPT IN SID
    # THE DICT sid_cid_clemma HAS THE C-LEMMA FOR EACH CONCEPT IN SID
    #######################################################################


    if langs2: # there may be more than 1 lang2, these dicts keep all the info

        # links[lang][fsid] = set(tsid)
        links = dd(lambda: dd(set)) # this holds the sid links between langs
        # l_sid_fullsent = {lang2: {sid: full_sentence} }
        l_sid_fullsent = dd(lambda: dd(lambda: ""))

        l_sid_wid = dd(lambda: dd(lambda: dd(lambda:list())))
        l_sid_cid_wid = dd(lambda: dd(lambda: dd(lambda: list())))
        l_sid_wid_cid = dd(lambda: dd(lambda: dd(lambda: list())))
        l_sid_wid_tag = dd(lambda: dd(lambda: dd(lambda: list())))
        
        l_sid_cid_tag = dd(lambda: dd(lambda: dd(lambda: str)))
        l_sid_cid_clemma = dd(lambda: dd(lambda: dd(lambda: str)))

        errlog.write("There were langs2: %s \n" % ' | '.join(langs2)) #LOG

        # try to find a link database between searchlang and lang2
        for lang2 in langs2:
            lang2_sids = set()
            if os.path.isfile("../db/%s-%s.db" % (searchlang, lang2)):

                # Links will always come from "searchlang" to "lang2"
                # links[lang][fsid] = set(tsid)
                # fsid should be in searchlang
                # for example links[10001] = (10002,10003)
                linkdb = "../db/%s-%s.db" % (searchlang, lang2)
                errlog.write("Found lang1-lang2: %s \n" % linkdb) #LOG
                lcon = sqlite3.connect("%s" % linkdb)
                lc = lcon.cursor()
                query="""SELECT fsid, tsid 
                         FROM slink 
                         WHERE fsid in (%s)""" % sids
                lc.execute(query)
                for (fsid, tsid) in lc:
                    links[lang2][int(fsid)].add(int(tsid))
                    lang2_sids.add(tsid) # this is a list of sids in the target langauge to fetch details

            elif os.path.isfile("../db/%s-%s.db" % (lang2, searchlang)):

                linkdb = "../db/%s-%s.db" % (lang2, searchlang)
                errlog.write("Found lang2-lang1: %s \n" % linkdb) #LOG
                lcon = sqlite3.connect("%s" % linkdb)
                lc = lcon.cursor()
                query="""SELECT fsid, tsid 
                         FROM slink  
                         WHERE tsid in (%s)""" % sids
                lc.execute(query)
                for (fsid, tsid) in lc:
                    links[lang2][int(tsid)].add(int(fsid))
                    lang2_sids.add(fsid)


            lang2_sids = ",".join("'%s'" % s for s in lang2_sids)
            errlog.write("Fetched sids: %s \n" % lang2_sids) #LOG
            errlog.write("links_dict: %s \n" % '|'.join(links.keys())) #LOG


            ##############################################
            # THIS IS TO GET THE LINKED LANGUAGES INFO
            # this will happen per lang in langs2.
            ##############################################

            corpusdb = "../db/%s.db" % lang2
            conc = sqlite3.connect(corpusdb)
            cc = conc.cursor()
            cc2 = conc.cursor()


            # STORE THE FULL SENTENCE, IN CASE THE LANG2 DOES NOT 
            # HAVE WORDS TO PRODUCE THE SENTENCE FROM...
            fetch_fullsent = """
            SELECT sid, sent.sent
            FROM sent
            WHERE sid in (%s)""" % lang2_sids
            cc.execute(fetch_fullsent)
            rows = cc.fetchall()
            for r in rows:
                (s, fullsent) = (r[0], r[1])
                l_sid_fullsent[lang2][s] = fullsent
            ######################################################


            fetch_sent = """
            SELECT sid, wid, word, lemma, pos
            FROM word
            WHERE sid in (%s)""" % lang2_sids
            cc.execute(fetch_sent)
            rows = cc.fetchall()
            for r in rows:
                (sid, wid, word, lemma, pos) = (r[0], r[1], r[2], r[3], r[4])
                pos = "unk" if pos == None else pos
                l_sid_wid[lang2][sid][wid] = [word, lemma, pos]


            fetch_sent_full_details = """
            SELECT w.sid, w.wid, w.word, w.lemma, w.pos, cwl.cid
            FROM (SELECT sid, wid, word, lemma, pos
                  FROM word
                  WHERE sid in (%s) ) w
            LEFT JOIN cwl
            WHERE w.wid = cwl.wid
            AND w.sid = cwl.sid
            ORDER BY w.sid""" % lang2_sids

            fetch_concept_details = """
            SELECT sid, cid, clemma, tag 
            FROM concept
            WHERE sid in (%s)
            ORDER BY sid""" % lang2_sids


            cc2.execute(fetch_concept_details)
            rows2 = cc2.fetchall()
            for r in rows2:
                (sid, cid, clemma, tag) = (r[0], r[1], r[2], r[3]) 
                l_sid_cid_tag[lang2][sid][cid] = tag
                l_sid_cid_clemma[lang2][sid][cid] = clemma
                sss.add(tag) # add also synsets for other languages

            cc.execute(fetch_sent_full_details)
            rows = cc.fetchall()

            for r in rows:
                (sid, wid, word, 
                 lemma, pos, cid) = (r[0], r[1], r[2], 
                                     r[3], r[4], r[5])
 
                l_sid_cid_wid[lang2][sid][cid].append(wid)
                l_sid_wid_cid[lang2][sid][wid].append(cid)
                l_sid_wid_tag[lang2][sid][wid].append(l_sid_cid_tag[lang2][sid][cid])

            conc.close()

    sss = ",".join("'%s'" % s for s in sss) # sqlite ready list of all synsets
    if senti in ['comp',['sentiwn'],['mlsenticon']]:
        
        #NEED TO OVERWRITE WN PATH (wn-ntumc.db) does not have sentiment
        wndb = "../../omw/wn-multix.db"

        ss_resource_sent = dd(lambda: dd(lambda: dd(float)))
        ###########################
        # Connect to wordnet.db
        ###########################
        con = sqlite3.connect(wndb)
        wn = con.cursor()
        ss_resource_sentiment = """
        SELECT synset, resource, xref, misc
        FROM xlink
        WHERE resource in ('MLSentiCon','SentiWN')
        AND synset in (%s)
        """ % (sss)
        
        wn.execute(ss_resource_sentiment)
        rows = wn.fetchall()

        for r in rows:
            (synset, resource, xref, misc) = (r[0], r[1], r[2], r[3])
            ss_resource_sent[synset][resource][xref] = float(misc)
                

else:
    sid_cid = dd(lambda: dd(lambda:list()))
    sid_wid = dd(lambda: dd(lambda:list()))
    sid_cid_wid = dd(lambda: dd(lambda: list()))
    sid_wid_cid = dd(lambda: dd(lambda: list()))
    sid_cid_tag = dd(lambda: dd(lambda: str))
    sid_cid_clemma = dd(lambda: dd(lambda: str))
    sid_matched_wid = dd(lambda: list())


################################################################
# FETCH COOKIE
################################################################
# hashed_pw = ""
# if 'HTTP_COOKIE' in os.environ:
#    for cookie in os.environ['HTTP_COOKIE'].split(';'):
#       (key, value ) = cookie.strip().split('=');
#       if key == "UserID":
#          usr = value
#       if key == "Password":
#          hashed_pw = value

################################################################
# HTML
################################################################

### Header
print(u"""Content-type: text/html; charset=utf-8\n
<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
    <link href="../tag-wn.css" rel="stylesheet" type="text/css">
    <script src="../tag-wn.js" language="javascript"></script>

    <!-- For DatePicker -->
    <link rel="stylesheet" href="//code.jquery.com/ui/1.11.2/themes/smoothness/jquery-ui.css">
    <script src="//code.jquery.com/jquery-1.10.2.js"></script>
    <script src="//code.jquery.com/ui/1.11.2/jquery-ui.js"></script>
    <script>
    $(function() {
      $( "#datefrom" ).datepicker();
      $( "#dateto" ).datepicker();
    });
    </script>

    <!-- FANCYBOX -->
    <!-- Needs JQuery -->
    <!-- Add FancyBox main JS and CSS files -->
    <script type="text/javascript" 
     src="../fancybox/source/jquery.fancybox.js?v=2.1.5"></script>
    <link rel="stylesheet" type="text/css" 
     href="../fancybox/source/jquery.fancybox.css?v=2.1.5" 
     media="screen" />
    <!-- Make FancyBox Ready on page load (adds Classes) -->
    <script type="text/javascript" 
     src="../fancybox-ready.js"></script>


    <!-- MULTIPLE SELECT -->
    <!-- Needs JQuery -->
    <!-- Add MultipleSelect main JS and CSS files -->
    <script type="text/javascript" 
     src="../multiple-select-master/jquery.multiple.select.js"></script>
    <link rel="stylesheet" type="text/css" 
     href="../multiple-select-master/multiple-select.css"/>
    <!-- Ready the function! -->
    <script>
        $('#selectpos').multipleSelect();
    </script> """),

print(""" \n <!-- TO SHOW POS DIVS IN A SELECT LANG OPTIONS-->
    <script>
    $(document).ready(function () {
      $('.defaulthide').hide();
      $('#pos-%s').show();
      $('#corpuslang').change(function () {
        $('.defaulthide').hide();
        $('#pos-'+$(this).val()).show();
      })
    });
    </script>""" % searchlang)

print(u"""<!-- TO SHOW / HIDE BY ID (FOR DIV)-->
    <script type="text/javascript">
     function toggle_visibility(id) {
         var e = document.getElementById(id);
         if(e.style.display == 'block')
            e.style.display = 'none';
            e.style.visibility = 'collapse';
         else
            e.style.display = 'block';
            e.style.visibility = 'visible';
     }
    </script>


    <!-- KICKSTART -->
    <script src="../HTML-KickStart-master/js/kickstart.js"></script> 
    <link rel="stylesheet" href="../HTML-KickStart-master/css/kickstart.css" media="all" />



    <style>
    mark { 
        background-color: #FFA6A6;
    }
    </style>
    <style>
      hr{
        padding: 0px;
        margin: 10px;    
      }
    </style>


    <!-- THIS IS A TRY OUT FOR A COOL CSS TOOLTIP! MUST USE class="tooltip-bottom" data-tooltip="I’m the tooltip data!" -->
    <style>

/**
 * Tooltips!
 */

/* Base styles for the element that has a tooltip */
[data-tooltip],
.tooltip {
  position: relative;
  cursor: pointer;
}

/* Base styles for the entire tooltip */
[data-tooltip]:before,
[data-tooltip]:after,
.tooltip:before,
.tooltip:after {
  position: absolute;
  visibility: hidden;
  -ms-filter: "progid:DXImageTransform.Microsoft.Alpha(Opacity=0)";
  filter: progid:DXImageTransform.Microsoft.Alpha(Opacity=0);
  opacity: 0;
  -webkit-transition: 
	  opacity 0.2s ease-in-out,
		visibility 0.2s ease-in-out,
		-webkit-transform 0.2s cubic-bezier(0.71, 1.7, 0.77, 1.24);
	-moz-transition:    
		opacity 0.2s ease-in-out,
		visibility 0.2s ease-in-out,
		-moz-transform 0.2s cubic-bezier(0.71, 1.7, 0.77, 1.24);
	transition:         
		opacity 0.2s ease-in-out,
		visibility 0.2s ease-in-out,
		transform 0.2s cubic-bezier(0.71, 1.7, 0.77, 1.24);
  -webkit-transform: translate3d(0, 0, 0);
  -moz-transform:    translate3d(0, 0, 0);
  transform:         translate3d(0, 0, 0);
  pointer-events: none;
}

/* Show the entire tooltip on hover and focus */
[data-tooltip]:hover:before,
[data-tooltip]:hover:after,
[data-tooltip]:focus:before,
[data-tooltip]:focus:after,
.tooltip:hover:before,
.tooltip:hover:after,
.tooltip:focus:before,
.tooltip:focus:after {
  visibility: visible;
  -ms-filter: "progid:DXImageTransform.Microsoft.Alpha(Opacity=100)";
  filter: progid:DXImageTransform.Microsoft.Alpha(Opacity=100);
  opacity: 1;
}

/* Base styles for the tooltip's directional arrow */
.tooltip:before,
[data-tooltip]:before {
  z-index: 1001;
  border: 6px solid transparent;
  background: transparent;
  content: "";
}

/* Base styles for the tooltip's content area */
.tooltip:after,
[data-tooltip]:after {
  z-index: 1000;
  padding: 8px;
  width: 160px;
  background-color: #000;
  background-color: hsla(0, 0%, 20%, 0.9);
  color: #fff;
  content: attr(data-tooltip);
  font-size: 13px;
  line-height: 1.2;
}

/* Directions */

/* Top (default) */
[data-tooltip]:before,
[data-tooltip]:after,
.tooltip:before,
.tooltip:after,
.tooltip-top:before,
.tooltip-top:after {
  bottom: 100%;
  left: 50%;
}

[data-tooltip]:before,
.tooltip:before,
.tooltip-top:before {
  margin-left: -6px;
  margin-bottom: -12px;
  border-top-color: #000;
  border-top-color: hsla(0, 0%, 20%, 0.9);
}

/* Horizontally align top/bottom tooltips */
[data-tooltip]:after,
.tooltip:after,
.tooltip-top:after {
  margin-left: -80px;
}

[data-tooltip]:hover:before,
[data-tooltip]:hover:after,
[data-tooltip]:focus:before,
[data-tooltip]:focus:after,
.tooltip:hover:before,
.tooltip:hover:after,
.tooltip:focus:before,
.tooltip:focus:after,
.tooltip-top:hover:before,
.tooltip-top:hover:after,
.tooltip-top:focus:before,
.tooltip-top:focus:after {
  -webkit-transform: translateY(-12px);
  -moz-transform:    translateY(-12px);
  transform:         translateY(-12px); 
}

/* Left */
.tooltip-left:before,
.tooltip-left:after {
  right: 100%;
  bottom: 50%;
  left: auto;
}

.tooltip-left:before {
  margin-left: 0;
  margin-right: -12px;
  margin-bottom: 0;
  border-top-color: transparent;
  border-left-color: #000;
  border-left-color: hsla(0, 0%, 20%, 0.9);
}

.tooltip-left:hover:before,
.tooltip-left:hover:after,
.tooltip-left:focus:before,
.tooltip-left:focus:after {
  -webkit-transform: translateX(-12px);
  -moz-transform:    translateX(-12px);
  transform:         translateX(-12px); 
}

/* Bottom */
.tooltip-bottom:before,
.tooltip-bottom:after {
  top: 100%;
  bottom: auto;
  left: 50%;
}

.tooltip-bottom:before {
  margin-top: -12px;
  margin-bottom: 0;
  border-top-color: transparent;
  border-bottom-color: #000;
  border-bottom-color: hsla(0, 0%, 20%, 0.9);
}

.tooltip-bottom:hover:before,
.tooltip-bottom:hover:after,
.tooltip-bottom:focus:before,
.tooltip-bottom:focus:after {
  -webkit-transform: translateY(12px);
  -moz-transform:    translateY(12px);
  transform:         translateY(12px); 
}

/* Right */
.tooltip-right:before,
.tooltip-right:after {
  bottom: 50%;
  left: 100%;
}

.tooltip-right:before {
  margin-bottom: 0;
  margin-left: -12px;
  border-top-color: transparent;
  border-right-color: #000;
  border-right-color: hsla(0, 0%, 20%, 0.9);
}

.tooltip-right:hover:before,
.tooltip-right:hover:after,
.tooltip-right:focus:before,
.tooltip-right:focus:after {
  -webkit-transform: translateX(12px);
  -moz-transform:    translateX(12px);
  transform:         translateX(12px); 
}

/* Move directional arrows down a bit for left/right tooltips */
.tooltip-left:before,
.tooltip-right:before {
  top: 3px;
}

/* Vertically center tooltip content for left/right tooltips */
.tooltip-left:after,
.tooltip-right:after {
  margin-left: 0;
  margin-bottom: -16px;
}
    </style>
""")

if release_match_style:
    print(""" <style> 
.match{
  color:black;
  font-weight: normal;
  text-decoration:none;
}
</style>""")

print("""<title>%s</title>
 </head>
 <body>
 """ % cginame)

# print sss #TEST
# print "senti_value: " + str(senti) #TEST
# print ss_resource_sent #TEST
# try: #TEST
#     print links #TEST
# except: #TEST
#     print "something happened to the links dict" #TEST

try:
# if 1 > 0: #TEST
    # print escape(showcorpus, quote=True) #TEST
    # print langs2  #TEST
    # print lang2_sids  #TEST
    # print l_sid_fullsent['eng']
    # for lang in l_sid_fullsent.keys():
    #     print lang  
    #     for sid in l_sid_fullsent[lang]:
    #         print str(sid) 
    #         #+ ':' + l_sid_fullsent[lang][sid]
    # print fetch_fullsent #TEST
    # print searchlang #TEST
    # print searchlang in langs2 #TEST
    # print "<p><br><br><br><br><br>" # TEST
    # print "<br><br>" #TEST
    # print "sids: " + sids + "<br><br><br>" #TEST 
    # print sid_cid #TEST

    if len(sids) == 0:
        print("<b>Results for: </b>")
        if searchquery == "":
            print("No query was made.")
        else:
            print(searchquery[:-1])
            
        print("<br>")
        print("<b>No results were found!</b>")

    # ALL THIS SHOULD BE: IF "CONCEPT" OR "C-LEMMA"
    # THEY SHOLD BE FILTERED BY TAG = x OR e
    # HERE WE'RE SHOWING BY EXISTING CONCEPTS
    elif concept_q != ('', False) or clemma_q != ('', False):

        count = 0
        for sid in sid_cid.keys():
            count += len(sid_cid[sid])
        print("<b>%d Results for: </b>" % count)
        print(escape(searchquery[:-1], quote=True))

        print("""<table class="striped tight">""")
        print("""<thead><tr><th>Sid</th><th>Sentence</th></tr></thead>""")

        ##################################################################
        # If there is more than one concept per sid match, we are
        # printing 2 copies of that sentence and showing the different
        # concepts highlighted!
        # We're also excluding by tag! (Don't show if tag = 'x' or 'e')
        ##################################################################
        for sid, cid_dict in sorted(sid_cid.items()):
            for cid, tag in sid_cid[sid].items():

                # sentiment = """<div style="height:0.5em; 
                # background: linear-gradient(to right"""

                print("""<tr>""")
                print("""<td><a class='largefancybox fancybox.iframe' 
                href='%s?corpus=%s&sid=%d&lemma=%s'>%s</a></td>
                """ % (showsentcgi, searchlang, sid, '', sid))

                s_string = ""
                for wid, wid_info in sorted(sid_wid[sid].items()):

                    ########################################################
                    # SENTIMENT
                    ########################################################
                    score = 0
                    MLSentiCon = 0
                    SentiWN = 0
                    if senti == 'comp':
                        for tag in sid_wid_tag[sid][wid]:
                            try:
                                MLSentiCon += (ss_resource_sent[tag]['MLSentiCon']['Positive'] + 
                                               -1*ss_resource_sent[tag]['MLSentiCon']['Negative'])
                            except:
                                # print "failed to add to MLSentiCon" #TEST
                                MLSentiCon += 0
                            try:
                                SentiWN += (ss_resource_sent[tag]['SentiWN']['Positive'] +
                                          -1*ss_resource_sent[tag]['SentiWN']['Negative'])
                            except:
                                # print "failed to add to SentiWN" #TEST
                                SentiWN += 0
                            score += (MLSentiCon + SentiWN)
                            
                        sentitooltip = """ MLSentiCon: %0.3f;  SentiWN: %0.3f; """ % (MLSentiCon, SentiWN)

                    elif senti == ['mlsenticon']:
                        for tag in sid_wid_tag[sid][wid]:
                            try:
                                MLSentiCon += (ss_resource_sent[tag]['MLSentiCon']['Positive'] + 
                                               -1*ss_resource_sent[tag]['MLSentiCon']['Negative'])
                            except:
                                MLSentiCon += 0
                                print("failed to add to MLSentiCon")
                            score += MLSentiCon
                        sentitooltip = """ MLSentiCon: %0.3f; """ % (MLSentiCon,)


                    elif senti == ['sentiwn']:
                        for tag in sid_wid_tag[sid][wid]:
                            try:
                                SentiWN += (ss_resource_sent[tag]['SentiWN']['Positive'] +
                                            -1*ss_resource_sent[tag]['SentiWN']['Negative'])
                            except:
                                SentiWN += 0

                            score += SentiWN

                        sentitooltip = escape(" SentiWN: %0.3f; " % SentiWN, quote=True)

                    else:
                        sentitooltip = ""
                    #########################################################
                    # END OF SENTIMENT (PRINTING BELOW)
                    #########################################################

                    html_word = escape(wid_info[0], quote=True)
                    html_lemma = escape(wid_info[1], quote=True)
                    html_pos = escape(wid_info[2], quote=True)

                    tags_tooltip = ""
                    if len(sid_wid_tag[sid][wid]) > 0:
                        tags_tooltip += "Concept(s):"
                        for tag in sid_wid_tag[sid][wid]:
                            tags_tooltip += """%s """ % (tag)


                    href_word = '<a href="%s?mode=wordview&' % (selfcgi,)
                    href_word += "searchlang=%s&sid=%s&" % (searchlang, sid)
                    href_word += "lemma=%s&postag=%s&" % (html_lemma, html_pos)
                    href_word += "word=%s" % (html_word,)

                    if len(sid_wid_tag[sid][wid]) > 0:
                        for i, tag in enumerate(sid_wid_tag[sid][wid]):
                            href_word += "&wordtag[]=%s" % (tag,)
                            wordcid = sid_wid_cid[sid][wid][i]
                            html_wordclemma = escape(sid_cid_clemma[sid][wordcid],quote=True)
                            href_word += "&wordclemma[]=%s" % (html_wordclemma,)
                    href_word += '"'

                    if  wid in sid_cid_wid[sid][cid]:
                        href_word += """ class='largefancybox 
                                         fancybox.iframe match'>%s</a>""" % (html_word)
                    else:
                        href_word += """ class='largefancybox fancybox.iframe'
                        style='color:black;text-decoration:none;'>%s</a>""" % (html_word)


                    ###############################################################
                    # SENTIMENT STYLE OPTIONS: coulds, boxes, default:underlined
                    ###############################################################
                    if 'sentiwn' in senti or 'mlsenticon' in senti or senti == 'comp':
                        # DISPLAY BY BACKGROUND BOXES
                        style = ""
                        if score > 0:
                            style = """style="background: linear-gradient(to right, 
                            rgba(51, 168, 255, %f), rgba(51, 168, 255, %f)); 
                            border-radius: 7px; padding: 0px 5px 0px 5px;"
                            """ % (0.3+score, 0.3+score)
                        elif score < 0:
                            if score < -0.3:
                                score += 0.3
                            style = """ style="background: linear-gradient(to right, 
                            rgba(255, 105, 4, %f), rgba(255, 105, 4, %f)); 
                            border-radius: 7px; padding: 0px 5px 0px 5px;"
                            """ % (0.4+abs(score), 0.4+abs(score))

                        s_string += """<span class="tooltip-bottom"
                        data-tooltip="Lemma: %s; POS: %s; %s %s"
                        %s >%s</span> """ % (html_lemma, html_pos, 
                                          tags_tooltip, sentitooltip, style, href_word)

                    # IF NO SENTIMENT
                    else:
                        s_string += """<span class="tooltip-bottom" 
                        data-tooltip="Lemma: %s; POS: %s; %s"
                        >%s</span> """ % (html_lemma, html_pos, 
                                                    tags_tooltip, href_word)


                print("""<td>%s""" % s_string)


                ############################ TRIAL
                # sid hold the original sentence id
                # links[lang][original_sid] outputs a set of translation sids
                for lang2 in langs2:
                    print("<p>")

                    for lsid in links[lang2][int(sid)]:

#####HERE!!! IF SENTENCE HAS NO WORDS, THEN IT CANNOT BE PRINTED!
                        if len(l_sid_wid[lang2][lsid].keys()) == 0:
                            # then this means there will be no words to print
                            s_string = l_sid_fullsent[lang2][lsid]
                        else:
                            s_string = ""


                        for wid, wid_info in l_sid_wid[lang2][lsid].items():


                            ########################################################
                            # SENTIMENT
                            ########################################################
                            score = 0
                            MLSentiCon = 0
                            SentiWN = 0
                            if senti == 'comp':
                                for tag in l_sid_wid_tag[lang2][sid][wid]:
                                    try:
                                        MLSentiCon += (ss_resource_sent[tag]['MLSentiCon']['Positive'] + 
                                                       -1*ss_resource_sent[tag]['MLSentiCon']['Negative'])
                                    except:
                                        # print "failed to add to MLSentiCon" #TEST
                                        MLSentiCon += 0
                                    try:
                                        SentiWN += (ss_resource_sent[tag]['SentiWN']['Positive'] +
                                                  -1*ss_resource_sent[tag]['SentiWN']['Negative'])
                                    except:
                                        # print "failed to add to SentiWN" #TEST
                                        SentiWN += 0
                                    score += (MLSentiCon + SentiWN)

                                sentitooltip = """ MLSentiCon: %0.3f;  SentiWN: %0.3f; """ % (MLSentiCon, SentiWN)

                            elif senti == ['mlsenticon']:
                                for tag in l_sid_wid_tag[lang2][sid][wid]:
                                    try:
                                        MLSentiCon += (ss_resource_sent[tag]['MLSentiCon']['Positive'] + 
                                                       -1*ss_resource_sent[tag]['MLSentiCon']['Negative'])
                                    except:
                                        MLSentiCon += 0
                                        print("failed to add to MLSentiCon")
                                    score += MLSentiCon
                                sentitooltip = """ MLSentiCon: %0.3f; """ % (MLSentiCon,)


                            elif senti == ['sentiwn']:
                                for tag in l_sid_wid_tag[lang2][sid][wid]:
                                    try:
                                        SentiWN += (ss_resource_sent[tag]['SentiWN']['Positive'] +
                                                    -1*ss_resource_sent[tag]['SentiWN']['Negative'])
                                    except:
                                        SentiWN += 0

                                    score += SentiWN

                                sentitooltip = escape(" SentiWN: %0.3f; " % SentiWN, quote=True)

                            else:
                                sentitooltip = ""

                            #########################################################
                            # END OF SENTIMENT (PRINTING BELOW)
                            #########################################################



                            html_word = escape(wid_info[0], quote=True)
                            html_lemma = escape(wid_info[1], quote=True)
                            html_pos = escape(wid_info[2], quote=True)

                            tags_tooltip = ""
                            if len(l_sid_wid_tag[lang2][lsid][wid]) > 0:
                                tags_tooltip += "Concept(s):"
                                for tag in l_sid_wid_tag[lang2][lsid][wid]:
                                    tags_tooltip += """%s """ % (tag)


                            href_word = """<a href="%s?mode=wordview&""" % (selfcgi,)
                            href_word += """searchlang=%s&sid=%s&""" % (lang2,sid)
                            href_word += """lemma=%s&postag=%s&""" % (html_lemma,
                                                                       html_pos)
                            href_word += """word=%s""" % (html_word,)

                            if len(l_sid_wid_tag[lang2][lsid][wid]) > 0:
                                for tag in l_sid_wid_tag[lang2][lsid][wid]:
                                    href_word += """&wordtag[]=%s""" % (tag,)
                            href_word += '"'

                            href_word += """ class='largefancybox 
                                                    fancybox.iframe'
                                style='color:black;text-decoration:none;'
                                >%s</a>""" % (html_word)


                            ###############################################################
                            # SENTIMENT STYLE OPTIONS: coulds, boxes, default:underlined
                            ###############################################################
                            if 'sentiwn' in senti or 'mlsenticon' in senti or senti == 'comp':

                                # DISPLAY BY BACKGROUND BOXES
                                style = ""
                                if score > 0:
                                    style = """style="background: linear-gradient(to right, 
                                    rgba(51, 168, 255, %f), rgba(51, 168, 255, %f)); border-radius: 7px; padding: 0px 5px 0px 5px;"
                                    """ % (0.3+score, 0.3+score)
                                elif score < 0:
                                    if score < -0.3:
                                        score += 0.3
                                    style = """ style="background: linear-gradient(to right, 
                                    rgba(255, 105, 4, %f), rgba(255, 105, 4, %f)); border-radius: 7px; padding: 0px 5px 0px 5px;"
                                    """ % (0.4+abs(score), 0.4+abs(score))

                                s_string += """<span class="tooltip-bottom" 
                                data-tooltip="Lemma: %s; POS: %s; %s %s"
                                %s >%s</span> """ % (html_lemma, html_pos, 
                                                  tags_tooltip, sentitooltip, style, href_word)

                            # IF NO SENTIMENT
                            else:

                                s_string += """<span class="tooltip-bottom" 
                                data-tooltip="Lemma: %s; POS: %s; %s"
                                >%s</span> """ % (html_lemma, html_pos, 
                                                    tags_tooltip, href_word)

                        print("%s" % s_string)

                        print("""<span title='%s'><sub>(%s)</sub>
                                 </span>""" % (lsid,lang2))
                    print("</p>")
                    ################ END TRIAL



                # THIS PRINTS THE UGLY LINE
                # sentiment += """);"></div>"""
                # if 'sentiwn' in senti or 'mlsenticon' in senti or senti == 'comp':
                #     print sentiment

                print("""</td>""")
                print("""</tr>""")
        print("</table>")

    #############################################
    # WORD-BASED SEARCH (NO CONCEPT RESTRICTION)
    #############################################
    elif len(sid_wid.keys()) > 0:
        count = 0
        for sid in sid_wid.keys():
            for wid, wid_info in sid_wid[sid].items():
                if wid in sid_matched_wid[sid]:
                    count += 1
        print("<b>%d Results for: </b>" % count)
        print(searchquery[:-1])


        print("""<table class="striped tight">""")
        print("""<thead><tr><th>Sid</th><th>Sentence</th></tr></thead>""")

        for sid in sorted(sid_wid.keys()):
            print("""<tr>""")
            # print """<td>%s</td>""" % sid

            print("""<td><a class='largefancybox fancybox.iframe' 
            href='%s?corpus=%s&sid=%d&lemma=%s'>%s</a></td>
            """ % (showsentcgi, searchlang, sid, '', sid))

            # print """<td>%s</td>""" % sid_wid[sid].items() #TEST

            s_string = ""
            for wid, wid_info in sid_wid[sid].items():

                ########################################################
                # SENTIMENT
                ########################################################
                score = 0
                MLSentiCon = 0
                SentiWN = 0
                if senti == 'comp':
                    for tag in sid_wid_tag[sid][wid]:
                        try:
                            MLSentiCon += (ss_resource_sent[tag]['MLSentiCon']['Positive'] + 
                                           -1*ss_resource_sent[tag]['MLSentiCon']['Negative'])
                        except:
                            # print "failed to add to MLSentiCon" #TEST
                            MLSentiCon += 0
                        try:
                            SentiWN += (ss_resource_sent[tag]['SentiWN']['Positive'] +
                                      -1*ss_resource_sent[tag]['SentiWN']['Negative'])
                        except:
                            # print "failed to add to SentiWN" #TEST
                            SentiWN += 0
                        score += (MLSentiCon + SentiWN)

                    sentitooltip = """ MLSentiCon: %0.3f;  SentiWN: %0.3f; """ % (MLSentiCon, SentiWN)

                elif senti == ['mlsenticon']:
                    for tag in sid_wid_tag[sid][wid]:
                        try:
                            MLSentiCon += (ss_resource_sent[tag]['MLSentiCon']['Positive'] + 
                                           -1*ss_resource_sent[tag]['MLSentiCon']['Negative'])
                        except:
                            MLSentiCon += 0
                            print("failed to add to MLSentiCon")
                        score += MLSentiCon
                    sentitooltip = """ MLSentiCon: %0.3f; """ % (MLSentiCon,)


                elif senti == ['sentiwn']:
                    for tag in sid_wid_tag[sid][wid]:
                        try:
                            SentiWN += (ss_resource_sent[tag]['SentiWN']['Positive'] +
                                        -1*ss_resource_sent[tag]['SentiWN']['Negative'])
                        except:
                            SentiWN += 0

                        score += SentiWN

                    sentitooltip = escape(" SentiWN: %0.3f; " % SentiWN, quote=True)

                else:
                    sentitooltip = ""
                #########################################################
                # END OF SENTIMENT (PRINTING BELOW)
                #########################################################


                html_word = escape(wid_info[0], quote=True)
                html_lemma = escape(wid_info[1], quote=True)
                html_pos = escape(wid_info[2], quote=True)

                tags_tooltip = ""
                if len(sid_wid_tag[sid][wid]) > 0:
                    tags_tooltip += "Concept(s):"
                    for tag in sid_wid_tag[sid][wid]:
                        tags_tooltip += """%s """ % (tag)


                href_word = """<a href="%s?mode=wordview&""" % (selfcgi,)
                href_word += """searchlang=%s&sid=%s&""" % (searchlang,sid)
                href_word += """lemma=%s&postag=%s&""" % (html_lemma,
                                                           html_pos)
                href_word += """word=%s""" % (html_word,)
                if len(sid_wid_tag[sid][wid]) > 0:
                    for tag in sid_wid_tag[sid][wid]:
                        href_word += """&wordtag[]=%s""" % (tag,)
                href_word += '"'


                # sid_matched_wid[sid] has a list of wid that should be matches!
                # if highlight:
                if wid in sid_matched_wid[sid]:
                    href_word += """ class='largefancybox fancybox.iframe 
                    match'>%s</a>""" % (html_word)
                else:
                    href_word += """ class='largefancybox fancybox.iframe'
                    style='color:black;text-decoration:none;'
                    >%s</a>""" % (html_word)


                ###############################################################
                # SENTIMENT STYLE OPTIONS: coulds, boxes, default:underlined
                ###############################################################
                if 'sentiwn' in senti or 'mlsenticon' in senti or senti == 'comp':

                    # DISPLAY BY BACKGROUND BOXES
                    style = ""
                    if score > 0:
                        style = """style="background: linear-gradient(to right, 
                        rgba(51, 168, 255, %f), rgba(51, 168, 255, %f)); border-radius: 7px; padding: 0px 5px 0px 5px;"
                        """ % (0.3+score, 0.3+score)
                    elif score < 0:
                        if score < -0.3:
                            score += 0.3
                        style = """ style="background: linear-gradient(to right, 
                        rgba(255, 105, 4, %f), rgba(255, 105, 4, %f));  border-radius: 7px; padding: 0px 5px 0px 5px;"
                        """ % (0.4+abs(score), 0.4+abs(score))

                    s_string += """<span class="tooltip-bottom" 
                    data-tooltip="Lemma: %s; POS: %s; %s %s"
                    %s >%s</span> """ % (html_lemma, html_pos, 
                                      tags_tooltip, sentitooltip, style, href_word)

                # IF NO SENTIMENT
                else:
                    s_string += """<span class="tooltip-bottom" 
                    data-tooltip="Lemma: %s; POS: %s; %s">%s</span> """ % (html_lemma, html_pos, 
                                         tags_tooltip, href_word)


            print("""<td>%s""" % s_string)



            ############################ TRIAL
            # sid hold the original sentence id
            # links[lang][original_sid] outputs a set of translation sids
            for lang2 in langs2:

                errlog.write("When printing, lang2 = '%s'\n" %(lang2)) #LOG

                print("<p>")

                #BUG!!! links.keys() only has 1 lang, even though langs2 has 2
                errlog.write("lsid list = '%s'\n" % '|'.join(links.keys())) #LOG
                for lsid in links[lang2][int(sid)]:
                    errlog.write("Found a lsid = '%d'\n" %(lsid)) #LOG

                    if len(l_sid_wid[lang2][lsid].keys()) == 0:
                        # then this means there will be no words to print
                        s_string = l_sid_fullsent[lang2][lsid]
                    else:
                        s_string = ""

                    for wid, wid_info in l_sid_wid[lang2][lsid].items():

                        ########################################################
                        # SENTIMENT
                        ########################################################
                        score = 0
                        MLSentiCon = 0
                        SentiWN = 0
                        if senti == 'comp':
                            for tag in l_sid_wid_tag[lang2][sid][wid]:
                                try:
                                    MLSentiCon += (ss_resource_sent[tag]['MLSentiCon']['Positive'] + 
                                                   -1*ss_resource_sent[tag]['MLSentiCon']['Negative'])
                                except:
                                    # print "failed to add to MLSentiCon" #TEST
                                    MLSentiCon += 0
                                try:
                                    SentiWN += (ss_resource_sent[tag]['SentiWN']['Positive'] +
                                              -1*ss_resource_sent[tag]['SentiWN']['Negative'])
                                except:
                                    # print "failed to add to SentiWN" #TEST
                                    SentiWN += 0
                                score += (MLSentiCon + SentiWN)

                            sentitooltip = """ MLSentiCon: %0.3f;  SentiWN: %0.3f; """ % (MLSentiCon, SentiWN)

                        elif senti == ['mlsenticon']:
                            for tag in l_sid_wid_tag[lang2][sid][wid]:
                                try:
                                    MLSentiCon += (ss_resource_sent[tag]['MLSentiCon']['Positive'] + 
                                                   -1*ss_resource_sent[tag]['MLSentiCon']['Negative'])
                                except:
                                    MLSentiCon += 0
                                    print("failed to add to MLSentiCon")
                                score += MLSentiCon
                            sentitooltip = """ MLSentiCon: %0.3f; """ % (MLSentiCon,)


                        elif senti == ['sentiwn']:
                            for tag in l_sid_wid_tag[lang2][sid][wid]:
                                try:
                                    SentiWN += (ss_resource_sent[tag]['SentiWN']['Positive'] +
                                                -1*ss_resource_sent[tag]['SentiWN']['Negative'])
                                except:
                                    SentiWN += 0

                                score += SentiWN

                            sentitooltip = escape(" SentiWN: %0.3f; " % SentiWN, quote=True)

                        else:
                            sentitooltip = ""

                        #########################################################
                        # END OF SENTIMENT (PRINTING BELOW)
                        #########################################################

                        html_word = escape(wid_info[0], quote=True)
                        html_lemma = escape(wid_info[1], quote=True)
                        html_pos = escape(wid_info[2], quote=True)

                        tags_tooltip = ""
                        if len(l_sid_wid_tag[lang2][lsid][wid]) > 0:
                            tags_tooltip += "Concept(s):"
                            for tag in l_sid_wid_tag[lang2][lsid][wid]:
                                tags_tooltip += """%s """ % (tag)


                        href_word = """<a href="%s?mode=wordview&""" % (selfcgi,)
                        href_word += """searchlang=%s&sid=%s&""" % (lang2,sid)
                        href_word += """lemma=%s&postag=%s&""" % (html_lemma,
                                                                   html_pos)
                        href_word += """word=%s""" % (html_word,)

                        if len(l_sid_wid_tag[lang2][lsid][wid]) > 0:
                            for tag in l_sid_wid_tag[lang2][lsid][wid]:
                                href_word += """&wordtag[]=%s""" % (tag,)
                        href_word += '"'

                        href_word += """ class='largefancybox fancybox.iframe'
                            style='color:black;text-decoration:none;'
                            > %s </a>""" % (html_word)


                        ###############################################################
                        # SENTIMENT STYLE OPTIONS: coulds, boxes, default:underlined
                        ###############################################################
                        if 'sentiwn' in senti or 'mlsenticon' in senti or senti == 'comp':
                            # DISPLAY BY BACKGROUND BOXES
                            style = ""
                            if score > 0:
                                style = """style="background: linear-gradient(to right, 
                                rgba(51, 168, 255, %f), rgba(51, 168, 255, %f)); border-radius: 7px; padding: 0px 5px 0px 5px;"
                                """ % (0.3+score, 0.3+score)
                            elif score < 0:
                                if score < -0.3:
                                    score += 0.3
                                style = """ style="background: linear-gradient(to right, 
                                rgba(255, 105, 4, %f), rgba(255, 105, 4, %f));  border-radius: 7px; padding: 0px 5px 0px 5px;"
                                """ % (0.4+abs(score), 0.4+abs(score))

                            s_string += """<span class="tooltip-bottom" 
                            data-tooltip="Lemma: %s; POS: %s; %s %s"
                            %s >%s</span> """ % (html_lemma, html_pos, 
                                              tags_tooltip, sentitooltip, style, href_word)

                        # IF NO SENTIMENT
                        else:
                            s_string += """<span class="tooltip-bottom" 
                            data-tooltip="Lemma: %s&#10; POS: %s &#10; %s %s">%s</span> """ % (html_lemma, html_pos, 
                                                 tags_tooltip, sentitooltip,href_word)


                    print("%s" % s_string)

                    print("""<span title='%s'><sub>(%s)</sub>
                             </span>""" % (lsid,lang2))

                    errlog.write("langs2:%s lsid=%d\n" %(lang2, lsid)) #LOG


                print("</p>")


            print("""</td>""")
            print("""</tr>""")

        print("</table>")

    else:
        print("Nothing found!")

except:
    print("<br>")
    print("<h6> Welcome! Please query the database!</h6>")


##########################################
# SEARCH FORM!
###########################################
print("""<hr>""")
# START FORM
print("""<form action="" id="newquery" method="post">""")

# SEARCH LANGUAGE
print("""<p style="line-height: 35px"><nobr>
          Language: <select name="searchlang" id="corpuslang" style="font-size:80%" >""")
for l in corpuslangs:
    if l == searchlang:
        print("""<option value ='%s' selected>%s</option>""" % (l, omwlang.trans(l, 'eng')))
    else:
        print("""<option value ='%s'>%s</option>""" % (l, omwlang.trans(l, 'eng')))
print("""</select>""")

# MULTISELECT FOR LANGS2
print("""<select id="langs2" name="langs2" multiple="multiple">""")
for l in corpuslangs:
    if l in langs2:
        print("""<option value='%s' selected>%s</option>
              """ % (l, omwlang.trans(l, 'eng')))
    else:
        print("""<option value='%s'>%s</option>
              """ % (l, omwlang.trans(l, 'eng')))
print("""</select>
        <script>
            $('#langs2').multipleSelect({
                placeholder: "Align with: (langs)",
                width: "13em"
            });
        </script>""")

print("""&nbsp;&nbsp;</nobr> """)
# TAG
print("""<nobr>Concept:""")
print("""<input name="concept" id="idconcept" size="9" pattern="None|x|e|w|loc|org|per|dat|oth|[<>=~!]?[0-9]{8}-[avnrxz]" title = "xxxxxxxx-a/v/n/r/x/z |x|e|w|loc|org|per|dat|oth" style="font-size:80%%" placeholder="%s"/>&nbsp;&nbsp;</nobr>""" % ph_concept)

# CLEMMA
print("""<nobr>C-lemma:""")
print("""<input name="clemma" size="12" title="Please Insert a Concept Lemma"  
         style="font-size:80%%" placeholder="%s"/>&nbsp;&nbsp;</nobr>""" % ph_clemma)

# WORD
print("""<nobr>Word:""")
print("""<input name="word" size="12" title="Please Insert a Word"  
         style="font-size:80%%" placeholder="%s"/>&nbsp;&nbsp;</nobr>""" % ph_word)

# LEMMA
print("""<nobr>Lemma:""")
print("""<input name="lemma" size="12" title="Please Insert a Lemma"  style="font-size:80%%" placeholder="%s"/></nobr>""" % ph_lemma)


# SID_FROM & SID_TO
print("""<nobr>SID (from):""")
if sid_from != 0:
    print("""<input name="sid_from" size="12" title="Minimum SID Allowed" 
    style="font-size:80%%" value="%s" />""" % sid_from)
else:
    print("""<input name="sid_from" size="12" title = "Minimum SID Allowed" 
    style="font-size:80%"/>""")
print("""SID (to):""")
if sid_to != 1000000:    
    print("""<input name="sid_to" size="12" title="Maximum SID Allowed" 
    style="font-size:80%%" value="%d"/>&nbsp;&nbsp;</nobr>""" % sid_to)
else:
    print("""<input name="sid_to" size="12" title="Maximum SID Allowed" 
    style="font-size:80%"/>&nbsp;&nbsp;</nobr>""")


# SENTIMENT
print("""<nobr>Sentiment:""")
if senti == 'comp':
    print("""<input type="checkbox" name="senti[]" value="mlsenticon" 
              id="senticheck" checked/>
             <label for="senticheck1" class="inline">MLSentiCon</label> 
             <input type="checkbox" name="senti[]" value="sentiwn" 
              id="senticheck" checked/>
             <label for="senticheck2" class="inline">SentiWN</label>&nbsp;&nbsp;</nobr>""")
elif senti == ['mlsenticon']:
    print("""<input type="checkbox" name="senti[]" value="mlsenticon" 
              id="senticheck" checked/>
             <label for="senticheck1" class="inline">MLSentiCon</label> 
             <input type="checkbox" name="senti[]" value="sentiwn" 
              id="senticheck" />
             <label for="senticheck2" class="inline">SentiWN</label>&nbsp;&nbsp;</nobr>""")
elif senti == ['sentiwn']:
    print("""<input type="checkbox" name="senti[]" value="mlsenticon" 
              id="senticheck" />
             <label for="senticheck1" class="inline">MLSentiCon</label> 
             <input type="checkbox" name="senti[]" value="sentiwn" 
              id="senticheck" checked/>
             <label for="senticheck2" class="inline">SentiWN</label>&nbsp;&nbsp;</nobr>""")
else:
    print("""<input type="checkbox" name="senti[]" value="mlsenticon" id="senticheck" />
         <label for="senticheck1" class="inline">MLSentiCon</label> 
         <input type="checkbox" name="senti[]" value="sentiwn" id="senticheck" />
         <label for="senticheck2" class="inline">SentiWN</label>&nbsp;&nbsp;</nobr>""")



# SHOWS POS SELECT AND HELP DIV PER LANGUAGE (HIDDEN/TRIGGERED BY
# SELECTING A LANGUAGE ABOVE)
for l in corpuslangs:
    print("""<nobr><span id="pos-%s" class="defaulthide">POS:""" % l)
    print("""<select id="selectpos-%s" name="selectpos-%s" 
              multiple="multiple">""" % (l, l))

    maxlenght = 7 # used to figure out the width of the select
    for p in sorted(pos_tags[l].keys()):
        if len(p) > maxlenght:
            maxlenght = len(p)

        if p in pos_form[searchlang]:
            print("""<option value ='%s' selected>%s</option>
              """ % (escape(p, quote=True), escape(p, quote=True)))
        else:
            print("""<option value ='%s'>%s</option>
              """ % (escape(p, quote=True), escape(p, quote=True)))

    print("""</select>
        <script>
            $('#selectpos-%s').multipleSelect({
                placeholder: "Select POS",
                width: "%dem"
            });
        </script>""" % (l, maxlenght+2))

    print("""<a class='fancybox' href='#postags-%s' 
          style='color:black;text-decoration:none;'><!--
          --><sup>?</sup></a></span></nobr>""" % l)

# SEARCH LIMITS
print("""<nobr>Limit: <select name="limit" style="font-size:80%">""")
for value in ['10','25','50','100','all']:
    if value == limit:
        print("""<option value ='%s' selected>%s</option>""" % (value, value))
    else:
        print("""<option value ='%s'>%s</option>""" % (value, value))
print("""</select>&nbsp;&nbsp;</nobr>""")


# SUBMIT BUTTON
print("""<button class="small"> <a href="javascript:{}"
         onclick="document.getElementById('newquery').submit(); 
         return false;"><span title="Search">
         <span style="color: #4D99E0;"><i class='icon-search'></i>
         </span></span></a></button></p>""")
print("""</form>""")




####################################
# FOOTER
####################################
print("""<hr><a href='%s'>More detail about the %s (%s)</a>
      """ % (url, cginame, ver))
print('<p>Developers:')
print(' <a href="">Luís Morgado da Costa</a> ')
print('&lt;<a href="mailto:lmorgado.dacosta@gmail.com">lmorgado.dacosta@gmail.com</a>&gt;')
print('; ')
print(' <a href="http://www3.ntu.edu.sg/home/fcbond/">Francis Bond</a> ')
print('&lt;<a href="mailto:bond@ieee.org">bond@ieee.org</a>&gt;')


####################################
# INVISIBLE DIV FOR POS TAGS HELPER
####################################
for l in corpuslangs:
    print("""<div id="postags-%s" style="display: none;">
                <h3>%s's POS Tags</h3>""" % (l, omwlang.trans(l, 'eng')))
    for p, info in sorted(pos_tags[l].items()):
        print( """<b>%s:</b> <span title='%s'> %s</span>
                  <br>""" % (p, info['eng_def'], info['def']))
    print("""</div>""")

print("  </body>")
print("</html>")

errlog.close()


######################################################################
