#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
# THIS SCRIPT IS USED TO CREATE NAMED ENTRIES.
# WE ARE ASSUMING THAT A COOKIE MUST HAVE SOME LANGUAGES SELECTED (FOR BROWSING)
# THESE ARE THE LANGUAGES THAT WILL BE AVAILABLE FOR ADDING INFORMATION
# IT REDIRECTS DB-WORK TO EDITWORDNET.CGI
################################################################################

import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import re, sqlite3
import os, http.cookies # cookies
from os import environ  # cookies

from ntumc_webkit import * # ntumc_dependencies
from lang_data_toolkit import * # ntumc_dependencies

################################################################################
# READ & PROCESS CGI FORM
################################################################################
form = cgi.FieldStorage()
lemma = form.getfirst("lemma", "")
lemma = lemma.strip()
lang = form.getfirst("lang", "eng")
gridmode = form.getvalue("gridmode", "ntumcgrid")
omwcgi = "wn-gridx.cgi?gridmode=%s" % (gridmode)


################################################################################
# GLOBAL VARIABLES & CONSTANTS
################################################################################
ne = ["org", "loc", "per", "dat", "oth", "num", "fch"]  # NE short codes
nehuman = ["Organization", "Location","Person",
           "Date/Time", "Other","Number", "Fictional Character"]  # NE human readable
ness = ['00031264-n','00027167-n','00007846-n',
        '15113229-n','00001740-n','13576101-n', 
        '09587565-n'] # NE hypernym synsets


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

if C['BackoffLang'].value in langselect:
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
# GUIDELINES (HIDDEN) PANE
################################################################################
guidelines = """<div class="info floatRight">
<a class="info"><span style="color: #4D99E0;">
<i class="icon-info-sign"></i>ReadMe</a>

<div class="show_info">
<h5>Quick Guidelines</h5>
<p>You need to choose a Named Entity type; 
  <br>Please include as many lemmas as possible;
  <br>Try to come up with, at least, one English lemma;
</p>
</div></div>"""
################################################################################


################################################################################
# HTML
################################################################################
print("""Content-type: text/html; charset=utf-8\n
<html>
  <head>
    <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
    <title>Create New Named Entity</title>
    <link href="../tag-wn.css" rel="stylesheet" type="text/css">

    <!-- IMPORT NTUMC COMMON STYLES -->
    <link href="../ntumc-common.css" rel="stylesheet" type="text/css">

    <!-- KICKSTART -->
    <script 
     src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js">
    </script>
    <script src="../HTML-KickStart-master/js/kickstart.js">
    </script>
    <link rel="stylesheet" 
     href="../HTML-KickStart-master/css/kickstart.css" media="all" /> 

    <style>
      hr{padding: 0px; margin: 10px;}
    </style>

  </head>
  <body>""")


if usrname not in valid_usernames: # CHECK LOGIN
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
    langdrop = "" # an html dropdown menu of languages available
    for l in langselect:
        if l == lang: # select lang as default
            langdrop += """<option value='%s' selected>%s</option>""" % (l, 
                                                    omwlang.trans(l, lang))
        else:
            langdrop += """<option value='%s'>%s</option>""" % (l, 
                                            omwlang.trans(l, lang))

    print("""<script type="text/javascript">

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
        newText.size = "10";
        newText.required = "Yes";

        var newDelButton = document.createElement('button');
        newDelButton.value = "-";
        var bttntxt = document.createTextNode("-");  // Create a text node
        newDelButton.appendChild(bttntxt);  // Append the text to <button>
        newDelButton.className = "small";
        newDiv.appendChild(selectLang);
        newDiv.appendChild(newText);
        newDiv.appendChild(newDelButton);
        container.appendChild(newDiv);
        newDelButton.onclick = function() { container.removeChild(newDiv); }
    }
    </script>""" % (langdrop))



    ############################################################################
    # HTML BODY
    ############################################################################
    print("""<h5>""")
    print(HTML.status_bar(usrname)) # USER STATUS BAR
    print("""Add Named Entity:</h5>""")
    print(guidelines)

    print("""<form action="editwordnet.cgi" method="post" target="log" 
	     <input type="hidden" name="usrname" value="%s"/>
	     <input type="hidden" name="deleteyn" value="nss"/>""") % usrname

    print("""<span id="neTypeContainer">
             <select id="netype" name="netype" required> """)
    print("<option value =''>Choose a type!</option>")
    for i, e in enumerate(ne):
        print("<option value ='%s'>%s</option>" %(e, nehuman[i]))
    print("""</select></span>""")

    print("""<p><select id="lang" name="lemmalangs[]">"""),
    for l in langselect:
        if l == lang: # Match with last searched lang
            print("<option value ='%s' selected>%s</option>" % (l, omwlang.trans(l, lang))),
        else:
            print("<option value ='%s'>%s</option>" % (l, omwlang.trans(l, lang))),
    print("</select>"),


    print("""<span id="synlemmaContainer">
             <input type="text" name="lemmalst[]" placeholder="lemma"  
              value="%s" size="10" required/><button 
              class="small" onClick="addNewSynLemma()">+</button>
	     </span><br>
             </p><input type="submit" value="Create NE"/>
	     </form>""" % lemma),


# Search Form (always visible)
print("<hr>")
print(HTML.search_form(omwcgi, lemma, langselect, lang, "Langs: ", lang, 90))
print("<hr>")
print(HTML.wordnet_footer())  # Footer

# Close HTML
print("</body></html>")
