#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi, urllib
# import cgitb; cgitb.enable()  # for troubleshooting
import sqlite3
import os, http.cookies
import sys
from ntumc_util import *
from ntumc_webkit import *

form = cgi.FieldStorage()
lang = form.getfirst("lang")
corpus = form.getfirst("corpus")

cgi_mode = form.getfirst("cgi_mode")

################################################################################
# MASTER COOKIE
################################################################################
if 'HTTP_COOKIE' in os.environ:
    C = http.cookies.SimpleCookie(os.environ['HTTP_COOKIE'])
else:
    C = http.cookies.SimpleCookie()

# FETCH USERID/PW INFO
if "UserID" in C:
    userID = C["UserID"].value
    hashed_pw = C["Password"].value
else:
    userID = "guest"
    hashed_pw = "guest"
################################################################################


redirect_sid = 0 # THIS SHOULD BE UPDATED 
html_log = []







###
### Process tags
###
con = sqlite3.connect("../db/%s.db" % corpus) ###
c = con.cursor()
c.execute("""PRAGMA recursive_triggers = 1""")


def process_tags(c):
    """ This function is sets the tag change. It is currently being used
    only in tag-word. The lexical tagger uses a different function below:
    process_tags_taglex()"""

    cids = form.getfirst("cids", '')
    for cd in cids.split(' '):
        if not cd:
            continue

        cdparts = cd.split('|')
        sid = int(cdparts[0])
        cid = int(cdparts[1])
        tag =  form.getfirst("cid_%s" % (cd,), None)
        com =  form.getfirst("com_%s" % (cd,), None)
        if com:
            com = com.strip()


        c.execute("""UPDATE concept SET tag=?, usrname=?
                     WHERE tag IS NOT ?
                     AND sid=? and cid=?""", 
                  (tag, userID, tag, sid, cid))
        if c.rowcount:
            html_log.append(u"""The concept ID: %s of sentence %s was 
                                 successfully tagged with %s by %s
                             """ % (str(cid), str(sid), tag, userID))

        c.execute("""UPDATE concept SET comment=?, usrname=? 
                     WHERE comment IS NOT ? 
                     AND sid=? AND cid=?""", 
                  (com, userID, com, sid, cid))
        if c.rowcount:
            html_log.append(u""" The comment of concept ID: %s of 
                                 sentence %s was successfully updated 
                                 by %s to: <br>"%s" 
                             """ % (str(cid), str(sid), userID, 
                                    cgi.escape(str(com))))

    return html_log



def process_tags_taglex(c):
    """ This function changes 1 tag. It is currently being used only in 
    tag-lexs. The sent-tagger uses a different function: process_tags()"""

    cids = form.getfirst("cids", '')
    for cd in cids.split(' '):
        if not cd:
            continue
        cdparts = cd.split('|')
        sid = int(cdparts[0])
        cid = int(cdparts[1])
        tag =  form.getfirst("cid_%d_%d" % (sid, cid), None)
        com =  form.getfirst("com_%d_%d" % (sid, cid), None)
        old_com = form.getfirst("oldcom_%d_%d" % (sid, cid), None)
        if com:
            com = com.strip()
        if old_com:
            old_com = old_com.strip()

        if tag:
            c.execute("""UPDATE concept 
                         SET tag=?, usrname=? 
                         WHERE tag IS NOT ? 
                         AND sid=? AND cid=?""", 
                      (tag, userID, tag, sid, cid))
            if c.rowcount == 1:
                html_log.append(u"""The concept ID: %s of sentence %s was 
                                    successfully tagged with %s by %s
                                 """ % (str(cid), str(sid), tag, userID))


            else: # nothing uptated, continue
                pass

        else: # The sentence in question received no tag, do nothing
            pass

        c.execute("""UPDATE concept 
                     SET comment=?, usrname=? 
                     WHERE comment IS NOT ? 
                     AND sid=? AND cid=?""", 
                  (com, userID, com, sid, cid))

        if c.rowcount == 1: # something updated, write out
            html_log.append(u""" The comment of concept ID: %s of 
                                 sentence %s was successfully updated 
                                 by %s to: <br>"%s" 
                             """ % (str(cid), str(sid), userID, 
                                    cgi.escape(str(com))))

        else: # nothing update, continue
            pass

    return html_log




def create_sentiment_sql(c):
    """This function is triggered if the database does not yet have
    the necessary strucutre for sentiment. It will add new tables
    and triggers."""

    # CREATE SENTIMENT TABLE IF IT DOES NOT EXIST
    c.execute("""CREATE TABLE IF NOT EXISTS sentiment
                 (sid INTEGER, cid INTEGER, score FLOAT,
                  username TEXT, PRIMARY KEY (sid, cid),
                 FOREIGN KEY(sid) REFERENCES sent(sid),
                 FOREIGN KEY(cid) REFERENCES concept(cid))""")

    # CREATE SENTIMENT_LOG TABLE (FOR TRIGGERS)
    c.execute("""CREATE TABLE IF NOT EXISTS sentiment_log
                 (sid_new INTEGER, sid_old INTEGER, 
                  cid_new INTEGER, cid_old INTEGER, 
                  score_new FLOAT, score_old FLOAT,
                  username_new TEXT, username_old TEXT,
                  date_update DATE)""")

    # # SHOULD CREATE TRIGGERS HERE!
    c.execute("""CREATE TRIGGER IF NOT EXISTS delete_sentiment_log
                 AFTER DELETE ON sentiment
                 BEGIN
                 INSERT INTO sentiment_log (sid_old,
                                            cid_old,
                                            score_old,
                                            username_old,
                                            date_update)
                 VALUES (old.sid,
                         old.cid,
                         old.score,
                         old.username,
                         DATETIME('NOW'));
                 END""")


    c.execute("""CREATE TRIGGER IF NOT EXISTS insert_sentiment_log
                 AFTER INSERT ON sentiment
                 BEGIN
                 INSERT INTO sentiment_log (sid_new,
                                            cid_new,
                                            score_new,
                                            username_new,
                                            date_update) 
                 VALUES (new.sid,
                         new.cid,
                         new.score,
                         new.username,
                         DATETIME('NOW'));
                 END""")

    html_log.append("The SQL structure for sentiment was created.")
    return html_log



def process_sentiment(c):
    """ This functions processes the sentiment scores provided it has 
    a sentence id, a wordid, and a concept id. Results are stored in 
    corpus database. """

    # lemma = form.getfirst("senti_lemma").strip()
    sid = form.getfirst("senti_sid").strip()
    cid = form.getfirst("senti_cid").strip()
    senti_score = form.getfirst("senti_score").strip()

    # INSERT SENTIMENT DATA
    c.execute("""INSERT OR REPLACE INTO sentiment 
                 (sid, cid,  score, username)
                 VALUES (?,?,?,?)""", (sid, cid, senti_score,  userID))


    log = """The sentiment score of the concept [%s (sid:%s)] 
             was updated to %s by %s""" % (cid, sid, str(senti_score), userID)

    html_log.append(log)
    return html_log




# def create_chunks_sql(c):
#     """This function is triggered if the database does not yet have
#     the necessary strucutre for chunk level analysis. 
#     It will add new tables and triggers."""

#     # CREATE CHUNK TABLE
#     c.execute("""CREATE TABLE IF NOT EXISTS chunks
#                  (sid INTEGER, xid INTEGER, score FLOAT,
#                   comment TEXT, username TEXT, 
#                  PRIMARY KEY (sid, xid),
#                  FOREIGN KEY(sid) REFERENCES sent(sid))""")

#     # CREATE CHUNK_LOG TABLE (FOR TRIGGERS)
#     c.execute("""CREATE TABLE IF NOT EXISTS chunk_log
#                  (sid_new INTEGER, sid_old INTEGER,
#                   xid_new INTEGER, xid_old INTEGER,
#                   score_new FLOAT, score_old FLOAT,
#                   comment_new TEXT, comment_old TEXT,
#                   username_new TEXT, username_old TEXT,
#                   date_update DATE)""")

#     # CREATE CHUNK-WORD-LINKS TABLE
#     c.execute("""CREATE TABLE IF NOT EXISTS xwl
#                  (sid INTEGER, wid INTEGER, xid INTEGER,
#                   username TEXT, PRIMARY KEY (sid, wid, xid),
#                  FOREIGN KEY(sid) REFERENCES sent(sid),
#                  FOREIGN KEY(wid) REFERENCES word(wid),
#                  FOREIGN KEY(xid) REFERENCES chunks(xid))""")

#     # CREATE CHUNK-WORD-LINKS LOG TABLE (FOR TRIGGERS)
#     c.execute("""CREATE TABLE IF NOT EXISTS xwl_log
#                  (sid_new INTEGER, sid_old INTEGER,
#                   wid_new INTEGER, wid_old INTEGER,
#                   xid_new INTEGER, xid_old INTEGER,
#                   username_new TEXT, username_old TEXT,
#                   date_update DATE)""")

#     html_log.append("""The SQL structure for chunk level 
#                        analysis was created.""")
#     return html_log

def process_chunks(c):

    # FETCH DATA FROM FORM
    chunk_wxids = form.getfirst("new_chunk").split(',')
    sid = form.getfirst("sid").strip()
    global redirect_sid
    redirect_sid = sid

    # FETCH CHUNKS
    chunks = dd(lambda: dd(lambda: dd(set)))
    # chunks[lang][sid][xid]=set(wids)
    chunks_senti = dd(lambda: dd(lambda: dd(int)))
    # chunks_sen[lang][sid][xid]= score

    fetch_chunks = """SELECT c.sid, c.xid, c.score, xwl.wid
                   FROM chunks as c
                   LEFT JOIN xwl
                   WHERE c.sid = ?
                   AND c.sid = xwl.sid
                   AND c.xid = xwl.xid
                   """
    c.execute(fetch_chunks, [int(sid)])
    rows = c.fetchall()
    for r in rows:
        (sid, xid, score, wid) = (r[0],r[1],r[2],r[3])
        chunks[lang][sid][xid].add(wid)
        chunks_senti[lang][sid][xid] = score


    # FETCH SENTIMENT SCORES BY WORD
    fetch_senti_wid = """SELECT sentiment.sid, cwl.wid, score 
               FROM sentiment 
               JOIN cwl WHERE sentiment.sid = cwl.sid 
               AND sentiment.cid = cwl.cid 
               AND sentiment.sid = ?"""
    c.execute(fetch_senti_wid, [int(sid)])

    # sentiment = {sid: {wid :  score}} 
    senti_wid = dd(lambda: dd(int))
    for (sid, wid, score) in c:
        senti_wid[int(sid)][int(wid)] = score



################################################################################


    ############################################################################

    # it could either be a wid999 or a xid999
    # regardless, always inherit sentiment from the first

    new_chunk = set()
    for chunk in chunk_wxids:
        if chunk.startswith('wid'):
            new_chunk.add(int(chunk.strip('wid')))

        elif chunk.startswith('xid'):
            xid = chunk.strip('xid')

            new_chunk = new_chunk | chunks[lang][sid][int(xid)]

    # log += ",".join(str(x) for x in (list(new_chunk)))



    # TRANSFER HEAD SENTIMENT SCORE
    first = chunk_wxids[0]
    if first.startswith('wid'):
        first_wid = int(first.strip('wid'))

        if senti_wid[sid][first_wid]:
            new_xid_score = senti_wid[sid][first_wid]
        else:
            new_xid_score = 0

    elif first.startswith('xid'):
        first_xid = int(first.strip('xid'))
        if chunks_senti[lang][sid][first_xid]:
            new_xid_score = chunks_senti[lang][sid][first_xid]
        else:
            new_xid_score = 0
    else:
        new_xid_score = 0


    # INSERT CHUNK DATA

    # 1. CREATE NEW CHUNK (ADD MAX+1)
    try:
        new_xid = 1 + max(chunks[lang][sid].keys())
    except:
        new_xid = 0

    # 2. INSERT CHUNK-WORD LINKS
    c.execute("""INSERT INTO chunks
                 (sid, xid, score, username)
                 VALUES (?,?,?,?)""", (sid, new_xid,
                                       new_xid_score,  userID))

    for wid in new_chunk:
        c.execute("""INSERT INTO xwl
                     (sid, wid, xid, username)
                     VALUES (?,?,?,?)""", (sid, wid, 
                                           new_xid, userID))

    log = """ [%s] created a new chunk.<br>""" % userID
    html_log.append(log)
    return html_log


def process_chunks_senti(c):
    sid = form.getfirst("sid").strip()
    global redirect_sid
    redirect_sid = sid
    xid = form.getfirst("xid").strip()
    score = form.getfirst("senti_score").strip()

    c.execute("""UPDATE chunks SET score=?, username=?
                 WHERE sid=? and xid=?""", 
              (score, userID, sid, xid))

    log = """[%s] updated the sentiment of chunkID %s 
             (to %s).<br>""" % (userID, xid, score)
    html_log.append(log)
    return html_log


def process_chunk_comment(c):
    sid = form.getfirst("sid").strip()
    global redirect_sid
    redirect_sid = sid
    xid = form.getfirst("xid").strip()
    try:
        comment = form.getfirst("comment").strip()
    except:
        comment = None

    c.execute("""UPDATE chunks SET comment=?, username=?
                 WHERE sid=? and xid=?""", 
              (comment, userID, sid, xid))

    log = """[%s] updated the comment of chunkID %s.<br>
             (New comment: '%s').<br>""" % (userID, xid, comment)


    html_log.append(log)
    return html_log
    


def delete_chunks(c):

    # FETCH DATA FROM FORM
    chunks2del = form.getfirst("del_chunk").split(',')
    sid = form.getfirst("sid").strip()
    global redirect_sid
    redirect_sid = sid

    for chunk in chunks2del:
        xid = chunk.strip('xid')

        # NEED TO UPDATE THE USER FIRST, THEN DELETE
        c.execute("""UPDATE chunks SET username=?
                     WHERE sid=? and xid=?""", 
                  (userID, sid, xid))

        c.execute("""UPDATE xwl SET username=?
                     WHERE sid=? and xid=?""", 
                  (userID, sid, xid))

        c.execute("""DELETE FROM chunks
                     WHERE sid=? and xid=?""", 
                  (sid, xid))

        c.execute("""DELETE FROM xwl
                     WHERE sid=? and xid=?""", 
                  (sid, xid))


    log = """[%s] deleted %s chunk(s).<br>
          """ % (userID, str(len(chunks2del)))
    html_log.append(log)
    return html_log

##############
# FROM HERE IS TO DEAL WITH LANGUAGE ERRORS LABELING
##############

def process_new_error(c):

    # FETCH DATA FROM FORM
    chunk_wxids = form.getfirst("new_chunk").split(',')
    sid = form.getfirst("sid").strip()
    global redirect_sid
    redirect_sid = sid

    # FETCH CHUNKS
    chunks = dd(lambda: dd(lambda: dd(set)))
    # chunks[lang][sid][eid]=set(wids)
    chunks_senti = dd(lambda: dd(lambda: dd(int)))
    # chunks_sen[lang][sid][eid]= score

    fetch_errors = """SELECT e.sid, e.eid, e.label, ewl.wid
                   FROM error as e
                   LEFT JOIN ewl
                   WHERE e.sid = ?
                   AND e.sid = ewl.sid
                   AND e.eid = ewl.eid
                   """
    c.execute(fetch_errors, [int(sid)])
    rows = c.fetchall()
    for r in rows:
        (sid, eid, label, wid) = (r[0],r[1],r[2],r[3])
        chunks[lang][sid][eid].add(wid)
        chunks_senti[lang][sid][eid] = label

    ############################################################################

    # it could either be a wid999 or a xid999
    # regardless, always inherit sentiment from the first

    new_chunk = set()
    for chunk in chunk_wxids:
        if chunk.startswith('wid'):
            new_chunk.add(int(chunk.strip('wid')))

        elif chunk.startswith('eid'):
            xid = chunk.strip('eid')

            new_chunk = new_chunk | chunks[lang][sid][int(xid)]


    # INSERT CHUNK DATA

    # 1. CREATE NEW CHUNK (ADD MAX+1)
    try:
        new_xid = 1 + max(chunks[lang][sid].keys())
    except:
        new_xid = 0


    sys.stderr.write("""INSERT INTO error (sid, eid, label, username) VALUES ({},{},{},{})""".format(sid, new_xid, None, userID))

    c.execute("""INSERT INTO error
                 (sid, eid, label, username)
                 VALUES (?,?,?,?)""", (sid, new_xid,
                                       None, userID))

    # 2. INSERT CHUNK-WORD LINKS
    for wid in new_chunk:

        sys.stderr.write("""INSERT INTO ewl (sid, wid, eid, username) VALUES ({},{},{},{})""".format(sid, wid, new_xid, userID))

        c.execute("""INSERT INTO ewl
                     (sid, wid, eid, username)
                     VALUES (?,?,?,?)""", (sid, wid, 
                                           new_xid, userID))

    log = """ [%s] created a new error. (please label it!)<br>""" % userID
    html_log.append(log)
    return html_log


def delete_errors(c):
    chunks2del = form.getfirst("del_chunk").split(',')
    sid = form.getfirst("sid").strip()
    global redirect_sid
    redirect_sid = sid

    for chunk in chunks2del:
        eid = chunk.strip('eid')

        # NEED TO UPDATE THE USER FIRST, THEN DELETE
        c.execute("""UPDATE error SET username=?
                     WHERE sid=? and eid=?""", 
                  (userID, sid, eid))

        c.execute("""UPDATE ewl SET username=?
                     WHERE sid=? and eid=?""", 
                  (userID, sid, eid))

        c.execute("""DELETE FROM error
                     WHERE sid=? and eid=?""", 
                  (sid, eid))

        c.execute("""DELETE FROM ewl
                     WHERE sid=? and eid=?""", 
                  (sid, eid))

    log = """[%s] deleted %s error(s).<br>
          """ % (userID, str(len(chunks2del)))
    html_log.append(log)
    return html_log


def error_comment(c):
    sid = form.getfirst("sid").strip()
    global redirect_sid
    redirect_sid = sid
    eid = form.getfirst("eid").strip()
    try:
        comment = form.getfirst("comment").strip()
    except:
        comment = None

    c.execute("""UPDATE error SET comment=?, username=?
                 WHERE sid=? and eid=?""",
              (comment, userID, sid, eid))

    log = """[%s] updated the comment of errorID %s.<br>
             (New comment:'%s').<br>""" % (userID, eid, comment)

    html_log.append(log)
    return html_log


def error_label(c):
    sid = form.getfirst("sid").strip()
    global redirect_sid
    redirect_sid = sid
    eid = form.getfirst("eid").strip()
    label = form.getfirst("error_label").strip()

    c.execute("""UPDATE error SET label=?, username=?
                 WHERE sid=? and eid=?""",
              (label, userID, sid, eid))

    log = """[%s] updated the label of errorID %s 
             (to %s).<br>""" % (userID, eid, label)
    html_log.append(log)
    return html_log







################################################################################
# MANAGE CGI MODES
################################################################################
if cgi_mode == "taglex":
    html_log = '<br>'.join(process_tags_taglex(c))
elif cgi_mode == "tagword":
    html_log = '<br>'.join(process_tags(c))

elif cgi_mode == "sentiment":
    try: # Try to insert directly
        html_log = '<br>'.join(process_sentiment(c))
    except: # Create structure and then insert
        create_sentiment_sql(c)
        html_log = '<br>'.join(process_sentiment(c))

elif cgi_mode == "chunks":
    try: # Try to insert directly
        html_log = '<br>'.join(process_chunks(c))
    except: # Create structure and then insert
        create_chunks_sql(c)  # FIXME(Wilson): This func was commented out...
        html_log = '<br>'.join(process_chunks(c))

elif cgi_mode == "chunk_sentiment":
    html_log = '<br>'.join(process_chunks_senti(c))

elif cgi_mode == "delete_chunks":
    html_log = '<br>'.join(delete_chunks(c))

elif cgi_mode == "chunk_comment":
    html_log = '<br>'.join(process_chunk_comment(c))



elif cgi_mode == "new_error":
    html_log = '<br>'.join(process_new_error(c))
elif cgi_mode == "delete_errors":
    html_log = '<br>'.join(delete_errors(c))
elif cgi_mode == "error_comment":
    html_log = '<br>'.join(error_comment(c))
elif cgi_mode == "error_label":
    html_log = '<br>'.join(error_label(c))



elif cgi_mode == "h_new_error":
    html_log = '<br>'.join(process_new_error(c))
elif cgi_mode == "h_delete_errors":
    html_log = '<br>'.join(delete_errors(c))
elif cgi_mode == "h_error_comment":
    html_log = '<br>'.join(error_comment(c))
elif cgi_mode == "h_error_label":
    html_log = '<br>'.join(error_label(c))



con.commit()



if cgi_mode in ("chunks", "chunk_sentiment", 
                "delete_chunks", "chunk_comment"):
    
    print(u"""Content-type: text/html; charset=utf-8 \n\n
    <!DOCTYPE html>
      <html>
        <head>
          <meta charset='utf-8'>
        </head>
        <body onload="document.logform.submit()">
        <form name="logform" action="tag-senti.cgi"  
              method="post">
         <input type="hidden" name="log_message" value="%s"/> 
         <input type="hidden" name="lang" value="%s"/>
         <input type="hidden" name="corpusdb" value="%s"/>
         <input type="hidden" name="sid" value="%s"/>
         </form>
         </body>
      </html>""" % (html_log, lang, corpus, redirect_sid))

elif cgi_mode in ("new_error", "delete_errors",
                  "error_comment", "error_label"):
    
    print(u"""Content-type: text/html; charset=utf-8 \n\n
    <!DOCTYPE html>
      <html>
        <head>
          <meta charset='utf-8'>
        </head>
        <body onload="document.logform.submit()">
        <form name="logform" action="tag-errors.cgi?corpusdb=%s"  
              method="post">
         <input type="hidden" name="log_message" value="%s"/> 
         <input type="hidden" name="corpusdb" value="%s"/>
         <input type="hidden" name="sid" value="%s"/>
         </form>
         </body>
      </html>""" % (corpus, html_log, corpus, redirect_sid))

elif cgi_mode in ("h_new_error", "h_delete_errors",
                  "h_error_comment", "h_error_label"):
    
    print(u"""Content-type: text/html; charset=utf-8 \n\n
    <!DOCTYPE html>
      <html>
        <head>
          <meta charset='utf-8'>
        </head>
        <body onload="document.logform.submit()">
        <form name="logform" action="hannah.cgi?corpusdb=%s"  
              method="post">
         <input type="hidden" name="log_message" value="%s"/> 
         <input type="hidden" name="corpusdb" value="%s"/>
         <input type="hidden" name="sid" value="%s"/>
         </form>
         </body>
      </html>""" % (corpus, html_log, corpus, redirect_sid))

else:
    ################################################################################
    # PRINT LOG
    ################################################################################
    print(u"""Content-type: text/html; charset=utf-8 \n\n
    <!DOCTYPE html>
       <html>
         <head style="top:-8px;"> 
           <meta charset='utf-8'>
             <title>Corpus Editor - Log </title>
         </head>
         <body style="margin:0 !important; margin-top:-10px !important; 
                      padding:0 !important;background-color: white;">
             <p> %s
         </body>
       </html>
     """ % html_log)
