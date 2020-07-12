#!/usr/bin/env python3
# -*- coding: utf-8 -*-
### fix some of the easy to fix bad tags
###
# FIXME(Wilson) importing from pysqlite2 was for the regex matching extension
#   since that chunk is commented out, should revert to plain sqlite3 import?
##import sqlite3
from pysqlite2 import dbapi2 as sqlite3

from nltk.corpus import wordnet as wn
from collections import defaultdict as dd

words = dd(set)
for pos in ['a', 'v', 'n', 'r']:
    for l in wn.all_lemma_names(pos):
        words[pos].add(l)
        words['x'].add(l)
def pl2sg (word):
    sg = word
    if word.endswith('ies') and word[:-3]+'y' in words['n']:
        sg = word[:-3]+'y'
    elif word.endswith('es') and word[:-2] in words['n']:
        sg = word[:-2]
    elif word.endswith('s') and word[:-1] in words['n']:
        sg = word[:-1]
    return sg

dbdir = ''

dbs = dict()

dbs['eng'] = ["eng-yoursing.db", "eng-story.db", "eng-essay.db"]
dbs['eng'] = ["eng-story.db"]

    

for lang in dbs:
    for db in dbs[lang]:
        print("Fixing %s: " % db)
        conn = sqlite3.connect(dbdir + db)
        conn.enable_load_extension(True)
        conn.load_extension("/usr/lib/sqlite3/pcre.so")
        conn.enable_load_extension(False)
        c = conn.cursor()
        d = conn.cursor()
        c.execute("UPDATE sent SET sent=trim(sent);")
        c.execute("UPDATE concept SET tag=trim(tag);")
        c.execute("UPDATE concept SET comment=trim(comment);")
        try:
            c.execute("ALTER TABLE word ADD COLUMN comment TEXT")
        except:
            pass # handle the error
        ## load regexpg
        ## fix punctuation (shoudl do in pos tagger)
        ## [ 〔 ――
        # for punct in [u'[', u'〔', u'――', u'"', u'(', u')', u'--', u'®', u'–', u'―',
        #               "'", '"']:
        #     print('"%s"' %  punct)
        #     c.execute("update word set pos='PU' where lemma=?;" , (punct,))
        #     c.execute("update concept set tag='p' where clemma=?;", (punct,))
        # ## Dates
        # c.execute(u"update concept set tag='dat:year' WHERE clemma REGEXP '^[一二三四五六七八九十]+年$' and clemma not in ('前年', '元年');")
        # c.execute(u"update concept set tag='dat:year' WHERE clemma REGEXP '^[０１２３４５６７８９]+年$' and clemma not in ('前年', '元年');")
        # c.execute(u"update concept set tag='dat:year' where cid in (SELECT cid FROM concept left join word on concept.sid == word.sid and (concept.wid == word.wid -1) where  lemma = '年' and clemma REGEXP '^[0-9]+')")
        # ### URLS
        
        # ### Plural
        # c.execute("update word set lemma= substr(word,0,3), comment='pl' where word like '%们' and pos = 'NN' and length(word) > 2;")

        ### mark unknowns
        c.execute("""select w.sid, w.wid, lemma, pos from word as w 
                     left join concept as c on w.sid=c.sid and w.wid=c.wid 
                     where pos not in ('PRP', 'PRP$', 'WP', 'WRB', 'EX', 'WDT', 'DT', 'RP', 'POS', 'WP$', 'NNP', 'IN', 'MD', 'TO', 'CC') 
                     and tag is null and tags is null and pos not like 'F%' and pos not like 'Z%';""")
        for (sid, wid, lemma, pos) in c:
            if not ((pos == "RB" and lemma in "because else".split())
                    or (pos == "NN" and lemma in "quo where everyone else how".split())
                    ## Assume we got the verbs right
                    or (pos == "RB" and lemma in "'ll".split())
                    or (pos.startswith("V") and lemma in "have be 're 'll 'm 've".split())):
                        print( "set to unknown: %s (%s)" % (lemma, pos))
                        # if db == "eng-story.db" and sid < 11000:
                #     (maxcid,) = d.execute("SELECT MAX(cid) FROM concept join sent where concept.sid=sent.sid and sent.scid =1").fetchone()
                # else:
                #     (maxcid,) = d.execute("SELECT MAX(cid) FROM concept").fetchone()
                # newcid = maxcid + 1
                # d.execute("INSERT INTO concept(sid, cid, wid, tag, clemma, comment) VALUES (?,?,?,?,?,?)", 
                #           (sid, newcid, wid, 'u', lemma, 'unk'))

        c.execute(u"select sid, wid, word from word where word like '%-%'")
        for (sid, wid, word) in c:
            result = ['???']
            if word == '--':
                result = [u'—']
            elif word.lower()  in words['x']:
                result = [word];
            elif word.replace('-', '_').lower()  in words['x']:
                result = [word.replace('-', '_')]
            elif word.replace('-', '').lower()  in words['x']:
                result = [word.replace('-', '')]
            elif pl2sg(word.lower())  in words['x']:
                result = [pl2sg(word.lower())]
            elif pl2sg(word.replace('-', '_').lower())  in words['x']:
                result = [pl2sg(word.replace('-', '_').lower())]
            elif pl2sg(word.replace('-', '').lower())  in words['x']:
                result = [pl2sg(word.replace('-', '').lower())]
            elif word.lower().endswith('-like'):
                result = [word.lower()[:-5], '-like']
            print("%d\t%s\t%s\t(%s)" % (sid, wid, word, ", ".join(result)))
        c.execute(u"select sid, wid, word, pos, lemma from word where lemma = '1' and word not in ('1', 'one')")
        for (sid, wid, word, pos, lemma) in c:
            ##print("\t".join([str(sid), str(wid), str(word), str(pos), str(lemma)]))
            d.execute('UPDATE word SET lemma = ? where sid = ? and wid =?', 
                      (word.lower(), sid, wid))
            if word.lower() in ['a', 'an']:
                d.execute('DELETE from concept where clemma = ? and sid = ? and wid =?', 
                          ('1', sid, wid))
            else:
                d.execute('UPDATE concept set clemma = ? where clemma = ? and sid = ? and wid =?', 
                          (word.lower(), '1', sid, wid))  
        d.execute("UPDATE word SET pos='DT' where word='a' and lemma='a'")
        d.execute("UPDATE word SET pos='DT' where word='an' and lemma='an'")
        c.execute(u"delete from concept where clemma = 'may_1'")
        def splitw (word, words, concept, concepts):
            c.execute("select sid, wid from word where word=? and pos=? and lemma=?", word)
            for (sid, wid) in c:
                ### make some space
                d.execute("select max(wid) from word where sid=?", (sid,))
                maxwid = d.fetchone()[0]
                ### clear old stuff
                d.execute("DELETE FROM word where  sid= ?  and wid =?", (sid, wid))
                d.execute("DELETE FROM concept where  sid= ?  and wid =?", (sid, wid))
                ## make room
                for wi in range(maxwid, wid, -1):
                    d.execute("UPDATE word SET wid =? where sid=? and wid=?", (wi + len(words) -1, sid, wi)) 
                    d.execute("UPDATE concept SET wid =? where sid=? and wid=?",  (wi + len(words) -1, sid, wi)) 
                ## add words
                for i in range(len(words)):
                    d.execute("INSERT INTO word(sid,wid,word,pos,lemma) VALUES (?,?,?,?,?)", 
                              (sid, wid+i, words[i][0], words[i][1], words[i][2]))
                ## insert concepts
                (maxcid,) = d.execute("SELECT MAX(cid) FROM concept").fetchone()
                newcid = maxcid + 1    
                if concept:
                    d.execute("INSERT INTO concept(sid, wid, cid, clemma, tag, tags) VALUES (?,?,?,?,?,?)", 
                              (sid, wid, newcid, concept[0], concept[1], concept[2]))
                    newcid +=1 
                for i in range(len(concepts)):
                    if concepts[i]:
                        d.execute("INSERT INTO concept(sid, wid, cid, clemma, tag, tags) VALUES (?,?,?,?,?,?)", 
                                  (sid, wid, newcid, concepts[i][0], concepts[i][1], concepts[i][2]))
                        newcid +=1 
        splitw(("ten_seconds", "Zu", "tm_s:10"), 
               [("ten", "Z", "10"), ("seconds", "NNS", "second")],
               (),     
               [(),
                ("second", "15235126-n", "02202146-a; 01016436-a; 04164529-n; 13611395-n; 07180372-n; 10568083-n; 15235126-n; 13846546-n; 00723783-n; 03587050-n; 15244650-n; 15246853-n; 00102881-r; 02556817-v; 02393304-v")])
        splitw(("a_second", "Zu", "TM_s:1"), 
               [("a", "DT", "a"), ("second", "NN", "second")],
               (),     
               [(),
                ("second", "02202146-a", "02202146-a; 01016436-a; 04164529-n; 13611395-n; 07180372-n; 10568083-n; 15235126-n; 13846546-n; 00723783-n; 03587050-n; 15244650-n; 15246853-n; 00102881-r; 02556817-v; 02393304-v")])
        splitw(("No.", "NNP", "no."), 
               [("No", "RB", "no"), (".", "Fp", ".")],
               (),     
               [("no", "00024356-r", "00024356-r; 14647722-n; 07205104-n; 00024587-r; 00050681-r; 02268485-a"),
                ()])
        splitw(("dancing-men", "NNS", "dancing-men"), 
               [("dancing", "VBG", "dance"), ("-men", "NNS", "man")],
               (),     
               [("dance", "01894649-v", "01894649-v; 00428270-n; 01708676-v; 07020538-n; 08253141-n; 07448717-n; 02099075-v"),
                ("man", "10287213-n", "08887716-n; 10289176-n; 02420991-v; 02472987-n; 10288516-n; 10289039-n; 10745332-n; 10287213-n; 10288763-n; 10582746-n; 03716327-n; 01088547-v; 02472293-n")])
        splitw(("fifty-pound", "JJ", "fifty-pound"), 
               [("fifty", "Z", "50"), ("-pound", "NN", "pound")],
               (),     
               [(),
                ("pound", "13686660-n", "06809756-n; 13695420-n; 13694936-n; 03993703-n; 13693641-n; 13648184-n; 13720302-n; 01175316-n; 13695674-n; 13686660-n; 13694017-n; 13694657-n")
                ])
        splitw(("powder-marking", "JJ", "powder-marking"), 
               [("powder", "NN", "powder"), ("-marking", "NN", "marking")],
               (),     
               [("powder", "15016314-n", "00332154-v; 14997012-n; 00042173-v; 15016314-n; 03994008-n"),
                ("marking", "04680285-n", "07270179-n; 04680285-n; 00263642-n; 00874977-n")])
        splitw(("dr._roylot", "JJ", "powder-marking"), 
               [("powder", "NN", "powder"), ("-marking", "NN", "marking")],
               (),     
               [("powder", "15016314-n", "00332154-v; 14997012-n; 00042173-v; 15016314-n; 03994008-n"),
                ("marking", "04680285-n", "07270179-n; 04680285-n; 00263642-n; 00874977-n")])
        splitw(("1100_pounds", "Zm", "$_gbp:1100"), 
               [("1100", "Z", "1100"), ("pounds", "NNS", "pound")],
               (),     
               [(),
                ("pound", "13686660-n", "06809756-n; 13695420-n; 13694936-n; 03993703-n; 13693641-n; 13648184-n; 13720302-n; 01175316-n; 13695674-n; 13686660-n; 13694017-n; 13694657-n")
                ])
        splitw(("750_pounds", "Zm", "$_gbp:750"), 
               [("750", "Z", "750"), ("pounds", "NNS", "pound")],
               (),     
               [(),
                ("pound", "13686660-n", "06809756-n; 13695420-n; 13694936-n; 03993703-n; 13693641-n; 13648184-n; 13720302-n; 01175316-n; 13695674-n; 13686660-n; 13694017-n; 13694657-n")
                ])
        splitw(("250_pounds", "Zm", "$_gbp:250"), 
               [("250", "Z", "250"), ("pounds", "NNS", "pound")],
               (),     
               [(),
                ("pound", "13686660-n", "06809756-n; 13695420-n; 13694936-n; 03993703-n; 13693641-n; 13648184-n; 13720302-n; 01175316-n; 13695674-n; 13686660-n; 13694017-n; 13694657-n")
                ])
        splitw(("1000_pounds", "Zm", "$_gbp:1000"), 
               [("1000", "Z", "1100"), ("pounds", "NNS", "pound")],
               (),     
               [(),
                ("pound", "13686660-n", "06809756-n; 13695420-n; 13694936-n; 03993703-n; 13693641-n; 13648184-n; 13720302-n; 01175316-n; 13695674-n; 13686660-n; 13694017-n; 13694657-n")
                ])
        splitw(("five_miles", "Zu", "ln_mi:5"), 
               [("five", "Z", "5"), ("miles", "NNS", "mile")],
               (),     
               [("5", "02186750-a", "02186750-a; 13744521-n"),
                ("mile", "13651218-n", "13655414-n; 13660868-n; 13776342-n; 07469325-n; 13660619-n; 13655262-n; 13651218-n; 13660337-n")])
        splitw(("seven_miles", "Zu", "LN_mi:7"), 
               [("seven", "Z", "7"), ("miles", "NNS", "mile")],
               (),     
               [("7", "02186970-a", "02186970-a; 13744916-n"),
                ("mile", "13651218-n", "13655414-n; 13660868-n; 13776342-n; 07469325-n; 13660619-n; 13655262-n; 13651218-n; 13660337-n")])
        

        ### Fix sherlock
        c.execute("update concept set tag ='09604451-n' where clemma like '%sherlock%' or clemma like '%holmes%';")
        conn.commit()
        c.close()
        d.close()

## split word (
## WORD: (word, pos, lemma)
## REPLACEMENT: [(word, pos, lemma), (word, pos, lemma)])
## MWE CONCEPT: (clemma, tag, tags)
## SWE CONCEPTS [(), (clemma, tag, tags)])
## splitw(("ten_seconds", "Zu", "tm_s:10"), [("ten", z, "10"), ("seconds", "NNS", "second")],
##        (),     [(),("second", "15235126-n", "02202146-a; 01016436-a; 04164529-n; 13611395-n; 07180372-n; 10568083-n; 15235126-n; 13846546-n; 00723783-n; 03587050-n; 15244650-n; 15246853-n; 00102881-r; 02556817-v; 02393304-v")])





