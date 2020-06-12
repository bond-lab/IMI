#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
# THIS SCRIPT IS USED TO CREATE NEW SYNSET ENTRIES (MANUALLY LINKED TO OTHERS).
# WE ARE ASSUMING THAT A COOKIE MUST HAVE SOME LANGUAGES SELECTED (FOR BROWSING)
# THESE ARE THE LANGUAGES THAT WILL BE AVAILABLE FOR ADDING INFORMATION
# IT REDIRECTS DB-WORK TO EDITWORDNET.CGI
#
# IF IT WAS LINKED FROM AN EXISTING SYNSET, IT PROVIDES SOME INFORMATION AND 
# AUTOMATIC LINKS TO THAT SYNSET.
################################################################################

import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import re, sqlite3
import os, http.cookies # cookies
from os import environ  # cookies

# Fixes encoding issues when reading cookies from os.environ
import os, sys
from importlib import reload
sys.getfilesystemencoding = lambda: 'utf-8'
reload(os)


from ntumc_webkit import * # ntumc_dependencies
from lang_data_toolkit import * # ntumc_dependencies

################################################################################
# READ & PROCESS CGI FORM
################################################################################
form = cgi.FieldStorage()
synset = form.getfirst("synset", "")
lemma = form.getfirst("lemma", "")
lemma = lemma.strip()
lang = form.getfirst("lang", "eng")
gridmode = form.getvalue("gridmode", "ntumcgrid")
omwcgi = "wn-gridx.cgi?gridmode=%s" % (gridmode)



################################################################################
# COOKIE
################################################################################
if 'HTTP_COOKIE' in os.environ:
    C = http.cookies.SimpleCookie(os.environ['HTTP_COOKIE'])
else:
    C = http.cookies.SimpleCookie()

if "SelectedLangs" in C:
    langselect = C['SelectedLangs'].value.split('::')
else:
    langselect = ['eng']

if "MainLang" in C:
    if C['MainLang'].value in langselect:
        lang = C['MainLang'].value
    else:
        lang = langselect[0]

if 'BackoffLang' in langselect and C['BackoffLang'].value in langselect:
    lang2 = C['BackoffLang'].value 
else:
    lang2 = langselect[0]

if "UserID" in C:
    usrname = C["UserID"].value
    hashed_pw = C["Password"].value
else:
    usrname = "guest"
    hashed_pw = "guest"
################################################################################


################################################################################
# HTML
################################################################################
print("""Content-type: text/html; charset=utf-8\n
<html>
  <head>
    <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
    <title>Open Multilingual Wordnet Editor</title>
    <link href="../tag-wn.css" rel="stylesheet" type="text/css">


    <!-- IMPORT NTUMC COMMON STYLES -->
    <link href="../ntumc-common.css" rel="stylesheet" type="text/css">


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
  <body>""")

if usrname not in valid_usernames:  # CHECK LOGIN
    print(HTML.status_bar(usrname))  # USER STATUS BAR
    print("""<i class="icon-user-md pull-left icon-4x"></i> """)
    print("""We're sorry, but you need to have an active username 
             to be able to access this area.<br>
             Please click the Home button, on the right and 
             proceed to login.<br>""")

else:
    ############################################################################
    # JAVASCRIPT
    ############################################################################
    langdrop = "" # this is an html dropdown menu of languages available
    for l in langselect:
        if lang == l:
            langdrop += "<option value ='%s' selected>%s</option>" % (l, 
                                                omwlang.trans(l, lang))
        else:
            langdrop += "<option value ='%s'>%s</option>" % (l, 
                                        omwlang.trans(l, lang))

    linkdrop = "<option value =''>Change Me!</option>"
    for l in synlinks:
        linkdrop += "<option value ='%s'>%s</option>" %(l, 
                                    omwlang.trans(l,lang))


    print("""<script type="text/javascript">

    function addNewRel() {
        var container = document.getElementById('synlinkContainer');
        var newDiv = document.createElement('div');
        var newText = document.createElement('input');
        newText.type = "text";
        newText.name = "linkedsyn[]";
        newText.pattern = "[0-9]{8}-[avnrxz]";
        newText.title = "xxxxxxxx-a/v/n/r/x/z"
        newText.required = "Yes";
        var selectRel = document.createElement('select');
        selectRel.innerHTML = "%s";
        selectRel.name = "synlink[]";
        selectRel.required = "Yes";
        newText.placeholder = "linked synset";
        newText.size = "10";

        var newDelButton = document.createElement('button');
        var bttntxt = document.createTextNode("-");  // Create a text node
        newDelButton.appendChild(bttntxt);  // Append the text to <button>
        newDelButton.className = "small";

        newDiv.appendChild(selectRel);
        newDiv.appendChild (document.createTextNode(" "));
        newDiv.appendChild(newText);
        newDiv.appendChild (document.createTextNode(" "));
        newDiv.appendChild(newDelButton);
        container.appendChild(newDiv);
        newDelButton.onclick = function() { container.removeChild(newDiv); }
    }

    function addNewSynLemma() {
        var container = document.getElementById('synlemmaContainer');
        var newDiv = document.createElement('div');
        var newText = document.createElement('input');
        newText.type = "text";
        newText.name = "lemmalst[]";
        var selectLang = document.createElement('select');
        selectLang.innerHTML = "%s";
        selectLang.name = "lemmalangs[]";
        newText.placeholder = "lemma";
        newText.size = "17";
        newText.required = "Yes";
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

    function addNewDef() {
        var container = document.getElementById('defContainer');
        var newDiv = document.createElement('div');
        var newText = document.createElement('textarea');
        newText.style.verticalAlign = "middle";
        newText.name = "deflst[]";
        newText.style.height = "3em";
        newText.required = "Yes";
        newText.placeholder = "definition (choose lang)";
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
        newText.style.height = "3em";
        newText.required = "Yes";
        newText.placeholder = "example";
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
    </script>""" % (linkdrop, langdrop, langdrop, langdrop))


    ############################################################################
    # GUIDELINES (HIDDEN) PANE
    ############################################################################
    guidelines = """<div class="info floatRight">
    <a class="info"><span style="color: #4D99E0;">
    <i class="icon-info-sign"></i>ReadMe</a>

    <div class="show_info">
     <h5>Quick Guidelines</h5>
     <p>You need to choose a Synset Name (English is always preferred); 
     <br>If it's language specific and no English name is possible, 
         assign the most frequent lemma in that language;
     <br>Add a part of speech (n > noun, v > verb, a > adjective, 
     r > adverb, x > classifier, z > ???);
     <br>At least one English definition is required (other 
         languages are possible);
     <br>Examples are preferred but optional;
     <br>Try to be exhaustive when adding lemmas;
     </p></div></div>"""
    ############################################################################

    ############################################################################
    # DISPLAY 2 CASES: IF THERE WAS A RELATED SYNSET + IF THERE WASN'T ONE
    ############################################################################
    print("<h5>")
    print(HTML.status_bar(usrname)) # USER STATUS BAR
    print("Add New Synset:</h5>")
    print(guidelines)

    if (synset): # IF THERE WAS A RELATED SYNSET

        # CONNECT TO WN
        wndb = "../db/wn-ntumc.db"
        con = sqlite3.connect(wndb)
        c = con.cursor()

        # FETCH DEFINITIONS
        defs = collections.defaultdict(list)
        c.execute("""SELECT lang, def 
                     FROM synset_def 
                     WHERE synset = ? """, (synset,))
        rows = c.fetchall()
        for r in rows:
            defs[r[0]].append(r[1].replace('"', '&quot;'))

        # FETCH EXAMPLES
        exes = collections.defaultdict(list)
        c.execute("""SELECT lang, def 
                     FROM synset_ex 
                     WHERE synset = ? """, (synset,))
        rows = c.fetchall()
        for r in rows:
            exes[r[0]].append(r[1].replace('"', '&quot;'))

        # FETCH LEMMAS (+FREQ)
        words = collections.defaultdict(list)
        c.execute("""SELECT sense.lang, lemma, freq 
                     FROM word left join sense on word.wordid = sense.wordid 
                     WHERE synset = ?
                     ORDER BY freq DESC""", (synset,))
        rows = c.fetchall()
        for r in rows:  # [lang][i] = (lemma, freq)
            words[r[0]].append((r[1], r[2]))

        ########################################################################
        # PRINT RELATED SYNSET INFORMATION
        ########################################################################
        print("The new synset will be linked to %s.<br>" % synset)

        for l in words:		
            if l in langselect:
                print("<b>%s lemmas:</b>" % omwlang.trans(l, lang))

                ws = list()
                for (w, f) in words[l]:  # (word, frequency)
                    if f:
                        ws.append("""%s<sup>%d</sup>""" %(w,f))
                    else:
                        ws.append(w)
                print(""" <i> %s</i><br>""" % (", ".join(ws)))

        for l in defs.keys():
            if l in langselect:
                print("<b>%s definition: </b>" % omwlang.trans(l, lang))
                for d in defs[l]:
                    print("%s; " % d)
                print("<br>")

        print("<hr>")
        ########################################################################

    # MAIN FORM (CREATE NEW SYNSET)
    print("""<p><form action="editwordnet.cgi" method="post" target="log">
	     <input type="hidden" name="deleteyn" value="nss"/>
	     <p><input type="text" placeholder="synset name" 
              name="engname" size="10" required/>
	     <input type="text" name="pos" placeholder="POS" 
              maxlength="1" size="3" pattern="[avnrxz]" 
              title="POS: n, v, a, r, x or z" required/></p>""")

    print("""<p><span id="synlinkContainer">
	     <select id="synlink" name="synlink[]" required>
             <option value =''>Change Me!</option>""")
    for l in synlinks:
        print("<option value ='%s'>%s</option>" %(l, omwlang.trans(l,lang)))


    if synset: # AUTO-FILL SYNSET
        print("""</select> <input type="text" name="linkedsyn[]" 
                 value="%s" size="10" pattern="[0-9]{8}-[avnrxz]"/>
	         <button class="small" onClick="addNewRel()">add synlink</button>
                 </span></p>""" % synset)
    else:
        print("""</select> <input type="text" name="linkedsyn[]"
                 placeholder="linked synset" size="10" 
                 pattern="[0-9]{8}-[avnrxz]" required/> <button 
                 class="small" onClick="addNewRel()">add synlink</button>
                 </span></p>""")

    # DEFINITIONS
    print("""<p><div id="defContainer"><div><nobr>""")
    print("""<input type="hidden" name="deflangs[]" value="eng"/>""")
    print("""<textarea id="def1" name="deflst[]"
              style="vertical-align:middle; height:3.5em;" 
              placeholder="english definition (req.)" 
              required></textarea>""")
    print("""<button class="small" 
             onClick="addNewDef()">add def</button></nobr>
             </div></div></p>""")

    # EXAMPLES
    print("""<p><div id="egContainer"><div><nobr>""")
    print("""<textarea placeholder="example" name="eglst[]"
              style="vertical-align:middle; height:3.5em;"></textarea>""")
    print("""<select id="eglang" name="eglangs[]">""")
    for l in langselect:
        if l == lang:
            print("""<option value ='%s' selected>%s
                     </option>""" % (l, omwlang.trans(l, lang)))
        else:
            print("""<option value ='%s'>%s
                     </option>""" % (l, omwlang.trans(l, lang)))
    print("""</select>""")
    print("""<button class="small" 
             onClick="addNewEg()">add ex</button></nobr>
             </div></div></p>""")


    # LEMMAS
    print("""<p><span id="synlemmaContainer"><span><nobr>
	     <input type="text" name="lemmalst[]" 
              placeholder="lemma" value="%s" size="17"
              required/>""" % lemma)
    print("""<select id="lang" name="lemmalangs[]">""")
    for l in langselect:
        if l == lang:
            print("""<option value ='%s' selected>%s
                     </option>""" % (l, omwlang.trans(l, lang)))
        else:
            print("""<option value ='%s'>%s
                     </option>""" % (l, omwlang.trans(l, lang)))
    print("""</select>""")
    print("""<button class="small" 
             onClick="addNewSynLemma()">add lemma</button></nobr>
             </span></span></p>""")


    print("""<p><input type="submit" 
             value="Create New Synset"/></p></form>""")



# Search Form (always visible)
print("<hr>")
print(HTML.search_form(omwcgi, lemma, langselect, lang, "Langs: ", lang2, 90))
print("<hr>")
print(HTML.wordnet_footer())  # Footer

# Close HTML
print("</body></html>")
