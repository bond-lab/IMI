#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
http://192.168.1.144/ntumc/cgi-bin/test.cgi?corpus=eng&lang=eng&lemma=%E8%B7%B3&Query=&lim=-1
"""

import cgi
import cgitb; cgitb.enable()
import http.cookies
from urllib import parse as uparse

import sys
import os
from importlib import reload

if os.name == 'posix':
    sys.getfilesystemencoding = lambda: 'utf-8'
    reload(os)




def echo(s):
    print(f'<p>{s}</p>')

def br():
    print('<br>')

_dec = uparse.unquote
_enc = uparse.quote
class UrllibCookie(http.cookies.SimpleCookie):
    pass
    def value_decode(self, val):
        return val, _dec(val)
    def value_encode(self, val):
        strval = str(val)
        return strval, _enc(strval)


testval = '跳'


print("Content-type: text/html; charset=utf-8\n\n")
print("""
<html>
<body>""")

echo(f'<a href="test2.cgi?testval={testval}">'
      'Click to go to test page, which injects some chinese into your cookie'
      '</a>')

# echo(f'<a href="test3.cgi?testval={testval}">'
#       'Click to go to second test page, which uses urllib.parse.quote to inject'
#       '</a>')



C = http.cookies.SimpleCookie()
if 'HTTP_COOKIE' in os.environ:
    C = http.cookies.SimpleCookie(os.environ['HTTP_COOKIE'])



C['__objenctest'] = testval
echo(f'testval = {C["__objenctest"]}')
echo('Writing and reading from cookie seems fine')

form = cgi.FieldStorage()
fr = form.getfirst('from', None)

if fr:
    echo(f'I see you redirected from test{fr}.cgi')
    
    t = C['__test'].value
    # if fr == '3':
    #     echo(f'Unquoting with urllib.parse.unquote')
    #     t = uparse.unquote(t)
    
    echo('Reading the stored value: %s' % t)

echo(f'fsencoding = {sys.getfilesystemencoding()}')

echo('Printing the whole cookie recovered from os.environ["HTTP_COOKIE"]:')
# sys.stdout = codecs.getwriter('utf8')(sys.stdout, errors='backslashreplace')
print(C)

print("""
</html>
""")
