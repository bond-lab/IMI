#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
#import cgitb; cgitb.enable()  # for troubleshooting
import re, sqlite3, collections
import sys,codecs 
import operator
#sys.stdout = codecs.getwriter('utf8')(sys.stdout)
from collections import defaultdict as dd

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
    sys.stderr.write((u"%s\n" % unicode(msg)).encode("ascii","ignore"))
    try:
        with codecs.open("../log/ntumc.txt", "a", encoding='utf-8') as logfile:
            logfile.write(u"%s\n" % unicode(msg))
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
        jilog(u"%s - Note=[%s]\n" % (self, unicode(task_note)))
        return self

#############################################################
# NTU-MC shared functions
#############################################################

def expandlem (lemma):  ### keep in sync with tag-lexs
    lems=set()
    lems.add(lemma)
    lems.add(lemma.lower())
    lems.add(lemma.replace('-',''))
    lems.add(lemma.replace('-','_'))
    lems.add(lemma.replace(' ','-'))
    lems.add(lemma.replace('_',''))
    lems.add(lemma.replace(' ',''))
    lems.add(lemma.upper())
    lems.add(lemma.title())
    # lems.add(lemma.replace('_',u'∥'))
    # lems.add(lemma.replace('-',u'∥'))
    # lems.add(lemma.replace(u'・',u'∥'))
    # lems.add(lemma.replace(u'ー',u'∥'))
    # lems.add(lemma.replace(' ',u'∥'))
    return lems

def pos2wn (pos, lang, lemma=''):
    ### FIXME: check and document --- Change POS for VN?
    if lang == 'jpn':
        if pos in [u'名詞-形容動詞語幹', u"形容詞-自立", u"連体詞"] \
                and not lemma in [u"この", u"その", u"あの"]:
            return 'a'
        elif pos in [u"名詞-サ変接続",  u"名詞-ナイ形容詞語幹", 
                     u"名詞-一般", u"名詞-副詞可能",  
                     u"名詞-接尾-一般", u"名詞-形容動詞語幹", 
                     u"名詞-数",  u"記号-アルファベット"]:
            return 'n'
        elif pos == "動詞-自立":
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
mtags_human = { "e":"e", 
              "x":"x", 
              "w":"w", 
              'org' : 'Organization', 
              'loc': 'Location', 
              'per': 'Person', 
              'dat': 'Date/Time',
              'oth': 'Other', 
              'num': 'Number', 
              'dat:year': 'Date: Year',
              '' : 'Not tagged',
              None : 'Not tagged'
}


def tbox(sss, cid, wp, tag, ntag, com):
    """Create the box for tagging entries: return a string"""
    box = "<span style='background-color: #eeeeee;'>"  ### FIXME cute css div
    for i, t in enumerate(sss):
        # 2012-06-25 [Tuan Anh]
        # Prevent funny wordwrap where label and radio button are placed on different lines
        box +="<span style='white-space: nowrap;background-color: #dddddd'><input type='radio' name='cid_%s' value='%s'" % (cid, t)
        if (t == tag):
            box += " CHECKED "
        if wp == t[-1]:
            box += " />%d<sub><font color='DarkRed' size='-2'>%s</font></sub></span>\n" % (i+1, t[-1])
        else:
            box += " />%d<sub><font size='-2'>%s</font></sub></span>\n" % (i+1, t[-1])
    for tk in mtags:
        # 2012-06-25 [Tuan Anh]
        # Friendlier tag value display
        tv = mtags_human[tk]
        box +="""<span style='white-space: nowrap;background-color:#dddddd'>
  <input type='radio' name='cid_%s' title='%s' value='%s'""" % (cid, tv, tk)
        if (tk == tag):
            box += " CHECKED "
        show_text = mtags_short[tk] if mtags_short.has_key(tk) else tk
        box += " /><span title='%s'>%s</span></span>\n" % (tv, show_text)
    tagv=''
    if unicode(tag) != unicode(ntag):
        tagv=ntag
    if tagv:
        box += """<span style='background-color: #dddddd;white-space: nowrap;border: 1px solid black'>%s</span>""" % tagv
#     box += """
# <input style='font-size:12px; background-color: #ececec;' 
#  title='tag' type='text' name='ntag_%s' value='%s' size='%d'
#  pattern ="loc|org|per|dat|oth|[<>=~!]?[0-9]{8}-[avnr]"
#  />""" % (cid, tagv, 8)
    comv = com if com is not None else '';
    box += """  <textarea style='font-size:12px; height: 18px; width: 150px; 
  background-color: #ecffec;' placeholder='comment (multiline ok)'
  title= 'comment' name='com_%s'>%s</textarea>""" % (cid, comv)

    box += "</span>"  ### FIXME cute css div
    return box

###
### get the synsets for a lemma
###
def lem2ss(c, lem, lang):
    """return a list of possible synsets for lang; backing off to lang1"""
    lems = list(expandlem(lem))
    c.execute("""SELECT distinct synset 
             FROM word LEFT JOIN sense ON word.wordid = sense.wordid 
             WHERE lemma in (%s) AND sense.lang = ?
             ORDER BY freq DESC""" % ','.join('?'*len(lems)), (lems + [lang]))
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
    query="""
UPDATE concept SET tag='x', usrname=? 
WHERE ROWID=(
    SELECT bcon.ROWID 
    FROM cwl AS a INNER JOIN cwl AS b ON a.sid=b.sid AND a.wid=b.wid 
    LEFT JOIN concept AS acon ON a.sid=acon.sid and a.cid=acon.cid
    LEFT JOIN concept AS bcon ON b.sid=bcon.sid and b.cid=bcon.cid
    WHERE a.sid=? and a.cid=? and acon.tag not in ('x', 'e') AND bcon.tag IS NULL
)"""
    c.execute(query, (usrname, sid,cid))
