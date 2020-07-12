#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##########################################################################
# This script allows add definitions to a specific synset 
##########################################################################

import cgi, urllib
import cgitb; cgitb.enable()  # for troubleshooting
import re, sqlite3, collections
import os, http.cookies # cookies
from os import environ  # cookies
from collections import defaultdict as dd

from ntumc_webkit import *  # imports HTML blocks
from lang_data_toolkit import * # imports langs & dicts

# Fixes encoding issues when reading cookies from os.environ
import os, sys
from importlib import reload
sys.getfilesystemencoding = lambda: 'utf-8'
reload(os)

################################################################################
# READ & PROCESS CGI FORM
################################################################################
form = cgi.FieldStorage()
ss = form.getfirst("ss", ())
synset = form.getfirst("synset", "")
lemma = form.getfirst("lemma", "")
lang = form.getfirst("lang", "eng")
gridmode = form.getvalue("gridmode", "ntumcgrid")
wndb = form.getvalue("wndb", "wn-ntumc")



### reference to self (.cgi)
selfcgi = "annot-gridx.cgi?gridmode=%s" % (gridmode)

### reference to wn-grid (search .cgi)
# omwcgi = "wn-gridx.cgi?gridmode=%s&wndb=%s" % (gridmode, wndb)

### working .db (should be the extended OMW) ?
wndb_path = "../db/{}.db".format(wndb)




### Connect to and update the database
con = sqlite3.connect(wndb_path)
c = con.cursor()


################################################################################
# MASTER COOKIE (LANGS)
################################################################################
if 'HTTP_COOKIE' in os.environ:
    C = http.cookies.SimpleCookie(os.environ['HTTP_COOKIE'])
else:
    C = http.cookies.SimpleCookie()

if "SelectedLangs" in C:
    langselect = C['SelectedLangs'].value.split('::')
else:
    langselect = ['eng']

# FETCH USERID/PW INFO
if "UserID" in C:
    userID = C["UserID"].value
    hashed_pw = C["Password"].value
else:
    userID = "guest"
    hashed_pw = "guest"


################################################################################
# HTML
################################################################################
print(u"""Content-type: text/html; charset=utf-8\n
<html>
 <head>
 <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
 <!-- The 2 meta tags below are to avoid caching informationto forms -->
 <META HTTP-EQUIV="Pragma" CONTENT="no-cache"> 
 <META HTTP-EQUIV="Expires" CONTENT="-1">

 <title>OMW-Editor</title>

 <link href="../tag-wn.css" rel="stylesheet" type="text/css">
 <script src="../tag-wn.js" language="javascript"></script>

  <!-- KICKSTART -->
  <script 
   src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js">
  </script>
  <script src="../HTML-KickStart-master/js/kickstart.js"></script>
  <link rel="stylesheet" 
   href="../HTML-KickStart-master/css/kickstart.css" media="all"/>

  <style>
    hr{padding: 0px; margin: 10px;}
  </style>

 </head>
 <body>
""")


################################################################################
# JAVASCRIPT
################################################################################
langdrop = ""
for l in langselect:
    if l == lang: # pre-select cmn
        langdrop += "<option value ='%s' selected>%s</option>" % (l, 
                                              omwlang.trans(l, lang))
    else:
        langdrop += "<option value ='%s'>%s</option>" % (l, 
                                    omwlang.trans(l, lang))

linkdrop = "<option value =''>Change Me!</option>"
for l in synlinks:
    linkdrop += "<option value ='%s'>%s</option>" %(l, omwlang.trans(l,lang))


print("""<script type="text/javascript">

function addNewDef() {
        var container = document.getElementById('defContainer');
        var newDiv = document.createElement('div');
        var newText = document.createElement('textarea');
        newText.style.verticalAlign = "middle";
        newText.name = "deflst[]";
        newText.placeholder = "definition";
        newText.style.height = "3.5em";
        newText.required = "Yes";
        var selectLang = document.createElement('select');
        selectLang.innerHTML = "%s";
        selectLang.name = "deflangs[]";
        var newDelButton = document.createElement('button');
        var bttntxt = document.createTextNode("-");  // Create a text node
        newDelButton.appendChild(bttntxt);  // Append the text to <button>
        newDelButton.className = "small";
        newDiv.appendChild(newText);
        newDiv.appendChild (document.createTextNode(" "));
        newDiv.appendChild(selectLang);
        newDiv.appendChild (document.createTextNode(" "));
        newDiv.appendChild(newDelButton);
        container.appendChild(newDiv);
        newDelButton.onclick = function() { container.removeChild(newDiv); }
}

</script>""" % (langdrop))



################################################################################
# FETCH CURRENT INFORMATION FROM DATABASE
################################################################################

# FETCH SYNSET NAME
ss_name = ""
ss_pos = ""
c.execute("""SELECT name, pos 
             FROM synset 
             WHERE synset = ?""", (synset,))
rows = c.fetchall()
ss_name = rows[0][0]
ss_pos = rows[0][1]


# FETCH COMMENTS
coms = []
c.execute("""SELECT comment, u, t 
             FROM synset_comment
             WHERE synset = ?
             ORDER BY t""", [synset])
rows = c.fetchall()
for r in rows:
    coms.append((cgi.escape(r[0],True),r[1],r[2]))


# FETCH DEFINITIONS
defs = collections.defaultdict(list)
c.execute("""SELECT lang, def 
             FROM synset_def 
             WHERE synset = ?""", (synset,))
rows = c.fetchall()
for r in rows:
    if r[0] in langselect:
        defs[r[0]].append(r[1].replace('"', '&quot;'))


# FETCH EXAMPLES
exes = collections.defaultdict(list)
c.execute("""SELECT lang, def 
             FROM synset_ex 
             WHERE synset = ?""", (synset,))
rows = c.fetchall()
for r in rows:
    if r[0] in langselect:
        exes[r[0]].append(r[1].replace('"', '&quot;'))

# FETCH LEMMAS
words = collections.defaultdict(list)
c.execute("""SELECT sense.lang, lemma, freq, confidence 
             FROM word 
             LEFT JOIN sense ON word.wordid = sense.wordid 
             WHERE synset = ? 
             ORDER BY freq DESC """, (synset,))
rows = c.fetchall()
for r in rows:  # [lang][i] = (lemma, freq)
    if r[0] in langselect:
        words[r[0]].append((r[1], r[2],r[3]))

# FETCH SYNLINKS
rels = collections.defaultdict(list)
c.execute("""SELECT link, synset2, name 
             FROM synlink 
             LEFT JOIN synset ON synlink.synset2 = synset.synset 
             WHERE synset1 = ?""", (synset,))
rows = c.fetchall()
for r in rows:  # [link][i] = (synset, name)
    rels[r[0]].append((r[1], r[2]))


################################################################################



if userID in valid_usernames: # CHECK LOGIN

    ### Prints Fetched Data:
    # print """<h6>Add New Definitions to Synset <a href="%s&synset=%s">%s</a>
    #       """ % (omwcgi,synset, synset)
    print("""<h6>Add New Definition""")
    # print HTML.status_bar(userID)  # Top Status Bar
    print("</h6>")


    ############################################################################
    # FORM 1 : ADD NEW INFO TO THE SYNSET
    # "deleteyn" == "add" (i.e. "add to synset")
    ############################################################################

    # target should be the same frame
    print("""<p><form action="editwordnet.cgi" method="post" target="_self" >
             <input type="hidden" name="deleteyn" value="add"/>
             <input type="hidden" name="synset" value="%s"/>
             <input type="hidden" name="wndb" value="%s"/>""" % (synset, wndb))

    print("Editing: ") #TEST
    print(wndb) #TEST
    print("<br>") #TEST

    print("""<strong>English Definition: </strong>""")
    for d in defs['eng']:
        print(d + '; ')


    # NEW DEFINITIONS
    print("""<p><div id="defContainer">""")
    print("""<textarea name="deflst[]" placeholder="definition" 
              style="vertical-align:middle; height:3.5em;"></textarea>""")
    print("""<select id="deflang" name="deflangs[]">""")
    for l in langselect:
        if lang == l:  ### label things with the query's own language label
            print("""<option value ='%s' selected>%s
                     </option>""" % (l, omwlang.trans(l, lang)))
        else:
            print("""<option value ='%s'>%s
                     </option>""" % (l, omwlang.trans(l, lang)))
    print("""</select>""")
    # print """<button class="small" 
    #          onClick="addNewDef()">add def</button></div>"""


    # NEW COMMENTS
    print("""<p><div id="comContainer">""")
    print( """<textarea name="comlst[]" placeholder="Comment" 
              style="vertical-align:middle; height:3.5em;"></textarea>""")
    # print """<button class="small" 
    #          onClick="addNewComment()">add Comment</button></div>"""



    print("""<p><input type="submit" value="Add to synset"/>""")
    print("""</form>""")
    print("<br><br><br>")




##################################################
# If user not in valid_usernames - No Edit! 
##################################################
else:
    print(HTML.status_bar(userID))  # USER STATUS BAR
    print("""<i class="icon-user-md pull-left icon-4x"></i> """)
    print("""We're sorry, but you need to have an active username 
             to be able to access this area.<br>
             Please click the Home button, on the right and 
             proceed to login.<br>""")

### Print Search Form (always visible below)
# print "<hr>"
# print HTML.search_form(omwcgi, lemma, langselect, lang)
# print "<hr>"
# print HTML.wordnet_footer()  # Footer

### Close HTML
print("""</body></html>""")

