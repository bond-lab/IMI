#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import re, sqlite3, datetime, time, re, itertools, traceback
import os
import http.cookies # cookies

from lang_data_toolkit import *
from lang_data_toolkit import valid_usernames as valid_usrs

# Fixes encoding issues when reading cookies from os.environ
import os, sys
from importlib import reload
sys.getfilesystemencoding = lambda: 'utf-8'
reload(os)

# wndb_path = "../db/wn-ntumc.db"

# stamp with NTUMC corpus (e.g. used to stamp new synsets)
ntumc = "ntumc" 

redirect_synset = ""


################################################################################
# MASTER COOKIE (LANGS)
################################################################################
if 'HTTP_COOKIE' in os.environ:
    C = http.cookies.SimpleCookie(os.environ['HTTP_COOKIE'])
else:
    C = http.cookies.SimpleCookie()

if "UserID" in C:
    usrname = C["UserID"].value
    hashed_pw = C["Password"].value
else:
    usrname = "guest"
    hashed_pw = "guest"
editor = usrname
################################################################################


try:
    # Get data from html form fields
    form = cgi.FieldStorage()

    wndb = form.getvalue("wndb", "wn-ntumc")
    wndb_path =  "../db/{}.db".format(wndb)

    synset = form.getvalue('synset')

    # this can be "add" (add new lemmas, ex, defs, ..), 
    # "mod" (modify) or "nss" (new synset), defines the editing mode
    deleteyn = form.getvalue('deleteyn')

    # info needed for nss (new synset)
    engname = form.getvalue('engname', "")

    pos = form.getvalue('pos')

    synlink = form.getlist('synlink[]')
    linkedsyn = form.getlist('linkedsyn[]')
    synlinko = form.getlist('synlinko[]')   # old
    linkedsyno = form.getlist('linkedsyno[]')   # old

    engdef = form.getvalue('engdef')
    lang = form.getvalue('lang')

    netype = form.getvalue('netype')


    # lemmas and lemmalangs are two lists that are co-referenced with the same index
    # (e.g. lemmas[0] is a lemma in the language lemmalangs[0])
    lemmas = form.getlist('lemmalst[]')
    lemmalangs = form.getlist('lemmalangs[]')


    # These are used both to edit and to create a new synset

    comlst = form.getlist('comlst[]')


    deflst = form.getlist('deflst[]')
    deflangs = form.getlist('deflangs[]')

    eglst = form.getlist('eglst[]')
    eglangs = form.getlist('eglangs[]')


    # Extra data needed to edit the entries
    lemmaos = form.getlist('lemmao[]') # lemma old
    lemmans = form.getlist('lemman[]') # lemma new

    confos = form.getlist('confo[]') # confidence old 
    confns = form.getlist('confn[]') # confidence new

    defos = form.getlist('defo[]') # definition old
    defns = form.getlist('defn[]') # definition new
    defelangs = form.getlist('defelangs[]') # definitions(edited) langs

    exeos = form.getlist('exeo[]')
    exens = form.getlist('exen[]')
    exeelangs = form.getlist('exeelangs[]') # examples(edited) langs 




    # TO EDIT A SYNSET, WE HAVE NOW A SINGLE FORM 
    # (FOR ALL LANGUAGES AT THE SAME TIME)
    edit_lemma_langs = form.getlist('edit_lemma_langs[]')
    edit_defs_langs = form.getlist('edit_defs_langs[]')
    edit_exe_langs = form.getlist('edit_exe_langs[]')

    # TO EDIT SYNSET NAME
    ss_name_old = form.getfirst('ss_name_old')
    ss_name_new = form.getfirst('ss_name_new')




    # dict to hold the relation oposites
    # relations are inserted with their oposites 
    # (e.g if X is hypo of Y, then Y is hype of X ) 
    relopp = {}
    for x in range(0, len(synlinks)):
        relopp[synlinks[x]] = synlinksopp[x]
    

    # Connects to wn-ntumc.db (edited version with datechanged, 
    # status and editor fields on most tables)
    conn = sqlite3.connect(wndb_path)
    curs = conn.cursor()

    # this is a placeholder for changes made (will print lines to the log)
    updatereport = ""

    # create the log (in case the file was not there before)
    notelog = open('addss_error.log', 'a+', encoding='utf-8')
    
    # create the error log for the cgi errors
    errlog = open('cgi_err.log', 'a+', encoding="utf-8")

    # time stamp
    datechanged = datetime.datetime.now().strftime('%Y-%m-%d.%H:%M:%S')
    


    #######################################################################################
    # EDIT MODEs: "add" (add info to synsets), "mod" (modify synsets) or "nss" (new synset)
    #######################################################################################

    #######################################
    # EDIT MODE: ADD (add info to synsets)
    #######################################
    if deleteyn == "add" and editor in valid_usrs:

        status = "new"
        redirect_synset = synset 

        updatereport += """\n Appending to Synset &nbsp;&nbsp;&nbsp;&nbsp; 
                              Date: %s &nbsp;&nbsp;&nbsp;&nbsp; Editor: %s<br> 
                        """  % (datechanged, editor)




        ###############################
        # INSERT NEW COMMENTS
        ###############################
        if len(comlst) != 0:
            msg = ''

            for com in comlst:
                com = com

                # INSERT NEW COMMENTS
                curs.execute("""INSERT INTO synset_comment
                                (synset, comment, u) 
                                VALUES (?,?,?) """,  
                             [synset, com, editor])

            updatereport += """Added comments to synset: %s<br>
                            """ % (synset)
        ###############################




        ###############################
        # IF THERE ARE NEW DEFINITIONS
        ###############################
        if len(deflst) != 0:
            
            defsrep = ""  # REPORT
            defscounter = 0
            for i, d in enumerate(deflst):
                d = d
                d = d.strip(u' .,;:!?。；：！')
                dlang = deflangs[i] # MATCH LANG PER DEF

                # FETCH THE HIGHEST SID (THERE IS ALWAYS SOMETHING TO RETURN)
                curs.execute(""" SELECT max(sid) from synset_def where synset like ? """, [synset])
                sid = int(curs.fetchone()[0]) + 1 # NEW SID is +1 to highest

                # INSERT NEW DEFINITONS
                curs.execute("""INSERT INTO synset_def(synset, lang, def, sid, usr) 
                                VALUES (?,?,?,?,?) """,  
                             [synset, dlang, d, sid, editor])

                defsrep += u' | ' + deflangs[i] + ':' + d
                defscounter = i +1

            updatereport += """\n Added <strong>%s</strong> definitions to synset: %s <br>
                               Definitions: %s <br>""" % (str(defscounter), synset, defsrep)





        # IF THERE ARE NEW EXAMPLES
        if len(eglst) != 0:

            egsrep = ""
            egscounter = 0
            for i, e in enumerate(eglst):
                e = e.strip()
                e = e.strip(u' .,;:!?。；：！')
                elang = eglangs[i]  # MATCH LANGUAGE PER EXAMPLE

                # FETCH THE HIGHEST SID (MAY FAIL)
                curs.execute("""SELECT max(sid) 
                                FROM synset_ex 
                                WHERE synset LIKE ? 
                             """, [synset])
                try: # TRY ADDING 1 
                    sid = int(curs.fetchone()[0]) + 1
                except: # ELSE THERE WERE NO EXAMPLES
                    sid = 0

                # insert data of the new example
                curs.execute("""INSERT INTO synset_ex(synset, lang, def, sid, usr) 
                                VALUES (?,?,?,?,?) """, 
                             [synset, elang, e, sid, editor])

                egsrep += u' | ' + eglangs[i] + ':' + e
                egscounter = i +1

            updatereport += """\n Added <strong>%s</strong> examples to synset: %s <br>
                               Examples: %s <br>""" % (str(egscounter), synset, egsrep)


        # IF THERE ARE NEW LEMMAS
        if len(lemmas) != 0:
            pos = synset[-1]

            lemmasrep = ""
            lemmascounter = 0
            for i, lemma in enumerate(lemmas):
                lang = lemmalangs[i] # match each lemma language
                lemma = lemma.strip() # the sqlite was rejecting other str 
                
                # CHECK IF WORDID EXISTS
                curs.execute("""SELECT wordid FROM word 
                                WHERE lemma=? 
                                AND pos=? AND lang=? """, 
                             [lemma, pos, lang])
                wordid = curs.fetchone() # returns a tuple

                if wordid != None: # KEEP WORDID
                    wordid = wordid[0]
                else:  # OR INSERT WORD + KEEP WORDID
                    curs.execute("""INSERT INTO word(wordid, lang, lemma, pos, usr) 
                                    VALUES (?,?,?,?,?)""", 
                                 [None, lang, lemma, pos, editor])
                    wordid = curs.lastrowid

                # CHECK THAT SENSE DOESN'T EXIST
                curs.execute("""SELECT wordid, synset, lang 
                                FROM sense
                                WHERE wordid=? 
                                AND synset=? AND lang=? 
                             """, [wordid, synset, lang])
                previouslemma = curs.fetchone() # returns a tuple

                if previouslemma == None:  # IF NO PREVIOUS LEMMA

                    # link wordid to synset sense, confidence of created synsets is 1.0
                    curs.execute("""INSERT INTO sense(synset, wordid, lang, confidence, src, usr)
                                    VALUES (?,?,?,?,?,?)""", 
                                 [synset, wordid, lang, 1.0, ntumc, editor])

                lemmascounter = i + 1
                lemmasrep +=  u' | ' +  lemmalangs[i] + ':' + lemma

            updatereport += """\n Added <strong>%s</strong> lemmas to synset: %s <br>
                               Lemmas: %s <br>""" % (str(lemmascounter), synset, lemmasrep)


        # IF THERE ARE NEW SYNLINKS
        if len(linkedsyn) != 0:
            linksrep = ""
            linkscounter = 0

            for i, link in enumerate(synlink):
                lss = linkedsyn[i].strip()

                # CHECK THAT SYNLINK DOESN'T EXIST
                curs.execute("""SELECT synset1, synset2 
                                FROM synlink
                                WHERE synset1=? 
                                AND synset2=? AND link=? 
                             """, [synset, lss, link])
                previoussynlink = curs.fetchone() # returns a tuple

                if previoussynlink == None:  # IF NO PREVIOUS SYNLINK, INSERT IT
                    curs.execute("""INSERT INTO synlink(synset1, synset2, link, usr) 
                                    VALUES (?,?,?,?)""", 
                                 [synset, lss, link, editor])


                if relopp[link]:
                    # CHECK THAT REVERSE_SYNLINK DOESN'T EXIST
                    curs.execute("""SELECT synset1, synset2 
                                    FROM synlink
                                    WHERE synset1=? 
                                    AND synset2=? AND link=? 
                                 """, [lss, synset, relopp[link]])
                    previoussynlink_rev = curs.fetchone() # returns a tuple

                    if previoussynlink_rev == None:  # IF NO PREVIOUS REVERSE_SYNLINK, INSERT IT
                        curs.execute("""INSERT INTO synlink(synset1, synset2, link, usr) 
                                        VALUES (?,?,?,?)""", 
                                     [lss, synset, relopp[link], editor])

                linkscounter = i + 1
                linksrep +=  u' | ' + synset + '---' + link + '---' + lss

            updatereport += """\n Added <strong>%s</strong> relations (and their inverses) to synset: %s <br>
                               Relations: %s <br>""" % (str(linkscounter), synset, linksrep)


    ############################################################################
    # EDIT MODE: MOD (editing or deleting previous entries)
    ############################################################################
    elif deleteyn == "mod" and editor in valid_usrs:

        redirect_synset = synset 
        updatereport += " %s was edited by %s: "  % (synset, editor)

        ########################################################################
        # CHECK FOR CHANGES TO THE SYNSET NAME
        ########################################################################
        try:
            ss_name_old = ss_name_old.strip()
            ss_name_new = ss_name_new.strip()                    
        except:
            pass
        if ss_name_old != ss_name_new and len(ss_name_new) > 0: # UPDATE ENTRY

            curs.execute("""UPDATE synset
                            SET usr=?, name=?
                            WHERE synset=?""", [editor, ss_name_new, synset])

            updatereport += """name updated (<del>%s</del> > %s); 
                            """ % (ss_name_old, ss_name_new)
        ########################################################################





        ########################################################################
        # CHECK FOR CHANGES TO COMMENTS
        ########################################################################
        comsnlst = form.getlist('comsn[]') # new comments
        comsolst = form.getlist('comso[]') # olds comments
        com_u_o = form.getlist('com_u_o[]') # comm user old
        com_t_o = form.getlist('com_t_o[]') # comm time old

        update = """UPDATE synset_comment
                    SET comment=?, u=?, t=CURRENT_TIMESTAMP
                    WHERE synset=? AND comment=? AND u=? AND t=? """

        pre_del = """UPDATE synset_comment SET u=?
                     WHERE synset=? AND comment=? AND u=? AND t=? """

        delete = """DELETE FROM synset_comment
                    WHERE synset=? AND comment=? AND u=? AND t=? """

        if len(comsnlst) == len(comsolst):
            for i, com in enumerate(comsnlst):
                com = com.strip()
                com_old = comsolst[i].strip()
                u_old = com_u_o[i]
                t_old = com_t_o[i]

                if com == com_old:
                    continue

                elif com == "!!!delete!!!": # DELETE
                    curs.execute(pre_del,[editor, synset, com_old, 
                                          u_old, t_old])

                    curs.execute(delete,[synset, com_old, u_old, t_old])

                    updatereport += """<br>Comment deleted 
                    (<del>%s</del>);""" % (com_old)

                else: # UPDATE

                    curs.execute(update,[com, editor, synset, 
                                         com_old, u_old, t_old])

                    updatereport += """<br>Comment updated 
                    (<del>%s</del> > %s);""" % (com_old, com)
        ########################################################################




        ########################################################################
        # CHECK FOR CHANGES TO LEMMAS
        # edit_lemma_langs = a list of languages per lemma
        # lemmaos = a list of lemmas that were previous in db
        # lemmans = a list of lemmas submitted (possibly edited)
        ########################################################################
        if len(lemmaos) == len(lemmans):
            pos = synset[-1]

            for i, (lemmao, lemman, lemma_lang) in enumerate(zip(lemmaos, 
                                                lemmans, edit_lemma_langs)):
                confo = confos[i]
                confn = confns[i]
                dif = abs(float(confo) - float(confn))
                lemmao = lemmao.strip()
                lemman = lemman.strip()                    

                # FETCH OLD WORDID (MUST EXIST)
                curs.execute("""SELECT wordid FROM word 
                                WHERE lemma=? AND pos=? AND lang=? 
                             """, [lemmao, pos, lemma_lang])
                wordid_old = curs.fetchone()[0] # returns a tuple


                if lemman == "delete!":  # DELETE
                    
                    # NEED TO UPDATE THE USR FIRST
                    curs.execute("""UPDATE sense SET usr=?
                                    WHERE synset=? AND lang=? AND wordid=?
                                    AND usr IS NOT ?
                                 """, [editor, synset, lemma_lang, 
                                       wordid_old, editor])
                    curs.execute("""DELETE FROM sense 
                                    WHERE synset=? AND lang=? AND wordid=?
                                 """, [synset, lemma_lang, wordid_old])

                    updatereport += "sense deleted (<del>%s</del>); " % (lemmao)

                elif lemmao != lemman:  # IF LEMMAS WERE DIFFERENT

                    # CHECK IF NEW WORD EXISTS (FOR WORDID)
                    curs.execute("""SELECT wordid FROM word
                                    WHERE lemma=? AND pos=? AND lang=?
                                 """, [lemman, pos, lemma_lang])
                    wordid_new = curs.fetchone() # returns a tuple

                    if wordid_new != None: # EXISTED
                        wordid_new = wordid_new[0]

                    else:  # ELSE, CREATE NEW WORD
                        curs.execute("""INSERT INTO word(wordid, lang, lemma, 
                                                         pos, usr) 
                                        VALUES (?,?,?,?,?)""", 
                                     [None, lemma_lang, lemman, pos, editor])
                        wordid_new = curs.lastrowid

                        updatereport += """new lemma added to '%s' (%s, %s);
                                        """ % (lemma_lang, lemman, pos)

                    # VERIFY IF SENSE ALREADY EXISTED
                    curs.execute("""SELECT wordid, synset, lang
                                    FROM sense
                                    WHERE wordid=? AND synset=? AND lang=?
                                 """, [wordid_new, synset, lemma_lang])

                    # IF NO PREVIOUS SENSE, INSERT NEW (CONF=1.0)
                    if not curs.fetchone(): 

                        # UPDATE OLD ENTRY
                        curs.execute("""UPDATE sense 
                                        SET usr=?, wordid=?, confidence=?, src=?
                                        WHERE synset=? AND lang=? AND wordid=?
                                     """, [editor, wordid_new, 1.0, ntumc, 
                                           synset, lemma_lang, wordid_old])

                        updatereport += """changed sense (<del>%s</del> > %s);
                                        """ % (lemmao, lemman)

                    else:
                        # DELETE OLD ENTRY (NEED TO UPDATE THE USR FIRST)
                        curs.execute("""UPDATE sense SET usr=?
                                        WHERE synset=? AND lang=? AND wordid=?
                                        AND usr IS NOT ?
                                     """, [editor, synset, lemma_lang, 
                                           wordid_old, editor])
                        curs.execute("""DELETE FROM sense 
                                        WHERE synset=? AND lang=? AND wordid=?
                                     """, [synset, lemma_lang, wordid_old])
                        
                        updatereport += "new sense already existed, old "
                        updatereport += """sense deleted (<del>%s</del>); 
                                        """ % (lemmao)

                # IF LEMMAS ARE THE SAME BUT CONF IS DIFFERENT
                elif dif > 0.001:  

                    # FETCH SOURCE TO APPEND "ntumc"
                    curs.execute("""SELECT src FROM sense
                                    WHERE synset=? AND lang=? AND wordid=?
                                 """, [synset, lemma_lang, wordid_old])
                    source = curs.fetchone()[0] # returns a tuple
                    source = source.split(';')

                    if "ntumc" in source:
                        pass
                    else:
                        source.append("ntumc")

                    src = ";".join(source)

                    # UPDATE CONFIDENCE AND SOURCE
                    curs.execute("""UPDATE sense
                                    SET usr=?, confidence=?, src=?
                                    WHERE synset=? AND lang=? AND wordid=?
                                """, [editor, confn, src, synset,
                                      lemma_lang, wordid_old])

                    updatereport += """the confidence of (%s) was updated: 
                                       (<del>%s</del> > %s);
                                    """ %(lemmao, confo, confn)
        ########################################################################



        ########################################################################
        # CHECK FOR CHANGES TO DEFINITIONS
        ########################################################################
        if len(defos) == len(defns):

            defsrep = ""  # string to print report
            for i, (defo, defn, def_lang) in enumerate(zip(defos, defns, 
                                                           edit_defs_langs)): 

                defo = defo # SQL 
                defn = defn # SQL 
                defo = defo.strip(u' .,;:?。；：')
                defn = defn.strip(u' .,;:?。；：')

                if defn == "delete!":  # IF "delete!", DELETE

                    # DELETE OLD ENTRY (NEED TO UPDATE THE USR FIRST)
                    curs.execute("""UPDATE synset_def SET usr=? 
                                    WHERE synset=? AND lang=? AND def=?
                                    AND usr IS NOT ?
                                 """, [editor, synset, def_lang, defo, editor])
                    curs.execute("""DELETE FROM synset_def 
                                    WHERE synset=? AND lang=? AND def=?
                                 """, [synset, def_lang, defo])

                    updatereport += """definition deleted (<del>%s</del>); 
                                    """ % (defo)


                elif defo != defn:  # IF THERE IS A CHANGE

                    curs.execute("""UPDATE synset_def SET usr=?, def=? 
                                    WHERE synset=? AND lang=? AND def=?
                                 """, [editor, defn, synset, def_lang, defo])

                    updatereport += """definition edited (<del>%s</del> > %s);
                                    """ % (defo, defn)
        ########################################################################



        ########################################################################
        # CHECK FOR CHANGES TO EXAMPLES
        ########################################################################
        if len(exeos) == len(exens):

            egsrep = ""  # string to print report
            for i, (exeo, exen, exe_lang) in enumerate(zip(exeos, exens, 
                                                           edit_exe_langs)):

                exeo = exeo # SQL
                exen = exen # SQL
                exeo = exeo.strip(u' .,;:?。；：')
                exen = exen.strip(u' .,;:?。；：')

                if exen == "delete!":  # IF "delete!", DELETE

                    # DELETE OLD ENTRY (NEED TO UPDATE THE USR FIRST)
                    curs.execute("""UPDATE synset_ex SET usr=?
                                    WHERE synset=? AND lang=? AND def=?
                                    AND usr IS NOT ?
                                 """, [editor, synset, exe_lang, exeo, editor])
                    curs.execute("""DELETE FROM synset_ex
                                    WHERE synset=? AND lang=? AND def=?
                                 """, [synset, exe_lang, exeo])
                    
                    updatereport += """example deleted (<del>%s</del>); 
                                    """ % (exeo)

                elif exeo != exen:  # IF THERE IS A CHANGE

                    # UPDATE OLD ENTRY (NEED TO UPDATE THE USR FIRST)
                    curs.execute("""UPDATE synset_ex SET usr=?, def=?
                                    WHERE synset=? AND lang=? AND def=?
                                 """, [editor, exen, synset, exe_lang, exeo])
 
                    updatereport += """example edited (<del>%s</del> > %s);
                                    """ % (exeo, exen)
        ########################################################################



        ########################################################################
        # CHECK FOR CHANGES IN SYNLINKS
        ########################################################################
        if len(synlink) == len(synlinko):

            for i, link in enumerate(synlink):
                slo = synlinko[i] # OLD SYNLINK
                lss = linkedsyn[i].strip() # NEW LINKED SYNSET
                lsso = linkedsyno[i] # OLD LINKED SYNSE

                ################################################################
                # CASES: DELETE SYNLINK; CHANGE SYNLINK; CHANGE LINKED SS ONLY;
                ################################################################

                if link == "delete!":

                    # NEED TO UPDATE THE USR FIRST
                    curs.execute("""UPDATE synlink SET usr=?
                                    WHERE synset1=? AND synset2=? AND link=?
                                    AND usr IS NOT ?
                                 """, [editor, synset, lsso, slo, editor])

                    curs.execute("""DELETE FROM synlink
                                    WHERE synset1=? AND synset2=? AND link=?
                                 """, [synset, lsso, slo])

                    updatereport += """synlink deleted (<del>%s:%s:%s</del>); 
                                    """ % (synset,slo, lsso)



                    if relopp[slo]:  # IF OLD SYNLINK HAD A REVERSE

                        # DELETE OLD ENTRY (NEED TO UPDATE THE USR FIRST)
                        curs.execute("""UPDATE synlink SET usr=?
                                        WHERE synset1=? AND synset2=? AND link=?
                                        AND usr IS NOT ?
                                     """, [editor, lsso, synset, 
                                           relopp[slo], editor])
                        curs.execute("""DELETE FROM synlink
                                        WHERE synset1=? AND synset2=? AND link=?
                                     """, [lsso, synset, relopp[slo]])


                        updatereport += """synlink deleted (<del>%s:%s:%s</del>); 
                                        """ % (lsso, relopp[slo], synset)

                elif link != slo:  # SYNLINK CHANGED

                    # UPDATE OLD ENTRY
                    curs.execute("""UPDATE synlink 
                                    SET usr=?, synset2=?, link=?, src=?
                                    WHERE synset1=? AND synset2=? AND link=?
                                 """, [editor, lss, link, ntumc, 
                                       synset, lsso, slo])

                    updatereport += """synlink changed (<del>%s:%s:%s</del> > 
                                       %s:%s:%s); 
                                    """ % (synset, slo, lsso, 
                                           synset, link, lss)


                    if relopp[slo]:  # IF OLD LINK HAD A REVERSE

                        if relopp[link]:  # AND NEW LINK HAS REVERSE, UPDATE THE OLD
                            curs.execute("""UPDATE synlink SET usr=?, synset1=?, link=?, src=?
                                            WHERE synset1=? AND synset2=? AND link=?
                                         """, [editor, lss, relopp[link], ntumc, 
                                               lsso, synset, relopp[slo]])

                            updatereport += """synlink changed (<del>%s:%s:%s</del> > 
                                               %s:%s:%s); 
                                            """ % (lsso, relopp[slo], synset,
                                                   lss, relopp[link], synset)



                        else:  # AND NEW LINK HAS NO REVERSE, DELETE THE OLD REVERSE
                            curs.execute("""UPDATE synlink SET usr=?
                                            WHERE synset1=? AND synset2=? AND link=?
                                            AND usr IS NOT ?
                                         """, [editor, lsso, synset, relopp[slo], editor])
                            curs.execute("""DELETE FROM synlink
                                            WHERE synset1=? AND synset2=? AND link=?
                                         """, [lsso, synset, relopp[slo]])
    
                            updatereport += """synlink deleted (<del>%s:%s:%s</del>); 
                                            """ % (lsso, relopp[slo], synset)



                    elif relopp[link]:  # OLD LINK DOESNT HAVE REVERSE BUT NEW LINK HAS

                        # INSERT THE NEW REVERSE LINK 
                        curs.execute("""INSERT INTO synlink (synset1, synset2, link, usr, src) 
                                         VALUES (?,?,?,?,?)
                                      """, [lss, synset, relopp[link], editor, ntumc])

                        updatereport += """synlink added (%s:%s:%s); 
                                            """ % (lss, relopp[link], synset)



                elif link == slo:  # SAME SYNLINK

                    if lsso != lss:  # AND LINKED SYNSET CHANGED

                        # UPDATE LINKED SYNSET
                        curs.execute("""UPDATE synlink SET usr=?, synset2=?, src=?
                                        WHERE synset1=? AND synset2=? AND link=? 
                                     """, [editor, lss, ntumc, synset, lsso, slo])

                        updatereport += """synlink changed (<del>%s:%s:%s</del> > 
                                           %s:%s:%s); 
                                        """ % (synset, slo, lsso, 
                                               synset, link, lss)


                        # UPDATE THE REVERSE SYNLINK, IF ANY
                        if relopp[slo]:

                            curs.execute("""UPDATE synlink SET usr=?, synset1=?, src=?
                                            WHERE synset1=? AND synset2=? AND link=? """, 
                                         [editor, lss, ntumc, lsso, synset, relopp[slo]])


                            updatereport += """synlink changed (<del>%s:%s:%s</del> > 
                                               %s:%s:%s); 
                                            """ % (lsso, relopp[slo], synset,
                                                   lss, relopp[link], synset)

                    else:  # NOTHING CHANGED
                        continue


        if updatereport == " %s was edited by %s: "  % (synset, editor):
            updatereport += "Nothing was changed."


    ############################################################################
    # EDITMODE: NSS (Add New Synsets) = NAMED ENTITIES + OTHER SYNSETS
    ############################################################################
    elif deleteyn == "nss" and editor in valid_usrs:
    
        # FETCH HIGHEST SYNSET (80000000 range)
        curs.execute("""SELECT max(synset) 
                        FROM synset
                        WHERE synset LIKE '8%' """)
        highestss = curs.fetchone()[0]

        ########################################################################
        # IF IT IS A NAMED ENTITY:
        # ss definition = ne:type (org/loc/per/...)
        # ss name = english lemma (if there is one), else: synset offset
        ########################################################################
        ne = ["org", "loc", "per","dat", "oth", "num", "fch"]
        if netype in ne:

            # PARENT SS PER NE TYPE (to generate instances)
            ness = ['00031264-n','00027167-n','00007846-n',
                    '15113229-n','00001740-n','13576101-n', '09587565-n']
            nesynset = {}
            for i in range(0, len(ne)):
                nesynset[ne[i]] = ness[i]

            pos = "n"
            link = "inst"
            engdef = "ne:" + netype

            # NEW SYNSET (POS = 'n')
            if highestss is None:
                synset = "80000000-" + pos
            else:
                highest = int(highestss[0:8])
                synset = str(highest + 1) + '-' + pos
            redirect_synset = synset 

            # the eng name looks for an english lemma, 
            # if it was not provided, then uses the offset number
            for i, ll in enumerate(lemmalangs):
                if ll == 'eng':
                    engname = lemmas[i]
                else:
                    engname = synset

            engname = engname.strip() # SQL

            # CREATE NEW SS
            curs.execute("""INSERT INTO synset(synset, pos, name, src, usr) 
                            VALUES (?,?,?,?,?)""", 
                        [synset, pos, engname, ntumc, editor])

            # INSERT ENGLISH DEFINITION
            curs.execute("""INSERT INTO synset_def(synset, lang, def, sid, usr) 
                            VALUES (?,?,?,?,?)""", 
                         [synset, "eng", engdef, 0, editor])

            # INSERT SYNLINKS
            lss = nesynset[netype]  # SYNSET NUMBER PER NE TYPE
            # "inst" LINK
            curs.execute("""INSERT INTO synlink(synset1, synset2, link, usr) 
                            VALUES (?,?,?,?)""", 
                         [synset, lss, "hasi", editor])
            # "hasi" LINK (reverse)
            curs.execute("""INSERT INTO synlink(synset1, synset2, link, usr) 
                            VALUES (?,?,?,?)""", 
                         [lss, synset, "inst", editor])


            # INSERT LEMMAS
            # i is the index of lemmalangs to be used as the language of this lemma
            for i, lemma in enumerate(lemmas):
                lang = lemmalangs[i]
                lemma = lemma.strip() # the sqlite was rejecting other str 

                # FIND IF THERE IS A WORDID
                curs.execute("""SELECT wordid FROM word 
                                WHERE lemma=? AND pos=? AND lang=?""", 
                             [lemma, pos, lang])
                wordid = curs.fetchone() # returns a tuple

                if wordid != None: # KEEP WORDID
                    wordid = wordid[0]
                else:  # OR CREATE NEW WORD + KEEP WORDID 
                    curs.execute("""INSERT INTO word(wordid, lang, lemma, pos, usr)
                                    VALUES (?,?,?,?,?)""", 
                                 [None, lang, lemma, pos,  editor])
                    wordid = curs.lastrowid
                
                # CREATE SENSE (link wordid to synset) 
                # DEFAULT CONF SCORE = 1.0
                curs.execute("""INSERT INTO sense(synset, wordid, lang, 
                                                  confidence, src, usr)
                                VALUES (?,?,?,?,?,?)""", 
                             [synset, wordid, lang, 1.0, ntumc, editor])

            lemmasrep = ""  # LEMMAS REPORT
            for i, lemma in enumerate(lemmas):
                lemma = lemma # the sqlite was rejecting other str 
                lemmasrep = lemmasrep + u' | ' + lemma + ',' + lemmalangs[i]


            updatereport += """<b>New Named Entity created by %s</b>; """  % (editor)
            updatereport += u"""Synset: %s; Lemmas: %s; Definitions: %s;  
                                Relations: %s---%s---%s |  %s---%s---%s
                             """ % (synset, lemmasrep, engdef, synset, 
                                    "hasi", lss, lss, "inst", synset)



        ########################################################################
        # IF IT WAS NOT A NAMED ENTITY:
        ########################################################################
        elif pos and engname and deflst and lemmas:
            
            engname = engname.strip() # SQL

            if highestss is None:
                synset = "80000000-" + pos
            else:
                highest = int(highestss[0:8])
                synset = str(highest + 1) + '-' + pos
            redirect_synset = synset 

            # CREATE NEW SYNSET
            curs.execute("""INSERT INTO synset(synset, pos, name, src, usr)
                            VALUES (?,?,?,?,?)""", 
                         [synset, pos, engname, ntumc, editor])

            # INSERT DEFINITIONS
            for i, d in enumerate(deflst): # d = each definition
                dlang = deflangs[i] # match the language of each

                d = d # SQL 
                d = d.strip(u' .,;:!?。；：！')

                # INSERT DEFINITION
                curs.execute("""INSERT INTO synset_def(synset, lang, def, 
                                                       sid, usr) 
                                VALUES (?,?,?,?,?) """,
                             [synset, dlang, d, i, editor])


            # INSERT (IF THERE ARE ANY) EXAMPLES
            if len(eglst) != 0:

                for i, e in enumerate(eglst):
                    e = e.strip()
                    e = e.strip(u' .,;:!?。；：！')
                    elang = eglangs[i]  # MATCH LANGUAGE PER EXAMPLE

                    # FETCH THE HIGHEST SID (MAY FAIL)
                    curs.execute("""SELECT max(sid) 
                                    FROM synset_ex 
                                    WHERE synset LIKE ? """, [synset])
                    try: # TRY ADDING 1
                        sid = int(curs.fetchone()[0]) + 1
                    except: # ELSE THERE WERE NO EXAMPLES
                        sid = 0

                    curs.execute("""INSERT INTO synset_ex(synset, lang, def,
                                                           sid, usr) 
                                    VALUES (?,?,?,?,?)""", 
                                 [synset, elang, e, sid, editor])


            # INSERT SYNLINKS
            for i, link in enumerate(synlink):
                lss = linkedsyn[i].strip()

                curs.execute("""INSERT INTO synlink(synset1, synset2, link, usr)
                                VALUES (?,?,?,?)""", 
                             [synset, lss, link, editor])

                # SYNLINK INVERSE
                if relopp[link]:
                    curs.execute("""INSERT INTO synlink(synset1, synset2, link, usr)
                                    VALUES (?,?,?,?)""",
                                 [lss, synset, relopp[link], editor])


            # INSERT LEMMAS
            for i, lemma in enumerate(lemmas):
                lang = lemmalangs[i]  # MATCH LANG PER LEMMA
                lemma = lemma.strip()

                # FIND IF THERE IS A WORDID
                curs.execute("""SELECT wordid 
                                FROM word 
                                WHERE lemma=? AND pos=? AND lang=? """, 
                             [lemma, pos, lang])
                wordid = curs.fetchone() # returns a tuple

                if wordid != None: # KEEP WORDID
                    wordid = wordid[0]
                else:  # OR CREATE NEW WORD + KEEP WORDID
                    curs.execute("""INSERT INTO word(wordid, lang, lemma, pos, usr) 
                                    VALUES (?,?,?,?,?)""", 
                                 [None, lang, lemma, pos, editor])
                    wordid = curs.lastrowid

                # CREATE SENSE (link wordid to synset) 
                # DEFAULT CONF SCORE = 1.0
                curs.execute("""INSERT INTO sense(synset, wordid, lang, 
                                                  confidence, src, usr)
                                VALUES (?,?,?,?,?,?)""", 
                             [synset, wordid, lang, 1.0, ntumc, editor])


            lemmasrep = ""
            for i, lemma in enumerate(lemmas):
                lemma = lemma
                lemmasrep = lemmasrep + u' | ' + lemma + ',' + lemmalangs[i]

            defsrep = ""
            for i, d in enumerate(deflst):
                d = d # the sqlite was rejecting other str 
                defsrep = defsrep + u' | ' + d + ',' + deflangs[i]

            egsrep = ""
            for i, d in enumerate(eglst):
                d = d # the sqlite was rejecting other str 
                egsrep = egsrep + u' | ' + d + ',' + eglangs[i]

            updatereport += """<b>New synset created by %s</b>; """  % (editor)
            updatereport += u"""Synset: %s; Lemmas: %s; Definitions: %s;  
                                Relations: %s---%s---%s  (and inverses);
                                Examples %s;
                             """ % (synset, lemmasrep, defsrep, 
                                    synset, synlink, linkedsyn, egsrep)



    ##############################
    # IF EDITOR NOT IN VALID USRS 
    ##############################
    elif editor not in valid_usrs:
        updatereport += """<b>Nothing Happened!!! USERNAME IS NOT VALID! %s""" % editor

    else:
        updatereport += """<b>Nothing Happened!!! REPORT THIS!"""


    ######################
    # PRINTS LOG TO FILE
    ######################
    if updatereport != "":
        notelog.write(' ---------- ' + updatereport + '\n')
        notelog.close()


    ##################
    # CLOSES FILES/DB
    ##################
    errlog.close()
    conn.commit()
    conn.close()

    # PRINT HTML-LOG
    print("""Content-type: text/html; charset=utf-8 \n\n
            <html>
              <head>
                <meta http-equiv='Content-Type' content='text/html; 
                      charset=utf-8'>
                  <title>Open Multilingual Wordnet Editor</title>
              </head>""")

    print("""<body onload="document.redirect.submit()">
             <form name="redirect" action="wn-gridx.cgi"  method="post" target="wn">
             <input type="hidden" name="lemma" value="%s"/>
             <input type="hidden" name="gridmode" value="ntumcgrid"/>
             </form>
             </body>""" % (redirect_synset))

    print("""<span style="font-size:70%%">%s</span>
             </body>
             </html> """ % (updatereport))


##########################
# IF SOMETHING WENT WRONG
##########################
except:

    # OPEN CGI_ERR.LOG
    errlog = open('cgi_err.log', 'a+', encoding="utf-8")
    errtime = '--- '+ time.ctime(time.time()) +' ---\n'
    errlog.write("\n"+errtime)
    traceback.print_exc(None, errlog)
    errlog.close()
    print("""Content-type: text/html; charset=utf-8 \n\n
            <html>
              <head>
                <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
                  <title>Open Multilingual Wordnet Editor</title>
              </head>
              <body bgcolor="#F5F5F5">
                  <b>CGI Error, please report to the maintainers.</b>
                  <br> %s
              </body>
            </html>
          """ % traceback.format_exc(None))
