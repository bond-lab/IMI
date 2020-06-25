#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##
## Summarize how much has been annotated
##


import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import os, http.cookies # cookie
import sqlite3
from collections import defaultdict as dd
import datetime

import json
from lang_data_toolkit import valid_usernames as valid_usrs
from ntumc_gatekeeper import concurs

# Fixes encoding issues when reading cookies from os.environ
import sys


###############################################################
# This cgi script will serve to access and edit the corpus db.
# It allows editing tags, and to correct segmentation problems.
# Eventually should also allow to create new datasets, etc.
###############################################################

form = cgi.FieldStorage()

db = form.getfirst("db", "../db/eng.db")
lang = db[-6:-3]

sid_from = form.getfirst("sid_from", 0)
sid_to = form.getfirst("sid_to", 1000000)

days = int(form.getfirst("days", 7))


selfcgi = "tag-status.cgi"
wncgi_noedit = "wn-gridx.cgi?gridmode=ntumc-noedit&lang=%s&lemma=%s"
wncgi_edit = "wn-gridx.cgi?usrname=%s&gridmode=ntumcgrid&lang=%s&lemma=%s"
taglexscgi = "tag-lexs.cgi?corpus=%s&lang=%s&usrname_cgi=%s&lemma=%s&Query=Search&lim=-1&sid_from=%s&sid_to=%s"

fix_corpus = "fix-corpus.cgi?corpus=%s&sid_edit=%s" # lang, user, sid
tag_word = "tag-word.cgi?corpus={}&lang={}&usrname_cgi={}&gridmode={}&sid={}" # lang, lang, usr, gridmode, sid



################################################################
# MASTER COOKIE
################################################################
if 'HTTP_COOKIE' in os.environ:
    C = http.cookies.SimpleCookie(os.environ['HTTP_COOKIE'])
else:
    C = http.cookies.SimpleCookie()

# FETCH USERID/PW INFO
if "UserID" in C:
    userID = C["UserID"].value
    hashed_pw = C["Password"].value
else:
    userID = "guest"
    hashed_pw = "guest"




################################################################
# HTML
################################################################
# Header
print(u"""Content-type: text/html; charset=utf-8\n
<!DOCTYPE html>\n
  <html>\n
    <head>

      <!-- KICKSTART -->
      <script 
       src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
      <script src="../HTML-KickStart-master/js/kickstart.js"></script>
      <link rel="stylesheet" 
       href="../HTML-KickStart-master/css/kickstart.css" media="all" /> 

      <!-- FANCYBOX -->
      <!-- Add jQuery library -->
      <script type="text/javascript" 
       src="../fancybox/lib/jquery-1.10.1.min.js"></script>
      <!-- Add fancyBox main JS and CSS files -->
      <script type="text/javascript" 
       src="../fancybox/source/jquery.fancybox.js?v=2.1.5"></script>
      <link rel="stylesheet" type="text/css" 
       href="../fancybox/source/jquery.fancybox.css?v=2.1.5" 
       media="screen" />
      <script type="text/javascript" 
       src="../fancybox-ready.js"></script>

      <!-- TOGGLE DIV VISIBILITY BY ID -->
      <script type="text/javascript">
         function toggle_visibility(id) {
           var e = document.getElementById(id);
           if(e.style.display == 'block')
              e.style.display = 'none';
           else
              e.style.display = 'block';
         }
      </script>


     <!-- TOGGLE DIV VISIBILITY BY ID -->
     <script type="text/javascript">
        function togglecol(id) {
            if (window.document.getElementById(id).style.visibility == "collapse") {
                window.document.getElementById(id).style.visibility = "visible";
            } else {
                window.document.getElementById(id).style.visibility = "collapse";
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
                window.document.getElementById(id).style.visibility = "visible";
           }
         } 
       }
     </script>

    </head>
    <body>\n""")





# print("""
#  <button onclick="togglecol('c2')">Show Col2</button> 
#  <button onclick="showallunder('supertable')">Show All Rows</button> 
# <table id="supertable">
#   <colgroup>
#     <col id="c1">
#     <col id="c2">
#     <col id="c3">
#   </colgroup>
#   <thead><tr>
#       <th>Concept</th>
#       <th>Count</th>
#       <th>Actions</th>
#   </tr></thead>
#   <tr id="ss1">
#     <td >Concept1   </td>
#     <td >Count1 </td>
#     <td id="ss3">Actions1 <button onclick="togglecol('ss1')">hide</button></td>
#   </tr>
#   <tr id="ss2">
#     <td>Concept2</td>
#     <td>Count2</td>
#     <td>Actions2 <button onclick="togglecol('ss2')">hide</button></td>
#   </tr>
# <table>""")

now = datetime.datetime.now()
then = now - datetime.timedelta(days=days)

print(f"<h2>Showing concept changes since {then}</h2>")

for db in "eng cmn jpn".split():
    conn, c = concurs(db)
    print(f"<h3>Changes in Corpus: {db}</h3>")
    c.execute(f"""SELECT  usrname_new, count(usrname_new), 
    GROUP_CONCAT(sid_new || ':' || clemma_new, ';') 
FROM concept_log 
WHERE date_update > ?
GROUP BY usrname_new""",
              (then.isoformat(),))

    if c:
        print("""<table>
        <tr><th>username</th><th>counts</th><th>concepts</th></tr>""")
        for r in c:
            if not r[2]:
                continue
            print("<tr>")
            print(f"<td>{r[0]}</td>")
            print(f"<td>{r[1]}</td>")
            changed= []
            for thing in r[2].split(';'):
                (sid, clemma) = thing.split(':')
                tagurl=tag_word.format(db, db, userID, "ntumcgrid", sid)
                changed.append(f"<a href='{tagurl}'>{clemma}</a>")
            changed_str=", ".join(changed)
            print(f"<td>{changed_str}</td>")
            print("</tr>")
        print("""</table>""")

        
# print("""<h4>Concepts tagged </h4>\n """ % (db,) )
# print("""<h6>From sentence %s to sentence %s</h6>""" % (sid_from, sid_to))



# ##############################
# # SELECT FROM concept BY tag
# ##############################
# lemma_tags = dd(lambda: dd(int))
# a.execute("""SELECT tag, clemma, count(*)
#              FROM concept
#              WHERE (tag in ('x','w','e','') OR tag is Null)
#              AND sid > ? AND sid < ?
#              GROUP BY clemma, tag
#              ORDER BY count(*)""", [sid_from, sid_to])
# for (tag, clemma, count) in a:
#     lemma_tags[tag][clemma] = count
    
# lemma_comments = dd(lambda: dd(str))
# a.execute("""SELECT tag, clemma, group_concat(comment, "; ") AS comments
# FROM concept  
# WHERE sid > ? AND sid < ?
# AND (tag in ('x','w','e','') OR tag is Null) 
# AND (comment != '' OR comment is not Null) 
# GROUP BY clemma, tag""", [sid_from, sid_to])
# for (tag, clemma, comments) in a:
#     lemma_comments[tag][clemma] = comments

    
# sid_tags = dd(lambda: dd(int))
# a.execute("""SELECT sid, tag, count(*) 
#              FROM concept
#              WHERE (tag in ('x','w','e','') OR tag is Null)
#              AND sid > ? AND sid < ?
#              GROUP BY sid, tag 
#              ORDER BY count(*)""", [sid_from, sid_to])
# for (sid, tag, count) in a:
#     sid_tags[tag][sid] = count

# sid_comments = dd(lambda: dd(str))
# sid_clemmas = dd(lambda: dd(str))
# a.execute("""SELECT sid, tag, group_concat(clemma, "; ") as clems, group_concat(comment, "; ") AS comments
# FROM concept  
# WHERE sid > ? AND sid < ?
# AND (tag in ('x','w','e','') OR tag is Null) 
# GROUP BY sid, tag""", [sid_from, sid_to])
# for (sid, tag, clemmas, comments) in a:
#     sid_comments[tag][sid] = comments
#     sid_clemmas[tag][sid] = clemmas


    
# lemma_all = dd(lambda: dd(list))
# a.execute("""SELECT sid, tag, clemma
#              FROM concept
#              WHERE (tag in ('x','w','e','') OR tag is Null)
#              AND sid > ? AND sid < ?
#              GROUP BY sid, tag 
#              ORDER BY count(*)""", [sid_from, sid_to])
# for (sid, tag, clemma) in a:
#     lemma_all[tag][clemma].append(sid)


# print("""<ul class="tabs left">
#          <li><a href="#Tags">Tags</a></li>
#          <li><a href="#w">Tagged 'w'</a></li>
#          <li><a href="#w_bysent">'w' (by sid)</a></li>
#          <li><a href="#e">Tagged 'e'</a></li>
#          <li><a href="#e_bysent">'e' (by sid)</a></li>
#          <li><a href="#None">Tagged 'None'</a></li>
#          <li><a href="#None_bysent">'None' (by sid)</a></li>
#          <li><a href="#x">Tagged 'x'</a></li>
#          <li><a href="#x_bysent">'x' (by sid)</a></li>
#          <li><a href="#empty">Tagged ' '</a></li>
#          <li><a href="#empty_bysent">' ' (by sid)</a></li>
#          </ul>""")


# print("""<div id="Tags" class="tab-content">""")
# for tag in lemma_tags.keys():
#     if tag == "":
#         tagdiv = "empty"
#     else:
#         tagdiv = tag
#     tag_dict = lemma_tags[tag]
#     count_types = len(tag_dict.values())
#     count_tokens = 0
#     for clemma, count in tag_dict.items():
#         count_tokens += count
#     print("""<h6>Concepts Tagged with '%s': %s Types (%s tokens)</h6>
#              """ % (tagdiv, count_types, count_tokens))
# print("""</div>""")

# for tag in lemma_tags.keys():
#     if tag == "":
#         tagdiv = "empty"
#     else:
#         tagdiv = tag

#     tag_dict = lemma_tags[tag]
#     all_dict = lemma_all[tag]
#     count_types = len(tag_dict.values())
#     count_tokens = 0
#     for clemma, count in tag_dict.items() :
#         count_tokens += count

#     print("""<div id="%s" class="tab-content">""" % tagdiv)
#     print("""<h6>Concepts Tagged with '%s': %s Types (%s tokens)</h6>
#              """ % (tagdiv, count_types, count_tokens))
# #    print("""<h5>%s Concepts tagged with '%s'</h5>""" % (count_types, tagdiv))
#     print("""<div style="width:50%"><table cellspacing="0" cellpadding="0" 
#               id="id_of_table" class="striped tight sortable">""")
#     print("""<thead><tr><th>Concept</th><th>Count</th>
#              <th>Actions</th><th>by sid</th><th>Comments</th></tr></thead>""")
#     for count, clemma in sorted([(co,cl) for (cl,co) in tag_dict.items()], reverse=True):
#         taglexs = taglexscgi % (lang,lang,userID,clemma, sid_from, sid_to)
#         wngrid = wncgi_edit % (userID,lang, clemma)
#         bysid =[]
#         if tag =='e':
#             for sid in all_dict[clemma]:
#                 fix_corpus_url = fix_corpus % (lang, sid)
#                 bysid.append("<a href='%s'>%s</a>" % (fix_corpus_url,sid))
#         bysidstr = ', '.join(bysid)
#         print("""<tr><td><nobr>%s</nobr>
#                      </td><td>%s</td>
#                      <td><a class='largefancybox fancybox.iframe' title='lookup in wordnet'
#                             href="%s"><i class="icon-search"></i></a>
#                          <a class='largefancybox fancybox.iframe'  title='lexical tagger'
#                             href="%s"><i class="icon-tags"></i></a></td>
#         <td>%s</td>
#         <td>%s</td>
#                     </tr>""" % (clemma,count,wngrid,
#                                 taglexs,bysidstr,
#                                 lemma_comments[tag][clemma]))
#     print("</table></div></div>")

# # URL column (when needed)
# # <th id="url" >URL</th> 
# # <td><nobr>http://172.21.174.40/ntumc/cgi-bin/%s</nobr></td>

# for tag in sid_tags.keys():
#     if tag == "":
#         tagdiv = "empty"
#     else:
#         tagdiv = tag

#     print("""<div id="%s_bysent" class="tab-content">""" % tagdiv)

#     tag_tokens = 0
#     for sid, count in sid_tags[tag].items():
#         tag_tokens += count

#     print("""<h6>%s Sentences need to be fixed (%s '%s' tokens)</h6>
#                   """ % (len(sid_tags[tag].keys()), tag, tag_tokens))

#     print("""<div style="width:75%"><table cellspacing="0" cellpadding="0"
#                           class="striped tight sortable">""")
#     print("""<thead><tr><th>SID</th><th>Count</th>
#                      <th>Actions</th><th>Clemmas</th><th>Comments</th></tr></thead>""")

#     for sid, count in sid_tags[tag].items():

#         fix_corpus_url = fix_corpus % (lang, sid)
#         tag_word_url = tag_word % (lang,lang,userID,"ntumcgrid",sid) 

#         print("""<tr><td><nobr>%s</nobr>
#                      </td><td>%s</td>
#                      <td><a class='largefancybox fancybox.iframe'
#                         href="%s"><i class="icon-edit"></i></a>
#                      <a class='largefancybox fancybox.iframe' 
#                         href="%s"><i class="icon-tags"></i></a></td>
#                      <td>%s</td><td>%s</td>
#                 </tr>""" % (sid,count,fix_corpus_url,tag_word_url,
#                             sid_clemmas[tag][sid], sid_comments[tag][sid]))
#     print("</table></div></div>")

# # URL column (when needed)
# # <th>URL</th>
# # <td><nobr>http://172.21.174.40/ntumc/cgi-bin/%s</nobr></td>




####################
# BOTTOM STATUS BAR
####################
print("""<br><span style="position: fixed; 
          bottom: 10px; right: 10px;">""")

if userID in valid_usrs:
    print(u"""<span title='Username'><button type="button" 
               style="font-size:20px; text-decoration:none; 
               color:black;" disabled>%s</button></span>""" % userID)
else:
    print(u"""<span title='Username'><button type="button" 
               style="font-size:20px; text-decoration:none; 
               color:red;" disabled>invalid_usr</button></span>""")

print("""<span title='Database'><a class='fancybox' 
          href='#goto'
          style='text-decoration:none;'>
          <button class="btn" type="submit"
          style='font-size:20px;'>%s</button></a>
         </span>""" % db)

print("""<span title='Database'><a href='dashboard.cgi'>
          <button class="btn" type="submit"
          style='font-size:20px;'><i class="icon-home"></i></button></a>
         </span>""")

print("""</span>""")  # CLOSES THE BOTTOM FLOATING BAR


            # #######################
            # # TOP RIGHT LOG BAR
            # #######################
            # print(u"""<br><span style="position:fixed; 
            #           top:10px; right:5px;">""")
            # if log_status == "":
            #     pass
            # else:
            #     print("""<table cellpadding="3" bgcolor="#fbfbfb" 
            #               style="border-collapse: collapse; 
            #               border: 1px solid black; display: inline-table; 
            #               margin-top: 5px;">""")
            #     print("""<tr style="text-align:center"><td>%s</td>
            #              </tr></table>""" %(log_status,))
            # print("""</span>""") # CLOSES THE TOP FLOATING BAR

            # print(""" </form> """) # CLOSES THE EDITING FORM



#############################
# INVISIVLE DIV TO GOTO FORM
#############################
print("""<div id="goto" style="width:400px;display: none;">
            <b>Select a database and an SID</b><br>""")

# onsubmit="window.location.reload(true)"
print("""<hr><form action="%s" method="post" 
         name="goto"> """ % (selfcgi))

print("""<center><table cellpadding="3" bgcolor="#E0E0E0" 
          style="border-collapse: collapse; border: 1px solid black; 
          margin-top: 5px;">""")

# CHOOSE DB
print("""<tr style="text-align:center">""")
print("""<td><span title="database">
         <b>database:</b></span></td>
         <td><select id="sid" name="db"
         style="text-align:center" required>""")

for valid_db in ["../db/eng.db","../db/cmn.db","../db/ind.db"]:
    if db == valid_db:
        print("""<option value ='%s' selected>%s
                 </option>""" % (valid_db, valid_db))
    else:
        print("""<option value ='%s'>%s
                 </option>""" % ( valid_db, valid_db))
print("""</select></td>""")
print("""</tr>""")

# CHOOSE SIDS
print("""<tr style="text-align:center">""")
print("""<td><span title="sid from">
          <b>sid from: </b></td><td><input type="text" size="8" 
          name="sid_from" style="text-align:center" 
          value="%s" required/> </span></td>""" % sid_from)
print("""</tr>""")
print("""<tr style="text-align:center">""")
print("""<td><span title="sid to">
          <b>sid to: </b></td><td><input type="text" size="8" 
          name="sid_to" style="text-align:center" 
          value="%s" required/> </span></td>""" % sid_to)
print("""</tr>""")

print("""</table></center>""")

print(u"""<center><span title='Go to...'">
          <input type="submit" value="Go"
           style="font-size:20px; text-decoration:none;
           color:green; margin-top: 5px;"></center>""")
print("""</form>""")
print("""</div>""")


#############
# CLOSE HTML
#############
print("""</body></html>\n""")

