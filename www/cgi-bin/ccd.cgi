#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import re, sqlite3, collections
import operator
from collections import namedtuple, defaultdict as dd

ccd_path = '../data/CCD.txt'

ccd_row = namedtuple(
    'CCD_Row',
    ['id1',
     'id2',
     'word',
     'field3',
     'pinyin',
     'field5',
     'pos',
     'field7',
     'sense',
     'example']
)

#backoff_re = re.compile(r'^(?P<id>\d+)\t#\s'
#                        ur'\u3010(?P<word>[^\u3011]+)\u3011'
#                        ur'\s*(?P<pinyin>[<>­-, ·\'’“”()\[%ɡ∥0123456789'
#                        ur'aáÁàÀǎāĀbBcCdDeéÉèÈĔěēĒfFgGhHiIíìǐījJkKlLmMḿnNo'
#                        ur'OóòǒōŌpPqQr RsStTuúùǔüǘǜǚūvwWxXyYzZα])'
#                        r'(?<rest>.*)$',
#                        re.UNICODE)

def load_ccd(path):
    d = dd(list)
    f = open(path, 'r', encoding='utf-8')
    header = next(f)
    nonblank = lambda s: s.strip() != ''
    for line in filter(nonblank, f):
        fields = line.strip().split('\t')
        try:
            row = ccd_row(*fields)
            d[row.word].append(row)
        except TypeError:
            continue
    return d

ccd = load_ccd(ccd_path)

form = cgi.FieldStorage()

lemma = form.getfirst("lemma", "")
lemma = lemma.strip()

print("Content-type: text/html; charset=utf-8\n")
print("<html>")
print("  <head>")
print("    <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>")
print("    <meta http-equiv='content-language' content='zh'>")
print("    <title>%s</title>" % (lemma))
print("  </head>")
print("  <body>")
print("""
<form method="post" action="ccd.cgi">
  <input type="text" name="lemma" value="%s">
  <input type="submit" name="Query" value="Search">
</form>
""" % (lemma,))

results = ccd.get(lemma, [])
if lemma and len(results) == 0:
    print('  <p style="font-size:2em">No results found for %s</p>' % lemma)
else:
    print('  <dl>')
    for row in results:
        _dt = ['%s' % row.word]
        if row.pinyin != 'None':
            _dt.append('%s' % row.pinyin)
        print('    <dt style="font-size:2em">%s</dt>' % (' '.join(_dt)))
        _dd = []
        if row.pos != 'None':
            _dd.append('[%s]' % row.pos)
        if row.sense != 'None':
            _dd.append(row.sense)
        if row.example != 'None':
            _dd.append(u'\u300C%s\u300D' % row.example)
        if len(_dd) > 0:
            print('    <dd style="font-size:1.5em">%s</dd>' % (' '.join(_dd)))
    print('  </dl>')

print("""
  <p style="font-size:1em">
    This CCD dictionary has been lent to us for research purposes; it may not
    be copied or redistributed.
  </p>
""")
print("  </body>")
print("</html>")

