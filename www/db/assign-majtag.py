#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
from collections import defaultdict as dd
import sys, os



# This script will compare the tags of the different databases
# (e.g. enga.db, engb.db, engc.db) and calculate a silver tag 
# that it then uses to retag the main database (e.g. eng.db).
# it also assigns the average of non None sentiment.

# THIS SHOULD BE RUN in THE DB FOLDER

################################################################################
# GLOBAL VARIABLES
################################################################################

# SET LANG
lang = 'eng'

# SET DB TO BE OVERWRITTEN
db_main = "eng.db"  # this is the db that will be overwritten

if os.path.isfile(db_main):
    conn_db_main = sqlite3.connect(db_main)
    main = conn_db_main.cursor()


# SET USERNAME FOR LOG
usr = "hg2002"  # usr that changes eng
usr += "-majtag"  # usr that changes eng



# SET SID TO / FROM
sid_from, sid_to = 48505, 49505


### delete the sentiment
main.execute("""
DELETE FROM sentiment
WHERE sid >=? and sid <=?""", (sid_from, sid_to))

dbs = [] # TRIPLET (A/B/..., db_path, corpus_code)
for i in ['A','B','C','D','E']:
    if os.path.isfile("%s%s.db" % (lang,i)):
        dbs.append((i, "%s%s.db" % (lang,i),"%s%s" % (lang,i)))



################################################################################
# FETCH DB DATA
################################################################################
sent = dict()
data = dd(lambda: dd(lambda: dd(lambda: dd(str))))  # agregates data by sentence


con = sqlite3.connect(dbs[0][1])
c = con.cursor()

c.execute("""SELECT sid, sent
             FROM  sent
             WHERE sid >= %s 
             AND sid <= %s""" % (sid_from, sid_to))
for (sid, sentence) in c:
    sent[sid] = sentence

con.close()

concept_query = """SELECT sid, cid, clemma, tag, tags, 
                          comment, usrname 
                   FROM concept 
                   WHERE sid >= %s AND sid <= %s 
                   ORDER BY sid, cid""" % (sid_from, sid_to)

word_query = """SELECT sid, wid, word, pos, lemma
                FROM word
                WHERE sid >= %s AND sid <= %s""" % (sid_from, sid_to)

senti_query = """SELECT sid, cid, score
                FROM sentiment
                WHERE sid >= %s AND sid <= %s""" % (sid_from, sid_to)


for db in dbs:
    db_ref = db[0].lower()
    con = sqlite3.connect(db[1])
    c = con.cursor()

    c.execute(concept_query)
    for (sid, cid, clemma, tag, tags, comment, usrname) in c:
        data[sid][cid][db_ref]['tag'] = str(tag).strip()
        data[sid][cid][db_ref]['clem'] = clemma
        data[sid][cid][db_ref]['usr'] = usrname
        data[sid][cid][db_ref]['senti'] = None
        if comment:
            data[sid][cid][db_ref]['com'] = comment

        sidcid = str(sid) + '_' + str(cid)
    c.execute(senti_query)
    for (sid, cid, score) in c:
        data[sid][cid][db_ref]['senti'] = float(score)

    con.close()
################################################################################




################################################################################
# CALCULATE SILVER DATA / MAJ TAG
################################################################################
for sid in sent.keys():

    for cid in data[sid].keys():

        tags = [] # LIST OF TAGS USED
        comms = '' # APPENDED COMMENTS
        sentiment = []
        for db in dbs:
            db_ref = db[0].lower()

            if data[sid][cid][db_ref]['tag'] != None and\
               data[sid][cid][db_ref]['tag'] != "None":
                tags.append(data[sid][cid][db_ref]['tag'])

            com = data[sid][cid][db_ref]['com']
            if com:
                comms += com + '; '
            if data[sid][cid][db_ref]['senti']:
                sentiment.append(data[sid][cid][db_ref]['senti'])

        try:
            mx = max(tags.count(t) for t in tags) # MOST USED TAG
        except:
            mx = 0

        if mx > 1:  # IF THERE WAS A MINIMUM AGREEMENT

            majtags =  list(set([t for t in tags if tags.count(t) == mx]))

            if len(majtags) == 1: # IF THERE IS NO TIE
                majtag = majtags[0]

            else:
                majtag = None

            if majtag == "None":
                 majtag = None

                 
            # SET TAG TO MAJTAG
            main.execute("""
                UPDATE concept 
                SET tag = ?, comment = ?, usrname=? 
                WHERE sid=? 
                AND cid = ?""", (majtag, comms, 
                                 usr, sid, cid))
            # set SENTIMENT to average of non-zero values
            if majtag and sentiment and len(majtag)>3:
                senti = sum(s for s in sentiment)/len(sentiment)
                main.execute("""
                INSERT INTO sentiment (sid,cid,score,username)
                VALUES(?,?,?,?)""", (sid, cid, senti, usr))

        else: # NO AGREEMENT

            main.execute("""
                UPDATE concept 
                SET tag = ?, comment = ?, usrname=? 
                WHERE sid=? 
                AND cid = ?""", (None, comms, 
                                 usr, sid, cid))
            main.execute("""
                DELETE FROM sentiment 
                WHERE sid=?  
                AND cid = ?""", (sid, cid))


# DRY RUN UNLESS UNCOMMENTED
main.close()
conn_db_main.commit()

sys.stderr.write('Tags were merged and updated into %s\n\n' % db_main)
