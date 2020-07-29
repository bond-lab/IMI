#!/usr/bin/env python
  # -*- coding: utf-8 -*-

import cgi
import cgitb; cgitb.enable()  # for troubleshooting
from ntumc_webkit import HTML
import sqlite3
from collections import defaultdict as dd

#import nltk
#from nltk.corpus import wordnet as pwn

import sys, os

from ntumc_gatekeeper import concurs

form = cgi.FieldStorage()




########
# HTML
########

# Header
print("""Content-type: text/html; charset=utf-8\n
         <!DOCTYPE html>\n
           <html>\n
           <head>
<title>NTU-MC Corpus Statistics</title>
</head>
<body>\n""")

print("""<h1>Summary of the NTU-MC</h1>\n """)  ## add date?
print(HTML.status_bar('')) ### get user
# print("""<form action="" method="post" >
#          <span id="search">
#          <select id="search" name="search">""")

# datedrop = """<option value ='' selected>Select</option>
#               <option value ='e'>e</option>
#               <option value ='w'>w</option>
#               <option value ='ew'>w/e</option>
#               <option value ='ebylemma'>e (by lemma)</option>
#               <option value ='wbylemma'>w (by lemma)</option>
#               <option value ='ewbylemma'>e/w (by lemma)</option>"""
# print(datedrop)
# print("""</select>
# sid_from:<input type="text" size="7" name="sid_from" value="%s"/>
# sid_to:<input type="text" size="7" name="sid_to" value="%s"/>
# <input type="submit" value="\Search"/></form>""" % (sid_from, sid_to))
doc2corpus=dd(str)

print("""<h2>Genres</h2>\n """)
langs =  ['eng', 'cmn', 'ind', 'jpn', 'ita', 'zsm']
for lang in langs:
    dbfile = '%s.db' % lang
    try:
        conn, c = concurs(dbfile)
    except FileNotFoundError:
        continue

    c.execute("select doc, corpus from doc left join corpus on doc.corpusID=corpus.corpusID")
    for doc, corpus in c:
        if doc in doc2corpus:
            if corpus != doc2corpus[doc]:
                print("Warning", doc, corpus)
        else:
            doc2corpus[doc]=corpus
    c.execute('select corpusID, corpus, title from corpus')
    corpora = c.fetchall()
    print("<table>\n<caption>Corpora for %s</caption>" % lang)
    print("""<tr>
    <th>Corpus</th>
    <th>ID</th>
    <th>Sentences</th>
    <th>Words</th>
    <th>Concepts</th>
    <th>(Distinct)</th>
    <th>e</th>
    <th>w</th>
    <th>None</th>
    <th>Range</th></tr>""")  
    for (corpusID, corpus, title) in corpora:
        c.execute("""select count(sent) from sent 
 where docid in (select docid from doc where corpusID=?)""", (corpusID,))
        sents = c.fetchone()[0]
        c.execute("""select min(sid), max(sid) from sent 
where docid in (select docid from doc where corpusID = ?)""", (corpusID,))
        srange = c.fetchone()
        c.execute("""select count(word) from word 
where sid in (select sid from sent 
where (docid in (select docid from doc where corpusID=?)))""", (corpusID,))
        words=c.fetchone()[0]
        c.execute("""select count(cid), count(distinct tag) from concept 
where tag not in ('e', 'x') 
and sid in (select sid from sent 
where (docid in (select docid from doc where corpusID=?)))""", (corpusID,))
        concepts, dconcepts =c.fetchone()
        c.execute("""select count(cid) from concept 
        where tag in ('e') 
        and sid in (select sid from sent 
        where (docid in (select docid from doc where corpusID=?)))""", (corpusID,))
        econcepts=c.fetchone()[0]
        c.execute("""select count(cid) from concept 
        where tag in ('w') 
        and sid in (select sid from sent 
        where (docid in (select docid from doc where corpusID=?)))""", (corpusID,))
        wconcepts=c.fetchone()[0]
        c.execute("""select count(cid) from concept 
        where tag is Null 
        and sid in (select sid from sent 
        where (docid in (select docid from doc where corpusID=?)))""", (corpusID,))
        nconcepts=c.fetchone()[0]


        if sents > 0:
            print("""<tr>
  <td>{}</td>
  <td>{}</td>
  <td align='right'>{:,d}</td>
  <td align='right'>{:,d}</td>
  <td align='right'>{:,d}</td>
  <td align='right'>{:,d}</td>
  <td align='right'>{:,d}</td>
  <td align='right'>{:,d}</td>
  <td align='right'>{:,d}</td>
  <td align='center'>{}&ndash;{}</td>
</tr>""".format(title, corpus, 
            sents, words,
            concepts, dconcepts,
            econcepts, wconcepts, nconcepts,
            int(srange[0] or 0), 
            int(srange[1] or 0))) 

    print("</table>")

print("""<h4>Current known Issues</h4>
<p>not all the data is up
<p>Missing a lot of Japanese and English catb!
<p>yoursing is from ver 3, ver 5 (with headers) is available)
<hr>
<p><a href="http://compling.hss.ntu.edu.sg/ntumc/">More Information about the Corpus</a>
<hr>
""")


def get_doc_stats(langs):
    doc_stats=dict()
    id2doc=dd(dict) # id2doc[docID][lang] = doc
    for lang in langs:
        dbfile = '%s.db' % lang
        try:
            conn, c = concurs(dbfile)
        except FileNotFoundError:
            continue
        c.execute('select docID, doc, title from doc')
        corpora = c.fetchall()
        for (docID, doc, title) in corpora:
            id2doc[docID][lang] = doc
            if doc not in doc_stats:
                doc_stats[doc]=dict()
            doc_stats[doc][lang] = dict()
            doc_stats[doc][lang]['title'] = title
            doc_stats[doc]['ID']   = docID
        c.execute('select docID, count(sent) from sent group by docID')
        for (docID, count) in c.fetchall():
            doc_stats[id2doc[docID][lang]][lang]['sents'] = count
        c.execute("""select docID , (100* count(tag) / count(cid)) as ratio  
        from concept as c join sent as s on c.sid = s.sid 
        group by docID order by ratio""")
        for (docID, ratio) in c.fetchall():
             doc_stats[id2doc[docID][lang]][lang]['ratio'] = ratio
            
    return doc_stats

print("""<h2>Documents</h2>\n """)

doc_stats = get_doc_stats(langs)

print("""<p>For each document, for each language, show how many sentences and the percentage of concepts that are tagged: more than 80 is shown in green, more than 20 in orange, otherwise gray.""")

print("<table border>")
print("<tr>")
print("<td>Document</td>")
colspan='2'
for lang in langs:
    print(f"<td colspan='{colspan}'>{lang}</td>")
print("</tr>")

for doc in sorted(doc_stats, key=lambda x: doc2corpus[x]):
    print("<tr>")
    #print("<th>{}</th><td>{}</td>".format(docID, doc_stats[docID].get('doc', '???')))
    for lang in langs:
        if lang == 'eng':
            if lang in doc_stats[doc]:
                print("<td><a title='{}'>{}</a></td>".format(doc,doc_stats[doc][lang].get('title', '?')))
            else:
                print("<td><a title='{}'>{}</a></td>".format(doc,doc))
        if lang in doc_stats[doc]:
            print("<td>{}</td>".format(doc_stats[doc][lang].get('sents', 0)))
            ratio = int(doc_stats[doc][lang].get('ratio', 0))
            if ratio > 80:
                bc = 'green'
            elif ratio > 20:
                bc = 'orange'
            else:
                bc = 'grey'
            print("<td style='background-color:{};'>{}</td>".format(bc, ratio))
        else:
            print("<td><br></td>")
            print("<td><br></td>")
    print("</tr>")
print("</table>")

print("""</body></html>\n""")
