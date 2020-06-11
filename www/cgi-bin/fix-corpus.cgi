#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################
# This cgi is a GUI access to change the corpus structure.
# It can change Sentences, Words and Concepts structures. 
################################################################

import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import http.cookies
import json
import os
import sqlite3
from collections import defaultdict as dd

from ntumc_util import *
from lang_data_toolkit import valid_usernames as valid_usrs
from lang_data_toolkit import pos_tags

###############################################################
# This function allows escaping text from the db to the html
# It is not needed in 'textarea's but it is needed in 'input's 
###############################################################

html_escape_table = {"&": "&amp;", '"': "&quot;", 
                     "'": "&apos;", ">": "&gt;",
                     "<": "&lt;"}
def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)

###############################################################
# This cgi script will serve to access and edit the corpus db.
# It allows editing tags, and to correct segmentation problems.
# Eventually should also allow to create new datasets, etc.
###############################################################

form = cgi.FieldStorage()

sid_edit = form.getfirst("sid_edit", "11000")

corpusdb = form.getfirst("corpus", "eng")
(dbexists, dbversion, dbmaster, dblang, dbpath) = check_corpusdb(corpusdb)


lang = dblang

# sid_from = form.getfirst("sid_from", int(sid_edit) - 2)
# sid_to = form.getfirst("sid_to", int(sid_edit) + 2)



wncgi_lemma = "wn-gridx.cgi?gridmode=ntumcgrid&lang=%s&lemma=" % (lang)
wncgi_ss = "wn-gridx.cgi?gridmode=ntumcgrid&lang=%s&synset=" % (lang)


#### TO EDIT THE DB
# Edit Mode (accepts: 'update', 'addword', 'delword', 
#                     'addconcept', 'delconcept')
editm = form.getfirst("editm", "")  

# To edit 'sent'
new_sent = form.getfirst("new_sent")
new_scomment = form.getfirst("new_scomment")
new_pid = form.getfirst("new_pid")
if new_scomment == None:
    new_scomment = "None"

# To edit 'word'
new_wid = form.getlist('new_wid[]')
new_word = form.getlist('new_word[]')
new_pos = form.getlist('new_pos[]')
new_lemma = form.getlist('new_lemma[]')
new_wcomment = form.getlist('new_wcomment[]')

# To edit 'concept'
new_cid = form.getlist('new_cid[]')
new_clemma = form.getlist('new_clemma[]')
new_wids = form.getlist('new_wids[]')
new_tag = form.getlist('new_tag[]')
new_comment = form.getlist('new_comment[]')



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

       <!-- The 2 meta tags below are to avoid caching 
            information to forms -->
       <META HTTP-EQUIV="Pragma" CONTENT="no-cache"> 
       <META HTTP-EQUIV="Expires" CONTENT="-1">

    <!-- KICKSTART -->
    <script 
     src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js">
    </script>


	<!-- Add fancyBox main JS and CSS files -->
	<script type="text/javascript" 
         src="../fancybox/source/jquery.fancybox.js?v=2.1.5"></script>
	<link rel="stylesheet" type="text/css" 
         href="../fancybox/source/jquery.fancybox.css?v=2.1.5" 
         media="screen" />
	<script type="text/javascript" 
         src="../fancybox-ready.js"></script>

</head>
<body>\n""")

# OLD JQUERY
# <!-- Add jQuery library -->
# <script type="text/javascript" 
#  src="../fancybox/lib/jquery-1.10.1.min.js"></script>

    # <script src="../HTML-KickStart-master/js/kickstart.js"></script>
    # <link rel="stylesheet" 
    #  href="../HTML-KickStart-master/css/kickstart.css" media="all" /> 


print("""<h2>Corpus Fixer</h2>\n """)

################
# CONNECT TO DB
################
conn_db = sqlite3.connect(dbpath)
a = conn_db.cursor()

######################################################
# GO TO THE DB FOR THE 1st TIME (FOR EDITING PURPOSES)
######################################################

######################
# FETCH words BY sid
######################
words = dict()
a.execute( """SELECT wid, word, pos, lemma, comment, usrname
              FROM word
              WHERE sid=? """, (sid_edit,))
for (wid, word, pos, lemma, comment, usrname) in a: 
    words[wid] = [word, pos, lemma, comment, usrname]

#####################################
# FETCH concept_to_word Links BY sid
#####################################
cwls = dd(lambda: [])
cwls_usr = dd()
a.execute("""SELECT wid, cid, usrname
             FROM cwl
             WHERE sid=? """, (sid_edit,))
for (wid, cid, usrname) in a:
    cwls[wid].append(cid)
    cwls_usr[wid] = usrname

########################
# FETCH THE HIGHEST WID
########################
a.execute("""SELECT max(wid)
             FROM word
             WHERE sid=? """, (sid_edit,))
try:
    maxwid = int(a.fetchone()[0])
except:
    maxwid = -1

####################################################
# EDIT DATABASE
# MODES: "update, "addword", "delword", 
#        "addconcept, "delconcept""
####################################################
log_status = ""
##########################
# UPDATE - CORRECT FIELDS
##########################
if editm == "update" and userID in valid_usrs:
    log_status += "Entered 'update' mode:<br> "

    # UPDATE SENT TABLE
    sent_up = new_sent.strip()

    pid_up = new_pid.strip()
    scomment_up = new_scomment.strip()
    # Update sent if sent != sent
    a.execute("""UPDATE sent SET sent=?, usrname=? 
                 WHERE sent IS NOT ? 
                 AND sid=?""", 
              (sent_up, userID, sent_up, sid_edit))

    # Update pid if pid != pid
    a.execute("""UPDATE sent SET pid=?, usrname=? 
                 WHERE pid IS NOT ? 
                 AND sid=?""", 
              (pid_up, userID, pid_up, sid_edit))


    # Update scomment if scomment != scomment
    if scomment_up == "None":
        a.execute("""UPDATE sent SET comment=?, usrname=? 
                     WHERE comment IS NOT ? 
                     AND sid=? """, 
                  (None, userID, None, sid_edit))
    else:
        a.execute("""UPDATE sent SET comment=?, usrname=? 
                     WHERE comment IS NOT ? 
                     AND sid=?""", 
                  (scomment_up, userID, scomment_up, sid_edit))

    log_status += u"Sent ✓; "


    # UPDATE WORD TABLE
    for i, wid in enumerate(new_wid):

        word_up = new_word[i].strip()
        lemma_up = new_lemma[i].strip()
        pos_up = new_pos[i].strip()

        wcomment_up = new_wcomment[i].strip()
        wcomment_up = wcomment_up.strip(u' .,;:!?。；：！')

        # Update word if word != word
        a.execute("""UPDATE word SET word=?, usrname=? 
                     WHERE word IS NOT ? 
                     AND sid=? AND wid=?""", 
                    (word_up, userID, word_up, sid_edit, wid))

        # Update pos if pos != pos
        a.execute("""UPDATE word SET pos=?, usrname=?
                     WHERE pos IS NOT ?
                     AND sid=? AND wid=?""",
                    (pos_up, userID, pos_up, sid_edit, wid))

        # Update lemma if lemma != lemma
        a.execute("""UPDATE word SET lemma=?, usrname=?
                     WHERE lemma IS NOT ?
                     AND sid=? and wid=?""",
                    (lemma_up, userID, lemma_up, sid_edit, wid))

        # Update wcomment if wcomment != wcomment
        if wcomment_up == "None":
            a.execute("""UPDATE word SET comment=?, usrname=?
                        WHERE comment IS NOT ?
                        AND sid=? and wid=?""",
                        (None, userID, None, sid_edit, wid))
        else:
            a.execute("""UPDATE word SET comment=?, usrname=?
                        WHERE comment IS NOT ?
                        AND sid=? and wid=?""",
                        (wcomment_up, userID, wcomment_up, sid_edit, wid))

    log_status += u"Words ✓; "

    # UPDATE CONCEPT TABLE
    for i, cid in enumerate(new_cid):

        clemma_up = new_clemma[i].strip()
        wids_up = set(json.loads(new_wids[i]))
        tag_up = new_tag[i].strip()

        comment_up = new_comment[i].strip()
        comment_up = comment_up.strip(u' .,;:!?。；：！')

        # Update tag if tag != tag
        if tag_up == "None":
            a.execute("""UPDATE concept SET tag=?, usrname=? 
                        WHERE tag IS NOT ? 
                        AND sid=? and cid=?""", 
                        (None, userID, None, sid_edit, cid))
        else:
            a.execute("""UPDATE concept SET tag=?, usrname=? 
                         WHERE tag IS NOT ? 
                         AND sid=? and cid=?""", 
                        (tag_up, userID, tag_up, sid_edit, cid))

        # Update clemma if clemma != clemma
        a.execute("""UPDATE concept SET clemma=?, usrname=? 
                     WHERE clemma IS NOT ? 
                     AND sid=? and cid=?""", 
                    (clemma_up, userID, clemma_up, sid_edit, cid))


        # Update comment if comment != comment
        if comment_up == "None":
            a.execute("""UPDATE concept SET comment=?, usrname=? 
                        WHERE comment IS NOT ? 
                        AND sid=? and cid=?""", 
                        (None, userID, None, sid_edit, cid))
        else:
            a.execute("""UPDATE concept SET comment=?, usrname=? 
                        WHERE comment IS NOT ? 
                        AND sid=? and cid=?""", 
                        (comment_up, userID, comment_up, sid_edit, cid))


        # Update cwl table (fetch old, compare, correct)
        wids_old = set()
        a.execute( """SELECT wid, usrname
                      FROM cwl 
                      WHERE sid LIKE ? AND cid=?""", [str(int(sid_edit)), cid])
        for (wid_old, usrname) in a:
            wids_old.add(wid_old)


        # Delete if they are no longer linked to concept
        for wid in wids_old:

            if wid in wids_up:
                # do nothing
                continue
            else:  # delete it (update usrname 1st if necessary)
                a.execute("""UPDATE cwl SET usrname=?
                             WHERE sid=? AND cid=? AND wid=?
                             AND usrname IS NOT ?
                          """, [userID, sid_edit, cid, wid, userID])
                a.execute("""DELETE FROM cwl 
                             WHERE sid=? AND cid=? AND wid=?
                          """, [sid_edit, cid, wid])

        # Create new word links to concept
        for wid in wids_up:

            if wid in wids_old:
                # do nothing
                continue
            else: # create new
                a.execute("""INSERT INTO cwl(sid, wid, cid, usrname) 
                             VALUES (?,?,?,?)
                          """, [sid_edit, wid, cid, userID])

    log_status += u"Concepts ✓; "


################################################################################
# ADDWORD - ADD A NEW WORD
################################################################################
elif editm == "addword" and userID in valid_usrs:
    log_status += "Entered 'addword' mode:<br> "

    wid_new = int(new_wid[0])
    word_up = new_word[0].strip()
    lemma_up = new_lemma[0].strip()
    pos_up = new_pos[0].strip()
    wcomment_up = new_wcomment[0].strip()
    wcomment_up = wcomment_up.strip(u' .,;:!?。；：！')

    # print "<br>wid new:" + str(wid_new)  #TEST
    # print "<br>new word:" + word_up  #TEST
    # print "<br>new lemma:" + lemma_up  #TEST
    # print "<br>maxwid: " + str(maxwid)  #TEST

    ############################################################################
    # IF NEW WID = MAXWID+1 (INSERT DIRECTLY) 
    ############################################################################
    if wid_new > maxwid: # Insert directly the new wid (> is always maxwid+1)

        if wcomment_up == "None":  # "None" string is considered "NONE" type 
            a.execute("""INSERT INTO word (sid, wid, word, pos, 
                                           lemma, comment, usrname)
                         VALUES (?,?,?,?,?,?,?)""",
                      (sid_edit, wid_new, word_up, pos_up, 
                       lemma_up, None, userID))
        else:
            a.execute("""INSERT INTO word (sid, wid, word, pos, 
                                           lemma, comment, usrname)
                         VALUES (?,?,?,?,?,?,?)""",
                      (sid_edit, wid_new, word_up, pos_up, 
                       lemma_up, wcomment_up, userID))

        log_status += u"New Word (no shifting needed) ✓; "
    
    ############################################################################
    # IF NEW ID WAS ALREADY IN THE SENTENCE (NEED TO DO SOME PUSHING AROUND)
    ############################################################################
    else:

        # MOVE EVERYTHING TO wid +1 until the desired position
        for wid in reversed(range(wid_new, maxwid+1)):

            a.execute("""UPDATE xwl SET wid=?, username=?
                         WHERE sid=? AND wid=?""",
                      (wid+1, userID, sid_edit, wid))

            a.execute("""UPDATE word SET wid=?, usrname=?
                         WHERE sid=? AND wid=?""",
                      (wid+1, userID, sid_edit, wid))

            a.execute("""UPDATE cwl SET wid=?, usrname=?
                         WHERE sid=? AND wid=?""",
                      (wid+1, userID, sid_edit, wid))


        # ADD NEW WORD
        if wcomment_up == "None":
            a.execute("""INSERT INTO word (sid, wid, word, pos,
                                           lemma, comment, usrname)
                         VALUES (?,?,?,?,?,?,?)""",
                      (sid_edit, wid_new, word_up, pos_up, 
                       lemma_up, None, userID))

        else:
            a.execute("""INSERT INTO word (sid, wid, word, pos,
                                           lemma, comment, usrname)
                         VALUES (?,?,?,?,?,?,?)""",
                      (sid_edit, wid_new, word_up, pos_up, 
                       lemma_up, wcomment_up, userID))




        # # INSERT NEW WORD AT MAX+1 POSITION (COPYING MAX)
        # a.execute("""INSERT INTO word (sid, wid, word, pos,
        #                                lemma, comment, usrname)
        #              VALUES (?,?,?,?,?,?,?)""",
        #           (sid_edit, maxwid+1, words[maxwid][0], words[maxwid][1],
        #            words[maxwid][2], words[maxwid][3], words[maxwid][4]))

        # # print "<br>INSERTED A NEW WORD with MAX+1 WID"  #TEST

        # # FOR EACH CONCEPT LINKED TO MAX WID, COPY THEIR CWL LINKS TO MAX+1
        # for conceptid in cwls[maxwid]:
        #     a.execute("""INSERT INTO cwl (sid, wid, cid, usrname)
        #                  VALUES (?,?,?,?)""",
        #               (sid_edit, maxwid+1, conceptid, cwls_usr[wid]))

        # # print "<br>INSERTED CWL LINKS FOR THE NEW WORD with MAX+1 WID"  #TEST

        # # UPDATE OTHER WIDs, COPY WID TO WID+1
        # updatingwid = maxwid
        # while (updatingwid > wid_new):  
        #     # PUSH EVERYTHING FORWARD until reaches wid_new
        #     a.execute("""UPDATE word SET word=?, pos=?, lemma=?, 
        #                                  comment=?, usrname=?
        #                  WHERE sid=? AND wid=?""",
        #               (words[updatingwid-1][0], words[updatingwid-1][1], 
        #                words[updatingwid-1][2], words[updatingwid-1][3], 
        #                words[updatingwid-1][4], sid_edit, updatingwid))

        #     # DELETE PREVIOUS CWL LINKS
        #     a.execute("""UPDATE cwl SET usrname=?
        #                  WHERE sid=? AND wid=?
        #                  AND usrname IS NOT ?
        #               """, [userID, sid_edit, updatingwid, userID])
        #     a.execute("""DELETE FROM cwl
        #                  WHERE sid=? AND wid=?
        #               """, [sid_edit, updatingwid])

        #     # TRANSFER CWL LINKS FROM PREVIOUS WID
        #     for conceptid in cwls[updatingwid-1]:
        #         a.execute("""INSERT INTO cwl (sid, wid, cid, usrname)
        #                      VALUES (?,?,?,?)""",
        #                    (sid_edit, updatingwid, conceptid, userID))

        #     updatingwid -= 1  # KEEP DECREASING UPDATING WID 


        # # UPDATE THE OLD WID WITH THE NEW WORD
        # # Update wid_new with new values
        # a.execute("""UPDATE word SET word=?, pos=?, lemma=?, usrname=?
        #              WHERE sid=? AND wid=?""",
        #           (word_up, pos_up, lemma_up, userID, sid_edit, wid_new))

        # # Update wcomment if wcomment != wcomment
        # if wcomment_up == "None":
        #     a.execute("""UPDATE word SET comment=?, usrname=? 
        #                 WHERE comment IS NOT ? 
        #                 AND sid=? and wid=?""", 
        #                 (None, userID, None, sid_edit, wid_new))
        # else:
        #     a.execute("""UPDATE word SET comment=?, usrname=? 
        #                 WHERE comment IS NOT ? 
        #                 AND sid=? and wid=?""", 
        #                 (wcomment_up, userID, wcomment_up, sid_edit, wid_new))

        # # DELETE PREVIOUS CWL LINKS
        # a.execute("""UPDATE cwl SET usrname=?
        #              WHERE sid=? AND wid=?
        #              AND usrname IS NOT ?
        #           """, [userID, sid_edit, updatingwid, userID])
        # a.execute("""DELETE FROM cwl
        #              WHERE sid=? AND wid=?
        #           """, [sid_edit, updatingwid])

        log_status += u"New Word (shifting around needed) ✓; "


################################################################################
# DELETE WORD (1. DELETE; 2. SHIFT DOWN THINGS;)
################################################################################
elif editm == "delword" and userID in valid_usrs:

    log_status += "Entered 'delword' mode:<br> "

    wid_del = int(new_wid[0])
    if wid_del in words.keys():

        ########################################################################
        # DELETE WID_DEL DEPENDENCIES
        ########################################################################
        # DELETE CHUNK-WORD LINKS
        a.execute("""UPDATE xwl SET username=?
                     WHERE sid=? AND wid=?
                     AND username IS NOT ?""", [userID, sid_edit, wid_del, userID])
        a.execute("""DELETE FROM xwl
                     WHERE sid=? AND wid=?""", [sid_edit, wid_del])

        # DELETE CWL LINKS
        a.execute("""UPDATE cwl SET usrname=?
                     WHERE sid=? AND wid=?
                     AND usrname IS NOT ?""", [userID, sid_edit, wid_del, userID])
        a.execute("""DELETE FROM cwl
                     WHERE sid=? AND wid=?""", [sid_edit, wid_del])

        # DELETE WORD
        a.execute("""UPDATE word SET usrname=?
                     WHERE sid=? AND wid=?""",
                  (userID, sid_edit, wid_del))
        a.execute("""DELETE FROM word
                     WHERE sid=? AND wid=?""",
                  (sid_edit,  wid_del))


        ########################################################################
        # SUBTRACT 1 FROM EVERY WID > WID_DEL (SHIFT DOWN)
        ########################################################################
        for wid in range(wid_del+1, maxwid+1):

            a.execute("""UPDATE xwl SET wid=?, username=?
                         WHERE sid=? AND wid=?""",
                      (wid-1, userID, sid_edit, wid))

            a.execute("""UPDATE word SET wid=?, usrname=?
                         WHERE sid=? AND wid=?""",
                      (wid-1, userID, sid_edit, wid))

            a.execute("""UPDATE cwl SET wid=?, usrname=?
                         WHERE sid=? AND wid=?""",
                      (wid-1, userID, sid_edit, wid))





        # for x in range(wid_del, maxwid):

            # # COPY THE WID+1 INTO WID (STARTING FROM THE ONE TO DELETE)
            # a.execute("""UPDATE word SET word=?, pos=?, lemma=?, 
            #                              comment=?, usrname=?
            #              WHERE sid=? AND wid=?""",
            #           (words[x+1][0], words[x+1][1], words[x+1][2],
            #            words[x+1][3], words[x+1][4], sid_edit, x))




            # # DELETE PREVIOUS CWL LINKS
            # a.execute("""UPDATE cwl SET usrname=?
            #              WHERE sid=? AND wid=?
            #              AND usrname IS NOT ?""", [userID, sid_edit, x, userID])
            # a.execute("""DELETE FROM cwl
            #              WHERE sid=? AND wid=?""", [sid_edit, x])


            # # TRANSFER CWL LINKS FROM PREVIOUS WID
            # for conceptid in cwls[x+1]:
            #     a.execute("""INSERT INTO cwl (sid, wid, cid, usrname)
            #                  VALUES (?,?,?,?)""",
            #                (sid_edit, x, conceptid, userID))


        # # DELETE PREVIOUS CWL LINKS of the last word
        # a.execute("""UPDATE cwl SET usrname=?
        #              WHERE sid=? AND wid=?
        #              AND usrname IS NOT ?""", [userID, sid_edit, 
        #                                        maxwid, userID])
        # a.execute("""DELETE FROM cwl
        #              WHERE sid=? AND wid=?""", [sid_edit, maxwid])

        # # DELETE MAXWID WORD
        # a.execute("""UPDATE word SET usrname=?
        #              WHERE sid=? AND wid=?""",
        #           (userID, sid_edit, maxwid))

        # a.execute("""DELETE FROM word
        #              WHERE sid=? AND wid=?""",
        #           (sid_edit, maxwid))

        log_status += u"Deleted Word ✓; "


#################################
# ADDCONCEPT - ADD A NEW CONCEPT
#################################
elif editm == "addconcept" and userID in valid_usrs:

    log_status += "Entered 'addconcept' mode:<br>"

    cid_new  = int(new_cid[0])
    clemma_up = new_clemma[0].strip()
    wids_up = set(json.loads(new_wids[0]))
    try:
        tag_up = new_tag[0].strip()
    except:
        tag_up = None
    comment_up = new_comment[0].strip()
    comment_up = comment_up.strip(u' .,;:!?。；：！')

    # print "<br>cid new:" + str(cid_new)  #TEST
    # print "<br>new cwlinks:" + str(wids_up)  #TEST
    # print "<br>new clemma:" + clemma_up  #TEST
    # print "<br>new tag:" + str(tag_up)  #TEST


    try:
        # INSERT NEW CONCEPT
        if comment_up == "None":
            a.execute("""INSERT INTO concept (sid, cid, clemma, tag,
                                              comment, usrname)
                         VALUES (?,?,?,?,?,?)""",
                      (sid_edit, cid_new, clemma_up, tag_up,
                       None, userID))
        else:
            a.execute("""INSERT INTO concept (sid, cid, clemma, tag,
                                          comment, usrname)
                         VALUES (?,?,?,?,?,?)""",
                      (sid_edit, cid_new, clemma_up, tag_up,
                       comment_up, userID))

        log_status += u"Inserted Concept ✓; "

        # FOR EACH WID LINKED TO CONCEPT, INSERT CWL LINKS
        for i in wids_up:
            a.execute("""INSERT INTO cwl (sid, wid, cid, usrname)
                             VALUES (?,?,?,?)""",
                          (sid_edit, i, cid_new, userID))

        log_status += u"Inserted C-W Links ✓; "
    except:
        log_status += u"""<span 
                          style="color:red"><b>
                          That concept already existed!</b><br>
                          (It may have been created at the same time!)<br>
                          Please check it and try again!</span>"""


################################
# DELCONCEPT - DELETE A CONCEPT
################################
elif editm == "delconcept" and userID in valid_usrs:

    log_status += "Entered 'delconcept' mode:<br> "

    cid_del = int(new_cid[0])
    # DELETE CONCEPT
    a.execute("""UPDATE concept SET usrname=?, tag='deleted'
                 WHERE sid=? AND cid=?
                 AND usrname IS NOT ?""", [userID, sid_edit, cid_del, userID])
    a.execute("""DELETE FROM concept
                 WHERE sid=? AND cid=?""", [sid_edit, cid_del])

    log_status += u"Deleted Concept ✓; "

    # DELETE CWL LINKS LINKING TO THIS CONCEPT
    a.execute("""UPDATE cwl SET usrname=?
                 WHERE sid=? AND cid=?
                 AND usrname IS NOT ?""", [userID, sid_edit, cid_del, userID])
    a.execute("""DELETE FROM cwl
                 WHERE sid=? AND cid=?""", [sid_edit, cid_del])

    log_status += u"Deleted C-W Links ✓; "

###########################################
# THIS IS THE SECOND CONNECTION TO THE DB
# AFTER ALL THE MODIFICATIONS, EVERYTHING
# DISPLAYED SHOULD BE UPDATED 
###########################################

#########################
# FETCH sentences BY sid
#########################
sent = dict()
pid = dict()
sentcomment = dict()
a.execute( """SELECT sid, pid, sent, comment
              FROM  sent
              WHERE sid LIKE ? """, [str(sid_edit)] )
for (sid, p, s, c) in a:
    sent[sid] = s
    pid[sid] = p
    sentcomment[sid] = c 

######################
# FETCH words BY sid
######################
words = dict()
a.execute( """SELECT wid, word, pos, lemma, comment
              FROM word
              WHERE sid LIKE ? """, [str(sid_edit)] )
for (wid, word, pos, lemma, comment) in a:
    words[wid] = [word, pos, lemma, comment]

########################
# FETCH concepts BY sid
########################
concepts = dict()
a.execute( """SELECT cid, clemma, tag, tags, 
                     comment, usrname 
              FROM concept 
              WHERE sid LIKE ? """, [str(sid_edit)] )

for (cid, clemma, tag, tags, comment, ursname) in a:
    concepts[cid] = [clemma, tag, ursname, comment]

#####################################
# FETCH concept_to_word Links BY sid
#####################################
cwls = dd(lambda: [])
cwls_usr = dd(lambda: set())
a.execute( """SELECT wid, cid, usrname 
              FROM cwl 
              WHERE sid LIKE ? """, [str(sid_edit)])

for (wid, cid, usrname) in a:
    cwls[cid].append(wid)
    cwls_usr[cid].add(usrname)


if userID in valid_usrs:

    for sid in sorted(sent.keys()):  # for sentence in selected range

        if str(sid) != sid_edit:  # THIS WOULD ALLOW FOR PRINTING CONTEXT
            continue  # this can be changed to display context sentences

        else:
            # FORM
            print("""<form action="fix-corpus.cgi?sid_edit=%s" 
                           method="post" name="concept"> 
                     <input type="hidden" name="editm" value="update"/>
                     <input type="hidden" name="corpusdb" value="%s"/>
                  """ % (sid, corpusdb))

            # SENTENCE TEXTAREA
            retag_url= "tag-word.cgi?gridmode=ntumcgrid&corpus=eng&lang=eng&sid={}".format(sid)
            print("""<h3>Edit sentence (%s): <a href='%s'>(retag)</a></h3> """ % (sid, retag_url))
            print("""<table cellpadding="3" bgcolor="#E0E0E0"
                     style="width: 700px;border-collapse:collapse; 
                     border: 1px solid black">""")
            print("""<tr><td><div ><textarea name="new_sent"
                     style="font-size:20px; width:700px;
                     height:100px">%s</textarea></div>
                  """ % (sent[sid]))
            print("""</td></tr>""")
            # SENTENCE COMMENT TEXTAREA
            print("""<tr style="text-align:center">""")
            if sentcomment[sid]:
                print(u"""<td><span title="comment">
                          <textarea rows="1" cols="65" name="new_scomment"
                           style="font-size:12px; width:700px;
                           height:50px">%s</textarea></span></td>
                       """ % (sentcomment[sid],))
            else:  # Print "None" box
                print(u"""<td><span title="comment">
                          <textarea rows="1" cols="65" name="new_scomment"
                           style="font-size:12px;width: 700px;height:50px; 
                           background-color: #E0E0E0"
                          >None</textarea></span></td>""")


            # SENTENCE PID
            print("""<tr style="text-align:center">""")
            print(u"""<td><span title="paragraph ID">
                      <input type="text"  name="new_pid"
                       style="font-size:12px;width:3em" value="%s"/></span></td>
                   """ % (pid[sid],))


            print("""</table><br><hr>""")

            #################################
            # UPDATE WORDS (Multiple tables)
            #################################
            print("""<h3> Edit words:</h3>""")
            for wid, (word, pos, lemma, comment) in words.items():

                # FIND THE TABLE WIDTH
                if len(lemma) == 1:
                    inputlenght = 5
                else:
                    inputlenght = len(lemma)
                    if inputlenght < 5:
                        inputlenght = 5
                    elif inputlenght > 8:
                        inputlenght = int(len(lemma)*0.8)


                print("""<table cellpadding="3" bgcolor="#E0E0E0"
                          style=" border-collapse: collapse; 
                          border: 1px solid black; display: inline-table; 
                          margin-top: 5px;">""")

                # WORDID / DELETE WORD
                print("""<tr style="text-align:center">""")
                print(u"""<td><span title='%s'><b>wid:%s</b></span>
                          <span title='delete wordid!' 
                           style="display:block; float:right; 
                           font-size:11px"><a 
                           href="fix-corpus.cgi?corpusdb=%s&sid_edit=%s&new_wid[]=%s&editm=delword"
                           style='color:red;text-decoration:none;'>
                          <b>x</b></a></span><input type="hidden" 
                           name="new_wid[]" value="%s"/>
                         </td>""" % (comment, wid, corpusdb, sid_edit, wid, wid))
                print("""</tr>""")

                # WORD SURFACE
                print("""<tr style="text-align:center">""")
                print("""<td><span title="word"><input type="text"
                         style="text-align:center;width:%dem" name="new_word[]" 
                         value="%s"/></span></td>
                      """ % (inputlenght, html_escape(word)))
                print("""</tr>""")



                # WORD LEMMA
                print("""<tr style="text-align:center">""")
                print("""<td><span title="lemma"><input type="text" 
                          name="new_lemma[]" value="%s"
                          style="text-align:center;width:%dem"/></span></td>
                      """ % (html_escape(lemma),inputlenght))
                print("""</tr>""")



                # WORD POS
                print("""<tr style="text-align:center">""")
                if pos_tags[lang][pos]['eng_def']:
                    pos_str = '%s:%s' % (pos, pos_tags[lang][pos]['eng_def'])
                else:
                    pos_str = 'unknown_tag'

                print("""<td><nobr><span title="%s"><select id="pos" 
                          name="new_pos[]" style="text-align:center; 
                          width:%dem">""" % (pos_str,inputlenght))
                for p in sorted(pos_tags[lang].keys()):
                    if p == pos:
                        print("""<option value ='%s'
                                  selected>%s</option>""" % (p, p))
                    else:
                        print("""<option value ='%s'>%s</option>""" %(p, p))
                print("""</select><a class='fancybox' href='#postags' 
                          style='color:black;text-decoration:none;'><!--
                          --><sup>?</sup></a></nobr></td>""")
                print("""</tr>""")

                
                # COMMENT
                print("""<tr style="text-align:center">""")
                if comment:
                    print(u"""<td><span 
                              title="comment ('None' will leave it empty)">
                              <textarea rows="2" cols="10" name="new_wcomment[]"
                              style="font-size:12px;width:%dem;" 
                              required>%s</textarea></span>
                              </td>""" % (inputlenght,comment))
                else:  # Print "None" box
                    print(u"""<td><span 
                              title="comment ('None' will leave it empty)">
                              <textarea rows="2" cols="10" name="new_wcomment[]"
                              style="font-size:12px;width:%dem; 
                              background-color: #E0E0E0" 
                              required>None</textarea>
                              </span></td>""" %(inputlenght,))
                print("""</tr>""")

                # END WORD TABLE
                print("""</table>""")
            print("""<br><br> <hr>""")


            ################
            # CONCEPT LEVEL
            ################
            print("""<h3> Edit concepts:</h3>""")
            for cid, (clemma, tag, ursname, comment) in concepts.items():

                # FIND INPUT LENGHT
                if len(clemma) == 1:
                    inputlenght = 7
                else:
                    inputlenght = len(clemma)
                    if inputlenght < 7:
                        inputlenght = 7
                    elif inputlenght > 8:
                        inputlenght = int(len(clemma)*0.8)


                print("""<table cellpadding="3" bgcolor="#E0E0E0" 
                          style="border-collapse: collapse; 
                          border: 1px solid black;display:inline-table; 
                          margin-top: 5px;">""")

                # CONCEPT ID / DELETE CONCEPT
                print("""<tr style="text-align:center">""")
                print(u"""<td><span><b>cid:%s</b></span>
                          <span title='delete concept!' style="color:red;
                          display: block; float: right; font-size:11px">
                          <a href="fix-corpus.cgi?corpusdb=%s&sid_edit=%s&new_cid[]=%s&editm=delconcept"
                          style='color:red;text-decoration:none;'>
                          <b>x</b></a></span><input type="hidden" 
                          name="new_cid[]" value="%s"/>
                          </td>""" % (cid, corpusdb, sid_edit, cid, cid))
                print("""</tr>""")

                # CONCEPT WORD LINKS (CWL)
                print("""<tr style="text-align:center">""")
                if cwls[cid] == []:
                    print("""<td><span title="wids"><input type="text"
                          name="new_wids[]" style="text-align:center; 
                         width:%dem;
                          background-color: #FF9696" value="%s"
                          style="text-align:center"/></span>
                          </td>
                      """ % (inputlenght, cwls[cid]))
                else:
                    print("""<td><span title="wids"><input type="text"
                          name="new_wids[]" value="%s"
                          style="text-align:center;width:%dem;"/></span>
                          </td>
                      """ % (cwls[cid],inputlenght))
                print("""</tr>""")

                
                # CONCEPT LEMMA (CLEMMA)
                clemma = html_escape(clemma.strip())  # escape & strip
                print("""<tr style="text-align:center">""")
                print("""<td><span title="clemma"><input type="text" 
                          name="new_clemma[]" value="%s"
                          style="text-align:center;width:%dem;"required/></span><!--
                          --><a class='fancybox fancybox.iframe' href='%s%s' 
                          style='color:black;text-decoration:none;'><!--
                          --><sup>?</sup></a></nobr></td>
                      """ % (clemma, inputlenght-1, wncgi_lemma, clemma))
                print("""</tr>""")


                # CONCEPT TAG
                if tag in ("e", "w"):
                    print("""<tr style="text-align:center">""")
                    print(u"""<td><nobr>
                          <span title="tag"><input type="text"
                           pattern ="None|x|e|w|loc|org|per|dat|dat:year|oth|[<>=~!]?[0-9]{8}-[avnr]"
                          name="new_tag[]" value="%s"
                          style="text-align:center;width:%dem; 
                          background-color: #FF9696" required/></span><!--
                          --><a class='fancybox fancybox.iframe' href='%s%s' 
                          style='color:black;text-decoration:none;'><!--
                          --><sup>?</sup></a></span></nobr></td>
                       """ % (str(tag).strip(), inputlenght-1, 
                              wncgi_ss, str(tag).strip()))
                    print("""</tr>""")
                elif tag:
                    print("""<tr style="text-align:center">""")
                    print(u"""<td><nobr>
                          <span title="tag"><input type="text"
                          name="new_tag[]" value="%s"
                          style="text-align:center;width:%dem;" 
                          required/></span><!--
                          --><a class='fancybox fancybox.iframe' href='%s%s' 
                          style='color:black;text-decoration:none;'><!--
                          --><sup>?</sup></a></span></nobr></td>
                       """ % (str(tag).strip(), inputlenght-1, 
                              wncgi_ss, str(tag).strip()))
                    print("""</tr>""")
                else:
                    print("""<tr style="text-align:center">""")
                    print(u"""<td><nobr><span title="Tag"><input type="text"
                          name="new_tag[]" value="None" 
                          style="text-align:center;width:%dem; 
                          background-color: #FF9696" required/></span><!--
                          --><a class='fancybox fancybox.iframe' href='%s%s' 
                          style='color:black;text-decoration:none;'><!--
                          --><sup>?</sup></a></nobr>
                          </td>""" %(inputlenght-1, wncgi_ss, str(tag).strip()))
                    print("""</tr>""")


                # CONCEPT COMMENT
                print("""<tr style="text-align:center">""")
                if comment:
                    print(u"""<td><span 
                           title="comment ('None' will leave it empty)">
                           <textarea rows="2" cols="10" name="new_comment[]"
                           style="font-size:12px;width:%dem;" 
                           required>%s</textarea>
                           </span></td>""" % (inputlenght, comment))
                else:  # PRINT 'None'
                    print("""<td><span 
                          title="comment ('None' will leave it empty)">
                          <textarea rows="2" cols="10" name="new_comment[]"
                          style="font-size:12px;width:%dem; 
                          background-color: #E0E0E0" 
                          required>None</textarea></span>
                          </td>""" %(inputlenght,))
                print("""</tr>""")

                print("""</table>""")


            ####################
            # BOTTOM STATUS BAR
            ####################
            print("""<br><span style="position: fixed; 
                      bottom: 10px; right: 5px;">""")

            print("""<span title='Add Word'><a class='fancybox' href='#addword' 
                      style='text-decoration:none;'>
                      <button class="btn" type="submit" 
                      style='font-size:20px;'>+Word</button></a></span>""")

            print("""<span title='Add Concept'><a class='fancybox' href='#addconcept' 
                      style='text-decoration:none;'>
                      <button class="btn" type="submit" 
                      style='font-size:20px;'>+Concept</button></a></span>""")

            print(u"""<span title='Submit'><input type="submit" value="Save"  
                       style="font-size:20px; text-decoration:none; 
                       color:green;"></span>""")

            print("""<br>&nbsp; """)

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
                     </span>""" % corpusdb)


            print("""</span>""")  # CLOSES THE BOTTOM FLOATING BAR


            #######################
            # TOP RIGHT LOG BAR
            #######################
            print(u"""<br><span style="position:fixed; 
                      top:10px; right:5px;">""")
            if log_status == "":
                pass
            else:
                print("""<table cellpadding="3" bgcolor="#fbfbfb" 
                          style="border-collapse: collapse; 
                          border: 1px solid black; display: inline-table; 
                          margin-top: 5px;">""")
                print("""<tr style="text-align:center"><td>%s</td>
                         </tr></table>""" %(log_status,))
            print("""</span>""") # CLOSES THE TOP FLOATING BAR

            print(""" </form> """) # CLOSES THE EDITING FORM


else:
    print(""" INVALID USER! PLEASE LOG IN! """)



####################################
# INVISIBLE DIV FOR POS TAGS HELPER
####################################
print("""<div id="postags" style="width:400px;display: none;">
            <h3>POS Tags</h3>""")
for p in sorted(pos_tags[lang].keys()):
    print( """<b>%s:</b> %s<br>""" % (p, pos_tags[lang][p]['eng_def']))
print("""</div>""")


#############################
# INVISIVLE DIV TO GOTO FORM
#############################
print("""<div id="goto" style="width:400px;display: none;">
            <b>Select a database and an SID</b><br>""")

# onsubmit="window.location.reload(true)"
print("""<hr><form action="fix-corpus.cgi?" method="post" 
         name="goto">
      """)

print("""<center><table cellpadding="3" bgcolor="#E0E0E0" 
          style="border-collapse: collapse; border: 1px solid black; 
          margin-top: 5px;">""")

# CHOOSE DB
print("""<tr style="text-align:center">""")
print("""<td><span title="DB"><b>DB:</b></span></td>
         <td><select id="sid" name="corpusdb"
         style="text-align:center" required>""")


corpusdb_in = False
for db in all_corpusdb():
    if corpusdb == db[0]:
        print("""<option value ='%s' selected>%s</option>""" % db)
        corpusdb_in = True
    else:
        print("""<option value ='%s'>%s</option>""" % db)
if corpusdb_in == False:
    print("<option value ='%s' selected>%s</option>" % (corpusdb, corpusdb))


print("""</select></td>""")
print("""</tr>""")

# CHOOSE SID
print("""<tr style="text-align:center">""")
print("""<td><span title="Go to SID">
          <b>SID: </b></td><td><input type="text" size="8" 
          name="sid_edit" style="text-align:center" 
          value="%s" required/> </span></td>""" % sid_edit)
print("""</tr>""")

print("""</table></center>""")

print(u"""<center><span title='Go to...'">
          <input type="submit" value="Go"  
           style="font-size:20px; text-decoration:none; 
           color:green; margin-top: 5px;"></center>""")
print("""</form>""")
print("""</div>""")


############################
# INVISIVLE DIV TO ADD WORD
############################
print("""<div id="addword" style="width:400px;display: none;">
            <b>Adding New Word to (SID:%s)</b><br>""" % (sid_edit,))

for w, l in sorted(words.items()):
    print(u"""| <b>%s:</b> %s """ % (w,l[0]))
print(u"""|""")

# onsubmit="window.location.reload(true)"
print("""<hr><form action="fix-corpus.cgi?sid_edit=%s" 
           method="post" name="addword"> 
         <input type="hidden" name="editm" value="addword"/>
         <input type="hidden" name="corpusdb" value="%s"/>
      """ % (sid_edit, corpusdb))

print("""<center><table cellpadding="3" bgcolor="#E0E0E0" 
          style="border-collapse:collapse; border:1px solid black; 
          margin-top:5px;">""")

print("""<tr style="text-align:center">""")
print(u"""<td><span title='Select new wid position (new word will occupy that position and push forward the remaining words)'>
              <b>Wid:</b></span></td><td>""")
print("""<span title="%s"><select id="pos" name="new_wid[]" 
                style="text-align:center" required>""" % "Select the WID position you want the word to go (other words will be pushed forward)")

for w in sorted(words.keys()):
      print("""<option value ='%s' selected>%s</option>""" % (w, w))
try:
    print("""<option value ='%s' selected>%s</option>""" % (w+1, w+1))
except: # NO WORDS
    print("""<option value ='%s' selected>%s</option>""" % (0, 0))
    

print("""</select></td>""")

print(""" """)
print("""</tr>""")

# NEW WORD POS
print("|%s|" % lang) #TEST
print("""<tr style="text-align:center">""")
print("""<td><span title="Select the POS of the new word">
         <b>POS:</b></td><td><select id="pos" name="new_pos[]" 
             style="text-align:center" required>""")

print("""<option value ='' selected>POS</option>""")
taghelp = ""
for i, (p, info) in enumerate(sorted(pos_tags[lang].items())):
    # print("""<option>%s,%s,%s</option>""" % (i,p,info) ) #TEST
    print("""<option value='%s'>%s</option>""" % (p, p))
    try:
        taghelp += "%s:%s;  " % (html_escape(p), html_escape(info['eng_def']))
    except:
        continue #!!! This is catching some bug (see sid 16116 for cmn)
    if i % 2 != 0:
        taghelp += "&#10;"
print("""</select></span><span title="%s"><sup>?</sup>
         </span></td>""" % taghelp)
print("""</tr>""")

# NEW WORD SURFACE FORM
print("""<tr style="text-align:center">""")
print("""<td><span title="Type the new surface form of the new word.">
          <b>Word: </b></td><td><input type="text" size="8" 
          name="new_word[]" style="text-align:center" required/>
          </span></td>""")
print("""</tr>""")

# NEW WORD LEMMA
print("""<tr style="text-align:center">""")
print("""<td><span title="Type the new lemmatised form of the new word.">
             <b>Lemma: </b></td><td><input type="text" size="8" 
          name="new_lemma[]" style="text-align:center" required/></span></td>""")
print("""</tr>""")

# NEW WORD COMMENT
print("""<tr style="text-align:center">""")
print(u"""<td><span title="comment ('None' will leave it empty)">
          <b>Comment: </b></td><td>
          <textarea rows="1" cols="16" name="new_wcomment[]"
           style="font-size:12px; background-color: #E0E0E0"
           required>None</textarea></span></td>""")
print("""</tr>""")

print("""</table></center>""")

print(u"""<center><span title='Create New Word!'">
          <input type="submit" value="Create New Word"  
           style="font-size:20px; text-decoration:none; 
           color:green; margin-top: 5px;"></center>""")
print("""</form>""")
print("""</div>""")


###############################
# INVISIVLE DIV TO ADD CONCEPT
###############################
print("""<div id="addconcept" style="width:400px;display: none;">
            <b>Adding New Concept to (SID:%s)</b><br>""" % (sid_edit,))

for w, l in sorted(words.items()):
    print(u"""| <b>%s:</b> %s """ % (w,l[0]))
print(u"""|""")


# onsubmit="window.location.reload(true)"
print("""<hr><form action="fix-corpus.cgi?sid_edit=%s" 
           method="post" name="addconcept"> 
         <input type="hidden" name="editm" value="addconcept"/>
         <input type="hidden" name="corpusdb" value="%s"/>
      """ % (sid_edit, corpusdb))


# NEW CONCEPT ID (Tries to find the lowest possible)
if len(concepts.keys()) > 0:
    new_cid = max(concepts.keys()) + 1
else: 
    new_cid = 0

print("""<input type="hidden" name="new_cid[]" value="%s"/>
         <center><b>New ConceptID: %s </b>""" % (new_cid,new_cid))


print("""<table cellpadding="3" bgcolor="#E0E0E0" 
          style="border-collapse: collapse; border: 1px solid black; 
          margin-top: 5px;">""")

# NEW CONCEPT LEMMA
print("""<tr style="text-align:center">""")
print("""<td><span title="Type the lemma of the new concept.">
             <b>C-Lemma: </b></td><td><input type="text" size="8" 
          name="new_clemma[]" style="text-align:center" required/></span></td>""")
print("""</tr>""")


# NEW CONCEPT-WORD LINKS (THIS IS READ AS A LIST)
print("""<tr style="text-align:center">""")
print("""<td><span title="Type the list of words it links to.">
             <b>C-W Links: </b></td><td><input type="text" 
               size="8" value="[]" 
          name="new_wids[]" style="text-align:center" required/></span></td>""")
print("""</tr>""")

# NEW CONCEPT TAG
print("""<tr style="text-align:center">""")
print("""<td><span title="The synset that should tag this concept.">
             <b>Tag: </b></td><td><input type="text" size="8" 
             pattern="[0-9]{8}-[avnr]|dat|dat:year|e|loc|num|org|oth|per|w|" 
             title = "xxxxxxxx-a/v/n/r"
              name="new_tag[]" style="text-align:center"/></span></td>""")
print("""</tr>""")



# NEW CONCEPT COMMENT
print("""<tr style="text-align:center">""")
print(u"""<td><span title="comment ('None' will leave it empty)">
          <b>Comment: </b></td><td>
          <textarea rows="1" cols="16" name="new_comment[]"
            style="font-size:12px; background-color: #E0E0E0"
          required >None</textarea></span></td>""")
print("""</tr>""")
print("""</table></center>""")


print(u"""<center><span title='Create New Concept!'">
          <input type="submit" value="Create New Concept"
           style="font-size:20px; text-decoration:none;
           color:green; margin-top: 5px;"></center>""")
print("""</form>""")
print("""</div>""")


#############
# CLOSE HTML
#############
print("""</body></html>\n""")
conn_db.commit()
