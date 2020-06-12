#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
import cgitb; cgitb.enable()
import http.cookies
import os


def echo(s):
    print(f'<p>{s}</p>')

# Fetch or create a cookie
C = http.cookies.SimpleCookie()
if 'HTTP_COOKIE' in os.environ:
    C = http.cookies.SimpleCookie(os.environ['HTTP_COOKIE'])

# Populate cookie with test value
form = cgi.FieldStorage()
test = form.getfirst('testval', '跳')

C['__test'] = test

# Headers to set cookie, redirect
with open('temp.txt', 'w', encoding='utf-8') as f:
    f.write(str(C))
print(C)
# with open('temp.txt', 'w') as f:
#     f.write(str(C))
# print("""Location: test.cgi?from=2""")

print("""Content-type: text/html; charset=utf-8\n""")

echo(f'Pushed this key-value pair into your cookie:')
echo(f'__test = "{test}"')
