#!/usr/bin/env python3
 # -*- coding: utf-8 -*-

import cgi
import cgitb; cgitb.enable()
import sqlite3
import json

baseurl = '/var/www/ntumc/db'

with open("data/check_list.json") as fh:
     students = json.load(fh)
     
#students = [["s1", "engA", 110009, 110024]]


print("""Content-type: text/html; charset=utf-8\n
<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Corpus Tagging Statistics</title>
    <link rel="icon" type="image/svg" href="icon.svg">
    <!-- Bootstrap CSS -->
    <link rel="stylesheet"
	  href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"
	  integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh"
	  crossorigin="anonymous">

  </head>
<body class="container">
<div class="column">

<h1>Corpus Tagging Statistics</h1>

<p>This shows the percentage tagged.  Some concepts are pretagged by me with 'x'.

<p>If your tagging is finished (> 99% tagged) then your row will be coloured a reassuring green.  If you have not yet started (only my tags), then your row will be 
coloured a warning pink!



\n""")


print("""<table  class="table table-hover">
<caption>Amount Tagged</caption>
<thead>
  <tr>
    <th>Student ID</th>
    <th>% tagged</th>
    <th>Corpus</th>
    <th>Sentences</th>
    <th>% don't tag (x)</th>
    <th>% error in corpus (e)</th>
    <th>% error in wordnet (w)</th>
  </tr>
</thead>
""")

started = 0
nonedone = 0
alldone = 0

def percent(num, denom, decimals=1):
     return f"{100*num/denom:.1f}%"

print("<tbody>")
for (sid, crp, sfrom, sto) in students:
    corpus = f'{baseurl}/{crp}.db'
    #print(corpus)
    conn = sqlite3.connect(corpus)
    c = conn.cursor()
    c.execute("""SELECT COUNT(clemma) FROM concept
WHERE sid >= ? and sid <= ?""", (sfrom, sto))
    nconcepts=c.fetchone()[0]
    c.execute("""SELECT COUNT(clemma) FROM concept
WHERE sid >= ? and sid <= ? and tag is not ?""",	(sfrom, sto, None))
    ntagged=c.fetchone()[0]
    c.execute("""SELECT COUNT(clemma) FROM concept
WHERE sid >= ? and sid <= ? and tag = 'x'""",	(sfrom, sto))
    xtagged=c.fetchone()[0]
    c.execute("""SELECT COUNT(clemma) FROM concept
WHERE sid >= ? and sid <= ? and tag = 'e'""",	(sfrom, sto))
    etagged=c.fetchone()[0]
    c.execute("""SELECT COUNT(clemma) FROM concept
WHERE sid >= ? and sid <= ? and tag = 'w'""",	(sfrom, sto))
    wtagged=c.fetchone()[0]
    if  ntagged / nconcepts > 0.99:
         colour=' style=background-color:lightgreen'
         alldone += 1
    elif ntagged == xtagged:
         colour=' style=background-color:pink'
         nonedone +=1
    else:
         colour = ''
         started += 1 
    print(f"""  <tr{colour} >
    <td>{sid}</td>
    <td style='text-align:right'>{percent(ntagged, nconcepts)}</td>
    <td>{crp}</td>
    <td>{sfrom}&ndash;{sto}</td>
    <td style='text-align:right'>{percent(xtagged, nconcepts)}</td>
    <td style='text-align:right'>{percent(etagged, nconcepts)}</td>
    <td style='text-align:right'>{percent(wtagged, nconcepts)}</td>
  </tr>""")
print("</tbody>")
print("</table>")
      
print(f"""
<p>Finished: {alldone} ({percent(alldone, len(students))})
<p>Started: {started} ({percent(started, len(students))})
<p>Not yet started: {nonedone} ({percent(nonedone, len(students))})
""")



    

print("""<hr>
</div>
</body>
</html>
""")