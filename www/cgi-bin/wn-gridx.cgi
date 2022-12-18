#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi, os, http.cookies
import cgitb; cgitb.enable()
from os import environ
import re, sqlite3, time
from collections import defaultdict as dd

from ntumc_webkit import HTML, NTUMC_Cookies, omw1_url, omw1x_url, fcbond_url
from ntumc_util import *
from ntumc_gatekeeper import concurs
from lang_data_toolkit import *
from html import escape, unescape

# Fixes encoding issues when reading cookies from os.environ
import os, sys
from importlib import reload
sys.getfilesystemencoding = lambda: 'utf-8'
reload(os)


start_time = time.time() # TIME

################################################################################
# FETCH DATA FROM CGI FORM
# langselect = Language updates. If empty, langs in cookie  will be used;
################################################################################
form = cgi.FieldStorage()
lang = escape(form.getfirst("lang", ""))
lang2 = escape(form.getfirst("lang2", "eng"))
ss = escape(form.getfirst("ss", ""))
synset = escape(form.getfirst("synset", ""))
lemma_raw = unescape(form.getfirst("lemma", "").strip())
lemma = escape(lemma_raw, quote=True)
pos = escape(form.getfirst("pos", ""))
gridmode = escape(form.getvalue("gridmode", "ntumcgrid"))
# langselect = form.getlist("langselect[]")
langselect = [escape(l) for l in form.getlist("langselect[]")]


################################################################################
if re.match('(\d+)-[avnrxz]',lemma):
    synset = lemma
    lemma = ''
################################################################################



################################################################################
# GLOBAL VARIABLES
################################################################################
scaling = 100

if gridmode not in ('ntumcgrid', 'wnja','cow', 'wnbahasa', 'ntumc-noedit',
                    'grid', 'gridx'):
#                    'ntumcgridA', 'ntumcgridB',
    gridmode = 'grid'

if gridmode == "ntumcgrid":
    langs = omwlang.ntumclist()
    wnnam = "NTUMC+ Open Multilingual Wordnet"
    wnurl = omw1_url  
    wnver = "0.9"
    wndb = "wn-ntumc"
    #wndb_path = "../db/"
    scaling = 90

# elif gridmode == "ntumcgridA":
#     langs = omwlang.ntumclist()
#     wnnam = "NTUMC+ Open Multilingual Wordnet"
#     wnurl = omw1_url  
#     wnver = "0.9"
#     wndb = "wn-ntumcA"
#     wndb_path = "../db/wn-ntumcA.db"
#     scaling = 90

# elif gridmode == "ntumcgridB":
#     langs = omwlang.ntumclist()
#     wnnam = "NTUMC+ Open Multilingual Wordnet"
#     wnurl = omw1_url  
#     wnver = "0.9"
#     wndb = "wn-ntumcB"
#     wndb_path = "../db/wn-ntumcB.db"
#     scaling = 90


elif gridmode == "ntumc-noedit":
    langs = omwlang.ntumclist()
    wnnam = "NTUMC+ Open Multilingual Wordnet"
    wnurl = omw1_url  
    wnver = "0.9"
    wndb = "wn-ntumc"
    wndb_path = "../db/{}.db".format(wndb)
    scaling = 90
        
elif gridmode == "grid":
     langs = omwlang.humanprojectslist()
     wnnam = "Open Multilingual Wordnet"
     wndb = "wn-multix"
     #@wndb_path = "../../omw/wn-multix.db"
     wnurl = omw1_url  
     wnver = "1.3"

elif gridmode == "cow":
    langs = ("cmn", "eng")
    wnnam = "Chinese Open Wordnet"
    wndb = "wn-ntumc"
    wnurl = "https://bond-lab.github.io/cow/"
    wnver = "1.2"

elif gridmode == "wnbahasa":
    langs = ("ind", "zsm", "eng")
    wnnam = "Wordnet Bahasa"
    wndb = "wn-ntumc"
    wnurl = "http://wn-msa.sourceforge.net"
    wnver = "1.0"

elif gridmode == "wnja":
    langs = ("jpn", "eng")
    wnnam = "Japanese Wordnet"
    wndb = "wn-ntumc"
    wnurl = "https://bond-lab.github.io/wnja/"
    wnver = "1.1"

elif gridmode == "gridx":
    langs = omwlang.alllangslist()
    wnnam = "Extended Open Multilingual Wordnet"
    wndb =  "wn-multix"
    wnurl =  omw1x_url
    wnver = "1.3"


    
omwnam = "Extended Open Multilingual Wordnet"
omwurl = omw1x_url
wncgi = "wn-gridx.cgi?gridmode=%s" % (gridmode)
editcgi = "annot-gridx.cgi" # allows for add/edit wordnet entries 
addnewcgi = "addnew.cgi" # adds new synsets
addnecgi = "addne.cgi" # adds Named Entities
sumocgi="http://54.183.42.206:8080/sigma/Browse.jsp?kb=SUMO&CorpuscularObject"

relnam= {'ants':u'⇔', 'derv':u'⊳', 'pert':u'⊞'}
################################################################################



### Connect to the database
#print('wndb_path', wndb_path)
#con = sqlite3.connect(wndb_path)
con, c  = concurs(wndb)


################################################################################
# (PRE)PROCESSING FUNCTIONS
################################################################################

def containsAny(str, set):
    """Check whether 'str' contains ANY of the chars in 'set'"""
    return 1 in [c in str for c in set]

def label(string, title, url):
    return "<a class='lbl' title='%s' href='%s'>%s</a>" % (title, url, string)

def sq(lst, sep):
    text = sep.join(lst)
    return text

def hword(word, words, src, conf):
    """highlight a word if it is in words; show src in title;
       show confidence as opacity and in title; FIXME show freq"""
    style = set()
    title = set()
    if src:
        title.add('src  %s' % src)
    if conf:
         title.add('conf  %0.2f' % conf)
         style.add('opacity: %f;' % (conf-0.3) if conf != 1.0 else '')
    titlestr= ''
    if title:
        titlestr= "title = '%s'" % '&#xA;'.join([escape(t) for t in title])
    if word in words:
        style.add('color:DarkGreen;')
    return "<span style='%s'%s>%s</span>" % (" ".join(style), titlestr, 
                                             escape(word))
################################################################################



################################################################################
# COOKIES (Set SelectedLangs, MainLang, BackoffLang, PreviousSearch)
################################################################################
if 'HTTP_COOKIE' in os.environ:
    C = http.cookies.SimpleCookie(os.environ['HTTP_COOKIE'])
else:
    C = http.cookies.SimpleCookie()

# If no languages were set, use cookie or default languages
if langselect == []:
    if "SelectedLangs" in C and gridmode not in ["cow","wnja","wnbahasa"]:
        langselect = C['SelectedLangs'].value.split('::')
    else:
        if gridmode == "ntumcgrid":
            langselect = omwlang.ntumclist()
        elif gridmode == "ntumc-noedit":
            langselect = omwlang.ntumclist()
        elif gridmode == "grid":
            langselect = ['eng','jpn','cmn','ind','msa']
        elif gridmode == "cow":
            langselect = ['eng', 'cmn']
        elif gridmode == "wnbahasa":
            langselect = ['eng','ind','msa']
        elif gridmode == "wnja":
            langselect = ['eng','jpn']
        elif gridmode == "gridx":
            langselect = ['eng','jpn','cmn','ind','msa']
        else:
            langselect = ['eng','jpn','cmn','ind','msa']

    C["SelectedLangs"] = '::'.join(langselect)    

else:
    C["SelectedLangs"] = '::'.join(langselect)


# MainLang / BackoffLang
if lang == "":
    if "MainLang" in C:
        if C['MainLang'].value in langselect:
            lang = C['MainLang'].value 
        else:
            lang = langselect[0]

        if C['BackoffLang'].value in langselect:
            lang2 = C['BackoffLang'].value 
        else:
            lang2 = langselect[0]

    else: # Default Langs
        if gridmode in ["ntumcgrid","ntumc-noedit","gridx","grid"]:
            lang = "eng"
        elif gridmode == "cow":
            lang = "cmn"
        elif gridmode == "wnbahasa":
            lang = "ind"
        elif gridmode == "wnja":
            lang = "jpn"
        else:
            lang = "eng"

        lang2 = "eng"

    C['MainLang'] = lang
    C['BackoffLang'] = lang2

else:
    C['MainLang'] = lang
    C['BackoffLang'] = lang2


if 'lemmas' in C:
    seen_lemmas = C['lemmas'].value.split('::')
else:
    seen_lemmas = list()
if lemma and lemma not in seen_lemmas:
    seen_lemmas.insert(0,lemma)
if seen_lemmas:
    C['lemmas'] = '::'.join(seen_lemmas)   
if len(seen_lemmas) > 10:
    seen_lemmas = seen_lemmas[:10]

# UserID / Password
if "UserID" in C:
    usrname = C["UserID"].value
    hashed_pw = C["Password"].value
else:
    usrname = "guest"
    hashed_pw = "guest"
################################################################################


################################################################################
# HTML (HEADER)
################################################################################
print(NTUMC_Cookies.secure(C)), # PRINT COOKIE
print("Content-type: text/html; charset=utf-8\n\n")
print(u"""<html>
<head>
  <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
  <meta http-equiv='content-language' content='zh'>
  <title>%s %s</title>
  <link href="../tag-wn.css" rel="stylesheet" type="text/css">
  <script src="../tag-wn.js" language="javascript"></script>


  <!-- KICKSTART -->
  <script 
   src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js">
  </script>
  <script src="../HTML-KickStart-master/js/kickstart.js"></script>
  <link rel="stylesheet" 
   href="../HTML-KickStart-master/css/kickstart.css" media="all" /> 


  <!-- NTUMC COMMON STYLES -->
  <link href="../ntumc-common.css" rel="stylesheet" type="text/css">





  <!-- FANCYBOX -->
  <!-- Needs jQuery library -->
  <!-- Add fancyBox main JS and CSS files -->
  <script type="text/javascript" 
   src="../fancybox/source/jquery.fancybox.js?v=2.1.5"></script>
  <link rel="stylesheet" type="text/css" 
   href="../fancybox/source/jquery.fancybox.css?v=2.1.5" 
   media="screen" />
  <script type="text/javascript" 
   src="../fancybox-ready.js"></script>



   <!-- TOGGLE DIV VISIBILITY OF COLUMNS BY ID -->
   <script type="text/javascript">

     <!-- HIDE ALL ROWS BY POS  -->
     function toggleRowsByClass(c) {
       var ids = document.getElementsByClassName(c);
       for (i = 0; i < ids.length; i++) {
         togglecol(ids[i].id);
       }
     }



     <!-- SHOW ONLY ROWS BY POS  -->
     function showOnlyRowsByClass(c) {

       var allPOS  = ['n', 'v', 'a', 'r'];
       var index = allPOS.indexOf(c);
       if (index > -1) {
         allPOS.splice(index, 1);
       }


       showallunder('ss_table');

       for (i = 0; i < allPOS.length; i++) {
     
         var ids = document.getElementsByClassName(allPOS[i]);
         for (z = 0; z < ids.length; z++) {
           togglecol(ids[z].id);
         }
       }
     }



      function togglecol(id1) {
          if (window.document.getElementById(id1).style.visibility == "collapse") {
              window.document.getElementById(id1).style.display = "table-row";
              window.document.getElementById(id1).style.visibility = "visible";

          } else {
              window.document.getElementById(id1).style.visibility = "collapse";
              window.document.getElementById(id1).style.display = "none";

             var element = document.getElementById('ss_table');
             var allElements = element.getElementsByTagName("*");
             var allIds = [];
             for (var i = 0, n = allElements.length; i < n; ++i) {
               var el = allElements[i];
               if (el.id) { allIds.push(el.id); }
             }

             for (index = 0; index < allIds.length; index++) {
               tableids = allIds[index];
               window.document.getElementById(tableids).style.boxSizing = "content-box";
       }

          }
      }
   </script>



   <!-- SHOW ALL UNDER ID -->
   <script type="text/javascript">
     function showallunder(myNode) {
       var element = document.getElementById(myNode);
       var allElements = element.getElementsByTagName("*");
       var allIds = [];
       for (var i = 0, n = allElements.length; i < n; ++i) {
         var el = allElements[i];
         if (el.id) { allIds.push(el.id); }
       }

       for (index = 0; index < allIds.length; index++) {
         id = allIds[index];
         if (window.document.getElementById(id).style.visibility == "collapse") {
              subElement = window.document.getElementById(id);
              removeClass(subElement, 'lightrow')
              subElement.style.display = "table-row";
              subElement.style.visibility = "visible";
         }
       } 
     }



      <!-- TOGGLE CLASS IN ELEMENT, USES hasClass underneath -->
      function addClass(el, className) {
        var classes = el.className.match(/\S+/g) || [];  
        if (!hasClass(el, className)) {
          classes.push(className);
        } else { var index = classes.indexOf(className);
                 classes.splice(index, 1);
               }
        el.className = classes.join(' ');
      }
      function removeClass(el, className) {
        var classes = el.className.match(/\S+/g) || [];  
        if (!hasClass(el, className)) {
        } else { var index = classes.indexOf(className);
                 classes.splice(index, 1);
               }
        el.className = classes.join(' ');
      }
      function hasClass(element, classNameToTestFor) {
          var classNames = element.className.split(' ');
          for (var i = 0; i < classNames.length; i++) {
              if (classNames[i].toLowerCase() == classNameToTestFor.toLowerCase()) {
                  return true;
              }
          }
          return false;
      }

   </script>


  <!-- TO SHOW / HIDE BY ID (FOR DIVs)-->
  <script type="text/javascript">
   function toggle_visibility(id) {
       var e = document.getElementById(id);
       if(e.style.display == 'block')
          e.style.display = 'none';
       else
          e.style.display = 'block';
   }
  </script>



   <style>
      /* lightrow is a faded yellow */
     .lightrow {
          background-color: #FFFFCC;
     }


      .hoverTable{
      }
      .hoverTable td{ 
      }
      /* Define the default color for all the table rows */
      .hoverTable tr{
      }
      /* Define the hover highlight color for the table row */
      .hoverTable tr:hover {
          background-color: #FFFFCC;
      }

  </style>

  <style>
    hr{
      padding: 0px;
      margin: 10px;    
    }
  </style>


  <style>
  blockquote {
  font: 14px/20px italic Times, serif;
  padding-left: 20px;
  padding-top: 0px;
  padding-bottom: 10px;
  padding-right: 10px;
  border: none;
  margin: 0px;
  text-indent: 20px;
  }
  </style>

</head>""" % (wnnam, wnver))

#   background-color: #dadada;
#  border: 1px solid #ccc;
#  border-bottom: 1px solid #ccc;


################################################################################
# HTML (BODY) > Display four cases: list of synsets; synset; lemma; nothing
################################################################################
print("<body>")


################################################################################
# IF QUERY == List of Synsets (this is used as a frame,  with the tagging tools)
################################################################################
if (ss):
    sss = ss.split()
    ass = placeholders_for(sss)
    lems = expandlem(lemma_raw)

    # Fetch Lemmas by gridmode
    if gridmode == "grid":
        sql = """SELECT synset, s.lang, lemma, 
                        freq, src, confidence 
                 FROM ( SELECT synset, lang, wordid, freq, src, confidence 
                        FROM sense 
                        WHERE synset in (%s) 
                        AND lang in (?,?) AND confidence IS '1.0') s
                 LEFT JOIN word
                 WHERE word.wordid = s.wordid
                 ORDER BY freq DESC"""

        c.execute(sql % ass, [*sss, lang, lang2])

    elif gridmode in ("cow","wnbahasa","wnja"):
        sql = """SELECT synset, s.lang, lemma, 
                        freq, src, confidence
                 FROM ( SELECT synset, lang, wordid, freq, src, confidence 
                        FROM sense
                        WHERE synset in (%s) 
                        AND lang in (?,?) 
                        AND confidence IS '1.0') s
                 LEFT JOIN word
                 WHERE word.wordid = s.wordid
                 ORDER BY freq DESC """
        c.execute(sql % ass, [*sss, lang, lang2])

    else: # gridx or ntumcgrid modes (do not restrict by confidence level)
        sql = """SELECT synset, s.lang, lemma, 
                        freq, src, confidence 
                 FROM ( SELECT synset, lang, wordid, freq, src, confidence 
                        FROM sense 
                        WHERE synset in (%s) 
                        AND lang in (?,?) ) s
                 LEFT JOIN word
                 WHERE word.wordid = s.wordid
                 ORDER BY freq DESC """
        c.execute(sql % ass, [*sss, lang, lang2])

    words = dd(lambda: dd(list))
    freq = dd(int)
    for r in c:
        ### FIXME take these out of the wordnet
        if not (r[1] == 'jpn' and '_' in r[2]):
            words[r[0]][r[1]].append((r[2], r[3],r[5],r[4]))
            if r[3]:
                freq[r[0]] += r[3]

    # Fetch Definitions                                                       
    c.execute("""SELECT synset, lang, sid, def
                 FROM synset_def
                 WHERE synset in (%s)
                 AND lang in (?, ?)
              """ % ass, [*sss, lang, lang2])

    defs = dd(lambda: dd(lambda: dd(str)))
    for r in c:
        defs[r[0]][r[1]][r[2]] = r[3]

    # Fetch Examples
    c.execute("""SELECT synset, lang, sid, def
                 FROM synset_ex 
                 WHERE synset in (%s) 
                 AND lang in (?, ?)
              """ % ass, [*sss, lang, lang2])

    exes = dd(lambda: dd(lambda: dd(str)))
    for r in c:
        exes[r[0]][r[1]][r[2]] = r[3]

    # Fetch Verb Frames
    c.execute("""SELECT xref, misc, confidence, synset
                 FROM xlink
                 WHERE synset in (%s)
                 AND resource = ?
              """ % ass, [*sss, 'svframes'])
    rows = c.fetchall()

    vframes = dd(lambda: dd(list))
    for r in rows:
        vframes[r[3]][r[0]].append(r[1]) # full string
        vframes[r[3]][r[0]].append(r[2]) # symbols
        vframes[r[3]][r[0]].append(vfargs[r[1]]) # V ArgNumbers



    # FETCH COMMENTS
    coms = dd(list)
    if gridmode == "ntumcgrid":
        c.execute("""SELECT synset, comment, u, t 
                     FROM synset_comment
                     WHERE synset in (%s)
                     ORDER BY t""" % ass, [*sss])
        rows = c.fetchall()
        for r in rows:
            comment = escape(r[1],True)
            user = r[2]
            t = r[3]

            coms[r[0]].append( (comment,user,t) )



    ###############################
    # Print HTML (List of Synsets)
    ###############################

    if gridmode == "ntumcgrid":

        print(HTML.status_bar(usrname))  # Top Status Bar


    print("<br>")
    print(HTML.showallunder_bttn("ss_table",'All'))
    print("&nbsp;&nbsp;")

    print(HTML.showOnlyRowsByClass_bttn('n','N'))
    print("&nbsp;")
    print(HTML.showOnlyRowsByClass_bttn('v','V'))
    print("&nbsp;")
    print(HTML.showOnlyRowsByClass_bttn('a','A'))
    print("&nbsp;")
    print(HTML.showOnlyRowsByClass_bttn('r','R'))
    print("&nbsp;&nbsp;")

    if gridmode == "ntumcgrid":

        print( HTML.multidict_bttn(lang, lemma))
        print( "&nbsp;")
        print( HTML.ne_bttn())
        print( "&nbsp;")
        print(HTML.newsynset_bttn())


        # TOGGLE SHOW/HIDE INDIVIDUAL POS
        # print "&nbsp;&nbsp;&nbsp;"
        # print HTML.hideRowsByClass_bttn('n','N'),
        # print HTML.hideRowsByClass_bttn('v','V'),
        # print HTML.hideRowsByClass_bttn('a','A'), 
        # print HTML.hideRowsByClass_bttn('r','R'),


    if gridmode == "ntumc-noedit":
        print(HTML.multidict_bttn(lang, lemma))
 
    print("""<table cellspacing="0" cellpadding="0" 
              id="ss_table" class="tight sortable hoverTable">""")
    # print("""<colgroup><col id="ss_ss"><col id="ss_lemma"><col id="ss_defs">
    #          <col id="ss_exs"><col id="ss_actions"></colgroup>""")
    print("""<thead><tr><th>SS</th><th>Lemmas</th><th>Definitions</th>
             <th>Examples</th>""")

    if gridmode == "ntumcgrid":
        print("""<th></th>""") # BUTTONS HOLDER

    print("""</tr></thead>""")


    for (i,s) in enumerate(sss):
        rowid = "row%s" % s
        # write up verb frames
        wfrmsset = []; wfrmscap = ''
        if s in vframes.keys(): # if synset has vframes
            for vid in sorted(vframes[s].keys()):
                wfrmscap += """ %s: %s &#xA;""" % (vid, vframes[s][vid][1]) 
                wfrmsset.append(vframes[s][vid][2])
            wfrmsset = sorted(list(set(wfrmsset)))
            wfrmsset = ', '.join(wfrmsset)
        
        if wfrmsset:
            wfrmssymb = """<span title='%s'>%s</span>
                        """ % (wfrmscap, wfrmsset)
        else:
            wfrmssymb = ''

        ### print offset number
        poscolor = ''
        if pos == s[-1]:
            poscolor=" color='DarkRed' "

        ss_pos = s[-1]
        print("""<tr class='%s' id='%s' 
              onclick="addClass(document.getElementById('%s'),'lightrow')">
                 <td valign='top'><nobr><a title='%s' 
                 href='%s&synset=%s&lang=%s&lang2=%s'>%02d</a>
                 <sub><font %s>%s</font></sub></nobr>
              """ % (ss_pos, rowid, rowid, s, wncgi, s, 
                     lang, lang2, i+1, poscolor, s[-1]))
        if freq[s] > 0: # FREQ + VERBFRAMES
            print("""<br><nobr><font size='-3'>(%d) %s</font><nobr>
                  """ % (freq[s], wfrmssymb))
        elif s[-1] == "v" and wfrmssymb != '': # ONLY VERBFRAMES
            print("""<br><font size='-3'>%s</font>
                  """ % wfrmssymb)

        print("<br>")
        print(HTML.hiderow_bttn(rowid))

        # COMMENTS
        if s in coms.keys():
            tip = ""
            for com in coms[s]:
                (comment, user, t) = com
                tip += "<p>"
                tip += """%s (%s): %s<p>
                       """ % (user, t, escape(comment,True))
            print("""<span style="color:#999999;" class='tooltip' title='%s'><i class="icon-comments"></i></span>""" % tip)

        print("</td>")

        ### print words
        if words[s][lang] and words[s][lang2] and lang != lang2:
            wsl1 = list() # for language 1
            wsl2 = list() # for language 2
            for (w, f, conf, src) in words[s][lang]:
                opac1 = (" style='opacity: %f'" % (conf-0.3)) if conf != 1.0 else ''
                freq1 = ("<sub>%d</sub>" % f) if f else ''
                wsl1.append("""<span title='source: %s&#xA;conf:
                                %0.2f' %s'>%s</span>%s""" % (src, conf, opac1, w, freq1))

            for (w, f, conf, src) in words[s][lang2]:
                opac2 = (" style='opacity: %f'" % (conf-0.3)) if conf != 1.0 else ''
                freq2 = ("<sub>%d</sub>" % f) if f else ''
                wsl2.append("""<span title='source: %s&#xA;conf:
                                %0.2f' %s'>%s</span>%s""" % (src, conf, opac2, w, freq2))

            print("""<td valign='top'><font size='-1'><!--
                     --><table style="width:100%%"><tr>
                     <td bgcolor = '#ededed'>%s</td></tr>
                     <tr><td>%s</td></tr></table></font>
                  """ % (", ".join(wsl1),", ".join(wsl2)))

        elif words[s][lang2]:

            wsl1 = list() # for eng
            for (w, f, conf, src) in words[s][lang2]:
                opac1 = (" style='opacity: %f'" % (conf-0.3)) if conf != 1.0 else ''
                freq1 = ("<sub>%d</sub>" % f) if f else ''
                wsl1.append("<span title='source: %s&#xA;conf:   %0.2f' %s'>%s</span>%s" % (src, conf, opac1, w, freq1))

            print("  <td  valign='top'><font size='-1'>%s</font>" % (", ".join(wsl1)))


        elif words[s][lang]:

            wsl1 = list() # for lang
            for (w, f, conf, src) in words[s][lang]:
                opac1 = (" style='opacity: %f'" % (conf-0.3)) if conf != 1.0 else ''
                freq1 = ("<sub>%d</sub>" % f) if f else ''
                wsl1.append("<span title='source: %s&#xA;conf:   %0.2f' %s'>%s</span>%s" % (src, conf, opac1, w, freq1))

            print("  <td  valign='top'><font size='-1'>%s</font>" % (", ".join(wsl1)))

        else:
            print("  <td  valign='top'><font size='-1'>%s</font>" % "NO LEX")

        # print "  <td  valign='top'>&nbsp;&nbsp;&nbsp;&nbsp;</td>"


        # Print definitions (BothLangs, SearchLang, BackoffLang)
        if defs[s][lang] and defs[s][lang2] and lang != lang2:

            tdf = list()
            for i in sorted(defs[s][lang].keys()):
                tdf.append(defs[s][lang][i])
            edf = list()
            for i in sorted(defs[s][lang2].keys()):
                edf.append(defs[s][lang2][i])

            print("""<td  valign='top'><span title='%s'>
                     <font size='-1'>%s</font></span></td>
                  """ % (sq(edf, "; "), sq(tdf, "; ")))

        elif defs[s][lang]:
            tdf = list()
            for i in sorted(defs[s][lang].keys()):
                tdf.append(defs[s][lang][i])

            print("""<td  valign='top'><font size='-1'>%s</font>
                     </td>""" % (sq(tdf, "; ")))

        elif defs[s][lang2]:
            tdf = list()
            for i in sorted(defs[s][lang2].keys()):
                tdf.append(defs[s][lang2][i])

            print("""<td  valign='top'><font size='-1'>%s</font>
                     </td>""" % (sq(tdf, "; ")))

        else:
            print("""<td  valign='top'><font size='-1'>
                      NO DEFINITION</font></td>""")


        # Print 5 Examples (BothLangs, SearchLang, BackoffLang)
        if exes[s][lang] and exes[s][lang2] and lang != lang2:

            tdf = list()
            for i in sorted(exes[s][lang].keys())[:5]:
                tdf.append(exes[s][lang][i])
            edf = list()
            for i in sorted(exes[s][lang2].keys())[:5]:
                edf.append(exes[s][lang2][i])

            print(u"""<td  valign='top'><span title='%s'><font size='-1'>
                      「%s」</font></span></td>""" % (sq(edf, "; "), sq(tdf, "; ")))

        elif exes[s][lang]:
            tdf = list()
            for i in sorted(exes[s][lang].keys())[:5]:
                tdf.append(exes[s][lang][i])
            print(u"""<td  valign='top'><font size='-1'>
                      <i>%s</i></font></td>""" % (sq(tdf, "; "),))

        elif exes[s][lang2]:
            tdf = list()
            for i in sorted(exes[s][lang2].keys())[:5]:
                tdf.append(exes[s][lang2][i])
            print(u"""<td  valign='top'><font size='-1'>
                      <i>%s</i></font></td>""" % (sq(tdf, "; "),))

        else:
            print("<td><br></td>")

        # Print editing interface
        if gridmode == "ntumcgrid":
            # Add New Synset and Edit synset buttons
            print("""<td style="vertical-align:center">""")
            print(HTML.editsynset_bttn(usrname, s))
            print(HTML.newsynset_bttn(s))
            print("""</td>""")



        print("</tr>\n")
    print("</table>\n")



###############################
# IF QUERY == A Single Synset
###############################
elif (synset):

    # FETCH COMMENTS
    coms = []

    if gridmode in ("ntumcgrid","ntumcgridA","ntumcgridB"):
        c.execute("""SELECT comment, u, t 
                     FROM synset_comment
                     WHERE synset = ?
                     ORDER BY t""", [synset])
        rows = c.fetchall()
        for r in rows:
            coms.append((escape(r[0],True),r[1],r[2]))


    # Check if it's part of Core
    c.execute("""SELECT core from core
                 WHERE synset = ? 
                 ORDER BY core""", (synset,))
    rows = c.fetchall()
    cores = []
    for r in rows:
        if r[0] == 1:
            cores.append(label(u'✪', 'Core Synset', 
            'http://wordnet.princeton.edu/wordnet/download/standoff/'))
    core = ' '.join(cores)

    # Fetch Definitions
    c.execute("""SELECT lang, sid, def, usr 
                 FROM synset_def 
                 WHERE synset = ?
              """, (synset,))
    rows = c.fetchall()
    defs = dd(lambda: dd(str))
  
    for r in rows:
        if r[3]:
            defs[r[0]][int(r[1])] = "{} <sub>({})</sub>".format(escape(r[2]),
                                                                escape(r[3]))
        else:
            defs[r[0]][int(r[1])] = "{}".format(escape(r[2]))
            
    # Fetch the highest definition ID
    # (in case the def sid is not 0 - e.g. was deleted)
    firstengdefid = 999
    for defid in defs['eng'].keys():
        if defid < firstengdefid:
            firstengdefid = defid

    # Fetch Verb Frames
    c.execute("""SELECT xref, misc, confidence 
                 FROM xlink
                 WHERE synset = ? 
                 AND resource = ? 
              """, (synset, 'svframes'))
    rows = c.fetchall()

    vframes = dd(list)
    for r in rows:
        vframes[r[0]].append(r[1]) # full string
        vframes[r[0]].append(r[2]) # symbols
        vframes[r[0]].append(vfargs[r[1]]) # V ArgNumbers

    wfrmsset = []
    wfrmscap = ''
    if vframes:
        for vid in vframes.keys():
            wfrmscap += """%s: %s &#xA;""" % (vid, vframes[vid][1]) 
            wfrmsset.append(vframes[vid][2])

        wfrmsset = sorted(list(set(wfrmsset)))
        wfrmsset = ', '.join(wfrmsset)
            
        wfrmssymb = """<span title='%s'><nobr>%s;&#160;</nobr></span>
                """ % (wfrmscap, wfrmsset)
    else:
        wfrmsset = ''
        wfrmssymb = ''



    print(HTML.status_bar(usrname))  # Top (Right) Status Bar

    # Print Synset ID and first sentence of English def + synset verbframes
    print("""<font size='+1'><b>%s</b> %s</font> '%s'; %s
          """ % (synset, core, defs['eng'][firstengdefid],wfrmssymb))

    # Print Top Search Form
    print("""<span style="float:right;">""")
    print(HTML.search_form(wncgi, lemma, langselect, lang, " ",lang2, scaling))
    print("""&nbsp;</span> """)

    ## Examples
    c.execute("""SELECT lang, sid, def 
                 FROM synset_ex 
                 WHERE synset = ? 
              """, (synset,))
    rows = c.fetchall()
    exes = dd(lambda: dd(str))
    for r in rows:
        exes[r[0]][r[1]] = r[2]


    # Fetch Lemmas by gridmode
    if gridmode == "ntumcgrid":
        c.execute("""SELECT s.lang, lemma, freq, 
                            confidence, src 
                     FROM (SELECT lang, wordid, freq, confidence, src
                           FROM sense
                           WHERE synset = ?) s
                     LEFT JOIN word
                     ON word.wordid = s.wordid 
                     ORDER BY freq DESC, confidence DESC
                  """, (synset,))

    elif gridmode == "grid": # senses with confidence == 1.0 in the wn-multi.db are the human projects
        c.execute("""SELECT s.lang, lemma, freq, 
                            confidence, src
                     FROM (SELECT lang, wordid, freq, confidence, src
                           FROM sense
                           WHERE synset = ?
                           AND sense.confidence IS '1.0') s
                     LEFT JOIN word
                     WHERE word.wordid = s.wordid
                     ORDER BY freq DESC, confidence DESC""", (synset,))

    elif gridmode in ("cow", "wnbahasa","wnja"):    
        c.execute("""SELECT s.lang, lemma, freq, 
                            confidence, src
                     FROM (SELECT lang, wordid, freq, confidence, src
                           FROM sense
                           WHERE synset = ?
                           AND sense.lang in (%s)
                           AND sense.confidence IS '1.0') s
                     LEFT JOIN word
                     WHERE word.wordid = s.wordid
                     ORDER BY freq DESC, confidence DESC
                  """ % ','.join('?'*len(langselect)), ([synset] + list(langselect)))

    else: # treat everything else as gridx
        c.execute("""SELECT s.lang, lemma, freq, 
                            confidence, src 
                     FROM (SELECT lang, wordid, freq, confidence, src
                           FROM sense
                           WHERE synset = ?) s
                     LEFT JOIN word
                     ON word.wordid = s.wordid 
                     ORDER BY freq DESC, confidence DESC
                  """, (synset,))

    rows = c.fetchall()
    words = dd(list)
    for r in rows:  # [lang][i] = (lemma, freq, confidence, src)
        words[r[0]].append((r[1], r[2], r[3], r[4]))


    # Fetch Sense-level Verb Frames
    c.execute("""SELECT xlinks.lang, lemma, xref, misc, confidence 
                 FROM xlinks
                 LEFT JOIN word
                 ON xlinks.wordid = word.wordid
                 WHERE synset = ?
                 AND resource = ?
              """, (synset, 'lvframes'))
    rows = c.fetchall()
    lvframes = dd(lambda: dd(list))

    for r in rows:
        # dict[lang][lemma] = [frameid, framestring, symbols]
        lvframes[r[0]][r[1]].append((r[2],r[3],r[4]))
 

    # Fetch Sense-Sense Links
    senslinks = dd(list)
    c.execute("""SELECT w1.lemma, w1.lang, link, 
                        w2.lemma, synset2 
                 FROM senslink 
                 LEFT JOIN word as w1 
                 ON senslink.wordid1 = w1.wordid 
                 LEFT JOIN word as w2 
                 ON senslink.wordid2 = w2.wordid  
                 WHERE synset1 = ?""",  (synset,))

    for r in c:  # senslinks[(lang, lemma1)] = (link, lemma2, synset2)
        senslinks[r[1], r[0]].append((r[2], r[3], r[4]))


    # Fetch Synset-Synset Relations
    c.execute("""SELECT link, synset2, name
                 FROM synlink 
                 LEFT JOIN synset 
                 ON synlink.synset2 = synset.synset 
                 WHERE synset1 = ?
              """, (synset,))
    rows = c.fetchall()

    rels = dd(list)
    for r in rows:  # [link][i] = (synset, name)
        rels[r[0]].append((r[1], r[2]))


    # Fetch Lexname
    c.execute("""SELECT xref, misc, confidence 
                 FROM xlink
                 WHERE synset = ? 
                 AND resource = ? 
              """, (synset, 'lexnames'))
    rows = c.fetchone()

    if rows:
        lexid = rows[0]
        lexname = rows[1]
        lexstring = rows[2]
        # Beautify lexname with subscript n,v,a instead of standard name
        lexname = "%s<sub>%s</sub>"  % (lexname.split('.')[1],
                                        lexn2wpos[lexname.split('.')[0]])
    else:
        lexid = "0"
        lexname = "unknown"
        lexstring = "we don't know the supersense"

    ### Images
    for sid in defs['img']:
        print("""<img align='right' width=200 
                  src ='../wn-ocal/img/%s.png' alt='%s'>
              """ % (defs['img'][sid], defs['img'][sid]))

    ### Words
    print("<table width='100%'>")
    # for l in list(set(words.keys()).intersection(langselect)):   
    # We're now intersecting languages showing with the selected languages
    for i, l in enumerate(sorted(list(set(words.keys()).intersection(langselect)))):
        if i % 2 ==0:
            trcolor = " bgcolor ='#ededed'"     # to gray out every other line in table
        else:
            trcolor = ""
        print("<tr %s>\n  <td><strong>%s</strong></td>" % (trcolor,
                                                           omwlang.trans(l, lang)))
        ws = list()
        for (w, f, conf, src) in words[l]:
            ## show confidence with opacity; freq as subscript
            opac = (" style='opacity: %f'" % (conf-0.3)) if conf != 1.0 else ''
            freq = ('<sub>%d</sub>' % f) if f else ''

            frmsymb = ''
            if w in lvframes[l].keys():
                for triple in lvframes[l][w]:
                    frmsymb += triple[2] + "&#xA;"

            deriv = '' # this holds the sense derivational links
            if senslinks[(l,w)]:
                sls = []
                for (lnk, l2, s2) in senslinks[(l,w)]:
                    sls.append("""
                        <a title='%s: %s (%s)'
                        href='%s&synset=%s&lang=%s'>%s</a>
                        """ % (lnk, l2, s2, wncgi, s2, l, relnam[lnk])
                    )
                     
                deriv += "<font size='-1'>(%s)</font>" % " ".join(sls)

            w = """<a style='color:black;text-decoration:none;'
                      href='%s&lemma=%s&lang=%s&lang2=%s'>%s</a> """ % (wncgi, w, l, lang2, w)

            ws.append("""<span title='source: %s&#xA;conf: %0.2f;&#xA;%s' %s'>%s</span>%s %s
                      """ % (src, conf, frmsymb, opac, w, freq, deriv))
        print("<td><i>%s</i>" % (", ".join(ws)))    # prints the list of word


        #############################
        # PRINT CLASSIFIERS (IF ANY)
        #############################
        resource = "cl_%s" % l
        c.execute("""SELECT xref, misc, confidence
                     FROM xlink
                     WHERE synset = ? AND resource = ?
                     ORDER BY confidence
                  """, (synset,resource))
        cl = c.fetchall()
        if cl:
            print("&nbsp;&nbsp;&nbsp;&nbsp;[CL: ")
            for i, (classifier, original_ss, distance) in enumerate(cl):
                c.execute("""SELECT name
                             FROM synset
                             WHERE synset = ?
                          """, (original_ss,))
                ssname = c.fetchone()[0]
                # this is to avoid annoying spaces after print statements!
                if i != len(cl)-1:
                    separator = ";"
                else:
                    separator = "]"

                print("""<span title="%s (%s)"><a style='color:black;text-decoration:none;'
                      href='%s&synset=%s&lang=%s&lang2=%s'>%s</a></span>%s""" % (ssname, 
                    distance, wncgi, original_ss, l, lang2, classifier, separator))


        #############################################
        # PRINT CORPUS LINK (IF LANGUAGE IN CORPUS)
        #############################################
        if l in corpuslangs:
            print("""<div style="display:block; float:right;">
                     <a class="largefancybox fancybox.iframe" 
                      href="showcorpus.cgi?searchlang=%s&concept=%s&langs2=%s">
                     <span title="NTUMC Examples"><span style="color: #4D99E0;">
                     <i class='icon-book'></i>
                    </span></span></a></div>""" % (l, synset, 'eng'))


        #############################################
        # PRINT IMAGES (NOT CURRENTLY BEING USED)
        #############################################
        if i==0 and len(defs['img']) > 0:
            # Images
            print("  <td rowspan=%d>" % len(words))
            for sid in defs['img']:
                print("""<img align='right' height=150 
                       src ='../wn-ocal/img/%s.png' alt='%s'><br>
                      """ % (defs['img'][sid], defs['img'][sid]))
            print("</td>")


        print("</tr>")
    print("</table>")

    #############################################
    # PRINT DEFINITIONS
    #############################################
    # print "<div id='line'><span>Definitions</span></div>\n"

    # if gridmode in ("ntumcgrid","ntumcgridA","ntumcgridB"):
    #     # Edit Synset and Add New Synset buttons
    #     print("<div id='line'><span>Definitions " + HTML.newdef_bttn(synset,wndb) + "</span></div>\n")
    # else:
    print("<div id='line'><span>Definitions</span></div>\n")
        
    print("<dl>")
    # intersection between (existing langs in defs and examples) 
    # and (langs allowed by the gridmode)
    for l in list(set(list(defs.keys()) + list(exes.keys())).intersection(langselect)):   
        if l == 'img':
            continue
        print("<dt><strong>%s</strong>" % omwlang.trans(l, lang))
        print("<dd>")
        # print "; ".join(defs[l][d] for d in defs[l]) 
        for d in defs[l]:
            print(str(defs[l][d]) + "<br>")
        print(" " )

        ###### EXPERIMENTAL AUDIO
        # if l == "eng":
        #     print HTML.googlespeech_text(l,". ".join(defs[l][d] for d in defs[l]))

        if exes[l]:  ### fixme should use lemmas to match examples (or do off line)
            examples = "; ".join([exes[l][d] for d in exes[l]][:5])  ## show only 5
             ### match longest first, in the unlikely case we have a '|' in the word, don't match
            w = '|'.join(sorted([w[0] for w in words[l] if '|' not in w[0]],key=len, reverse=True))
            examples = re.sub(r"(%s)" % w, r"<font color='green'>\1</font>", examples)
            ## Using Horizontal bar instead of quotes as it is less language dependent
            print(u"― <i>%s</i>" % examples)
    print("</dl>")

    ### Relations
    print("<div id='line'><span>Relations</span></div>\n")
    print("<table>")

    if rels:
        for rel in  ["hypo", "also", "hype", "inst", 
                     "hasi", "mmem", "msub", "mprt", 
                     "hmem", "hsub", "hprt", "attr", 
                     "sim", "enta", "caus", "dmnc", 
                     "dmnu", "dmnr", "dmtc", "dmtu", 
                     "dmtr", "eqls","ants","qant", "hasq"]:
            if rels[rel]:
                  print(u"<tr><td valign='top'><strong>%s</strong></td>" % \
                      omwlang.trans(rel, l))
                  print("<td>")
                  for (sss, name) in rels[rel]:
                      print("<a title='%s' href='%s&synset=%s&lang=%s&lang2=%s'>%s</a>" % \
                          (sss, wncgi, sss, lang, lang2, name))
                  print("</td></tr>")

    # Print Lexid
    print("""<tr><td valign='top'><strong>
             <span title='lexnames'>Semantic Field:</span></strong></td>
             <td valign='top'><span title='%s: %s'>%s</span></td>
          """ % (lexid, lexstring, lexname))
    
    print("</table>\n"    )

    # Print Verb Frames
    if vframes:
        print("<div id='line'><span>Verb Frames</span></div>\n")
        print("<table><tr><td valign='top'>")

        for vid in vframes.keys():
            print("""<span title='%s: %s'><nobr>%s;&#160;&#160;</nobr></span>
                  """ % (vid, vframes[vid][1], vframes[vid][0]))
        print("""</td></tr></table>\n""")

    # Print External References
    print("<div id='line'><span>External Links</span></div>\n")

    # SUMO
    c.execute("""SELECT xref, misc 
                 FROM xlink 
                 WHERE resource='sumo'
                 AND synset=?""", (synset,))
    xrefs = c.fetchall()
    if xrefs:
        print("<p>%s:  " % label('SUMO', 'Suggested Upper Merged Ontology', 
                                'http://www.ontologyportal.org/'))
        for (xref, misc) in xrefs:
            print("""%s <a href='%s&%s'>%s</a>\n
                  """  % (misc,  sumocgi,  xref, xref))

    # TempoWN
    c.execute("""SELECT xref, misc 
               FROM xlink 
               WHERE resource='TempoWN' 
               AND synset=?""", (synset,))
    xrefs = c.fetchall()
    if xrefs:
        print("<p>%s:  " % label('TempoWN', 'Tempo Wordnet',  
                                 'https://tempowordnet.greyc.fr/'))
        for (xref, misc) in xrefs:
                opacity = float(misc)+0.3    
                if xref == "Past":
                    print('<font style="opacity: %f; font-size:150%%"> %s</font>' % (opacity,
                        u'◀' if float(misc) >= 0.05 else u'◁'))
                elif xref == "Present":
                    print('<font style="opacity: %f; font-size:150%%"> %s</font>' % (opacity,
                        u'▲' if float(misc) >= 0.05 else u'△'))
                elif xref == "Future":
                    print('<font style="opacity: %f; font-size:150%%"> %s</font>' % (opacity,
                        u'▶' if float(misc) >= 0.05 else u'▷'))
                else:
                    continue
                    
        for (xref, misc) in xrefs:
                if xref == "Past":
                    print("(%s: %0.03f;" % (xref, float(misc)))
                elif xref == "Present":
                    print("%s: %0.03f;" % (xref, float(misc)))
                elif xref == "Future":
                    print("%s: %0.03f)" % (xref, float(misc)))
                else:
                    continue

    # SentiWN
    c.execute("""SELECT xref, misc
               FROM xlink 
               WHERE resource='SentiWN' 
               AND synset=?""", (synset,))
    xrefs = c.fetchall()
    if xrefs:
        print("<p>%s: " % label('SentiWN', 'SentiWordNet3.0',  
                                 'http://sentiwordnet.isti.cnr.it/'))
        for (xref, misc) in xrefs:
            opacity = float(misc)+0.3    
            if xref == "Positive":
                print('<font color="green" style="opacity: %f; font-size:150%%"> %s</font>' % (opacity,
                    u'▲' if float(misc) >= 0.05 else u'△'))
            else:
                print('<font color="red" style="opacity: %f; font-size:150%%"> %s</font>' % (opacity,
                    u'▼' if float(misc) >= 0.05 else u'▽'))
        
        for (xref, misc) in xrefs:
                if xref == 'Positive':    
                    print("<font color='green'>(+%0.02f</font>" % (float(misc)))
                else:
                    print("<font color='red'>-%0.02f)</font>" % (float(misc)))


    # MLSentiCon
    c.execute("""SELECT xref, misc 
               FROM xlink 
               WHERE resource='MLSentiCon' 
               AND synset=?""", (synset,))
    xrefs = c.fetchall()
    if xrefs:
        print("%s: " % label('MLSentiCon', 'Multilingual Sentiment Lexicon',  
                                 'http://timm.ujaen.es/recursos/ml-senticon/'))
        for (xref, misc) in xrefs:
            opacity = float(misc)+0.3    
            if xref == "Positive":
                print('<font color="green" style="opacity: %f; font-size:150%%"> %s</font>' % (opacity,
                    u'▲' if float(misc) >= 0.05 else u'△'))
            else:
                print('<font color="red" style="opacity: %f; font-size:150%%"> %s</font>' % (opacity,
                    u'▼' if float(misc) >= 0.05 else u'▽'))
        
        for (xref, misc) in xrefs:
                if xref == 'Positive':    
                    print("<font color='green'>(+%0.02f</font>" % (float(misc)))
                else:
                    print("<font color='red'>-%0.02f)</font>" % (float(misc)))


    # PRINT COMMENTS
    if len(coms) > 0:
        print("<div id='line'><span>Comments</span></div>\n")
    for com in coms:
        (comment, user, t) = com
        print("<p>")
        print("""<b><sub> %s (%s)</sub></b> <br>
                 <blockquote>%s</blockquote>
                 """ % (user, t, comment))


    if gridmode == "ntumcgrid":
        # Edit Synset and Add New Synset buttons
        print(HTML.editsynset_bttn(usrname, synset))
        print(HTML.newsynset_bttn(synset))


#######################################
# IF QUERY == Lemma (string)
#######################################
elif (lemma):   ## Show all the entries for this lemma in language
    print(HTML.status_bar(usrname))  # Top (Right) Status Bar
    print(u"<h6>Results for «&#8239;%s&#8239;» (%s)</h6>\n" % (lemma, lang))
    ## note the use of narrow non-breaking spaces


    lems = list(expandlem(lemma_raw)) 


    # FIXME! Order the synsets by sense frequency

    if lemma.startswith('def::'):
        print('def', lemma[5:])
        c.execute("""SELECT DISTINCT synset 
                     FROM synset_def 
                     WHERE def GLOB ?  
                     AND lang = ?
                     LIMIT 200
                  """, [str(lemma[5:]), lang])
        print(c)
    else:


        if containsAny(lemma, ".*+?[]"):
            glob = " OR lemma GLOB ? " # % lemma
        else:
            glob = ""

        lemma_q = "lemma IN (%s) %s " % (placeholders_for(lems), glob)



        if gridmode in ('cow','wnbahasa','wnja','grid'):     
            sense_conf = """ AND sense.confidence IS '1.0' """
        else: # ('gridx','ntumcgrid')
            sense_conf = ""

        qparams = list(lems)             # consumed in "lemma IN (...)"
        if glob:
            qparams.append(lemma)  # consumed by "OR lemma GLOB ?"
        qparams.append(lang)       # consumed by "sense.lang = ?"
        c.execute("""SELECT DISTINCT synset
                     FROM word 
                     LEFT JOIN sense
                     WHERE word.wordid = sense.wordid
                     AND ( %s )
                     %s
                     AND sense.lang = ?
                     LIMIT 200
                  """ % (lemma_q, sense_conf), 
                  qparams)

    row = c.fetchall()

    sss = set()

    # If there is matches of the lemma in that language
    if row:
        for s in row:
            sss.add(s[0])

        ass = placeholders_for(sss)

        if gridmode in ('cow','wnbahasa','wnja','grid'):     
            sense_conf = """ AND sense.confidence IS '1.0' """
        else: # ('gridx','ntumcgrid')
            sense_conf = ""


        c.execute("""SELECT synset, s.lang, lemma, 
                            freq, src, confidence
                     FROM ( SELECT synset, lang, wordid, freq, 
                                   src, confidence 
                            FROM sense
                            WHERE synset in (%s) 
                            AND lang in (?,?) 
                            %s ) s
                     LEFT JOIN word
                     WHERE word.wordid = s.wordid
                     ORDER BY freq DESC
                  """ % (ass, sense_conf), [*sss, lang, lang2] )



        words = dd(lambda: dd(list))
        freq = dd(int)
        for r in c:
        ### FIXME take these out of the wordnet
            if not (r[1] == 'jpn' and '_' in r[2]):
                # words[synset][lang][(lemma, freq, src, confidence)]
                words[r[0]][r[1]].append((r[2], r[3], r[4], r[5]))
                if r[3]:
                    freq[r[0]] += r[3]

        # Fetch definitions
        c.execute("""SELECT synset, lang, sid, def 
                     FROM synset_def 
                     WHERE synset in (%s) 
                     AND lang in (?, ?)
                  """ % ass, [*sss, lang, lang2])

        defs = dd(lambda: dd(lambda: dd(str)))
        for r in c:
            defs[r[0]][r[1]][r[2]] = r[3]


        # Fetch Domain Categories (for definitions)
        # synset2 is the category of synset1
        c.execute("""SELECT synset1, synset2, name 
                     FROM synlink
                     LEFT JOIN synset
                     WHERE synset2 = synset
                     AND synset1 in (%s) 
                     AND link = 'dmnc'
                  """ % ass, [*sss])
        # synset1 : [synset2, name]
        dmncs = dd(list)
        for r in c:
            dmncs[r[0]] = [r[1],r[2]]


        # Fetch Verb Frames
        c.execute("""SELECT xref, misc, confidence, synset 
                     FROM xlink
                     WHERE synset in (%s) 
                     AND resource = '%s' 
                  """ % (ass, 'svframes'), [*sss])
        rows = c.fetchall()

        vframes = dd(lambda: dd(list))
        for r in rows:
            vframes[r[3]][r[0]].append(r[1]) # full string
            vframes[r[3]][r[0]].append(r[2]) # symbols
            vframes[r[3]][r[0]].append(vfargs[r[1]]) # V ArgNumbers

        ###########################################
        # Print  HTML for List of Synsets by Lemma
        ###########################################
        print("<table>\n")
        for (i, s) in enumerate(sss):

            if dmncs[s] != []:
                dmnc = """[in <a href='%s&synset=%s&lang=%s&lang2=%s'>%s</a>]""" %  (wncgi, s, lang, lang2, dmncs[s][1])
            else:
                dmnc = ''

            # write up verb frames
            wfrmsset = []; wfrmscap = ''
            if s in vframes.keys(): # if synset has vframes
                for vid in sorted(vframes[s].keys()):
                    wfrmscap += """%s: %s &#xA;""" % (vid, vframes[s][vid][1]) 
                    wfrmsset.append(vframes[s][vid][2])
                wfrmsset = sorted(list(set(wfrmsset)))
                wfrmsset = ', '.join(wfrmsset)

            if wfrmsset:
                wfrmssymb = """<span title='%s'>%s</span>""" % (wfrmscap, wfrmsset)
            else:
                wfrmssymb = ''

            print("<tr>\n")

            # Synset
            print("""<td valign='top'><a href='%s&synset=%s&lang=%s&lang2=%s'>
                     <nobr>%s""" %  (wncgi, s, lang, lang2, s))
            if freq[s] > 0: ### frequency
                print("<font size='-1'>(%d)</font>" % (freq[s]))
            print("</nobr><br><font size='-1'>%s</font></a></td>" % wfrmssymb)



            ### print words
            if words[s][lang] and words[s][lang2] and lang != lang2:
                print("""<td  valign='top'><table style="width:100%%"><tr>
                         <td bgcolor = '#ededed'>%s</td></tr>
                         <tr><td>%s</td></tr></table></font>""" % \
                (sq([hword(w,lems,src,conf) for (w,f,src,conf) in words[s][lang]], ", "),
                 sq([hword(w,lems,src,conf) for (w,f,src,conf) in words[s][lang2]], ", ")))
            elif words[s][lang]:
                print("  <td  valign='top'>%s</font>" % \
                    sq([hword(w,lems,src,conf) for (w,f,src,conf) in words[s][lang]], ", "))
            else:
                print("  <td valign='top'>%s</font>" % "NO LEX")

            print("  <td  valign='top'>&nbsp;&nbsp;&nbsp;&nbsp;</td>")


            # Print definitions
            if defs[s][lang] and defs[s][lang2] and lang != lang2:
                tdf = list()  # stores defs in the search lang
                for i in sorted(defs[s][lang].keys()):
                    tdf.append(defs[s][lang][i])
                edf = list()  # stores defs in the support lang
                for i in sorted(defs[s][lang2].keys()):
                    edf.append(defs[s][lang2][i])

                print("""<td  valign='top'>%s <span title='%s'>%s</span>
                         </td>""" % (dmnc,sq(edf, "; "), sq(tdf, "; ")))

            elif defs[s][lang]:
                tdf = list()  # stores defs in the search lang
                for i in sorted(defs[s][lang].keys()):
                    tdf.append(defs[s][lang][i])

                print("<td  valign='top'>%s %s</td>" % (dmnc, sq(tdf, "; ")))

            elif defs[s][lang2]:
                edf = list()  # stores defs in the search lang
                for i in sorted(defs[s][lang2].keys()):
                    edf.append(defs[s][lang2][i])

                print("<td  valign='top'>%s %s</td>" % (dmnc, sq(edf, "; ")))

            else:
                print("<td  valign='top'>%s %s</font>" %(dmnc, "NO DEFINITION"))

            if gridmode == "ntumcgrid":
                # Add New Synset and Edit synset buttons
                print("""<td style="vertical-align:center">""")
                print(HTML.editsynset_bttn(usrname, s))
                print(HTML.newsynset_bttn(s))
                print("""</td>""")

            print("</tr>\n")
        print("</table>")

    ######################
    # If nothing is found
    ######################
    else:
        lemstr =  ", ".join(lems)
        print(f"<p>No synsets found (for any of {lemstr})!")


        # Quick "Search again in Lang2" button
        if lang != lang2:
            print("""<form method="post" action="%s">
            <strong>Look it up again in:</strong>
            <input type="hidden" name="lemma" value="%s">
            <input type="hidden" name="lang" value="%s">
            <input type="hidden" name="lang2" value="%s">
            <input type="submit" name="Query" value="%s">
            </form></p>""" % (wncgi, lemma, lang2, lang, 
                              omwlang.trans(lang2, lang)))

        if gridmode == "ntumcgrid":
            # Print bottom buttons (+NE, +NewSS, Multidict)
            print(HTML.ne_bttn(),)
            print(HTML.newsynset_bttn(),)
            print(HTML.multidict_bttn(lang, lemma))
        if gridmode == "ntumc-noedit":
            print(HTML.multidict_bttn(lang, lemma))


################################################################################
# If nothing was added in search (default display)
################################################################################
else:
    print("<h4> Welcome to the %s (%s)</h4>\n" % (wnnam, wnver))

    if gridmode == "ntumcgrid":
        print(HTML.ne_bttn())
        print(HTML.newsynset_bttn())
        print(HTML.multidict_bttn(lang, lemma))
    if gridmode == "ntumc-noedit":
        print(HTML.multidict_bttn(lang, lemma))

################################################################################
# Warn users if the list was truncated (current limit is 200)
################################################################################
try: # sss may not have been defined before
    if len(sss) == 200:
        print("""This list has been truncated to 200 entries.""")
except:
    pass

################################################################################
# Search Interface, User Interface  & Footer
################################################################################
print("""<hr><p>""")

# This is the original that takes the full list of languages!
# print HTML.search_form(wncgi, lemma, langs, lang, "Langs: ", lang2, scaling),

print(HTML.search_form(wncgi, lemma, langselect, lang, "Langs: ", lang2, scaling)) # Print Search Form
# print HTML.language_selection(langselect, langs, wncgi)

# # Multidict should be ported excluding CCD 
# # (which we don't have permission to share)
# if gridmode != "ntumcgrid":
#     if lang in ("cmn", "eng"):
#         print HTML.multidict_bttn(lang, lemma)

end_time = time.time()



# Print Search History
if lemma in seen_lemmas:
    seen_lemmas.remove(lemma)
if len(seen_lemmas) > 0:
    print("<hr>")
    print("Seen Lemmas: ")
    for w in seen_lemmas:
        print ("""<a style='color:black;text-decoration:none;'
                   href='%s&lemma=%s'>%s</a>; """ % (wncgi, w, w))


#print synset_hist #TEST


# Print Language Selection Panel
print("""<hr><div style="font-size:90%;color:grey;float:right">""")
print(HTML.language_selection(langselect, langs, wncgi))
print("""<br><span style="font-size:80%%;color:grey;">(%s seconds)</span></div>"""  % (str(end_time - start_time)[:7]))

print("<nobr><a href='%s'>More detail about the %s (%s)</a></nobr>" % (wnurl, wnnam, wnver))
if gridmode != "gridx":
    print("""<br>This project is now integrated in the 
             <a href='%s'> %s (%s)</a>""" % (omwurl, omwnam, wnver))
print(f"""<br>Maintainer: <a href="{fcbond_url}">
             Francis Bond</a>""")
print('&lt;<a href="mailto:bond@ieee.org">bond@ieee.org</a>&gt;')

print("  </body>")
print("</html>")
