#!/usr/bin/env python
  # -*- coding: utf-8 -*-

import cgi
import cgitb; cgitb.enable()  # for troubleshooting

import sqlite3
from collections import defaultdict as dd

#import nltk
#from nltk.corpus import wordnet as pwn

import sys, os

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
# <input type="submit" value="Search"/></form>""" % (sid_from, sid_to))
print("""<h2>Genres</h2>\n """)
dbdir='../db'
langs =  ['eng', 'cmn', 'ind', 'jpn', 'ita']
for lang in langs:
    dbfile = "%s/%s.db" % (dbdir, lang)
    if not os.path.isfile(dbfile):
      continue
    ##print("%s" % dbfile)
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
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
<p>yoursing is from ver 3, ver 5 (with headers) is available)
<hr>
<p><a href="http://compling.hss.ntu.edu.sg/ntumc/">More Information about the Corpus</a>
""")


def get_doc_stats(langs):
    doc_stats=dict()
    for lang in langs:
        dbfile = "%s/%s.db" % (dbdir, lang)
        if not os.path.isfile(dbfile):
            continue
        ##print("%s" % dbfile)
        conn = sqlite3.connect(dbfile)
        c = conn.cursor()
        c.execute('select docID, doc, title from doc')
        corpora = c.fetchall()
        for (docID, doc, title) in corpora:
            if docID not in doc_stats:
                doc_stats[docID]=dict()
            doc_stats[docID][lang] = dict()
            doc_stats[docID][lang]['title'] = title
            doc_stats[docID]['doc']   = doc
            c.execute('select count(sent) from sent where docID=?', (docID,))
            doc_stats[docID][lang]['sents'] = c.fetchone()[0]

            
    return doc_stats

print("""<h2>Documents</h2>\n """)

doc_stats = get_doc_stats(langs)

print("<table>")
for docID in doc_stats:
    print("<tr>")
    print("<th>{}</th><td>{}</td>".format(docID, doc_stats[docID].get('doc', '???')))
    for lang in langs:
        if lang in doc_stats[docID]:
            print("<td>{}</td>".format(doc_stats[docID][lang].get('title', '?')))
            print("<td>{}</td>".format(doc_stats[docID][lang].get('sents', 0)))
        else:
            print("<td><br></td>")
            print("<td><br></td>")
    print("</tr>")
print("</table>")

print("""</body></html>\n""")
