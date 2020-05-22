#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import re, sqlite3, datetime, time, re, itertools, traceback

from ntumc_util import *
from ntumc_webkit import *

# import sys,codecs
# sys.stdout = codecs.getwriter('utf8')(sys.stdout)


################################################################################
# This scrip edits the linked corpus database.
# It will be able to link sentences, words and concepts
# for now it is desinged only for sentence linking!
################################################################################
valid_modes = ['sentence_link', 'del_sentence_link','word_link']
html_log = []  # List of messages to print as log

form = cgi.FieldStorage()
edit_mode = form.getfirst("edit_mode")
lang_from = form.getfirst("lang_from")
lang_to = form.getfirst("lang_to")
linked_db = form.getfirst("linked_db")
username = form.getfirst("username")
new_sent_link = form.getfirst("new_sent_link")
delete_sent_link = form.getfirst("delete_sent_link")

new_word_link = form.getfirst("new_word_link")
delete_word_link = form.getfirst("delete_word_link")


# FIELDS TO RETURN
l1 = form.getfirst("lang1")
l2 = form.getfirst("lang2")
docName = form.getfirst("docName")

################################################################################
# PREPROCESSING FORM DATA
################################################################################
linkeddb_match_lang = False
if new_sent_link:
    sent_pair = new_sent_link.split('|||')
    if sent_pair[0][0:3] == lang_to and sent_pair[1][0:3] == lang_from:
        fsid = sent_pair[1][3:]
        tsid = sent_pair[0][3:]
        linkeddb_match_lang = True
    elif sent_pair[1][0:3] == lang_to and sent_pair[0][0:3] == lang_from:
        fsid = sent_pair[0][3:]
        tsid = sent_pair[1][3:]
        linkeddb_match_lang = True
    else:
        html_log.append("""You can only link between 2 different languages!""")

elif delete_sent_link:
    sent_pair = delete_sent_link.split('|||')
    if sent_pair[0][0:3] == lang_to and sent_pair[1][0:3] == lang_from:
        fsid = sent_pair[1][3:]
        tsid = sent_pair[0][3:]
        linkeddb_match_lang = True
    elif sent_pair[1][0:3] == lang_to and sent_pair[0][0:3] == lang_from:
        fsid = sent_pair[0][3:]
        tsid = sent_pair[1][3:]
        linkeddb_match_lang = True
    else:
        html_log.append("Please Report BUG(1)!")

elif new_word_link:
    word_pair = new_word_link.split('|||')
    if word_pair[0].split('_')[0] == lang_to and word_pair[1].split('_')[0] == lang_from:
        fsid = word_pair[1].split('_')[1]
        fwid = word_pair[1].split('_')[2]
        tsid = word_pair[0].split('_')[1]
        twid = word_pair[0].split('_')[2]
        linkeddb_match_lang = True
        html_log.append("""PASSED 1.1!""")
    elif word_pair[1].split('_')[0] == lang_to and word_pair[0].split('_')[0] == lang_from:
        fsid = word_pair[0].split('_')[1]
        fwid = word_pair[0].split('_')[2]
        tsid = word_pair[1].split('_')[1]
        twid = word_pair[1].split('_')[2]
        linkeddb_match_lang = True
        html_log.append("""PASSED 1.2!""")
    else:
        html_log.append("""You can only link between 2 different languages!""")




# GET ANCHOR TO RETURN
if l1 == lang_from and linkeddb_match_lang:
    anchor_return = "%s%s" % (l1, fsid)
elif linkeddb_match_lang:
    anchor_return = "%s%s" % (l1, tsid)
else:
    anchor_return = ""
################################################################################


################################################################################
# CONNECT TO DB
################################################################################
con = sqlite3.connect(linked_db) 
c = con.cursor()
################################################################################


################################################################################
# PREPARE FUNCTIONS
################################################################################
def create_sentence_triggers(c):
    """This function created the triggers for sentence linking, if it
    didn't have them already. It will add a new log table and triggers.
    Trigers for links are not editable, so triggers are only created for 
    new and deleted links."""

    # CREATE LOG TABLE (FOR TRIGGERS)
    c.execute("""CREATE TABLE IF NOT EXISTS slink_log
                 (fsid_new INTEGER, fsid_old INTEGER,
                  tsid_new INTEGER, tsid_old INTEGER, 
                  ltype_new TEXT, ltype_old TEXT,
                  conf_new FLOAT, conf_old FLOAT,
                  comment_new TEXT, comment_old TEXT,
                  usrname_new TEXT, usrname_old TEXT,
                  date_update DATE)""")

    # CREATE TRIGGERS
    c.execute("""CREATE TRIGGER IF NOT EXISTS delete_slink_log
                 AFTER DELETE ON slink
                 BEGIN
                 INSERT INTO slink_log (fsid_old,
                                        tsid_old,
                                        ltype_old,
                                        conf_old,
                                        comment_old,
                                        usrname_old,
                                        date_update)
                 VALUES (old.fsid,
                         old.tsid,
                         old.ltype,
                         old.conf,
                         old.comment,
                         old.usrname,
                         DATETIME('NOW'));
                 END """)

    c.execute("""CREATE TRIGGER IF NOT EXISTS insert_slink_log
                 AFTER INSERT ON slink
                 BEGIN
                 INSERT INTO slink_log (fsid_new,
                                        tsid_new,
                                        ltype_new,
                                        conf_new,
                                        comment_new,
                                        usrname_new,
                                        date_update) 
                 VALUES (new.fsid,
                         new.tsid,
                         new.ltype,
                         new.conf,
                         new.comment,
                         new.usrname,
                         DATETIME('NOW'));
                 END""")

    return None



def create_word_triggers(c):
    """This function created the triggers for word linking, if it
    didn't have them already. It will add a new log table and triggers.
    Trigers for links are not editable, so triggers are only created for 
    new and deleted links."""


    # CREATE LOG TABLE (FOR TRIGGERS)
    c.execute("""CREATE TABLE IF NOT EXISTS wlink_log
                 (fsid_new INTEGER, fsid_old INTEGER,
                  fwid_new INTEGER, fwid_old INTEGER,
                  tsid_new INTEGER, tsid_old INTEGER,
                  twid_new INTEGER, twid_old INTEGER,
                  ltype_new TEXT, ltype_old TEXT,
                  conf_new FLOAT, conf_old FLOAT,
                  comment_new TEXT, comment_old TEXT,
                  usrname_new TEXT, usrname_old TEXT,
                  date_update DATE)""")


    # CREATE TRIGGERS
    c.execute("""CREATE TRIGGER IF NOT EXISTS delete_wlink_log
                 AFTER DELETE ON wlink
                 BEGIN
                 INSERT INTO wlink_log (fsid_old,
                                        fwid_old,
                                        tsid_old,
                                        twid_old,
                                        ltype_old,
                                        conf_old,
                                        comment_old,
                                        usrname_old,
                                        date_update)
                 VALUES (old.fsid,
                         old.fwid,
                         old.tsid,
                         old.twid,
                         old.ltype,
                         old.conf,
                         old.comment,
                         old.usrname,
                         DATETIME('NOW'));
                 END """)

    c.execute("""CREATE TRIGGER IF NOT EXISTS insert_wlink_log
                 AFTER INSERT ON wlink
                 BEGIN
                 INSERT INTO wlink_log  (fsid_new,
                                         fwid_new,
                                         tsid_new,
                                         twid_new,
                                         ltype_new,
                                         conf_new,
                                         comment_new,
                                         usrname_new,
                                        date_update)
                 VALUES (new.fsid,
                         new.fwid,
                         new.tsid,
                         new.twid,
                         new.ltype,
                         new.conf,
                         new.comment,
                         new.usrname,
                         DATETIME('NOW'));
                 END""")

    return None

################################################################################






################################################################################
# LINK THINGS
################################################################################
if (edit_mode in valid_modes) and (username in valid_usernames) \
   and linkeddb_match_lang:

    if edit_mode == "sentence_link":  # NEW LINK IF IT DIDN'T EXIST

        # Make sure there are triggers to save the changes;
        create_sentence_triggers(c)

        c.execute("""INSERT INTO slink(fsid, tsid, conf, usrname) 
                     SELECT ?,?,?,? 
                     WHERE NOT EXISTS(SELECT 1 
                                      FROM slink 
                                      WHERE fsid = ? 
                                      AND tsid = ? )""", 
                  [fsid, tsid, 1.0, username, 
                   fsid, tsid])

        log = "Sentence link (%s-%s | %s-%s)" % (lang_from, fsid,
                                                     lang_to, tsid)
        log += " created/updated by %s. " % username
        html_log.append(log)


    elif edit_mode == "del_sentence_link":  # DELETE SENTENCE LINK

        c.execute("""UPDATE slink SET usrname = ?
                     WHERE fsid = ? AND tsid = ? 
                     AND usrname IS NOT ?""",
                  [username, fsid, tsid, username])

        c.execute("""DELETE FROM slink
                     WHERE fsid = ? AND tsid = ?
                     AND usrname = ?""",
                  [fsid, tsid, username])

        log = "The sentence link (%s-%s | %s-%s)" % (lang_from, fsid,
                                                     lang_to, tsid)
        log += " was deleted by %s. " % (username)
        html_log.append(log)




    elif edit_mode == "word_link":  # NEW WORD LINK

        html_log.append("""ENTERED WORDLINK!""")

        try:

            create_word_triggers(c)
            html_log.append("""CREATED THE TRIGGERS!""")


            html_log.append("""
INSERT INTO wlink(fsid, tsid, fwid, twid, conf, usrname) SELECT %s,%s,%s,%s,%s,%s  WHERE NOT EXISTS(SELECT 1 
 FROM wlink WHERE fsid = %s AND tsid = %s AND fwid = %s AND twid = %s ) <br>""" %  (fsid, tsid, fwid, twid, 1.0, username, fsid, tsid, fwid, twid) )



            c.execute("""INSERT INTO wlink(fsid, tsid, fwid, twid, conf, usrname) 
                         SELECT ?,?,?,?,?,?
                         WHERE NOT EXISTS(SELECT 1 
                                          FROM wlink 
                                          WHERE fsid = ? 
                                          AND tsid = ? 
                                          AND fwid = ? 
                                          AND twid = ? )""", 
                      [fsid, tsid, fwid, twid, 1.0, username, 
                       fsid, tsid, fwid, twid])

            html_log.append("""CREATED THE LINK IN THE DATABASE!""")


            log = "Word link (%s-sid%s:wid%s | %s-sid%s:wid%s)" % (lang_from, fsid,fwid,
                                                                   lang_to, tsid, twid)
            log += " created/updated by %s. " % username
            html_log.append(log)

        except:
            html_log.append(new_word_link)
            html_log.append('<br>')
            html_log.append('; '.join([str(fsid), str(tsid), str(fwid), str(twid), '1.0', username, 
                       str(fsid), str(tsid), str(fwid), str(twid)]))


con.commit()
################################################################################



############################################################################
# REDIRECT TO PREVIOUS PAGE (BY CGI-MODE)
# This redirects back to the previous interface, returning the necessary
# values to go back to the original place in a form;
############################################################################
print (u"""Content-type: text/html; charset=utf-8 \n\n
<!DOCTYPE html>
  <html>
    <head>
      <meta charset='utf-8'>
    </head>""")

if edit_mode == "sentence_link" or edit_mode == "del_sentence_link": 
    print("""<body onload="document.logform.submit()">
          <form name="logform" action="sent-linking.cgi#%s"  method="post">
          <input type="hidden" name="log_message" value="%s" /> 
          <input type="hidden" name="l1" value="%s"/>
          <input type="hidden" name="l2" value="%s"/>
          <input type="hidden" name="docName" value="%s"/>
          </form>
          </body>""" % (anchor_return, '<br>'.join(html_log), l1, l2, docName))

elif edit_mode == "word_link": 
    print("""<body onload="document.logform.submit()">
          <form name="logform" action="word-linking.cgi#%s"  method="post">
          <input type="hidden" name="log_message" value="%s" /> 
          <input type="hidden" name="l1" value="%s"/>
          <input type="hidden" name="l2" value="%s"/>
          </form>
          </body>""" % (anchor_return, '<br>'.join(html_log), l1, l2))
else:
    print("""<body>%s</body>""" % "<br>".join(html_log))
print("""</html>""") 




# try:
#     # Get data from html form fields
#     form = cgi.FieldStorage()

#     synset = form.getvalue('synset')

#     # this can be "add" (add new lemmas, ex, defs, ..), 
#     # "mod" (modify) or "nss" (new synset), defines the editing mode
#     deleteyn = form.getvalue('deleteyn')

#     # info needed for nss (new synset)
#     engname = form.getvalue('engname')
#     pos = form.getvalue('pos')

#     synlink = form.getlist('synlink[]')
#     linkedsyn = form.getlist('linkedsyn[]')
#     synlinko = form.getlist('synlinko[]')   # old
#     linkedsyno = form.getlist('linkedsyno[]')   # old

#     engdef = form.getvalue('engdef')
#     lang = form.getvalue('lang')

#     netype = form.getvalue('netype')

#     usrname = form.getvalue('usrname')

#     # lemmas and lemmalangs are two lists that are co-referenced with the same index
#     # (e.g. lemmas[0] is a lemma in the language lemmalangs[0])
#     lemmas = form.getlist('lemmalst[]')
#     lemmalangs = form.getlist('lemmalangs[]')


#     # These are used both to edit and to create a new synset
#     deflst = form.getlist('deflst[]')
#     deflangs = form.getlist('deflangs[]')

#     eglst = form.getlist('eglst[]')
#     eglangs = form.getlist('eglangs[]')


#     # Extra data needed to edit the entries

#     lemmaos = form.getlist('lemmao[]') # lemma old
#     lemmans = form.getlist('lemman[]') # lemma new

#     confos = form.getlist('confo[]') # confidence old 
#     confns = form.getlist('confn[]') # confidence new

#     defos = form.getlist('defo[]') # definition old
#     defns = form.getlist('defn[]') # definition new
#     defelangs = form.getlist('defelangs[]') # definitions(edited) langs

#     exeos = form.getlist('exeo[]')
#     exens = form.getlist('exen[]')
#     exeelangs = form.getlist('exeelangs[]') # examples(edited) langs 


#     # dict to hold the relation oposites
#     relopp = {}
#     synlinks = ["also", "hype", "inst", "hypo", 
#             "hasi", "mmem", "msub", "mprt", 
#             "hmem", "hsub", "hprt", "attr", 
#             "sim", "enta", "caus", "dmnc", 
#             "dmnu", "dmnr", "dmtc", "dmtu", 
#             "dmtr", "eqls","ants","hasq","qant"]

#     # relations are inserted with their oposites 
#     # (e.g if X is hypo of Y, then Y is hype of X ) 
#     # entailment and causation don't have oposites, 
#     synlinksopp = ["also", "hypo", "hasi", "hype", 
#                "inst", "hmem", "hsub", "hprt", 
#                "mmem", "msub", "mprt", "attr", 
#                "sim", None, None, "dmtc", 
#                "dmtu", "dmtr", "dmnc", "dmnu", 
#                "dmnr", "eqls","ants","qant", "hasq"]

#     for x in xrange(0, len(synlinks)):
#         relopp[synlinks[x]] = synlinksopp[x]
    


#     # Connects to wn-ntumc.db (edited version with datechanged, 
#     # status and editor fields on most tables)
#     conn = sqlite3.connect(wndb)
#     curs = conn.cursor()

#     # this is a placeholder for changes made (will print lines to the log)
#     updatereport = "<hr>"

#     # create the log (in case the file was not there before)
#     notelog = codecs.open('addss_error.log', 'a+', 'utf-8')
    
#     # create the error log for the cgi errors
#     errlog = codecs.open('cgi_err.log', 'a+', "utf-8")

#     # time stamp
#     datechanged = datetime.datetime.now().strftime('%Y-%m-%d.%H:%M:%S')
    

#     # Name of editor is read by the cgifields
#     if usrname:
#         editor = usrname
#     else:
#         editor = "someone"

#     #######################################################################################
#     # EDIT MODEs: "add" (add info to synsets), "mod" (modify synsets) or "nss" (new synset)
#     #######################################################################################

#     #######################################
#     # EDIT MODE: ADD (add info to synsets)
#     #######################################
#     if deleteyn == "add" and editor in valid_usrs:

#         # new entries will have "new" printed in their status column
#         status = "new"

#         updatereport += """\n Appending to Synset &nbsp;&nbsp;&nbsp;&nbsp; 
#                               Date: %s &nbsp;&nbsp;&nbsp;&nbsp; Editor: %s<br> 
#                         """  % (datechanged, editor)

#         # IF THERE ARE NEW DEFINITIONS
#         if len(deflst) != 0:
            
#             defsrep = ""  # REPORT
#             defscounter = 0
#             for i, d in enumerate(deflst):
#                 d = d
#                 d = d.strip(u' .,;:!?。；：！')
#                 dlang = deflangs[i] # MATCH LANG PER DEF

#                 # FETCH THE HIGHEST SID (THERE IS ALWAYS SOMETHING TO RETURN)
#                 curs.execute(""" SELECT max(sid) from synset_def where synset like '%s' """ % synset)
#                 sid = int(curs.fetchone()[0]) + 1 # NEW SID is +1 to highest

#                 # INSERT NEW DEFINITONS
#                 curs.execute("""INSERT INTO synset_def(synset, lang, def, sid, usr) 
#                                 VALUES (?,?,?,?,?) """,  
#                              [synset, dlang, d, sid, editor])

#                 defsrep += u' | ' + deflangs[i] + ':' + d
#                 defscounter = i +1

#             updatereport += """\n Added <strong>%s</strong> definitions to synset: %s <br>
#                                Definitions: %s <br>""" % (str(defscounter), synset, defsrep)

#         # IF THERE ARE NEW EXAMPLES
#         if len(eglst) != 0:

#             egsrep = ""
#             egscounter = 0
#             for i, e in enumerate(eglst):
#                 e = e.strip()
#                 e = e.strip(u' .,;:!?。；：！')
#                 elang = eglangs[i]  # MATCH LANGUAGE PER EXAMPLE

#                 # FETCH THE HIGHEST SID (MAY FAIL)
#                 curs.execute("""SELECT max(sid) 
#                                 FROM synset_ex 
#                                 WHERE synset LIKE '%s' 
#                              """ % synset)
#                 try: # TRY ADDING 1 
#                     sid = int(curs.fetchone()[0]) + 1
#                 except: # ELSE THERE WERE NO EXAMPLES
#                     sid = 0

#                 # insert data of the new example
#                 curs.execute("""INSERT INTO synset_ex(synset, lang, def, sid, usr) 
#                                 VALUES (?,?,?,?,?) """, 
#                              [synset, elang, e, sid, editor])

#                 egsrep += u' | ' + eglangs[i] + ':' + e
#                 egscounter = i +1

#             updatereport += """\n Added <strong>%s</strong> examples to synset: %s <br>
#                                Examples: %s <br>""" % (str(egscounter), synset, egsrep)


#         # IF THERE ARE NEW LEMMAS
#         if len(lemmas) != 0:
#             pos = synset[-1]

#             lemmasrep = ""
#             lemmascounter = 0
#             for i, lemma in enumerate(lemmas):
#                 lang = lemmalangs[i] # match each lemma language
#                 lemma = lemma.strip() # the sqlite was rejecting other str 
                
#                 # CHECK IF WORDID EXISTS
#                 curs.execute("""SELECT wordid FROM word 
#                                 WHERE lemma=? 
#                                 AND pos=? AND lang=? """, 
#                              [lemma, pos, lang])
#                 wordid = curs.fetchone() # returns a tuple

#                 if wordid != None: # KEEP WORDID
#                     wordid = wordid[0]
#                 else:  # OR INSERT WORD + KEEP WORDID
#                     curs.execute("""INSERT INTO word(wordid, lang, lemma, pos, usr) 
#                                     VALUES (?,?,?,?,?)""", 
#                                  [None, lang, lemma, pos, editor])
#                     wordid = curs.lastrowid

#                 # CHECK THAT SENSE DOESN'T EXIST
#                 curs.execute("""SELECT wordid, synset, lang 
#                                 FROM sense
#                                 WHERE wordid=? 
#                                 AND synset=? AND lang=? 
#                              """, [wordid, synset, lang])
#                 previouslemma = curs.fetchone() # returns a tuple

#                 if previouslemma == None:  # IF NO PREVIOUS LEMMA

#                     # link wordid to synset sense, confidence of created synsets is 1.0
#                     curs.execute("""INSERT INTO sense(synset, wordid, lang, confidence, src, usr)
#                                     VALUES (?,?,?,?,?,?)""", 
#                                  [synset, wordid, lang, 1.0, ntumc, editor])

#                 lemmascounter = i + 1
#                 lemmasrep +=  u' | ' +  lemmalangs[i] + ':' + lemma

#             updatereport += """\n Added <strong>%s</strong> lemmas to synset: %s <br>
#                                Lemmas: %s <br>""" % (str(lemmascounter), synset, lemmasrep)


#         # IF THERE ARE NEW SYNLINKS
#         if len(linkedsyn) != 0:
#             linksrep = ""
#             linkscounter = 0

#             for i, link in enumerate(synlink):
#                 lss = linkedsyn[i].strip()

#                 # CHECK THAT SYNLINK DOESN'T EXIST
#                 curs.execute("""SELECT synset1, synset2 
#                                 FROM synlink
#                                 WHERE synset1=? 
#                                 AND synset2=? AND link=? 
#                              """, [synset, lss, link])
#                 previoussynlink = curs.fetchone() # returns a tuple

#                 if previoussynlink == None:  # IF NO PREVIOUS SYNLINK, INSERT IT
#                     curs.execute("""INSERT INTO synlink(synset1, synset2, link, usr) 
#                                     VALUES (?,?,?,?)""", 
#                                  [synset, lss, link, editor])


#                 if relopp[link]:
#                     # CHECK THAT REVERSE_SYNLINK DOESN'T EXIST
#                     curs.execute("""SELECT synset1, synset2 
#                                     FROM synlink
#                                     WHERE synset1=? 
#                                     AND synset2=? AND link=? 
#                                  """, [lss, synset, relopp[link]])
#                     previoussynlink_rev = curs.fetchone() # returns a tuple

#                     if previoussynlink_rev == None:  # IF NO PREVIOUS REVERSE_SYNLINK, INSERT IT
#                         curs.execute("""INSERT INTO synlink(synset1, synset2, link, usr) 
#                                         VALUES (?,?,?,?)""", 
#                                      [lss, synset, relopp[link], editor])

#                 linkscounter = i + 1
#                 linksrep +=  u' | ' + synset + '---' + link + '---' + lss

#             updatereport += """\n Added <strong>%s</strong> relations (and their inverses) to synset: %s <br>
#                                Relations: %s <br>""" % (str(linkscounter), synset, linksrep)


#     ########################################################
#     # EDIT MODE: MOD (editing or deleting previous entries)
#     ########################################################
#     elif deleteyn == "mod" and editor in valid_usrs:

#         updatereport += """\n Entering editing mode: &nbsp;&nbsp;&nbsp;&nbsp; 
#                               Date: %s &nbsp;&nbsp;&nbsp;&nbsp; Editor: %s<br> 
#                         """  % (datechanged, editor)

#         # CHECK FOR CHANGES TO DEFINITIONS
#         if len(defos) == len(defns):
#             i = 0
#             defsrep = ""  # string to print report

#             for defo, defn in zip(defos, defns): # zip() creates a list of tuples of type [(x[0],y[0]),...]
#                 dlang = defelangs[i] # MATCH THE LANG PER DEF
#                 i += 1

#                 if defn == "delete!":  # IF "delete!", DELETE
#                     defo = defo # the sqlite was rejecting other str 

#                     # DELETE OLD ENTRY (NEED TO UPDATE THE USR FIRST)
#                     curs.execute("""UPDATE synset_def SET usr=? 
#                                     WHERE synset=? AND lang=? AND def=?
#                                     AND usr IS NOT ?
#                                  """, [editor, synset, dlang, defo, editor])
#                     curs.execute("""DELETE FROM synset_def 
#                                     WHERE synset=? AND lang=? AND def=?
#                                  """, [synset, dlang, defo])

#                     defsrep += u' | ' + '<del>' +  defo + '</del> was deleted '
#                     updatereport += """\n Deleted definition of synset: %s <br>
#                                       %s <br>""" % (synset, defsrep)


#                 elif defo != defn:  # IF THERE IS A CHANGE
#                     defo = defo # the sqlite was rejecting other str 
#                     defn = defn # the sqlite was rejecting other str 
#                     defn = defn.strip(u' .,;:?。；：') # avoid punctuation in definitions

#                     # UPDATE OLD ENTRY
#                     curs.execute("""UPDATE synset_def SET usr=?, def=? 
#                                     WHERE synset=? AND lang=? AND def=?
#                                  """, [editor, defn, synset, dlang, defo])

#                     defsrep = u' | ' + '<del>' +  defo + '</del> >>> ' +  defn
#                     updatereport += """\n Edited definition of synset: %s <br>
#                                       %s <br>""" % (synset, defsrep)


#         # CHECK FOR CHANGES TO EXAMPLES
#         if len(exeos) == len(exens):
#             i = 0
#             egsrep = ""  # string to print report

#             for exeo, exen in zip(exeos, exens):
#                 elang = exeelangs[i]  # MATCH THE LANG PER EX
#                 i += 1

#                 if exen == "delete!":  # IF "delete!", DELETE
#                     exeo = defo # the sqlite was rejecting other str 

#                     # DELETE OLD ENTRY (NEED TO UPDATE THE USR FIRST)
#                     curs.execute("""UPDATE synset_ex SET usr=?
#                                     WHERE synset=? AND lang=? AND def=?
#                                     AND usr IS NOT ?
#                                  """, [editor, synset, elang, exeo, editor])
#                     curs.execute("""DELETE FROM synset_ex
#                                     WHERE synset=? AND lang=? AND def=?
#                                  """, [synset, elang, exeo])
                    
#                     egsrep = u' | ' + '<del>' +  exeo + '</del> '
#                     updatereport += """\n Deleted example of synset: %s <br>
#                                       %s <br>""" % (synset, egsrep)


#                 elif exeo != exen:  # IF THERE IS A CHANGE
#                     exeo = exeo # the sqlite was rejecting other str 
#                     exen = exen # the sqlite was rejecting other str 
#                     exen = exen.strip(u' .,;:?。；：') # avoid punctuation

#                     # UPDATE OLD ENTRY (NEED TO UPDATE THE USR FIRST)
#                     curs.execute("""UPDATE synset_ex SET usr=?, def=?
#                                     WHERE synset=? AND lang=? AND def=?
#                                  """, [editor, exen, synset, elang, exeo])
 
#                     egsrep = u' | ' + '<del>' +  exeo + '</del> >>> ' +  exen
#                     updatereport += """\n Edited example of synset: %s <br>
#                                       %s <br>""" % (synset, egsrep)


#         # CHECK FOR CHANGES TO LEMMAS
#         if len(lemmaos) == len(lemmans):
#             pos = synset[-1]
#             i = 0

#             for lemmao, lemman in zip(lemmaos, lemmans):
#                 confo = confos[i]
#                 confn = confns[i]
#                 i += 1
#                 dif = abs(float(confo) - float(confn))
#                 lemmao = lemmao.strip()
#                 lemman = lemman.strip()                    

#                 # FETCH OLD WORDID (MUST EXIST)
#                 curs.execute("""SELECT wordid FROM word 
#                                 WHERE lemma=? AND pos=? AND lang=? 
#                              """, [lemmao, pos, lang])
#                 wordid_old = curs.fetchone()[0] # returns a tuple


#                 if lemman == "delete!":  # DELETE
                    
#                     # DELETE OLD ENTRY (NEED TO UPDATE THE USR FIRST)
#                     curs.execute("""UPDATE sense SET usr=?
#                                     WHERE synset=? AND lang=? AND wordid=?
#                                     AND usr IS NOT ?
#                                  """, [editor, synset, lang, wordid_old, editor])
#                     curs.execute("""DELETE FROM sense 
#                                     WHERE synset=? AND lang=? AND wordid=?
#                                  """, [synset, lang, wordid_old])

#                     updatereport += "<br> Deleted lemma (<del>%s</del>) in %s" %(lemmao, synset)


#                 elif lemmao != lemman:  # IF LEMMAS WERE DIFFERENT

#                     # CHECK IF NEW WORD EXISTS (FOR WORDID)
#                     curs.execute("""SELECT wordid FROM word
#                                     WHERE lemma=? AND pos=? AND lang=?
#                                  """, [lemman, pos, lang])
#                     wordid_new = curs.fetchone() # returns a tuple

#                     if wordid_new != None: # EXISTED
#                         wordid_new = wordid_new[0]

#                     else:  # ELSE, CREATE NEW WORD
#                         curs.execute("""INSERT INTO word(wordid, lang, lemma, pos, usr) 
#                                         VALUES (?,?,?,?,?)""", 
#                                      [None, lang, lemman, pos, editor])
#                         wordid_new = curs.lastrowid
#                         updatereport += "<br> New word (%s)[%s] was added to langague (%s)" % (lemman, pos, lang)


#                     # VERIFY IF SENSE ALREADY EXISTED
#                     curs.execute("""SELECT wordid, synset, lang
#                                     FROM sense
#                                     WHERE wordid=? AND synset=? AND lang=?
#                                  """, [wordid_new, synset, lang])

#                     if not curs.fetchone():  # IF NO PREVIOUS SENSE, INSERT NEW (CONF=1.0)

#                         # UPDATE OLD ENTRY
#                         curs.execute("""UPDATE sense SET usr=?, wordid=?, confidence=?, src=?
#                                         WHERE synset=? AND lang=? AND wordid=?
#                                      """, [editor, wordid_new, 1.0, ntumc, 
#                                            synset, lang, wordid_old])

#                         updatereport += "<br>Sense (<del>%s</del>) became (%s) in %s" %(lemmao, lemman, synset)

#                     else:
#                         # DELETE OLD ENTRY (NEED TO UPDATE THE USR FIRST)
#                         curs.execute("""UPDATE sense SET usr=?
#                                         WHERE synset=? AND lang=? AND wordid=?
#                                         AND usr IS NOT ?
#                                      """, [editor, synset, lang, wordid_old, editor])
#                         curs.execute("""DELETE FROM sense 
#                                         WHERE synset=? AND lang=? AND wordid=?
#                                      """, [synset, lang, wordid_old])
                        
#                         updatereport += "<br> Deleted lemma (<del>%s</del>) in %s" %(lemmao, synset)
#                         updatereport += "<br> The new sense already existed."


#                 elif dif > 0.001:  # IF LEMMAS ARE THE SAME BUT CONF IS DIFFERENT

#                     # FETCH SOURCE TO APPEND "ntumc"
#                     curs.execute("""SELECT src FROM sense
#                                     WHERE synset=? AND lang=? AND wordid=?
#                                  """, [synset, lang, wordid_old])
#                     source = curs.fetchone()[0] # returns a tuple
#                     source = source.split(';')

#                     if "ntumc" in source:
#                         pass
#                     else:
#                         source.append("ntumc")

#                     src = ";".join(source)

#                     # UPDATE CONFIDENCE AND SOURCE
#                     curs.execute("""UPDATE sense 
#                                     SET usr=?, confidence=?, src=? 
#                                     WHERE synset=? AND lang=? AND wordid=?
#                                 """, [editor, confn, src, synset, lang, wordid_old])

#                     updatereport += """<br> confidence of lemma (%s) synset %s 
#                                        was updated: from (<del>%s</del>) to (%s)
#                                     """ %(lemmao, synset, confo, confn)

#         # CHECK FOR CHANGES IN SYNLINKS
#         if len(synlink) == len(synlinko):

#             for i, link in enumerate(synlink):
#                 slo = synlinko[i] # OLD SYNLINK
#                 lss = linkedsyn[i].strip() # NEW LINKED SYNSET
#                 lsso = linkedsyno[i] # OLD LINKED SYNSE

#                 ################################################################
#                 # CASES: DELETE SYNLINK; CHANGE SYNLINK; CHANGE LINKED SS ONLY;
#                 ################################################################

#                 if link == "delete!":

#                     # DELETE OLD ENTRY (NEED TO UPDATE THE USR FIRST)
#                     curs.execute("""UPDATE synlink SET usr=?
#                                     WHERE synset1=? AND synset2=? AND link=?
#                                     AND usr IS NOT ?
#                                  """, [editor, synset, lsso, slo, editor])

#                     curs.execute("""DELETE FROM synlink
#                                     WHERE synset1=? AND synset2=? AND link=?
#                                  """, [synset, lsso, slo])

#                     linksrep_del = u' | ' + synset + '---' + slo + '---' + lsso + u' | '

#                     if relopp[slo]:  # IF OLD SYNLINK HAD A REVERSE

#                         # DELETE OLD ENTRY (NEED TO UPDATE THE USR FIRST)
#                         curs.execute("""UPDATE synlink SET usr=?
#                                         WHERE synset1=? AND synset2=? AND link=?
#                                         AND usr IS NOT ?
#                                      """, [editor, lsso, synset, relopp[slo], editor])
#                         curs.execute("""DELETE FROM synlink
#                                         WHERE synset1=? AND synset2=? AND link=?
#                                      """, [lsso, synset, relopp[slo]])

#                         linksrep_del += u' | ' + lsso + '---' + relopp[slo] + '---' + synset + u' | '

#                     updatereport += "<br>Deleted Synlinks: <del> %s </del> " % (linksrep_del)

#                 elif link != slo:  # SYNLINK CHANGED

#                     # UPDATE OLD ENTRY
#                     curs.execute("""UPDATE synlink SET usr=?, synset2=?, link=?, src=?
#                                     WHERE synset1=? AND synset2=? AND link=?
#                                  """, [editor, lss, link, ntumc, synset, lsso, slo])

#                     linksrep_up = "<del>" + u' | ' + synset + '---' + slo + '---' + lsso + u' | ' + "</del>"
#                     linksrep_up += " >>>" + u' | ' + synset + '---' + link + '---' + lss + u' | '

#                     linksrep_del = ''
#                     linksrep_new = ''
#                     if relopp[slo]:  # IF OLD LINK HAD A REVERSE

#                         if relopp[link]:  # AND NEW LINK HAS REVERSE, UPDATE THE OLD
#                             curs.execute("""UPDATE synlink SET usr=?, synset1=?, link=?, src=?
#                                             WHERE synset1=? AND synset2=? AND link=?
#                                          """, [editor, lss, relopp[link], ntumc, 
#                                                lsso, synset, relopp[slo]])

#                             linksrep_up += "<del>" + u' | ' + lsso + '---' + relopp[slo] + '---' + synset + u' | ' + "</del>"
#                             linksrep_up += " >>>" + u' | ' + lss + '---' + relopp[link] + '---' + synset + u' | '


#                         else:  # AND NEW LINK HAS NO REVERSE, DELETE THE OLD REVERSE
#                             curs.execute("""UPDATE synlink SET usr=?
#                                             WHERE synset1=? AND synset2=? AND link=?
#                                             AND usr IS NOT ?
#                                          """, [editor, lsso, synset, relopp[slo], editor])
#                             curs.execute("""DELETE FROM synlink
#                                             WHERE synset1=? AND synset2=? AND link=?
#                                          """, [lsso, synset, relopp[slo]])
    
#                             linksrep_del += u' | ' + lsso + '---' + relopp[slo] + '---' + synset + u' | '

#                     elif relopp[link]:  # OLD LINK DOESNT HAVE REVERSE BUT NEW LINK HAS

#                         # INSERT THE NEW REVERSE LINK 
#                         curs.execute("""INSERT INTO synlink (synset1, synset2, link, usr, src) 
#                                          VALUES (?,?,?,?,?)
#                                       """, [lss, synset, relopp[link], editor, ntumc])

#                         linksrep_new += u' | ' + lss + '---' + relopp[link] + '---' + synset + u' | '


#                     updatereport += "<br>Synlinks Updated: %s " % (linksrep_up)

#                     if linksrep_del != '':
#                         updatereport += "<br>Synlinks Deleted: <del>%s</del> " % (linksrep_del)
#                     if linksrep_new != '':
#                         updatereport += "<br>Synlinks Added: %s " % (linksrep_new)


#                 elif link == slo:  # SAME SYNLINK

#                     if lsso != lss:  # AND LINKED SYNSET CHANGED

#                         # UPDATE LINKED SYNSET
#                         curs.execute("""UPDATE synlink SET usr=?, synset2=?, src=?
#                                         WHERE synset1=? AND synset2=? AND link=? 
#                                      """, [editor, lss, ntumc, synset, lsso, slo])

#                         linksrep_up = "<del>" + u' | ' + synset + '---' + slo + '---' + lsso + u' | ' + "</del>"
#                         linksrep_up += " >>>" + u' | ' + synset + '---' + link + '---' + lss + u' | '


#                         # UPDATE THE REVERSE SYNLINK, IF ANY
#                         if relopp[slo]:

#                             curs.execute("""UPDATE synlink SET usr=?, synset1=?, src=?
#                                             WHERE synset1=? AND synset2=? AND link=? """, 
#                                          [editor, lss, ntumc, lsso, synset, relopp[slo]])

#                             linksrep_up += "<del>" + u' | ' + lsso + '---' + relopp[slo] + '---' + synset + u' | ' + "</del>"
#                             linksrep_up += " >>>" + u' | ' + lss + '---' + relopp[link] + '---' + synset + u' | '

#                         updatereport += "<br> Synlinks Updated: %s" % (linksrep_up)

#                     else:  # NOTHING CHANGED
#                         continue

#     ###################################
#     # EDITMODE: NSS (Add New Synsets)
#     ###################################

#     # ONLY VALID USRS CAN EDIT WORDNET 
#     elif deleteyn == "nss" and editor in valid_usrs:
    
#         # fetch the highest synset (in the 8000 0000 range)
#         curs.execute(""" SELECT max(synset) from synset where synset like '8%' """)
#         highestss = curs.fetchone()[0]

#         ############################
#         # IF IT IS A NAMED ENTITY
#         ############################
#         # Types of NE
#         ne = ["org", "loc", "per","dat", "oth", "num"]
#         if netype in ne:

#             updatereport += """\n New Named Entity &nbsp;&nbsp;&nbsp;&nbsp; 
#                                Date: %s &nbsp;&nbsp;&nbsp;&nbsp; Editor: %s<br> 
#                             """  % (datechanged, editor)

#             # PARENT SS PER NE TYPE (to generate instances)
#             ness = ['00031264-n','00027167-n','00007846-n',
#                     '15113229-n','00001740-n','13576101-n']
#             nesynset = {}
#             for i in xrange(0, len(ne)):
#                 nesynset[ne[i]] = ness[i]

#             pos = "n"
#             link = "inst"

#             # defs are of format "ne:org/loc/per/..."
#             engdef = "ne:" + netype

#             # get a synset number
#             if highestss is None:
#                 synset = "80000000-" + pos
#             else:
#                 highest = int(highestss[0:8])
#                 synset = str(highest + 1) + '-' + pos


#             # the eng name looks for an english lemma, 
#             # if it was not provided, then uses the offset number
#             for i, ll in enumerate(lemmalangs):
#                 if ll == 'eng':
#                     engname = lemmas[i]
#                 else:
#                     engname = synset

#             engname = engname # the sqlite was rejecting other str 


#             # CREATE NEW SS
#             curs.execute("""INSERT INTO synset(synset, pos, name, src, usr) 
#                             VALUES (?,?,?,?,?)""", 
#                         [synset, pos, engname, ntumc, editor])

#             # INSERT ENGLISH DEFINITION
#             curs.execute("""INSERT INTO synset_def(synset, lang, def, sid, usr) 
#                             VALUES (?,?,?,?,?)""", 
#                          [synset, "eng", engdef, 0, editor])

#             # INSERT SYNLINKS
#             lss = nesynset[netype]  # SYNSET NUMBER PER NE TYPE
#             # "inst" LINK
#             curs.execute("""INSERT INTO synlink(synset1, synset2, link, usr) 
#                             VALUES (?,?,?,?)""", 
#                          [synset, lss, "hasi", editor])
#             # "hasi" LINK (reverse)
#             curs.execute("""INSERT INTO synlink(synset1, synset2, link, usr) 
#                             VALUES (?,?,?,?)""", 
#                          [lss, synset, "inst", editor])


#             # INSERT LEMMAS
#             # i is the index of lemmalangs to be used as the language of this lemma
#             for i, lemma in enumerate(lemmas):
#                 lang = lemmalangs[i]
#                 lemma = lemma.strip() # the sqlite was rejecting other str 

#                 # FIND IF THERE IS A WORDID
#                 curs.execute("""SELECT wordid FROM word 
#                                 WHERE lemma=? AND pos=? AND lang=?""", 
#                              [lemma, pos, lang])
#                 wordid = curs.fetchone() # returns a tuple

#                 if wordid != None: # KEEP WORDID
#                     wordid = wordid[0]
#                 else:  # OR CREATE NEW WORD + KEEP WORDID 
#                     curs.execute("""INSERT INTO word(wordid, lang, lemma, pos, usr)
#                                     VALUES (?,?,?,?,?)""", 
#                                  [None, lang, lemma, pos,  editor])
#                     wordid = curs.lastrowid
                
#                 # CREATE SENSE (link wordid to synset) 
#                 # DEFAULT CONF SCORE = 1.0
#                 curs.execute("""INSERT INTO sense(synset, wordid, lang, 
#                                                   confidence, src, usr)
#                                 VALUES (?,?,?,?,?,?)""", 
#                              [synset, wordid, lang, 1.0, ntumc, editor])

#             lemmasrep = ""  # LEMMAS REPORT
#             for i, lemma in enumerate(lemmas):
#                 lemma = lemma # the sqlite was rejecting other str 
#                 lemmasrep = lemmasrep + u' | ' + lemma + ',' + lemmalangs[i]

#             updatereport += u"""\n Synset: %s 
#                                 <br> Lemmas: %s <br> Definitions: %s 
#                                 <br> Relations: %s---%s---%s |  %s---%s---%s
#                              """ % (synset, lemmasrep, engdef, synset, 
#                                     "hasi", lss, lss, "inst", synset)


#         ###################################
#         # CREATING OTHER SYNSETS (NOT NEs)
#         ###################################
#         elif pos and engname and deflst and lemmas:

#             try:  # ACCEPTS ONLY ENGLISH NAMES USING ASCII
#                 engname
#             except UnicodeDecodeError:
#                 updatereport += """
#                  \n Failed to create a new synset. <br>
#                  The <strong>english name</strong> provided 
#                  for the synset must not contain special 
#                  characters"""
#             else:
#                 updatereport += """
#                 \n Adding New Synset &nbsp;&nbsp;&nbsp;&nbsp; 
#                 Date: %s &nbsp;&nbsp;&nbsp;&nbsp; Editor: %s<br> 
#                 """  % (datechanged, editor)

#                 if highestss is None:
#                     synset = "80000000-" + pos
#                 else:
#                     highest = int(highestss[0:8])
#                     synset = str(highest + 1) + '-' + pos

#                 # CREATE NEW SYNSET
#                 curs.execute("""INSERT INTO synset(synset, pos, name, 
#                                                    src, usr)
#                                 VALUES (?,?,?,?,?)""", 
#                              [synset, pos, engname, ntumc, editor])

#                 # INSERT DEFINITIONS
#                 for i, d in enumerate(deflst): # d = each definition
#                     dlang = deflangs[i] # match the language of each

#                     d = d # the sqlite was rejecting other str 
#                     d = d.strip(u' .,;:!?')

#                     # insert data of the new definition
#                     curs.execute("""INSERT INTO synset_def(synset, lang, def, sid, usr) 
#                                     VALUES (?,?,?,?,?) """,  
#                                  [synset, dlang, d, i, editor])


#                 # IF THERE ARE NEW EXAMPLES
#                 if len(eglst) != 0:

#                     for i, e in enumerate(eglst):
#                         e = e.strip()
#                         e = e.strip(u' .,;:!?。；：！')
#                         elang = eglangs[i]  # MATCH LANGUAGE PER EXAMPLE

#                         # FETCH THE HIGHEST SID (MAY FAIL)
#                         curs.execute("""
#                             SELECT max(sid) 
#                             FROM synset_ex 
#                             WHERE synset LIKE '%s' 
#                             """ % synset)
#                         try: # TRY ADDING 1
#                             sid = int(curs.fetchone()[0]) + 1
#                         except: # ELSE THERE WERE NO EXAMPLES
#                             sid = 0

#                         # INSERT NEW EXAMPLES
#                         curs.execute("""
#                             INSERT INTO synset_ex(synset, lang, def, 
#                                                   sid, usr) 
#                             VALUES (?,?,?,?,?)""", 
#                             [synset, elang, e, sid, editor])


#                 # INSERT SYNLINKS
#                 for i, link in enumerate(synlink):
#                     lss = linkedsyn[i].strip()

#                     curs.execute("""INSERT INTO synlink(synset1, synset2, link, usr)
#                                     VALUES (?,?,?,?)""", 
#                                  [synset, lss, link, editor])

#                     # SYNLINK INVERSE
#                     if relopp[link]:
#                         curs.execute("""INSERT INTO synlink(synset1, synset2, link, usr)
#                                         VALUES (?,?,?,?)""",
#                                      [lss, synset, relopp[link], editor])


#                 # INSERT LEMMAS
#                 for i, lemma in enumerate(lemmas):
#                     lang = lemmalangs[i]  # MATCH LANG PER LEMMA
#                     lemma = lemma.strip()

#                     # FIND IF THERE IS A WORDID
#                     curs.execute("""SELECT wordid 
#                                     FROM word 
#                                     WHERE lemma=? AND pos=? AND lang=? """, 
#                                  [lemma, pos, lang])
#                     wordid = curs.fetchone() # returns a tuple

#                     if wordid != None: # KEEP WORDID
#                         wordid = wordid[0]
#                     else:  # OR CREATE NEW WORD + KEEP WORDID
#                         curs.execute("""INSERT INTO word(wordid, lang, lemma, pos, usr) 
#                                         VALUES (?,?,?,?,?)""", 
#                                      [None, lang, lemma, pos, editor])
#                         wordid = curs.lastrowid

#                     # CREATE SENSE (link wordid to synset) 
#                     # DEFAULT CONF SCORE = 1.0
#                     curs.execute("""INSERT INTO sense(synset, wordid, lang, 
#                                                       confidence, src, usr)
#                                     VALUES (?,?,?,?,?,?)""", 
#                                  [synset, wordid, lang, 1.0, ntumc, editor])

#                 lemmasrep = ""
#                 for i, lemma in enumerate(lemmas):
#                     lemma = lemma
#                     lemmasrep = lemmasrep + u' | ' + lemma + ',' + lemmalangs[i]

#                 defsrep = ""
#                 for i, d in enumerate(deflst):
#                     d = d # the sqlite was rejecting other str 
#                     defsrep = defsrep + u' | ' + d + ',' + deflangs[i]

#                 egsrep = ""
#                 for i, d in enumerate(eglst):
#                     d = d # the sqlite was rejecting other str 
#                     egsrep = egsrep + u' | ' + d + ',' + eglangs[i]


#                 updatereport += """\n Synset: %s <br> Lemmas: %s <br> 
#                                     Definitions: %s <br> 
#                                     Examples: %s <br> 
#                                     Relations: %s --- %s --- %s (and inverses)
#                                 """ % (synset, lemmasrep, defsrep, egsrep, synset, synlink, linkedsyn)

#     ##############################
#     # IF EDITOR NOT IN VALID USRS 
#     ##############################
#     elif editor not in valid_usrs:
#         updatereport += """<b>Nothing Happened!!! USERNAME IS NOT VALID!"""

#     else:
#         updatereport += """<b>Nothing Happened!!! REPORT THIS!"""


#     ######################
#     # PRINTS LOG TO FILE
#     ######################
#     if updatereport != "<hr>":
#         notelog.write(' ---------- ' + updatereport + '\n')
#         notelog.close()


#     ##################
#     # CLOSES FILES/DB
#     ##################
#     errlog.close()
#     conn.commit()
#     conn.close()

#     # PRINT HTML-LOG
#     print """Content-type: text/html; charset=utf-8 \n\n
#             <html>
#               <head>
#                 <meta http-equiv='Content-Type' content='text/html; 
#                       charset=utf-8'>
#                   <title>Open Multilingual Wordnet Editor</title>
#               </head>
#               <body bgcolor="#F5F5F5">
#                   %s
#               </body>
#             </html>
#           """ % (updatereport)

# ##########################
# # IF SOMETHING WENT WRONG
# ##########################
# except:

#     # OPEN CGI_ERR.LOG
#     errlog = codecs.open('cgi_err.log', 'a+', "utf-8")

#     errtime = '--- '+ time.ctime(time.time()) +' ---\n'
#     errlog.write("\n"+errtime)
#     traceback.print_exc(None, errlog)
#     errlog.close()

#     print """Content-type: text/html; charset=utf-8 \n\n
#                 <html>
#                   <head>
#                     <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
#                       <title>Open Multilingual Wordnet Editor</title>
#                   </head>
#                   <body bgcolor="#F5F5F5">
#                       <b>CGI Error, please report to the mantainers.</b>
#                       <br> %s
#                   </body>
#                 </html>
#           """ % traceback.format_exc(None)
