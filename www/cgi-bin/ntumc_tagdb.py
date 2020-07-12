#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#import re, sqlite3, collections
from ntumc_util import jilog, placeholders_for

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
    """
    cur - sqlite3.Cursor
    lems - list
    lim, sid_from, sid_to - int
    """
    query = """
        SELECT sid, cid, clemma, tag, tags, comment 
        FROM concept 
        WHERE clemma IN (%s) 
            AND sid >= ? AND sid <= ?
        ORDER BY tag, sid, cid LIMIT ? 
    """ % placeholders_for(lems)
    #print query
    limits = [int(sid_from), int(sid_to), int(lim)]
    cur.execute(query, lems + limits)
    return cur.fetchall()

def select_cwlink(cur, lems, lim):
    query = """
        SELECT sid, wid, cid 
        FROM cwl
        WHERE sid IN (
            SELECT sid 
            FROM concept 
            WHERE clemma IN (%s) 
            ORDER BY tag, sid, cid 
            LIMIT ?)
    """ % placeholders_for(lems)
    cur.execute(query, lems + [int(lim)])
    return cur.fetchall()

def select_tag_distribution(cur, lems):
    query = """
        SELECT count(tag), tag 
        FROM concept
        WHERE clemma in (%s)
        GROUP BY tag 
        ORDER BY count(tag) DESC;
    """ % placeholders_for(lems)
    #jilog('Executing query: %s' % query)
    #jilog('Values: %s' % str(lems))
    cur.execute(query, lems)
    return cur.fetchall()

def select_word(cur, lems, lim):
    query = """
        SELECT wid, word, pos, lemma, sid 
        FROM word 
        WHERE sid IN (
           SELECT sid 
           FROM concept 
           WHERE clemma IN (%s) 
           ORDER BY tag, sid, cid 
           LIMIT ?
        ) ORDER BY sid, wid
    """ % placeholders_for(lems)
    cur.execute(query, lems + [int(lim)])
    return cur.fetchall()

def select_sentence_id(cur,lemma):
    query = """
        SELECT DISTINCT sid 
        FROM word 
        WHERE lemma LIKE ? 
            OR word LIKE ?
    """
    cur.execute(query, [lemma, lemma])
    return cur.fetchall()

def select_word_from_sentence(cur, sids):
    query = """
        SELECT sid, wid, word, lemma
        FROM word 
        WHERE sid IN (%s)
        ORDER BY sid, wid
    """ % placeholders_for(sids)
    cur.execute(query, list(sids))
    return cur.fetchall()

# 2014-06-30 [Tuan Anh]
# fix 500 items limitation
def select_other_concept(cur, lems, lim):
    lim = [int(lim)]
    
    all_sids_query = """
        SELECT DISTINCT sid FROM concept
        WHERE clemma IN (%s) 
        ORDER BY tag, sid, cid LIMIT ?
    """ % placeholders_for(lems)
    
    all_cids_query = """
        SELECT DISTINCT cid FROM concept 
        WHERE clemma in (%s) 
        ORDER BY tag, sid, cid LIMIT ?
    """ % placeholders_for(lems)
    
    query = """
        SELECT b.cid, b.sid, b.wid, c.clemma, c.tag, c.tags, c.comment  
        FROM concept AS z
        JOIN cwl AS a ON  z.sid=a.sid AND z.cid=a.cid 
        JOIN cwl AS b ON a.sid=b.sid AND a.wid=b.wid 
        JOIN concept AS c ON b.sid=c.sid AND b.cid=c.cid 
        WHERE z.sid IN (%s) 
            AND z.cid IN (%s)
            AND z.clemma in (%s)
    """ % (all_sids_query, all_cids_query, placeholders_for(lems))
    
    jilog("Find other concept: %s [lemma = %s]" % (query, lems))
    cur.execute(query, lems + lim + lems + lim + lems)
    return cur.fetchall()

## 2014-07-01 [Tuan Anh]
# Add filter
def select_corpus(cur, lang):
    query = """SELECT * FROM corpus WHERE language=?;"""
    cur.execute(query, [lang])
    results = cur.fetchall()
    return results
    

## ACCESS [WORDNET]

def select_wordnet_freq(wcur, all_synsets):
    a_query = """
        SELECT lemma, freq, synset 
        FROM sense 
        LEFT JOIN word ON word.wordid = sense.wordid 
        WHERE synset IN (%s) 
            AND sense.lang = ? 
        ORDER BY synset, freq DESC
    """ % placeholders_for(all_synsets)
    
    jilog("I'm selecting %s" % a_query)
    jilog("using values %s" % list(all_synsets))
    
    #tm.start()
    wcur.execute(a_query, list(all_synsets) + ['eng'])
    results = wcur.fetchall()
    #tm.stop().log("task = select word left join sense")
    return results

def select_synset_def(wcur, all_synsets):
    a_query = """
        SELECT def, synset 
        FROM synset_def 
        WHERE synset in (%s) 
            AND lang = ? 
        ORDER BY synset, sid
    """ % placeholders_for(all_synsets)

    jilog("I'm selecting %s\n" % a_query)
    jilog("using values %s" % list(all_synsets))
    #tm.start()
    wcur.execute(a_query, list(all_synsets) + ['eng'])
    results = wcur.fetchall()
    #tm.stop().log("task = select synset_def")
    return results

def select_synset_def_ex(wcur, all_synsets):
    a_query = """
        SELECT def, synset 
        FROM synset_ex 
        WHERE synset IN (%s) 
            AND lang = ? 
        ORDER BY synset, sid
    """ % placeholders_for(all_synsets)
    
    jilog("I'm selecting %s\n" % a_query)
    jilog("using values %s" % list(all_synsets))
    #tm.start()
    wcur.execute(a_query, list(all_synsets) + ['eng'])
    results = wcur.fetchall()
    #tm.stop().log("task = synset_ex")
    return results
####################################################################
# END OF DB ACCESS CODE
####################################################################
