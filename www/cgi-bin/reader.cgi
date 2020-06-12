#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi, urllib, http.cookies, os
import cgitb; cgitb.enable()  # for troubleshooting
import re, sqlite3, collections
from collections import defaultdict as dd
from ntumc_util import *
from ntumc_webkit import *
from lang_data_toolkit import *

# Fixes encoding issues when reading cookies from os.environ
import os, sys
from importlib import reload
sys.getfilesystemencoding = lambda: 'utf-8'
reload(os)

################################################################################
# CGI FIELD STORAGE & CONSTANTS
################################################################################
wndb = "../db/wn-ntumc.db"

form = cgi.FieldStorage()
docName = form.getfirst("docName")
log_message = form.getfirst("log_message", "")

fl_docID = 0
tl_docID = 0


################################################################################
# FIND AND CONNECT TO THE DATABASES
################################################################################

# TESTING NEW DB
corpusdb = form.getfirst('corpusdb', 'eng') # corpus + version (e.g. engA)
corpusdb2 = form.getfirst('corpusdb2', 'cmn')

(dbexists, dbversion, dbmaster, dblang, dbpath) = check_corpusdb(corpusdb)
(db2exists, db2version, db2master, db2lang, db2path) = check_corpusdb(corpusdb2)

if dbexists and db2exists:
    l1 = dblang
    l2 = db2lang

else:
    l1 = 'eng'
    l2 = 'cmn'



fl = l1
tl = l2

if l1 != None and l2 != None and os.path.isfile('../db/'+l1+'-'+l2+'.db'):
    db = '../db/'+l1+'-'+l2+'.db'
    fldb = '../db/'+l1+'.db'
    tldb = '../db/'+l2+'.db'

elif l1 != None and l2 != None and os.path.isfile('../db/'+l2+'-'+l1+'.db'):
    db = '../db/'+l2+'-'+l1+'.db'
    tldb = '../db/'+l1+'.db'
    fldb = '../db/'+l2+'.db'
    fl = l2
    tl = l1

else:
    db = None
    fldb = None
    tldb = None
    fl = None
    tl = None


if db != None:
    conn = sqlite3.connect(db)
    curs = conn.cursor()
    conn_fl = sqlite3.connect(fldb)
    curs_fl = conn_fl.cursor()
    conn_tl = sqlite3.connect(tldb)
    curs_tl = conn_tl.cursor()

################################################################################
# FETCH INFORMATION ABOUT THE DOCUMENTS IN THE DB
################################################################################
docs = []
engconn = sqlite3.connect("../db/eng.db")
engc = engconn.cursor()
engc.execute("""SELECT doc, title, docid FROM doc""")
rows = engc.fetchall()
for r in rows:
    (doc, title, docid) = (r[0],r[1],r[2])
    docs.append((doc, title, docid))
################################################################################

################################################################################
sents = dd(lambda: dd(str))
sents_links = dd(lambda: dd(set))
spid = dd(lambda: dd(str))
if db != None:
    ############################################################################
    # FETCH THE DOC_ID FROM THE DOC_NAME
    fetch_docID = """SELECT docid FROM doc WHERE doc=? """
    curs_fl.execute(fetch_docID, [docName])
    rows = curs_fl.fetchall()
    for r in rows:
        fl_docID = r[0]
    curs_tl.execute(fetch_docID)
    rows = curs_tl.fetchall()
    for r in rows:
        tl_docID = r[0]
    ############################################################################

    ############################################################################
    fetch_sents_fl = """SELECT sid, pid, sent FROM sent 
                        WHERE docID = ? """
    fetch_sents_tl = """SELECT sid, pid, sent FROM sent 
                        WHERE docID = ? """

    curs_fl.execute(fetch_sents_fl, [int(fl_docID)])
    rows = curs_fl.fetchall()
    for r in rows:
        (sid, pid, sent) = (r[0],r[1], r[2])
        sents[fl][sid] = sent 
        spid[fl][sid] = pid

    curs_tl.execute(fetch_sents_tl, [int(fl_docID)])
    rows = curs_tl.fetchall()
    for r in rows:
        (sid, pid, sent) = (r[0],r[1], r[2])
        sents[tl][sid] = sent
        spid[tl][sid] = pid
    ############################################################################

    ############################################################################
    fl_sids = placeholders_for(sents[fl].keys())
    fetch_all = """SELECT slid, fsid, tsid
                   FROM slink
                   WHERE fsid in (%s) """ % fl_sids
    curs.execute(fetch_all, list(sents[fl].keys()))
    rows = curs.fetchall()
    for r in rows:
        (slid, fsid, tsid) = (r[0],r[1],r[2])

        sents_links[fl][fsid].add(tsid)
        sents_links[tl][tsid].add(fsid)
    ############################################################################

################################################################################




gridmode = form.getfirst("gridmode", "ntumc-noedit")

# lang = form.getfirst("lang", "cmn")
# corpus = form.getfirst("corpus", "cmn")

# tsid = int(form.getfirst("sid", 10000)) #default to sentence 1000
# twid = int(form.getfirst("wid", 0)) #default to first word

# window = int(form.getfirst("window", 4)) #default context of four sentences
# if window > 200:
#     window = 200

# textSize = form.getfirst("textSize", '120%')

################################################################################


################################################################################
# MASTER COOKIE
################################################################################
# if 'HTTP_COOKIE' in os.environ:
#     C = http.cookies.SimpleCookie(os.environ['HTTP_COOKIE'])
# else:
#     C = http.cookies.SimpleCookie()

# # FETCH USERID/PW INFO
# if "UserID" in C:
#     userID = C["UserID"].value
#     hashed_pw = C["Password"].value
# else:
#     userID = "guest"
#     hashed_pw = "guest"
################################################################################




################################################################################
# HTML FUNCTIONAL BLOCKS
################################################################################
def header():

    if dbexists:
        tagsenti_cgi = "tag-senti.cgi?corpusdb=" + dbexists + "&sid="
        fixcorpus_cgi = "fix-corpus.cgi?corpusdb=" + dbexists + "&sid_edit="
        tagword_cgi = "tag-word.cgi?corpus=" + dbexists + "&lang=" + dblang + "&sid="
    else:
        tagsenti_cgi = ""
        fixcorpus_cgi = ""
        tagword_cgi = ""



    html = ''
    html += """<!DOCTYPE html>
    <head>
    <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
    <link href="../common.css" rel="stylesheet" type="text/css">
    <link href="../tag-wn.css" rel="stylesheet" type="text/css">
    <script src="../tag-wn.js" language="javascript"></script>
    <script src='../jquery.js' language='javascript'></script>

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

    <!-- KICKSTART -->
    <script src="../HTML-KickStart-master/js/kickstart.js"></script>
    <link rel="stylesheet" href="../HTML-KickStart-master/css/kickstart.css" 
     media="all" /> 

    <title>NTUMC Reader</title>

    <style>
      hr{
        padding: 0px;
        margin: 5px;    
      }
    </style>
    """


    html += """
    <script>  // THIS SNIPPET IS USED TO CHECK KEYS PRESSED
    window.addEventListener("keydown", keysPressed, false);
    window.addEventListener("keyup", keysReleased, false);
    var keys = [];
    function keysPressed(e) {
      // store an entry for every key pressed
      keys[e.keyCode] = true;
    }
    function keysReleased(e) {
      // mark keys that were released
      keys[e.keyCode] = false;
    }


    function opensid(sid, lang, db) {
      if (keys[67]) { // C key (for Chunk Tagger)
          keys = [];
          window.open("%s" + sid, "_blank");
          //alert("C key was pressed!" + sid);
      } 

      else if (keys[83]) { // S key (for Sentence Tagger) 
          keys = [];
          window.open("%s" + sid, "_blank");
           //alert("S key pressed!" + sid); 
        } 
      else if (keys[90]) { // Z key (for FixCorpus)
          keys = [];
          window.open("%s" + sid, "_blank");
     } 

      else {
         // alert("No key was pressed!")
    }

  }
  </script>

""" % (tagsenti_cgi,tagword_cgi,fixcorpus_cgi)

    html += """</head><body>"""



    return html



################################################################################
# SEARCH FORM
################################################################################
def search_form():
    html  = """<form id="goto" action="" method="post" 
                style="display:inline-block">"""
    html += """<b>DB1:</b>"""
    html += """<select id="corpusdb1" name="corpusdb1">"""


    corpusdb_in = False
    for db in all_corpusdb():
        if db[0] == corpusdb:
            html += "<option value ='%s' selected>%s</option>" % db
            corpusdb_in = True
        else:
            html += "<option value ='%s'>%s</option>" % db
    # This allows linking to a specific (not listed) CorpusDB
    if corpusdb_in == False:
        html += "<option value ='%s' selected>%s</option>" % (corpusdb,corpusdb)
    html += """</select> """

    html += """<b> DB2:</b>"""
    html += """<select id="corpusdb2" name="corpusdb2">"""

    corpusdb2_in = False
    for db in all_corpusdb():
        if db[0] == corpusdb2:
            html += "<option value ='%s' selected>%s</option>" % db
            corpusdb2_in = True
        else:
            html += "<option value ='%s'>%s</option>" % db
    # This allows linking to a specific (not listed) CorpusDB
    if corpusdb2_in == False:
        html += "<option value ='%s' selected>%s</option>" % (corpusdb2,corpusdb2)
    html += """</select>"""
    html += """<select name="docName">"""
    html += """<option value ='' selected>Select Document</option>"""

    next_docName = docs[0][0]
    for current_doc_i, d in enumerate(docs):
        if d[0] == docName:
            try:
                next_docName = docs[current_doc_i + 1][0]
            except: # there is no 'next'
                next_docName = docs[current_doc_i][0]
            html += "<option value ='%s' selected>%s (%d)</option>""" % d
        else:
            html += "<option value ='%s'>%s (%d)</option>""" % d

    html += """</select>"""
    html += """<span><button class="small"><a href="javascript:{}"
          onclick="document.getElementById('goto').submit();return false;"
          style="text-decoration:none">
         <span style="color: #4D99E0;font-size:15px;">Go</span></a>
         </button></span>"""
    html += """</form>"""


    # NEXT BUTTON
    html += """<form id="next_doc" action="" method="post" 
      style="display:inline-block">"""
    html += """<input type="hidden" name="l1" value="%s"/>""" % l1
    html += """<input type="hidden" name="l2" value="%s"/>""" % l2
    html += """<input type="hidden" name="docName" value="%s"/>""" % next_docName
    html += """<span><button class="small"><a href="javascript:{}"
          onclick="document.getElementById('next_doc').submit();return false;"
          style="text-decoration:none">
         <span style="color: #4D99E0;font-size:15px;">Next</span></a>
         </button></span>"""
    html += """</form>"""
    html += "<hr style='margin-top:10px;margin-bottom:10px;'/>"

    return html


def show_doc():
    html = ""

    pid = 0
    for sid in sorted(sents[l1].keys()):

        trans = ''
        for i in sents_links[l1][sid]:
            trans += sents[l2][i] + ' '


        if spid[l1][sid] == "-1":
            style_begin = "<h4>"
            style_end = "</h4>"

        elif spid[l1][sid] == "-3": 
            style_begin = "<h5>"
            style_end = "</h5>"

        elif spid[l1][sid] == "-5": 
            style_begin = "<h6>"
            style_end = "</h6>"
            
        elif pid != spid[l1][sid]:
            style_begin = "</p><p>"
            style_end = ""
            pid = spid[l1][sid]

        else:
            style_begin = ""
            style_end = ""
            
            
        # html += str(spid[l1][sid]) #TEST
        html += style_begin
        html += """<a  onclick="return opensid('%s', '%s', '%s');"
                    style='color:black;text-decoration:none;'
                    title='%s'> 
                """ % (sid, l1, l1, cgi.escape(trans))
        html += cgi.escape(sents[l1][sid])
        html += "</a>"
        html += style_end


    return html



########## HTML
print(u"""Content-type: text/html; charset=utf-8\n\n""")
print(header())
print(search_form())
print(show_doc())
print("  </body>")
print("</html>")
