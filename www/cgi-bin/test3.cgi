#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import cgi
import cgitb; cgitb.enable()
import http.cookies
import os

from urllib import parse as uparse


_dec = uparse.unquote
_enc = uparse.quote
class UrllibCookie(http.cookies.SimpleCookie):
    def value_decode(self, val):
        return val, _dec(val)
    def value_encode(self, val):
        strval = str(val)
        return strval, _enc(strval)


def echo(s):
    print(f'<p>{s}</p>')

# Fetch or create a cookie
C = UrllibCookie()
if 'HTTP_COOKIE' in os.environ:
    C = UrllibCookie(os.environ['HTTP_COOKIE'])

# Populate cookie with test value
form = cgi.FieldStorage()
test = form.getfirst('testval', '跳')

C['__test'] = test

# Headers to set cookie, redirect
print(C)
print("""Location: test.cgi?from=3""")

print("""Content-type: text/html; charset=utf-8\n""")

echo(f'Pushed this key-value pair into your cookie:')
echo(f'__test = "{test}"')
