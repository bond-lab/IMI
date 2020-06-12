#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##########################################################################
# This script allows editing of a specific synset (and all it's lemmas,
# definitions, examples, etc.)
#
# Wishlist: 
# - Allow changing the POS of the synset (??)
# - Allow change/choose the Semantic Field (lexname)
# - 
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
synset = form.getfirst("synset", "00001740-n")
lemma = form.getfirst("lemma", "")
lang = form.getfirst("lang", "eng")
gridmode = form.getvalue("gridmode", "ntumcgrid")

### reference to self (.cgi)
selfcgi = "annot-gridx.cgi?gridmode=%s" % (gridmode)

### reference to wn-grid (search .cgi)
omwcgi = "wn-gridx.cgi?gridmode=%s" % (gridmode)

### working .db (should be the extended OMW) ?
wndb = "../db/wn-ntumc.db"



### Connect to and update the database
con = sqlite3.connect(wndb)
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

function addNewLemma() {
    var container = document.getElementById('lemmaContainer');
    var newDiv = document.createElement('div');
    var newText = document.createElement('input');
    newText.type = "text";
    newText.name = "lemmalst[]";
    newText.placeholder = "lemma";
    newText.required = "Yes";
    newText.size = "17";
    var selectLang = document.createElement('select');
    selectLang.innerHTML = "%s";
    selectLang.name = "lemmalangs[]";
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

function addNewComment() {
	var container = document.getElementById('comContainer');
	var newDiv = document.createElement('div');
	var newText = document.createElement('textarea');
        newText.style.verticalAlign = "middle";
	newText.name = "comlst[]";
	newText.placeholder = "comment";
        newText.style.height = "3.5em";
        newText.required = "No";
        var newDelButton = document.createElement('button');
        var bttntxt = document.createTextNode("-");  // Create a text node
        newDelButton.appendChild(bttntxt);  // Append the text to <button>
        newDelButton.className = "small";
	newDiv.appendChild(newText);
        newDiv.appendChild (document.createTextNode(" "));
	newDiv.appendChild(newDelButton);
	container.appendChild(newDiv);
	newDelButton.onclick = function() { container.removeChild(newDiv); }
}

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


function addNewEg() {
	var container = document.getElementById('egContainer');
	var newDiv = document.createElement('div');
	var newText = document.createElement('textarea');
        newText.style.verticalAlign = "middle";
	newText.name = "eglst[]";
	newText.placeholder = "example";
        newText.style.height = "3.5em";
        newText.required = "Yes";
        var selectLang = document.createElement('select');
        selectLang.innerHTML = "%s";
        selectLang.name = "eglangs[]";
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

function addNewRel() {
	var container = document.getElementById('synlinkContainer');
	var newDiv = document.createElement('div');
	var newText = document.createElement('input');
	newText.type = "text";
	newText.name = "linkedsyn[]";
        var selectRel = document.createElement('select');
        selectRel.innerHTML = "%s";
        selectRel.name = "synlink[]";
        selectRel.required = "Yes";
        newText.pattern = "[0-9]{8}-[avnrxz]";
	newText.placeholder = "linked synset";
        newText.title = "xxxxxxxx-a/v/n/r/x/z"
	newText.size = "17";
        newText.required = "Yes";
        var newDelButton = document.createElement('button');
        var bttntxt = document.createTextNode("-");  // Create a text node
        newDelButton.appendChild(bttntxt);  // Append the text to <button>
        newDelButton.className = "small";
        newDiv.appendChild(newText);
        newDiv.appendChild (document.createTextNode(" "));
        newDiv.appendChild(selectRel);
        newDiv.appendChild (document.createTextNode(" "));
	newDiv.appendChild(newDelButton);
	container.appendChild(newDiv);
	newDelButton.onclick = function() { container.removeChild(newDiv); }
}
</script>""" % (langdrop, langdrop, langdrop, linkdrop))



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
    print("""<h6>Editing Synset <a href="%s&synset=%s">%s</a>
          """ % (omwcgi,synset, synset))
    print(HTML.status_bar(userID))  # Top Status Bar
    print("</h6>")


    ############################################################################
    # FORM 1 : ADD NEW INFO TO THE SYNSET
    # "deleteyn" == "add" (i.e. "add to synset")
    ############################################################################
    print("""<div id='line'><span>Add New Information</span></div>""")
    print("""<p><form action="editwordnet.cgi" method="post" target="log">
             <input type="hidden" name="deleteyn" value="add"/>
             <input type="hidden" name="synset" value="%s"/>""" % (synset))


    # NEW COMMENTS
    print("""<p><div id="comContainer">""")
    print("""<textarea name="comlst[]" placeholder="Comment" 
             style="vertical-align:middle; height:3.5em;"></textarea>""")
    print("""<button class="small" 
             onClick="addNewComment()">add Comment</button></div>""")



    # NEW LEMMAS
    print("""<p><span id="lemmaContainer"><span><input type="text" 
             name="lemmalst[]" placeholder="lemma" size="17" />""")
    print("""<select id="lemmalang" name="lemmalangs[]">""")
    for l in langselect:
        if l  == lang:
            print("""<option value ="%s" selected>%s
                     </option>""" % (l, omwlang.trans(l, lang)))
        else:
            print("""<option value ="%s">%s
                     </option>""" % (l, omwlang.trans(l, lang)))
    print("""</select>""")
    print("""<button class="small" 
             onClick="addNewLemma()">add lemma</button></span></span>""")


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
    print("""<button class="small" 
             onClick="addNewDef()">add def</button></div>""")


    # NEW EXAMPLES
    print("""<p><div id="egContainer">""")
    print("""<textarea name="eglst[]" placeholder="example"
             style="vertical-align:middle; height:3.5em;"></textarea>""")
    print("""<select id="eglang" name="eglangs[]">""")
    for l in langselect:
        if lang == l:  ### label things with the query's own language label
            print("""<option value ='%s' selected>%s
                     </option>""" % (l, omwlang.trans(l, lang)))
        else:
            print("""<option value ='%s'>%s
                     </option>""" % (l, omwlang.trans(l, lang)))
    print("""</select>""")
    print("""<button class="small" onClick="addNewEg()">add ex
             </button></div>""")


    # NEW SYNLINKS
    print("""<p><div id="synlinkContainer">""")
    print("""<input type="text" name="linkedsyn[]" placeholder="linked synset" 
          pattern="[0-9]{8}-[avnrxz]" title="xxxxxxxx-a/v/n/r/x/z" size="17"/>""")
    print("""<select id="synlink" name="synlink[]">
              <option value =''>Change Me!</option>""")
    for l in synlinks:
            print("<option value ='%s'>%s</option>" %(l, omwlang.trans(l,lang)))
    print("""</select>""")
    print("""<button class="small" onClick="addNewRel()">add synlink
             </button></div></p>""")


    print("""<input type="submit" value="Add to synset"/>""")
    print("""</form>""")





    ############################################################################
    # FORM 2 : EDIT INFO FROM THE SYNSET
    # "deleteyn" == "mod" (i.e. "modify synset")
    ############################################################################

    deleteme = "✘"
    print("<br><div id='line'><span>Edit Existing Information</span></div>")

    print("""<form id="update" action="editwordnet.cgi" method="post" target="log">
             <input type="hidden" name="synset" value="%s"/> \n  
             <input type="hidden" name="deleteyn" value="mod"/>
          """ % (synset))


    # EDIT SYNSET NAME
    print("""<p><input type="hidden" name="ss_name_old" value="%s"/>""" % ss_name)
    print("""<b>Name:</b> <input type="text" name="ss_name_new" value="%s"
             style="width:8em;" /></p>""" % ss_name)






    # EDIT SYNSET POS (NOT READY YET)
    # print("""<input type="hidden" name="ss_pos_old" value="%s"/>""" % ss_pos)
    # print("""<b>POS:</b> <input type="text" name="ss_pos_new" value="%s"
    #          style="width:2em;" pattern="[avnrxz]" />""" % ss_pos)
    # WHAT WOULD MEAN CHANGING THE POS?
    # - change change synset.pos
    # - change offset number
    # - change every lemma's (sense) pos
    # - change sense's synset link
    # - change every synlink
    # - change all external resources (sentiment, tempo, verb-frames, etc.)
    # ... etc. ?

    # EDIT LEMMAS
    for l in words:
        print("<p><strong>%s (Lemmas):</strong><br></p>" % omwlang.trans(l, lang))

        ws = list()   # list to store html entries of each word
        # for (word, frequency) in the list of lemmas per language (l)
        for (w, f, c) in words[l]:
            ws.append("""<input type="hidden" name="lemmao[]" value="%s"/>
                         <input type="hidden" name="edit_lemma_langs[]" value="%s"/>
                         <input type="hidden" name="confo[]" value="%f"/>

                         <nobr><input type="text" style="width:%dem;" name="lemman[]" 
                         value="%s"/><span title="Confidence"><!--
                         --><input type="text" style="width:3em;" name="confn[]" 
                         value="%0.2f" pattern="(0(\.[0-9]*)?)|1(\.[0]*)?" 
                         title="Confidence [0.0-1.0]" "/></span><!--
                      """ %(w, l, c, 8, w, c))

            # if f: # append frequency (if some)
            #     ws.append("""--><span style="font-size:80%%" 
            #     title="Frequency"><sub>%d</sub></span><!--""" % f)


            # Link to automatic deletion
            ws.append("""--><span style="font-size:85%%" 
            title="Delete lemma"><!--
            --><a href="editwordnet.cgi?deleteyn=mod&synset=%s&edit_lemma_langs[]=%s&lemmao[]=%s&lemman[]=delete!&confo[]=%s&confn[]=%s"
             style="color:black;text-decoration:none;" 
            target="log">%s</a></span></nobr>&nbsp;&nbsp;&nbsp;
                       """ % (synset, l, 
                              urllib.parse.quote(w), c, c,deleteme))

        # prints the html list of lemmas 
        print("""<p>%s</p>""" % (" ".join(ws)))


    # EDIT DEFINITIONS
    for l in defs.keys():
        if l == 'img':
                continue
        print("<p><strong>%s (Definitions):</strong></p>" % omwlang.trans(l, lang)) 
        print("<p>")
        for d in defs[l]:
            print("""<input type="hidden" name="defo[]" value="%s"/>
                     <input type="hidden" name="edit_defs_langs[]" value="%s"/>
                     <textarea style="vertical-align:middle; width:25em; 
                      height:3.5em;" name="defn[]">%s</textarea><!--""" % (d, l, d))
            print("""--><span style="font-size:85%%" title="Delete link"><!--
--><a href="editwordnet.cgi?deleteyn=mod&synset=%s&defo[]=%s&defn[]=delete!&edit_defs_langs[]=%s"
  style="color:black;text-decoration:none;" target="log">%s</a></span></nobr>&nbsp;&nbsp;&nbsp;
                          """ % (synset, d, l, deleteme))
        print("</p>")


    # EDIT EXAMPLES
    for l in exes.keys():
        print("<p><strong>%s (Examples):</strong></p>" % omwlang.trans(l, lang))
        print("<p>")
        for d in exes[l]:
            print("""<input type="hidden" name="exeo[]" value="%s"/>
                     <input type="hidden" name="edit_exe_langs[]" value="%s"/>
                     <textarea style="vertical-align:middle; width:25em; 
                      height:3.5em;" name="exen[]">%s</textarea><!--
                 """ % (d, l, d))
            print("""--><span style="font-size:85%%" title="Delete link"><!--
--><a href="editwordnet.cgi?deleteyn=mod&synset=%s&exeo[]=%s&exen[]=delete!&edit_exe_langs[]=%s"
  style="color:black;text-decoration:none;" target="log">%s</a></span></nobr>&nbsp;&nbsp;&nbsp;
                          """ % (synset, d, l, deleteme))
        print("</p>")



    # EDIT SYNLINKS
    if rels: # rels {link {synset2, name}}
        print("<p><b>Relations:</b></p>")
        print("<p>") 
        for r in rels:
            for (osynset, name) in rels[r]:
                print("""<nobr><select id="synlink" name="synlink[]">""")
                for l in synlinks:
                    if r == l:
                        print("""<option value ='%s' selected>%s
                                 </option>""" %(l, omwlang.trans(l,lang)))
                    else:
                        print("""<option value ='%s'>%s
                                 </option>""" %(l, omwlang.trans(l,lang)))
                print("</select>")
                print("""<input type="hidden" name="synlinko[]" 
                          value="%s"/><!--""" % r)

                print("""--><span title= %s><input type="hidden" 
                             name="linkedsyno[]" value="%s"/><!--
                         --><input type="text" size="7" name="linkedsyn[]" 
                             pattern="[0-9]{8}-[avnrxz]" title="xxxxxxxx-a/v/n/r/x/z" 
                             value="%s"/></span><!--""" % (name, osynset, osynset))

                print("""--><span style="font-size:85%%" title="Delete link"><!--
--><a href="editwordnet.cgi?deleteyn=mod&synset=%s&synlinko[]=%s&synlink[]=delete!&linkedsyn[]=%s&linkedsyno[]=%s"
style="color:black;text-decoration:none;" target="log">%s</a></span></nobr>&nbsp;&nbsp;&nbsp;
                      """ % (synset, r, osynset, osynset, deleteme))
        print("</p>")






    # EDIT COMMENTS
    # print coms
    if len(coms) > 0:
        print("<p><strong>Comments:</strong></p>")
    for i, com in enumerate(coms):
        (comment, user, time) = com
        print("<p>")
        print("""<input type="hidden" name="comso[]" value="%s"/>
                 <input type="hidden" name="com_u_o[]" value="%s"/>
                 <input type="hidden" name="com_t_o[]" value="%s"/>
                 <sub> %s (%s)</sub> <br>
                 <textarea id="com%s" style="vertical-align:middle; width:25em; 
                  height:3.5em;" name="comsn[]">%s</textarea><!--
                 """ % (comment, user, time, user, time, i, comment))

        print("""--><span style="font-size:85%%" title="Delete">""" +
              """<a onclick="document.getElementById('com%s').value""" % i +
              """='!!!delete!!!'; document.getElementById('update').submit();"""+
              """ return false" style="color:black;text-decoration:none;" """ +
              """ target="log">%s</a></span></nobr>
              """ % deleteme)

        print("</p>")







    # CLOSE FORM
    print("""<input type="submit" value="Update Synset"/></form>""") 
    ############################################################################



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
print("<hr>")
print(HTML.search_form(omwcgi, lemma, langselect, lang))
print("<hr>")
print(HTML.wordnet_footer())  # Footer

### Close HTML
print("""</body></html>""")

