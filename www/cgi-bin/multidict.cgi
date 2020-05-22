#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import re, sqlite3, collections
import operator
from collections import namedtuple, defaultdict as dd

langdef = namedtuple(
    "LanguageDefinition",
    [
        "id",  # the iso-639-3 code for the language
        "name",  # the language name
        "color",  # the color to use for tab titles, etc.
    ]
)

languages = {
    "cmn": langdef("cmn", "Chinese", "red"),
    "eng": langdef("eng", "English", "blue"),
}

dictdef = namedtuple(
    "DictionaryDefinition",
    [
        "id",  # an identifier to use internally (e.g. HTML element IDs)
        "name",  # The name to display in the tab
        "language",  # The iso-639-3 code
        "type",  # "mono" or "bi" for mono-/bi-lingual dictionary
        "url"  # The URL to query. Use {q} in place of the query string
    ]
)

# dictionaries is a list of dictionaries defined with the dictdef
# namedtuple. The order of the list is the order their respective tabs
# appear on the web page
dictionaries = [
    # chinese (cmn)
    dictdef("cmn-wikipedia", "Wikipedia", "cmn", "mono", "http://zh.wikipedia.org/w/index.php?search={q}"),
    dictdef("cmn-wiktionary", "Wiktionary", "cmn", "mono", "http://zh.wiktionary.org/zh-hans/{q}"),
#    dictdef("cmn-ccd", "CCD", "cmn", "mono", "ccd.cgi?lemma={q}"),
    dictdef("cmn-zdic", "ZDic", "cmn", "mono", "http://www.zdic.net/search/?q={q}#cd"),
    dictdef("cmn-dreye", "Dr. Eye", "cmn", "bi", "http://www.dreye.com.cn/ews/{q}--00--.html"),
    dictdef("cmn-youdao", "Youdao", "cmn", "bi", "https://www.youdao.com/search?q={q}#phrsListTab"),
    dictdef("cmn-iciba", "Iciba", "cmn", "bi", "http://www.iciba.com/{q}#dict_main"),
    dictdef("cmn-bing", "Bing", "cmn", "bi", "http://cn.bing.com/dict/search?q={q}"),
    dictdef("cmn-baike", "BaiKe", "cmn", "bi", "http://www.baike.com/wiki/{q}"),
    dictdef("cmn-mdbg", "MDBG", "cmn", "bi", "http://www.mdbg.net/chindict/chindict.php?page=worddict&wdqb={q}"),
    # english (eng)
    dictdef("eng-mdbg", "MDBG", "eng", "bi", "http://www.mdbg.net/chindict/chindict.php?page=worddict&wdqb={q}"),
    dictdef("eng-baike", "BaiKe", "eng", "bi", "http://www.baike.com/wiki/{q}"),
    dictdef("eng-bing", "Bing", "eng", "bi", "http://cn.bing.com/dict/search?q={q}"),
    dictdef("eng-iciba", "Iciba", "eng", "bi", "http://www.iciba.com/{q}#dict_main"),
    dictdef("eng-youdao", "Youdao", "eng", "bi", "https://www.youdao.com/search?q={q}#phrsListTab"),
    dictdef("eng-collins", "Collins", "eng", "mono", "http://www.collinsdictionary.com/dictionary/english/{q}"),
    dictdef("eng-oxford", "Oxford", "eng", "mono", "http://www.oxforddictionaries.com/definition/english/{q}"),
    dictdef("eng-ah", "American Heritage", "eng", "mono", "http://www.ahdictionary.com/word/search.html?q={q}"),
    dictdef("eng-wiktionary", "Wiktionary", "eng", "mono", "http://en.wiktionary.org/w/index.php?search={q}"),
    dictdef("eng-wikipedia", "Wikipedia", "eng", "mono", "http://en.wikipedia.org/w/index.php?search={q}"),
]

form = cgi.FieldStorage()

lg1 = languages[form.getfirst('lg1', 'cmn')]
lg2 = languages[form.getfirst('lg2', 'eng')]
lemma1 = form.getfirst('lemma1', '').strip()
lemma2 = form.getfirst('lemma2', '').strip()

print("Content-type: text/html; charset=utf-8\n")
print("<html>")
print(u"""
<head>
  <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
  <meta http-equiv='content-language' content='zh'>
  <title>"{lemma1}" | "{lemma2}" Multi-dictionary Search</title>
  <link rel="stylesheet" href="../css/ui-lightness/jquery-ui-1.10.4.custom.min.css">
  <style>
    #tabs .ui-tabs-active {{
      background-image: none;
      background-color: wheat;
    }}
  </style>
  <script src="../jquery.js"></script>
  <script src="../jquery-ui.js"></script>
</head>
""".format(lemma1=lemma1, lemma2=lemma2))

print("""
<body>
  <table>
  <tr>
    <td>
      <form action="javascript:send_{lang1.id}_query();">
        <span style="color:{lang1.color};font-weight:bold;">{lang1.name} Words:</span>
        <input type="text" id="{lang1.id}_query">
        <input type="submit" value="Search">
      </form>
    </td>
    <td> &nbsp; </td>
    <td>
      <form action="javascript:send_{lang2.id}_query();">
        <span style="color:{lang2.color};font-weight:bold;">{lang2.name} Words:</span>
        <input type="text" id="{lang2.id}_query" />
        <input type="submit" value="Search">
      </form>
    </td>
  </tr>
  </table>
""".format(lang1=lg1, lang2=lg2))

print("""<div id="tabs">
  <ul>""")
for d in dictionaries:
    lg = languages[d.language]
    print(u'    <li><a href="#tabs-{d.id}" style="color: {lg.color};">{d.name}</a></li>'\
          .format(d=d, lg=lg))
print("  </ul>")

for d in dictionaries:
    print("""
    <div id="tabs-{d.id}">
      <iframe id="{d.id}" width="100%" height="100%" src="" sandbox="">
        <p>Your browser does not support iframes. Please try a different browser.</p>
      </iframe>
    </div>
    """.format(d=d))

print("</div>")

print("""
<script>
  function send_{lg.id}_query()
  {{
    var q = document.getElementById("{lg.id}_query").value;
""".format(lg=lg1))
for d in dictionaries:
    if d.language != lg1.id:
        continue
    url = d.url.format(q='" + q + "')  # get out of javascript quotes and append q
    print(u'    document.getElementById("{d.id}").src="{url}";'.format(d=d, url=url))
print("""
  }}

  function send_{lg.id}_query()
  {{
    var q = document.getElementById("{lg.id}_query").value;
""".format(lg=lg2))

for d in dictionaries:
    if d.language != lg2.id:
        continue
    url = d.url.format(q='" + q + "')  # get out of javascript quotes and append q
    print(u'    document.getElementById("{d.id}").src="{url}";'.format(d=d, url=url))
print(u"""
  }}

  $(function() {{
    $( "#tabs" ).tabs({{heightStyle: "fill"}});
    $( "#{lg1.id}_query" ).val("{lemma1}");
    $( "#{lg2.id}_query" ).val("{lemma2}");
    send_{lg1.id}_query();
    send_{lg2.id}_query();
  }});
</script>
""".format(lemma1=lemma1, lemma2=lemma2, lg1=lg1, lg2=lg2))

print("""</body>
</html>
""")
