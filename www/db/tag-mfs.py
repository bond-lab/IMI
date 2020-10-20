#
#
# usage tag-mfs.py src tgt
# get frequencies from src (+pwn)
# tag target
# what to do with 'x'?
# what to do with MWE?
#

srcdb = "engC.db"
srcdocs =  ['spec', 'danc', 'redh', 'scan']
sentifile='merge.tsv'
tgtdb = "engD.db"
tgtfrom = 48505
tgtto = 49505


from nltk.corpus import wordnet as wn
import sqlite3
from collections import defaultdict as dd
#from functools import lru_cache
#from scipy.stats import entropy
import sys

freq = dd(lambda: dd(int))

def ss2id(ss):
    pos = ss.pos().replace('s', 'a')
    return "{:08d}-{}".format(ss.offset(), pos)

smoothie = 0.1
###
### get frequencies
###
### PWN
###
def pwn(freq):
    ls = set() ### all the lemmas
    tf = int() ### total frequency
    for s in wn.all_synsets():
        for l in s.lemmas():
            if l.count() > 0:
                freq[l.name().replace('_', ' ')][ss2id(s)] += l.count()
                ls.add(l)
                tf +=1
            elif l.count() == 0:
                ### smooth
                freq[l.name().replace('_', ' ')][ss2id(s)] += smoothie
                
    print("Added PWN: \t{} lemmas, {} occurrences".format(len(ls),tf),
          file=sys.stderr)

###
### ntumc
###

def ntumc(freq, docs, weight=1):
    """Add frequencies from documents in corpus"""
    ls = set() ### all the lemmas
    tf = int() ### total frequency   
    conn = sqlite3.connect(srcdb)
    c = conn.cursor()
    constraints = [] 
    for doc in docs:
        c.execute("""select min(sid), max(sid) from sent 
        where docid = (select docid from doc where doc = ?)
        """, (doc,))
        for (smin, smax) in c:
            constraints.append("(sid >= {} and sid <=  {})".format(smin, smax))
    c.execute("""
    SELECT TRIM(clemma), TRIM(tag) FROM concept
    WHERE """ + " OR ".join(constraints))
    for (l, t) in c:
        if t is None:  # if not annotated ignore
            continue
        freq[l][t] += weight
        #print (l,t)
        ls.add(l)
        if t not in ('x', 'e'):  # don't count errors and don't tag
            tf += 1
    print("Added NTUMC: \t{} lemmas, {} occurrences".format(len(ls),tf),
          file=sys.stderr)


        
#@lru_cache(maxsize=256)
def mfs(l, pos, freq):
    """Return the most frequent sense if I have seen this before
       If it is monosemous return that sense
       Otherwise return None"""
    ### FIXME use the POS
    if pos == '@':
        return 'x' ### don't tag
    if l in freq:
        senses = sorted([(freq[l][s], s) for s in freq[l]], reverse=True)
        if senses[0][0] > smoothie or len(senses) == 1:
            return senses[0][1]
        else:
            return None
    else:
        return None

### debug
def testme(freq):
    for l in freq:
#    print(l, list(freq[l].values()))
        # print ("\n{} (entropy = {})".format(l,
        #                                     entropy(list(freq[l].values())), base=2))
        for s in freq[l]:
            print (l, s, freq[l][s],sep='\t')
           

            for w, p in [('the', 'x'), ('in', 'x'), ('have', 'v'),
                         ('bank', 'n'), ('dog-cart', 'n'), ('hobbit', 'n'),
                         ('Frodo', 'n'), ('splonge', 'v'), ('dehydration', 'n') ]:
                print(w, p, mfs(w, p, freq), sep='\t')

def pos2wn (pos):
    """Take PTB POS and return wordnet POS
       a, v, n, r, x or @ 'don't tag'
       z becomes z"""
    if pos in "CC EX IN MD POS RP VAX TO".split():
        return '@'
    elif pos in "PDT DT JJ JJR JJS PRP$ WDT WP$".split():
        return 'a'
    elif pos in "RB RBR RBS WRB".split():
        return 'r'
    elif pos in "VB VBD VBG VBN VBP VBZ".split():
        return 'v'
    elif pos == "UH": # or titles
        return 'x'
    elif pos == "z": # phrase
        return 'z'
    else: #   CD NN NNP NNPS NNS PRP SYM WP
        return 'n';



                
def tagdb(tgtdb, tgtfrom, tgtto, freq, senti):
    """Tag the DB with MFS"""
    ### FIXME use POS
    ### FIXME harmonize SWE and MWE
    ### 
    sentiment_threshold = 0.05
    conn = sqlite3.connect(tgtdb)
    c = conn.cursor()
    d = conn.cursor()
    ### delete the sentiment
    c.execute("""
    DELETE FROM sentiment
    WHERE sid >=? and sid <=?""", (tgtfrom, tgtto))
    ### get wids 
    cwl = dd(list)
    c.execute("""
    SELECT sid, cid, wid FROM cwl
    WHERE sid >=? and sid <=?
    ORDER by sid, cid, wid
    """, (tgtfrom, tgtto))
    for sid, cid, wid in c:
        cwl[(sid, cid)].append(wid)
    word = {}
    c.execute("""
    SELECT sid, wid, word, pos, lemma FROM word
    WHERE sid >=? and sid <=?
    """, (tgtfrom, tgtto))
    for sid, wid, w, pos, lemma in c:
        #print  (w, pos, lemma)
        word[(sid, wid)] = (w, pos, lemma)
    concepts = {}
    c.execute("""
    SELECT sid, cid, clemma, tag FROM concept
    WHERE sid >=? and sid <=?""", (tgtfrom, tgtto))
    good = 0
    bad = 0
    for (sid, cid, clemma, tag) in c:
        ### fixme use the actual POS
        if len(cwl[(sid, cid)]) == 1:
            pos = word[(sid, cwl[(sid, cid)][0])][1]
        else:
            pos = 'z' #phrase (MWE)
        wp = pos2wn(pos)
        newtag=mfs(clemma, wp, freq)
        if newtag is None and pos == "NNP": 
            newtag = 'per'   # more common than 'loc' by a factor of 2
        if pos == 'z':
            pmatch = 'pos-mwe'
        elif newtag and (newtag[-1] == wp):
            pmatch = 'pos-match'
        else:
            pmatch = 'pos-none'
        print(sid, cid, pos, wp, tag, newtag, pmatch, tag==newtag, clemma, sep='\t')
        if tag==newtag:
            good +=1
        else:
            bad += 1
            d.execute("""
            UPDATE CONCEPT SET tag = ?
            WHERE sid=? and cid=?""", (newtag, sid, cid))
            ### adduser
        sentiment = senti[newtag]
        #print (sentiment, newtag) 
        if sentiment > sentiment_threshold:
            d.execute("""INSERT INTO sentiment (sid,cid,score,username)
VALUES(?,?,?,?)""", (sid, cid, sentiment, "tag-mfs"))
            print ("SENTIMENT", sentiment, newtag) 
            
    print("Accuracy:", good / (good+bad), good, bad)
    conn.commit()

def getsenti(filename):
    """get the sentiment values from a file"""
    senti=dd(float)
    fh =  open(filename)
    for l in fh:
        (ss,score) = l.strip().split('\t')
        ### ignore low values (not confident)
        if abs(float(score)) < 0.2:
            score = 0.0
        senti[ss] = 100 * float(score)
    print("Read sentiment for: \t{} synsets".format(len(senti)),
          file=sys.stderr)
    return senti

pwn(freq)
senti = getsenti(sentifile)
ntumc(freq,srcdocs, weight=3)

#print(senti)
#testme(freq)
tagdb(tgtdb,tgtfrom, tgtto,freq,senti)

