#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
#import cgitb; cgitb.enable()  # for troubleshooting
import re, sqlite3, collections
import os, sys 
import operator
from collections import defaultdict as dd
import warnings
import unicodedata

from ntumc_gatekeeper import placeholders_for as _placeholders_for

#############################################################
# Configuration
#############################################################
#tagcgi = 'tag-lex.cgi' # DEPRECATED - WILL BE REMOVED SOON
taglcgi="tag-lexs.cgi"
tagwcgi="tag-word.cgi"
showsentcgi="show-sent.cgi"
logincgi="login.cgi"
### reference to wn-grid (search .cgi)
omwcgi = "wn-gridx.cgi"
# wordnets
wncgi = "wn-gridx.cgi"
wndb = "../db/wn-ntumc.db"

#############################################################
# Utilities for debugging
#############################################################

# 2014-06-12 [Tuan Anh]
def jilog(msg):
    sys.stderr.write((u"%s\n" % msg))
    try:
        with open("../log/ntumc.txt", "a", encoding='utf-8') as logfile:
            logfile.write(u"%s\n" % msg)
    except Exception as ex:
        sys.stderr.write(str(ex))
        pass

# I added a timer class here for performance optimisation
import time
class Timer:
    def __init__(self):
        self.start_time = time.time()
        self.end_time = time.time()
    def start(self):
            self.start_time = time.time()
            return self
    def stop(self):
        self.end_time = time.time()
        return self
    def __str__(self):
        return "Execution time: %.2f sec(s)" % (self.end_time - self.start_time) 
    def log(self, task_note = ''):
        jilog(u"%s - Note=[%s]\n" % (self, task_note))
        return self

#############################################################
# NTU-MC shared functions
#############################################################

def expandlem (lemma):  ### keep in sync with tag-lexs
    lems=set()
    lems.add(lemma)
    ### case
    lems.add(lemma.lower())
    lems.add(lemma.upper())
    lems.add(lemma.title())
    ### hyphen, underbar, space
    lems.add(lemma.replace('-',''))
    lems.add(lemma.replace('-',' '))
    lems.add(lemma.replace(' ','-'))
    lems.add(lemma.replace('_',''))
    lems.add(lemma.replace(' ',''))
    ### normalize unicode
    lems.add(unicodedata.normalize('NFKC', lemma))
    lems.add(unicodedata.normalize('NFKC', lemma).lower())
    lems.add(unicodedata.normalize('NFKC', lemma).upper())
    lems.add(unicodedata.normalize('NFKC', lemma).title())
    # lems.add(lemma.replace('_',u'∥'))
    # lems.add(lemma.replace('-',u'∥'))
    # lems.add(lemma.replace(u'・',u'∥'))
    # lems.add(lemma.replace(u'ー',u'∥'))
    # lems.add(lemma.replace(' ',u'∥'))
    return lems

def pos2wn (pos, lang, lemma=''):
    ### FIXME: check and document --- Change POS for VN?
    if lang == 'jpn':
        if pos in [u'名詞-形容動詞語幹', u"形容詞-自立", u"連体詞"]:
            return 'a'
        elif pos in [u"名詞-サ変接続",  u"名詞-ナイ形容詞語幹", 
                     u"名詞-一般", u"名詞-副詞可能",  
                     u"名詞-接尾-一般", u"名詞-形容動詞語幹", 
                     u"名詞-数",  u"記号-アルファベット"]:
            return 'n'
        elif pos in [u"動詞-自立", u"動詞-サ変接続"]:
            return 'v'
        elif pos in [u"副詞-一般", u"副詞-助詞類接続"]:
            return 'r'
        else:
            return 'x'
    elif lang=='eng': 
        if  pos == 'VAX':  #local tag for auxiliaries
            return 'x'
        elif pos in ['CD', 'NN', 'NNS', 'NNP', 'NNPS', 'WP', 'PRP']: 
            # include proper nouns and pronouns
            ## fixme flag for proper nouns
            return 'n'
        elif pos.startswith('V'):
            return('v')
        elif pos.startswith('J') or pos in ['WDT',  'WP$', 'PRP$', 'PDT', 'PRP'] or \
                (pos=='DT' and not lemma in ['a', 'an', 'the']):  ### most determiners
            return('a')
        elif pos.startswith('RB') or pos == 'WRB':
            return('r')
        else:
            return 'x'
    elif lang=='cmn':
        if pos in "NN NN2 CD DT PN PN2 LC M M2 NR NT".split():
            return 'n'
        elif pos in "VV VV2 VC VE".split():
            return 'v'
        elif pos in "JJ JJ2 OD VA VA2".split():
            return 'a'
        elif pos in "AD AD2 ETC ON".split():
            return 'r'
        else:
            return 'x'
    elif lang=='vie':
        if pos in "N Np Nc Nu Ny B".split():
            return 'n'
        elif pos in "V".split():
            return 'v'
        elif pos in "A".split():
            return 'a'
        elif pos in "L R".split():
            return 'r'
        else:
            return 'x'
    elif lang in ('ind', 'zsm'):
        if pos in "nn nn2 nnc nng nnp nnu nns2  prp wp prl vnb".split():
            return 'n'
        elif pos in "vbi vbt vbd vbb vbl".split():
            return 'v'
        elif pos in "jj jj2 jjs jjs2 jje jje2 dt".split():
            return 'a'
        elif pos in "rb".split():
            return 'r'
        else:
            return 'x'
    else:
        return 'u'

#half = u' 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~'
#full = u'　０１２３４５６７８９ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ！゛＃＄％＆（）＊＋、ー。／：；〈＝〉？＠［\\］＾＿‘｛｜｝～'
#half2full = dict((ord(x[0]), x[1]) for x in zip(half, full)
#full2half = dict((ord(x[0]), x[1]) for x in zip(full, half)
#print u'Hello, world!'.translate(half2full)


###
### tagging functions
###

# Add more tags in
mtags = [ 'e', 'x', 'w' ] + ["org", "loc", "per", "dat", "oth", "num", "dat:year"]
mtags_short = { "e":"e", 
              "x":"x", 
              "w":"w", 
              'org' : 'Org', 
              'loc': 'Loc', 
              'per': 'Per', 
              'dat': 'Dat',
              'oth': 'Oth', 
              'num': 'Num', 
              'dat:year': 'Year',
              '' : 'Not tagged',
              None : 'Not tagged'
}
mtags_human = { "e":"Error in the Corpus", 
              "x":"No need to tag", 
              "w":"Wordnet needs improvement", 
              'org' : 'Organization', 
              'loc': 'Location', 
              'per': 'Person', 
              'dat': 'Date/Time',
              'oth': 'Other (Name)', 
              'num': 'Number', 
              'dat:year': 'Date: Year',
              '' : 'Not tagged',
              None : 'Not tagged'
}



# LMC: THIS IS A TEST TO REDESIGN THE TAG BOX
def tbox(sss, cid, wp, tag, com):
    """Create the box for tagging entries: return a string"""
    box = "<span>"
    for i, t in enumerate(sss):

        box +="""<nobr><span style="color:#4D99E0;font-size:13px;
                  border-radius: 10px; background: #ededed;"
                  onchange="document.getElementById('tagword').submit(); 
                  return false">&nbsp;
                  <label for="cid_%s">%s<sub><font size='-2'>%s</font>
                  </sub></label>
                  <input type="radio" name="cid_%s" id="cid_%s" 
                  value="%s" %s >&nbsp;</span>&nbsp;</nobr>
               """ % (cid+str(i), str(i+1), t[-1], 
                      cid, cid+str(i), t,
                      " checked " if t==tag else "")

    for tk in mtags:
        tv = mtags_human[tk]
        box +=""" <nobr><span title="%s" style="color:#4D99E0;font-size:13px;
                   border-radius: 10px; background: #ededed;">&nbsp;
                  <label for="cid_%s"> %s </label>
                  <input type="radio" name="cid_%s" id="cid_%s" value="%s" 
                  onchange="document.getElementById('tagword').submit(); 
                  return false" %s >&nbsp;</span>&nbsp;</nobr>
               """ % (tv, 
                   cid+tk, 
                mtags_short[tk] if tk in mtags_short else tk, 
                cid, cid+tk, tk, 
                " checked " if tk==tag else "")

    # COMMENT
    comv = com if com is not None else '';
    box += """  <textarea style='font-size:12px; height: 25px; width: 100px;' 
    placeholder='Comment' onblur="document.getElementById('tagword').submit();"
    title= 'Comment' name='com_%s'>%s</textarea>""" % (cid, comv)

    box += "</span>"

    # box += """<span style="color: #4D99E0;" 
    #           onclick="document.getElementById('tagword').submit();">
    #           <i class='icon-ok-sign'></i></span>"""
    return box



################################################################################
# 2016.02.25 LMC  -- Checking Meta of CorpusDBs
################################################################################
def check_corpusdb(corpusdb):
   """ This function takes a corpusdb argument of form 'eng', 'eng1', 
       'engB' (etc.), and returns 4 statements: 
       1) whether it exists (self or False)
       2) version, i.e. if it's a master or copy ('master','A','B',...)
       3) the master db associated with it (can be self)
       4) the language of the database
       5) the db path
   """
   exists = False
   if corpusdb.endswith('.db'):
       dbpath = '../db/' + corpusdb
   else:
       dbpath = '../db/' + corpusdb + '.db'
   if os.path.isfile(dbpath):
       exists = corpusdb

   if exists:
       conn = sqlite3.connect(dbpath)
       c = conn.cursor()
       c.execute("""SELECT lang, version, master FROM meta""")
       (lang, version, master) = c.fetchone()
   else:
       (lang, version, master) = ('unknown', 'unknown', 'unknown')

   return (exists, version, master, lang, dbpath)

################################################################################

################################################################################
# 2016.02.25 LMC  -- Listable CorpusDBs
################################################################################
def all_corpusdb():

    corpusdb_list = [('eng','EnglishDB'), 
                     ('eng2','English2DB'),
                     ('cmn','ChineseDB'),
                     ('jpn','JapaneseDB'),
                     ('ita','ItalianDB'),
                     ('kor','KoreanDB')]

    return corpusdb_list

################################################################################




###
### get the synsets for a lemma
###
def lem2ss(c, lem, lang):
    """return a list of possible synsets for lang; backing off to lang1

    TODO(Wilson): Migrate to ntumc_tagdb.py?
    """
    lems = list(expandlem(lem))
    query = """
        SELECT DISTINCT synset 
        FROM word
        LEFT JOIN sense ON word.wordid = sense.wordid 
        WHERE lemma in (%s) 
            AND sense.lang = ?
        ORDER BY freq DESC
    """ % placeholders_for(lems)
    c.execute(query, list(lems) + [lang])
    rows = c.fetchall()
    # if not rows and lang != lang1:
    # w.execute("""SELECT distinct synset
    #              FROM word LEFT JOIN sense ON word.wordid = sense.wordid 
    #              WHERE lemma in (%s) AND sense.lang = ? and sense.status is not 'old'
    #              ORDER BY freq DESC""" % ','.join('?'*len(lems)), (lems + [lang1]))
    # rows = w.fetchall()
    # com_all='FW:eng'

    ### sort by POS
    return sorted([s[0] for s in rows], key=lambda x: x[-1])

def set_rest_x(c, usrname, sid, cid):
    query = """
        UPDATE concept 
        SET tag='x', usrname=? 
        WHERE ROWID=(
            SELECT bcon.ROWID 
            FROM cwl AS a
            INNER JOIN cwl AS b ON a.sid=b.sid AND a.wid=b.wid 
            LEFT JOIN concept AS acon ON a.sid=acon.sid AND a.cid=acon.cid
            LEFT JOIN concept AS bcon ON b.sid=bcon.sid AND b.cid=bcon.cid
            WHERE a.sid=? 
                AND a.cid=? 
                AND acon.tag NOT IN ('x', 'e') 
                AND bcon.tag IS NULL)
    """
    c.execute(query, (usrname, sid,cid))


def _deprecating(old, new):
    """This would look cooler as a decorator..."""
    warnings.warn(f'{old} has migrated to {new}', DeprecationWarning)


def placeholders_for(*args, **kwargs):
    """Depreciation wrapper for database._placeholders_for()"""
    _deprecating('ntumc_util.placeholders_for()', 'databases.placeholders_for()')
    return _placeholders_for(*args, **kwargs)
