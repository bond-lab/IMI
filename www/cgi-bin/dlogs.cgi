#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
# This cgi is the Wordnet Editing Review / Logging Reports  
# The logs of the WN.db can be accessed here by user, date or a combination 
# of these. 
# Currently, it shows only newly created synsets.

# ToDo: see added lemmas, and definitions, examples, relations, etc.
################################################################################

import cgi, urllib
import cgitb; cgitb.enable()  # for troubleshooting
import os
import http.cookies
import re, sqlite3, collections
from collections import defaultdict as dd
import datetime
from ntumc_webkit import *
from ntumc_util import placeholders_for
from lang_data_toolkit import *




form = cgi.FieldStorage()
lang = form.getfirst("lang", "eng")
lang2 = form.getfirst("lang2", "eng") # backoff language


viewmode = form.getfirst("viewmode")

userid = form.getfirst("userid", "all") # defaults to every user 
mode = form.getfirst("mode") # viewing mode


exclude_undated = form.getfirst("exclude_undated")
searchlang = form.getlist("searchlang[]") # language to specify search 
version = form.getfirst("version", "0.1")




### reference to self (.cgi)
selfcgi = "dlogs.cgi"

### working wordnet.db 
wndb = "../db/wn-ntumc.db"

### corpus db?
corpusdb = form.getfirst("corpusdb", "../db/eng.db")


### reference to wn-grid (search .cgi)
omwcgi = "wn-gridx.cgi"


wncgi_edit = "wn-gridx.cgi?usrname=%s&gridmode=ntumcgrid&synset=%s"
taglexscgi = "tag-lexs.cgi?corpus=%s&lang=%s&usrname_cgi=%s&lemma=%s&Query=Search&lim=-1&sid_from=%s&sid_to=%s"

fix_corpus = "fix-corpus.cgi?db_edit=%s&usr=%s&sid_edit=%s" # db, user, sid
tag_word = "tag-word.cgi?corpus=%s&lang=%s&usrname_cgi=%s&gridmode=ntumcgrid&sid=%s" # lang, lang, usr, sid




user_list = valid_usernames + valid_usernames_old



################################################################################
# SETTING UP DATE LIMITS
################################################################################
if "today" in form:
    dfrom = datetime.date.today()
    dto = datetime.date.max
elif "yesterday" in form:
    dfrom = datetime.date.today() - datetime.timedelta(1)
    dto = datetime.date.max
elif "threedays" in form:
    dfrom = datetime.date.today() - datetime.timedelta(3)
    dto = datetime.date.max
elif "sevendays" in form:
    dfrom = datetime.date.today() - datetime.timedelta(7)
    dto = datetime.date.max
else:
    datefrom = form.getfirst("datefrom") # start date
    if datefrom:
        try:
            dfrom = datetime.date(int(datefrom.split('/')[2]),
                                  int(datefrom.split('/')[0]),
                                  int(datefrom.split('/')[1]))
        except:
            dfrom = datetime.date(int(datefrom.split('-')[0]),
                                  int(datefrom.split('-')[1]),
                                  int(datefrom.split('-')[2]))
            
    else:
        dfrom = datetime.date.min

    dateto = form.getfirst("dateto") # end date
    if dateto:
        try:
            dto = datetime.date(int(dateto.split('/')[2]),
                                int(dateto.split('/')[0]),
                                int(dateto.split('/')[1]))

        except:
            dto = datetime.date(int(dateto.split('-')[0]),
                                int(dateto.split('-')[1]),
                                int(dateto.split('-')[2]))

    else:
        dto = datetime.date.max
################################################################################




################################################################################
# Connect to the Wordnet Database
################################################################################
con = sqlite3.connect(wndb)
wn = con.cursor()

################################################################################
# FINDING NEW SYNSETS
# newsenses[user][date][(synset, lemma, pos, lang)]
################################################################################

newsynsets = """SELECT synset.synset, name, synset.usr, def, lang
                FROM synset
                LEFT JOIN synset_def
                WHERE synset_def.synset = synset.synset
                AND src = 'ntumc' """

wn.execute(newsynsets)
rows = wn.fetchall()
#user_list = set()
ntumc_user = dd(lambda: dd(str)) 
ss_defs = dd()
ss_lang_defs = dd(lambda: dd(str)) 

for r in rows:
    (synset, ssname, user, definition, l) = (r[0],r[1],r[2],r[3],r[4])
#    user_list.add(user)
    ntumc_user[user][synset] = ssname
    ss_defs[synset] = definition
    ss_lang_defs[synset][l] += definition + "; "

# Checking for tags
ass = placeholders_for(ss_lang_defs.keys())

synsetdates = """
SELECT synset_new, date_update
FROM synset_log
WHERE synset_new in (%s) 
""" % ass

wn.execute(synsetdates, list(ss_lang_defs.keys()))
ss_dates = dd()
rows = wn.fetchall()
for r in rows:
    (synset, date) = (r[0],r[1])
    date = date.split()[0]
    d = datetime.date(int(date.split('-')[0]),
                      int(date.split('-')[1]),
                      int(date.split('-')[2]))
    ss_dates[synset] = d


# CLEAN UP DATA BY DATE
# THIS DELETES ANY DATA THAT IS NOT IN THE DATE SPAN
if dfrom:
    for synset, date in ss_dates.items():
        if date < dfrom:
            del ss_defs[synset]
            del ss_lang_defs[synset]

            for user in user_list:
                try:
                    del ntumc_user[user][synset]
                except:
                    pass
if dto:
    for synset, date in ss_dates.items():
        if date > dto:
            del ss_defs[synset]
            del ss_lang_defs[synset]

            for user in user_list:
                try:
                    del ntumc_user[user][synset]
                except:
                    pass


delete_undatedss= []
if exclude_undated == "yes":
    for user in user_list:
        for synset in ntumc_user[user]:
            if synset not in ss_dates:
                delete_undatedss.append(synset)
    for user in user_list:
        for synset in delete_undatedss:
                try:
                    del ntumc_user[user][synset]
                except:
                    pass
################################################################################


# Get the list of updated synsets (after clean ups)
ass = placeholders_for(ss_lang_defs.keys())



checksenses = """
SELECT synset, count(*)
FROM sense
WHERE synset IN (%s)
GROUP BY synset""" % ass

wn.execute(checksenses, list(ss_lang_defs.keys()))
ss_senses = dd() # number of senses per synset
rows = wn.fetchall()
for r in rows:
    (synset, senses) = (r[0],r[1])
    ss_senses[synset] = senses


corpususage = """
SELECT concept.sid, cid, tag, clemma, sent
FROM concept
LEFT JOIN sent
ON concept.sid = sent.sid
WHERE tag in (%s) """ % ass

tagsdict = dd(lambda: dd(list)) # tags by synset tagsdict[synset]=[sid,cid]
for valid_db in ["../db/eng.db","../db/cmn.db", "../db/ind.db"]:
    if not os.path.isfile(valid_db):
        continue
    ###########################
    # Connect to corpus.db
    ###########################
    conc = sqlite3.connect(valid_db)
    cc = conc.cursor()

    cc.execute(corpususage, list(ss_lang_defs.keys()))
    rows = cc.fetchall()

    for r in rows:
        (sid, cid, tag, clemma, sent) = (r[0], r[1], r[2], r[3], r[4])
        tagsdict[valid_db[-6:-3]][tag].append((sid, cid, clemma, sent))

    conc.close()


################################################################################
# FIND NEW SENSES
# newsenses[user][date] = set([synset, lemma, pos, lang],...)
################################################################################
newsenses = dd(lambda: dd(set)) 
newsenses_len = dd(int) # total count of lemmas created by an user
synset_set = set() # this holds the synsets used (to fetch defs)
newsenses_sql = """SELECT synset_new, wordid_new, lemma, 
                          lang_new, usr_new, date_update 
                   FROM (SELECT synset_new, wordid_new, lemma, 
                                lang_new, usr_new, date_update 
                         FROM sense_log 
                         LEFT JOIN word 
                         WHERE wordid_new = wordid) as sub 
                   LEFT JOIN sense 
                   WHERE synset_new = sense.synset 
                   AND wordid_new = sense.wordid"""

wn.execute(newsenses_sql)
rows = wn.fetchall()
for r in rows:
    (synset, wid, lemma, lang, usr, date) = (r[0],r[1],r[2],r[3],r[4],r[5])
    date = date.split()[0]
    date = datetime.date(int(date.split('-')[0]),
                      int(date.split('-')[1]),
                      int(date.split('-')[2]))

    if date >= dfrom and date <= dto:
        newsenses[usr][date].add((synset, lemma, lang))
        newsenses_len[usr] += 1
        synset_set.add(synset)
################################################################################



################################################################################
# Fetching Synset Names & Definitions
################################################################################
ass = placeholders_for(synset_set)

wn.execute("""SELECT synset.synset, lang, def, sid, name
              FROM synset_def
              LEFT JOIN synset
              WHERE synset.synset = synset_def.synset 
              AND synset_def.synset in ({}) """.format(ass),
           list(synset_set))

rows = wn.fetchall()
defs = dd(lambda: dd(set))
names = dd(str)
for r in rows:
    (synset, lang, defin, sid, name) = (r[0],r[1],r[2],r[3],r[4])
    defs[synset][lang].add((sid, defin))
    names[synset] = name
################################################################################



################################################################################
# FIND CHANGED TAGS IN ALL CORPUS DATABASES  
# changed_tags[user][db][date] = set([sid, clemma, new tag, old tag, 
#                                     comment, username_old],...)
################################################################################
changed_tags = dd(lambda: dd(lambda: dd(set))) 
changed_tags_len = dd(int) # total count of tags changed by an user

changed_tags_sql = """ SELECT sid_new, clemma_new, tag_new, tag_old, 
                              comment_new, usrname_new, date_update,
                              usrname_old 
                       FROM concept_log"""

for db in ["../db/eng.db","../db/cmn.db", "../db/ind.db"]:
    if not os.path.isfile(db):
        continue
    ###########################
    # Connect to corpus.db
    ###########################
    conc = sqlite3.connect(db)
    cc = conc.cursor()

    cc.execute(changed_tags_sql)
    rows = cc.fetchall()

    for r in rows:

        (sid, clemma, tag_new, tag_old) = (r[0], r[1], r[2], r[3])
        (comment, user, date, user_old) = (r[4], r[5], r[6], r[7])


        time = date.split()[1]
        date = date.split()[0]
        date = datetime.date(int(date.split('-')[0]),
                          int(date.split('-')[1]),
                          int(date.split('-')[2]))

        if date >= dfrom and date <= dto:
            changed_tags[user][db][date].add((sid, clemma, tag_new, tag_old, 
                                              comment, user_old, time))
            changed_tags_len[user] += 1

    conc.close()

################################################################################






# c.execute("""SELECT s.lang, lemma, freq, 
#                     confidence, src
#              FROM (SELECT lang, wordid, freq, confidence, src
#                    FROM sense
#                    WHERE synset = ?
#                    AND sense.confidence IS '1.0') s
#              LEFT JOIN word
#              WHERE word.wordid = s.wordid
#              ORDER BY freq DESC, confidence DESC""", (synset,))


# # Fetching Definitions
# c.execute("""SELECT synset, lang, def, sid, 
#                     datechanged, status, editor 
#              FROM synset_def 
#              WHERE synset in (%s) """ % ass)

# rows = c.fetchall()
# defs = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(list))) # definitions dict by synset
# for r in rows:
#     (synset, lang, defin, sid) = (r[0],r[1],r[2],r[3])
#     (datech, status, editor) = (r[4],r[5],r[6])

#     defs[synset][lang][sid] = [defin, datech, status, editor]


# # Fetching Relations
# c.execute("""SELECT synset1, link, synset2,  
#                     name, synlink.status, synlink.editor 
#              FROM synlink 
#              LEFT JOIN synset 
#              ON synlink.synset2 = synset.synset 
#              WHERE  synset1 in (%s) """ % ass)
# rows = c.fetchall()
# relsdict = collections.defaultdict(list)
# for r in rows:  # dict[ss1][i] = (link, synset2, name, status)
#     (ss1, link, ss2, name, status, editor) = (r[0],r[1],r[2],r[3],r[4], r[5])

#     relsdict[ss1].append((link, ss2, name, status, editor))





################################################################################
# PRODUCE STRING FOR DATE SPAN 
################################################################################
datespan = ""
if dfrom != datetime.date.min and dto != datetime.date.max:
    datespan = "(from " + str(dfrom) + " to " + str(dto) + ")"
elif dfrom != datetime.date.min:
    datespan = "(from " + str(dfrom) + ")"
elif dto != datetime.date.max:
    datespan = "(to " + str(dto) + ")"
################################################################################


################################################################################
# SELECTING USERS
################################################################################
if userid == "all":
    selected_users = user_list
else:
    selected_users = [userid]
################################################################################



################################################################
# FETCH COOKIE
################################################################
# hashed_pw = ""
# if 'HTTP_COOKIE' in environ:
#    for cookie in environ['HTTP_COOKIE'].split(';'):
#       (key, value ) = cookie.strip().split('=');
#       if key == "UserID":
#          usr = value
#       if key == "Password":
#          hashed_pw = value



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

# print(C), # No need to print cookie since it's set by the dashboard!
### Header
print(u"""Content-type: text/html; charset=utf-8\n
<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
    <link href="../tag-wn.css" rel="stylesheet" type="text/css">
    <script src="../tag-wn.js" language="javascript"></script>

    <!-- For DatePicker -->
    <link rel="stylesheet" href="//code.jquery.com/ui/1.11.2/themes/smoothness/jquery-ui.css">
    <script src="//code.jquery.com/jquery-1.10.2.js"></script>
    <script src="//code.jquery.com/ui/1.11.2/jquery-ui.js"></script>
    <script>
    $(function() {
      $( "#datefrom" ).datepicker();
      $( "#dateto" ).datepicker();
    });
    </script>

    <!-- FANCYBOX -->
    <!-- Needs JQuery -->
    <!-- Add FancyBox main JS and CSS files -->
    <script type="text/javascript" 
     src="../fancybox/source/jquery.fancybox.js?v=2.1.5"></script>
    <link rel="stylesheet" type="text/css" 
     href="../fancybox/source/jquery.fancybox.css?v=2.1.5" 
     media="screen" />
    <!-- Make FancyBox Ready on page load (adds Classes) -->
    <script type="text/javascript" 
     src="../fancybox-ready.js"></script>


    <!-- TO SHOW / HIDE BY ID (FOR DIV)-->
    <script type="text/javascript">
     function toggle_visibility(id) {
         var e = document.getElementById(id);
         if(e.style.display == 'block')
            e.style.display = 'none';
         else
            e.style.display = 'block';
     }
    </script>

    <!-- KICKSTART -->
    <script src="../HTML-KickStart-master/js/kickstart.js"></script> 
    <link rel="stylesheet" href="../HTML-KickStart-master/css/kickstart.css" media="all" />


    <style>
    mark { 
        background-color: #FFA6A6;
    }
    </style>

    <title>NTUMC Reports</title>
 </head>
 <body>
 """)



print("""<h5>""")
print(HTML.status_bar(userID))  # Top Status Bar
print("""NTUMC Reports </h5>""")

if viewmode != "tags_only":
    # START FORM
    print("""<form action="" method="post">""")
    # PRINT USER DROPDOWN
    print("""Select by user: <select id="userid" name="userid">""")
    print("""<option value ='all'>all</option>""")
    for user in user_list:
        if user == userid:
            print("<option value ='%s' selected>%s</option>" % (user, user))
        else:
            print("<option value ='%s'>%s</option>" % (user, user))
    print("""</select>""")

    print("""Filter:
             <span id="selectdate">
             <select id="mode" name="mode">""")
    print("""<option value ='all'>Show all</option>
             <option value ='tagsview'>Show New Tags</option>""")
    print("""</select>""")

    print("""<input type="checkbox" name="exclude_undated" 
              value="yes" checked> Exclude undated""")

    # PRINT DATE FROM/TO
    print("""<br>Date from:""")
    print("""<input name="datefrom" size="9" id="datefrom"/>""")
    print("""Date to:""")
    print("""<input name="dateto" size="9" id="dateto"/>""")
    print("""<input type="submit"  value="Search"/><br>""")

    print("""<input type="submit" name="sevendays" value="7 days"/>""")
    print("""<input type="submit" name="threedays" value="3 Days"/>""")
    print("""<input type="submit" name="yesterday" value="Yesterday"/>""")
    print("""<input type="submit" name="today" value="Today"/></form>""")



    # To sort users by the number of new synsets created
    # Will not show users that have done nothing
    new_ss_by_user = dd(int)
    for user in ntumc_user:
        if len(ntumc_user[user]) != 0:
            new_ss_by_user[user] = len(ntumc_user[user])




if mode == "all":


    print("""<h6>Showing "All Edits" %s </h6><br>""" % (datespan,))

    for user in selected_users:
        ####################################################################
        # SHOWING NEW SYNSETS
        ####################################################################
        if new_ss_by_user[user] > 0:
            print("""%s (%s new synsets):
                  """ % (user, str(new_ss_by_user[user])))

            print("""<a onclick="toggle_visibility('%snewss');">
                     [show/hide]</a>""" % user)
            print("""<div id="%snewss" style="display: none">""" % user)

            print("""<table class="striped tight sortable">""")
            print("""<thead><tr><th>Date</th><th>Synset</th>
                       <th>Name</th><th>Definition</th>
                       <th>Usage</th><th></th></tr></thead>""")

            for synset in ntumc_user[user]:
                wncgi_url = wncgi_edit % (userID, synset)

                print("""<tr>""")
                try:
                    print("""<td>%s</td>""") % ss_dates[synset]
                except:
                    print("""<td>no_date</td>""")

                print("""<td><a class='largefancybox fancybox.iframe' 
                       href='%s'>""" % (wncgi_url,) + synset + "</a></td>")
                print("<td>" + ntumc_user[user][synset] + "</td>")

                try:
                    if ss_lang_defs[synset]['eng']:
                        print("<td>" + ss_lang_defs[synset]['eng'] + "</td>")
                    else:
                        print("<td><mark>no_eng_def</mark></td>")
                except:
                    print("<td><mark>no_eng_def</mark></td>")


                total_tooltip = ""
                total_count = 0
                for corpus in tagsdict.keys():
                    total_count += len(tagsdict[corpus][synset])

                    total_tooltip += "%s:" % corpus
                    total_tooltip +=  str(len(tagsdict[corpus][synset]))
                    total_tooltip += ";&#10;"

                print("""<td><span title="%s">""") % (total_tooltip,)
                if total_count == 0:
                    print("<mark>" + str(total_count) + "</mark></td>")
                else:
                    print(str(total_count) + "</td>")

                try:
                    if ss_senses[synset]:
                        print("<td></td>")
                except:
                        print("""<td><span style="color:#FFA6A6;"
                                  title="Has no senses!">
                                 <i class='icon-warning-sign'></i>
                                 </span></td>""")
                print("</tr>")

            print("""</table>""")
            print("""</div><br>""")


        ####################################################################
        # SHOWING NEW SENSES
        ####################################################################
        if newsenses_len[user] > 0:

            print("""%s (%s new senses):
                  """ % (user, str(newsenses_len[user])))

            print("""<a onclick="toggle_visibility('%snewsenses');">
                     [show/hide]</a>""" % user)
            print("""<div id="%snewsenses" style="display: none">""" % user)

            print("""<table class="striped tight sortable">""")
            print("""<thead><tr><th>Date</th><th>Synset</th>
                       <th>Name</th><th>Definition</th>
                       <th>New Sense</th><th></th></tr></thead>""")


            for date in newsenses[user]:
                for (synset, sense, lang) in newsenses[user][date]:

                    wncgi_url = wncgi_edit % (userID, synset)

                    print("""<tr>""")
                    print("""<td>%s</td>""") % date

                    print("""<td><a class='largefancybox fancybox.iframe' 
                           href='%s'>""" % (wncgi_url,) + synset + "</a></td>")
                    print("<td>" + names[synset] + "</td>")

                    try:
                        eng_definition = list(defs[synset]['eng'])[0][1]
                        print("<td>" + eng_definition + "</td>")
                    except:
                        print("<td><mark>no_eng_def</mark></td>")

                    print("<td>%s (%s)</td>") % (sense, lang)

                    print("<td></td>")  # THIS COULD BE DELETED + ABOVE 
                    print("</tr>")

            print("""</table>""")
            print("""</div><br>""")
            ################################################################



            # changed_tags[user][date][db].add((sid, clemma, tag_new, tag_old, 
            #                                   comment, user, date))
            # changed_tags_len[user] += 1


        ####################################################################
        # SHOWING NEW TAGS
        ####################################################################
        if changed_tags_len[user] > 0:

            print("""%s (%s tags changed):
                  """ % (user, str(changed_tags_len[user])))

            tags_url =  selfcgi + "?datefrom=%s&dateto=%s" % (dfrom,dto)
            tags_url += "&userid=%s&mode=%s" % (user,"tagsview") 
            tags_url += "&viewmode=%s" % ("tags_only")

            print("""<td><a class='largefancybox fancybox.iframe'
            href='%s' style='text-decoration:none'>""" % tags_url + "[show]" + "</a></td>")


        # USER SEPARATOR
        if new_ss_by_user[user]>0 or newsenses_len[user] > 0 \
                or changed_tags_len[user] > 0:
            print("""</div><hr>""")


elif mode == "tagsview":

    print("""<h6>Showing "All Tags" %s </h6><br>""" % (datespan,))
    for user in selected_users:

        ####################################################################
        # SHOWING NEW TAGS
        ####################################################################
        if changed_tags_len[user] > 0:

            print("""%s (%s tags changed):
                  """ % (user, str(changed_tags_len[user])))

            print("""<a onclick="toggle_visibility('%snewtags');">
                     [show/hide]</a>""" % user)

            if viewmode != "tags_only":
                print("""<div id="%snewtags" style="display: none">""" % user)
            else:
                print("""<div id="%snewtags">""" % user)

            for db in changed_tags[user]:
                print("""<table class="striped tight sortable">""")
                print("""<thead><tr><th>Date</th><th>SID</th>
                           <th>Concept</th><th style="width: 350px">From >>> To</th>
                           <th>Comment</th><th></th></tr></thead>""")
                for date in changed_tags[user][db]:
                    for (sid, clemma, tag_new, tag_old, comment, 
                         user_old, time) in changed_tags[user][db][date]:

                        if user_old == None:
                            user_old = ""
                        else:
                            user_old = "(%s)" % user_old
                        if tag_old == None or tag_old == "":
                            tag_old = "NULL"
                        if tag_new == None or tag_new == "":
                            tag_new = "NULL"
                        if comment == None:
                            comment = ""

                        omw_old_tag = wncgi_edit % (userID, tag_old)
                        omw_new_tag = wncgi_edit % (userID, tag_new)

                        corpuslang = db[-6:-3]

                        tagword_url = tag_word % (corpuslang, corpuslang, 
                                                  userID, sid)

                        print("""<tr>""")
                        print("""<td>{} ({})</td>""".format(date, time))

                        print("""<td><a target="_blank")
                               href='%s'>%s</td>""" % (tagword_url, sid))

                        print("<td>" + clemma + "</td>") 
                        # SHOULD THIS TO TO TAGLEX / WORDNET?


                        print("""<td><a target="_blank" href='%s'>""" % (omw_old_tag,) + tag_old + """</a> %s """ % user_old + " >> " + """<a target="_blank" href='%s'>""" % (omw_new_tag,) + tag_new + " </td>")
                        
                        print("<td>{}</td>".format(comment if comment else ''))
                        print("</tr>")

            print("""</table>""")
            ################################################################



        # USER SEPARATOR
        if changed_tags_len[user] > 0:
            print("""</div><hr>""")
    
    sys.exit(0)



# Footer
print("""<p><a href='http://compling.hss.ntu.edu.sg/'>
         NTU Computational Linguistics Lab</a><br>""")
print("""Maintainer: <a href="http://www3.ntu.edu.sg/home/fcbond/")>
         Francis Bond</a>""")
print("""&lt;<a href="mailto:bond@ieee.org">bond@ieee.org</a>&gt;""")


print("  </body>")
print("</html>")
