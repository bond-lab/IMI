#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#import re, sqlite3, collections
from ntumc_util import jilog

####################################################################
# DATABASE ACCESS
####################################################################

###
### If you set a word with multiple concepts to a real tag
### then set any other untagged concepts to 'x' (don't tag)
###
def set_others_x(cursor, usrname, sid, cid):
    query = """
        UPDATE concept SET tag='x', usrname=?, comment='shadowed MWE'
        WHERE ROWID=(
            SELECT b.ROWID 
            FROM cwl AS a INNER JOIN cwl AS b ON a.sid=b.sid AND a.wid=b.wid 
            LEFT JOIN concept AS acon ON a.sid=acon.sid and a.cid=acon.cid
            LEFT JOIN concept AS bcon ON b.sid=bcon.sid and b.cid=bcon.cid
            WHERE a.sid=? and a.cid=? and acon.tag not in ('x', 'e') AND bcon.tag IS NULL
       )"""
    cursor.execute(query, (usrname, sid, cid))

# totag query
# lems = list(expandlem(lemma))
def select_concept(cur, lems, lim, sid_from, sid_to):
    query = """SELECT sid, cid, clemma, tag, tags, comment 
               FROM concept WHERE clemma in (%s) 
               AND sid >= %s AND sid <= %s
               ORDER BY tag, sid, cid LIMIT ? 
            """ % (','.join('?'*len(lems)), sid_from, sid_to)
    #print query 
    cur.execute(query, lems + [int(lim)])
    return cur.fetchall()

def select_cwlink(cur, lems, lim):
    return cur.execute("""
        SELECT sid, wid, cid 
        FROM cwl
        WHERE sid in (select sid from concept where clemma in (%s) 
                      order by tag, sid, cid LIMIT ?)"""% ','.join('?'*len(lems)), 
                               lems + [int(lim)]).fetchall()

def select_tag_distribution(cur, lems):
        query = """SELECT count(tag), tag FROM concept WHERE clemma in (%s) group by tag order by count(tag) desc; """ % ','.join('?'*len(lems))
        #jilog('Executing query: %s' % query)
        #jilog('Values: %s' % str(lems))
        cur.execute(query, lems)
        return cur.fetchall()

def select_word(cur, lems, lim):
    return cur.execute("""select wid, word, pos, lemma, sid 
                               from word where sid in (select sid from concept 
                               where clemma in (%s) 
                               order by tag, sid, cid LIMIT ?) order by sid, wid""" % ','.join('?'*len(lems)),
                            lems + [ int(lim)]).fetchall()

def select_sentence_id(cur,lemma):
    return cur.execute("select distinct sid from word where lemma like ? or word like ?", (lemma, lemma)).fetchall()

def select_word_from_sentence(cur, sids):
    return cur.execute("select sid, wid, word, lemma from word where sid in (%s) order by sid, wid" % ','.join(sids)).fetchall()

# 2014-06-30 [Tuan Anh]
# fix 500 items limitation
def select_other_concept(cur, lems, lim):
    all_sids_query = """SELECT distinct sid FROM concept WHERE clemma in (%s) ORDER BY tag, sid, cid LIMIT %d""" % (','.join('?'*len(lems)), int(lim))
    all_cids_query = """SELECT distinct cid FROM concept WHERE clemma in (%s) ORDER BY tag, sid, cid LIMIT %d""" % (','.join('?'*len(lems)), int(lim))
    query="""SELECT b.cid, b.sid, b.wid, c.clemma, c.tag, c.tags, c.comment  
                 FROM concept AS z
                 JOIN cwl AS a ON  z.sid=a.sid and z.cid=a.cid 
                 JOIN cwl AS b ON a.sid=b.sid and a.wid=b.wid 
                 JOIN concept as c on b.sid=c.sid and b.cid=c.cid 
                 WHERE z.sid in (%s) and z.cid in (%s) and z.clemma in (%s)"""  % (
            all_sids_query,  all_cids_query, ','.join('?'*len(lems)))
    jilog("Find other concept: %s [lemma = %s]" % (query, lems))
    return cur.execute(query, lems + lems + lems).fetchall()

## 2014-07-01 [Tuan Anh]
# Add filter
def select_corpus(cur, lang):
    query = """SELECT * FROM corpus WHERE language=?;"""
    results = cur.execute(query, (lang,)).fetchall()
    return results
    

## ACCESS [WORDNET]

def select_wordnet_freq(wcur, all_synsets):
    a_query = "select lemma, freq, synset from sense left join word on word.wordid = sense.wordid where synset in (%s) and sense.lang = ? ORDER BY synset, freq DESC" % ','.join(["'%s'" % x for x in all_synsets] )
    jilog("I'm selecting %s" % a_query)
    #tm.start()
    results = wcur.execute(a_query, ('eng',)).fetchall()
    #tm.stop().log("task = select word left join sense")
    return results

def select_synset_def(wcur, all_synsets):
    a_query = "SELECT def, synset FROM synset_def WHERE synset in (%s) and lang = ? order by synset, sid" % ','.join(["'%s'" % x for x in all_synsets] )
    jilog("I'm selecting %s\n" % a_query)
    #tm.start()
    results = wcur.execute(a_query, ('eng',)).fetchall()
    #tm.stop().log("task = select synset_def")
    return results

def select_synset_def_ex(wcur, all_synsets):
    a_query = "SELECT def, synset FROM synset_ex WHERE synset in (%s) and lang = ? order by synset, sid" % ','.join(["'%s'" % x for x in all_synsets] )
    jilog("I'm selecting %s\n" % a_query)
    #tm.start()
    results = wcur.execute(a_query, ('eng',)).fetchall()
    #tm.stop().log("task = synset_ex")
    return results
####################################################################
# END OF DB ACCESS CODE
####################################################################
