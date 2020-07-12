#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from collections import defaultdict as dd
import sys

import nltk
from nltk.corpus import wordnet as pwn


# SIDs TO and FROM, only these will be replaced
sid_from = 11000
sid_to = 11609

# It allows to compare up to 4 databases
dba = "enga.db"
dbb = "engb.db"
dbc = "engc.db"
dbd = "engd.db"  # old eng.db (renamed to engd.db)

db_main = "eng.db"  # this is the db that will be overwritten
conn_db_main = sqlite3.connect(db_main)
main = conn_db_main.cursor()

usr = "hg2002"  # usr that changes eng

##########################
# FETCH sentences BY sid
##########################
conn_dba = sqlite3.connect(dba)
a = conn_dba.cursor()

sent = dict()
a.execute( """SELECT sid, sent
              FROM  sent
              WHERE sid >= ? AND sid <= ?""", [sid_from, sid_to] )
for (sid, s) in a:
    sent[sid] = s

#########################
# FETCH concept tags
#########################

# DATA stores the tags for comparison!
data = dd(lambda: dd(lambda: dd(lambda: dd(str))))  # agregates data by sentence
data_ag = dd(lambda: dd(lambda: dd(lambda: dd(str))))  # agreegates all data
ag_scores = dd(lambda: dd(int))  # e.g. {sid: {'AvsS' : 0.8} }

concept_query = """SELECT sid, cid, clemma, tag, tags, 
                          comment, ntag, usrname 
                   FROM concept 
                   WHERE sid >= ? AND sid <= ?
                   ORDER BY sid, cid"""

word_query = """SELECT sid, wid, word, pos, lemma
                FROM word
                WHERE sid >= %s AND sid <= %s""" % (sid_from, sid_to)


# DATABASE A (connected on Sentences)
a.execute(concept_query, [sid_from, sid_to])
for (sid, cid, clemma, tag, tags, comment, ntag, usrname) in a:
    data[sid][cid]['a']['tag'] = str(tag).strip()
    data[sid][cid]['a']['ntag'] = str(ntag).strip()
    data[sid][cid]['a']['tags'] = str(tags).strip()
    data[sid][cid]['a']['clem'] = str(clemma).strip()
    data[sid][cid]['a']['com'] = comment
    data[sid][cid]['a']['usr'] = usrname

    sidcid = str(sid) + '_' + str(cid)
    data_ag['all'][sidcid]['a']['tag'] = str(tag).strip()

# DATABASE B
connb = sqlite3.connect(dbb)
b = connb.cursor()
b.execute(concept_query, [sid_from, sid_to])

for (sid, cid, clemma, tag, tags, comment, ntag, usrname) in b:
    data[sid][cid]['b']['tag'] = str(tag).strip()
    data[sid][cid]['b']['ntag'] = str(ntag).strip()
    data[sid][cid]['b']['tags'] = str(tags).strip()
    data[sid][cid]['b']['clem'] = str(clemma).strip()
    data[sid][cid]['b']['com'] = comment
    data[sid][cid]['b']['usr'] = usrname

    sidcid = str(sid) + '_' + str(cid)
    data_ag['all'][sidcid]['b']['tag'] = str(tag).strip()

# DATABASE C
connc = sqlite3.connect(dbc)
c = connc.cursor()
c.execute(concept_query, [sid_from, sid_to])

for (sid, cid, clemma, tag, tags, comment, ntag, usrname) in c:
    data[sid][cid]['c']['tag'] = str(tag).strip()
    data[sid][cid]['c']['ntag'] = str(ntag).strip()
    data[sid][cid]['c']['tags'] = str(tags).strip()
    data[sid][cid]['c']['clem'] = str(clemma).strip()
    data[sid][cid]['c']['com'] = comment
    data[sid][cid]['c']['usr'] = usrname

    sidcid = str(sid) + '_' + str(cid)
    data_ag['all'][sidcid]['c']['tag'] = str(tag).strip()

# DATABASE D
conng = sqlite3.connect(dbd)
g = conng.cursor()
g.execute(concept_query, [sid_from, sid_to])

for (sid, cid, clemma, tag, tags, comment, ntag, usrname) in g:
    data[sid][cid]['g']['tag'] = str(tag).strip()
    data[sid][cid]['g']['ntag'] = str(ntag).strip()
    data[sid][cid]['g']['tags'] = str(tags).strip()
    data[sid][cid]['g']['clem'] = str(clemma).strip()
    data[sid][cid]['g']['com'] = comment
    data[sid][cid]['g']['usr'] = usrname

    sidcid = str(sid) + '_' + str(cid)
    data_ag['all'][sidcid]['g']['tag'] = str(tag).strip()

# SILVER DATA (Generated from A, B, and G)
for sid in sent.keys():

    for cid in data[sid].keys():  # each concept used in sentence

        tags = [data[sid][cid]['a']['tag'],
                 data[sid][cid]['b']['tag'],
                # data[sid][cid]['c']['tag'],
                 data[sid][cid]['g']['tag']]
        mx = max(tags.count(t) for t in tags)

        comms = ''
        acom = data[sid][cid]['a']['com']
        if acom:
            acom.strip(' ;,.')
            comms += acom
            comms += '; '
        bcom = data[sid][cid]['b']['com']
        if bcom:
            bcom.strip(' ;,.')
            comms += bcom
            comms += '; '
        ccom = data[sid][cid]['c']['com']
        if ccom:
            ccom.strip(' ;,.')
            comms += ccom
            comms += '; '
        gcom = data[sid][cid]['g']['com']
        if gcom:
            try:
                gcom = gcom.split("None; ")[1]
            except:
                continue
            gcom.strip(' ;,.')
            comms += gcom
            comms += '; '

        if comms == '':
            comms = None

        if mx > 1:  # IF THERE WAS A MINIMUM AGREEMENT
            majtag =  [t for t in tags if tags.count(t) == mx][0]

            if majtag == "None":
                majtag = '?'

                # SET TAG TO NONE
                main.execute("UPDATE concept SET tag = ?, comment = ?, usrname=? WHERE sid=? AND cid = ?", (None, comms, usr, sid, cid))

            else:
                # SET TAG TO MAJTAG
                main.execute("UPDATE concept SET tag = ?, comment = ?, usrname=? WHERE sid=? AND cid = ?", (majtag, comms, usr, sid, cid))

            data[sid][cid]['s']['tag'] = majtag

            sidcid = str(sid) + '_' + str(cid)
            data_ag['all'][sidcid]['s']['tag'] = majtag

        else:
            data[sid][cid]['s']['tag'] = '?'  # NO AGREEMENT
            data_ag['all'][sidcid]['s']['tag'] = '?'

            ### set TAG
            main.execute("UPDATE concept SET tag = ?, comment = ?, usrname=? WHERE sid=? AND cid = ?", (None, comms, usr, sid, cid))

conn_db_main.commit()

a.close()
b.close()
c.close()
g.close()

main.close()

sys.stderr.write('Tags were merged and updated into %s' % db_main)
