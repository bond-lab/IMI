#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3, codecs
from collections import defaultdict as dd

import nltk
from nltk.corpus import wordnet as pwn

import sys  #, codecs
# sys.stdout = codecs.getwriter('utf8')(sys.stdout)

# # SIDs TO and FROM, only these will be replaced
# sid_from = 11000
# sid_to = 11609

# It allows to compare up to 4 databases
# dba = "enga.db"
# dbb = "engb.db"
# dbc = "engc.db"
# dbd = "engd.db"  # old eng.db (renamed to engd.db)

db_main = "cmn.db"  # this is the db that will be overwritten
conn_db_main = sqlite3.connect(db_main)
main = conn_db_main.cursor()

wndb = "wn-ntumc.db"
conn_db_wn = sqlite3.connect(wndb)
wn = conn_db_wn.cursor()

usr = "auto-tag-classifiers"  # usr that changes eng

################################################
# FETCH CLASSIFIERS BY sid, cid, clemma, tag
################################################

# {sid: cid: clemma: tag}
concept_dict = dd(lambda: dd(lambda: dd(str)))
main.execute("""SELECT concept.sid, concept.cid, clemma, tag
             FROM word LEFT JOIN concept LEFT JOIN cwl 
             WHERE word.sid = concept.sid
             AND word.sid = cwl.sid
             AND cwl.wid = word.wid
             AND cwl.cid = concept.cid
             AND pos = "M"
             AND (tag IS Null OR tag in ('x','w'))""")

for (sid, cid, clemma, tag) in main:
    concept_dict[sid][cid][clemma] = str(tag).strip()


################################################
# FETCH CLASSIFIERS BY synset, lemma
################################################

cl_lemma = dict()
wn.execute("""SELECT synset.synset, lemma 
              FROM synset LEFT JOIN synlink LEFT JOIN sense LEFT JOIN word 
              WHERE sense.synset = synset.synset 
              AND sense.wordid = word.wordid 
              AND synset1 = synset.synset 
              AND synset2 = "06308436-n" 
              AND link = "dmnc" """)

for synset, lemma in wn:
    cl_lemma[lemma] = synset


count_w = 0
count_ss = 0
# SILVER DATA (Generated from A, B, and G)
for sid in concept_dict.keys():
    for cid in concept_dict[sid]:
        for clemma in concept_dict[sid][cid]:

            if clemma in cl_lemma:
                concept_dict[sid][cid][clemma] = cl_lemma[clemma]
                count_ss += 1
            else:
                concept_dict[sid][cid][clemma] = "w"
                count_w += 1
                

            tag = concept_dict[sid][cid][clemma]
            print(clemma + " should be tagged with: " + tag)  #TEST

            # UPDATE TAGS
            main.execute("""UPDATE concept 
                            SET tag = ?, usrname=? 
                            WHERE sid = ? 
                            AND cid = ?
                            AND tag IS NOT ?""", (tag, usr, sid, cid,tag))

conn_db_main.commit()

main.close()
wn.close()

print("""%s re-tagged with a synset; %s re-tagged with 'w' """% (count_ss,count_w))
sys.stderr.write('Classifiers were tagged in %s' % db_main)
