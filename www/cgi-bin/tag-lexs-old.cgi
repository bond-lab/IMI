#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi, urllib, Cookie, os
import cgitb; cgitb.enable()  # for troubleshooting
import re, sqlite3, collections
from collections import defaultdict as dd
from ntumc_util import *
from ntumc_webkit import *
from lang_data_toolkit import *
import time

wnnam = "Open Multilingual Wordnet"
wnver = "1.0"
wnurl = "http://compling.hss.ntu.edu.sg/omw/index.html"

form = cgi.FieldStorage()

version = form.getfirst("version", "0.1")
usrname_cgi = form.getvalue("usrname_cgi")

#synset = form.getfirst("synset", "")
lemma = form.getfirst("lemma", "")
lemma = lemma.strip()

lang = form.getfirst("lang", "cmn")
corpus = form.getfirst("corpus", "cmn")
# jilog(">>> corpus = %s" % corpus)
ss = form.getfirst("ss", "")
lim = int(form.getfirst("lim", 499))
sfcorpus = form.getfirst("sfcorpus", "")
#log=open('log.txt', 'w')  codecs.open


### reference to self (.cgi)
wncgi = "tag-lexs.cgi"

### working wordnet.db 
wndb = "../db/wn-ntumc.db"

### working corpus.db
corpusdb = "../db/cmn.db"

### reference to wn-grid (search .cgi)
omwcgi = "wn-gridx.cgi"

valid_usernames = ['fcbond','lmorgado','letuananh','wangshan','rosechen',
                   'tanzhixin','seayujie','honxuemin','wangwenjie',
                   'lewxuhong','yuehuiting','eshleygao']

# Checks for a username cookie and assigns it to usrname
user_cookie = NTUMC_Cookies.read_user_cookie(usrname_cgi)
usrname = user_cookie['user_name'].value



###
### If you set a word with multiple concepts to a real tag
### then set any other untagged concepts to 'x' (don't tag)
###
set_others_x="""
UPDATE concept SET tag='x', usrname=? 
WHERE ROWID=(
    SELECT b.ROWID 
    FROM cwl AS a INNER JOIN cwl AS b ON a.sid=b.sid AND a.wid=b.wid 
    LEFT JOIN concept AS acon ON a.sid=acon.sid and a.cid=acon.cid
    LEFT JOIN concept AS bcon ON b.sid=bcon.sid and b.cid=bcon.cid
    WHERE a.sid=? and a.cid=? and acon.tag not in ('x', 'e') AND bcon.tag IS NULL
)"""

lems = list(expandlem(lemma))
lms = ",".join("'%s'" % l  for l in lems)

### process the tags
if corpus:
    db_path = '../db/%s.db' % corpus
    con = sqlite3.connect(db_path)
    jilog("I'm connecting to %s" % db_path)
    c = con.cursor()
    cids = form.getfirst("cids", '')
    dtag = form.getfirst("cid_all", None)
    dntag = form.getfirst("ntag_all", None)
    dcom = form.getfirst("com_all", None)
    addme = form.getfirst("addme", "")
    addme = addme.strip()
    tgs = dd(lambda: [None, None]) 

    print (u"ERROR: %s" % unicode(cids))
    
    for cd in cids.split(' '): ### prefer local ntag
        if not cd:
            continue
        cdparts = cd.split('|')
        sid = int(cdparts[0])
        cid = int(cdparts[1])
        tag =  form.getfirst("cid_%d_%d" % (sid, cid), None)
        jilog('im here - tag=%s' % tag)
        com =  form.getfirst("com_%d_%d" % (sid, cid), None)
        if com:
            com = com.strip()
        ntag = form.getfirst("ntag_%d_%d" % (sid, cid), None)
        
        if tag: ### then local tag
            c.execute("update concept set tag=?, usrname=? where tag IS NOT ? and sid=? and cid=?", (tag, usrname, tag, sid, cid))
            c.execute(set_others_x, (usrname, sid, cid,))
            jilog('im here tag=%s - sid=%s - cid=%s' % (tag, sid, cid))
        elif dtag: ### then default tag
            #log.write("dtag\n")
            c.execute("update concept set tag=?, usrname=? where sid=? and cid=?", (dtag, usrname, sid, cid))
            c.execute(set_others_x, (sid, cid,))
            jilog('ntag - sid=%s - cid=%s' % (sid, cid))
        ### don't do anything otherwise
        ### always update the comment
        c.execute("update concept set comment=?, usrname=? where comment IS NOT ? and sid=? and cid=?", (com, usrname, com, sid, cid))
    if addme:
        ### add this as a concept
        ls = re.split(ur' |_|∥', addme)
        c.execute("select distinct sid from word where lemma like ? or word like ?", ('%s' % ls[0],ls[0]))
        sids = ",".join(str(s[0]) for s in c.fetchall())
        ##print sids
        if sids:
            sents = dd(lambda:dd(list))
            c.execute("select sid, wid, word, lemma from word where sid in (%s) order by sid, wid" % sids) 
            for (sid, wid, word, lem) in c:
                sents[sid][wid] = (word,lem)
                #print word
            matches = dd(list)
            for sid in sents:
                matched = []
                sentlength=len(sents[sid])
                for i in sents[sid]:
                    if sents[sid][i][0] == ls[0] or sents[sid][i][1] == ls[0]:
                        matched = [i]
                        ### matched first word
                        for j in range(1,len(ls)):  ## no skip for now
                            if i+j < sentlength and ls[j] in sents[sid][i+j]:
                                matched.append(i+j) 
                        if len(matched) == len(ls):
                            matches[sid].append(matched)
            for sid in matches:
                for wids in matches[sid]:
                    ###
                    ### Add the concept
                    ###
                    c.execute("select max(cid) from concept where sid = ?", (int(sid),))
                    (maxcid,) = c.fetchone()
                    newcid = maxcid + 1
                    c.execute("INSERT INTO concept(sid, cid, tag, clemma, comment, usrname) VALUES (?,?,?,?,?,?)",
                              (sid, newcid, None, addme, None, usrname))
                    for wid in wids:
                        c.execute("""INSERT INTO cwl(sid, wid, cid, usrname) 
                                     VALUES (?,?,?,?)""",
                                  (sid, wid, newcid, usrname))


    con.commit()

### Connect to the wn database
wn = sqlite3.connect(wndb)
w = wn.cursor()

com_all=''
w.execute("""SELECT distinct synset 
             FROM word LEFT JOIN sense ON word.wordid = sense.wordid 
             WHERE lemma in (%s) AND sense.lang = ? and sense.status is not 'old'
             ORDER BY freq DESC""" % ','.join('?'*len(lems)), (lems + [lang]))
rows = w.fetchall()
#print(unicode(lms) + ' - ' + unicode(lang))
if not rows and lang != 'eng':
    w.execute("""SELECT distinct synset
                 FROM word LEFT JOIN sense ON word.wordid = sense.wordid 
                 WHERE lemma in (%s) AND sense.lang = ? and sense.status is not 'old'
                 ORDER BY freq DESC""" % ','.join('?'*len(lems)), (lems + ['eng']))
    rows = w.fetchall()
    com_all='FW:eng'
sss = sorted([s[0] for s in rows], key=lambda x: x[-1])  ### sort by POS
ss = " ".join(sss)
lmss = "\\".join("%s" % l  for l in lems)



########## HTML

### Checked User Cookie (above), and now prints it ('unknown' will be de default) 
print(user_cookie)

### Header
print(u"""Content-type: text/html; charset=utf-8\n""")

# empty lines so that the browser knows that the header is over
print ""
print ""
print(u"""<html>
  <head>
    <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
    <link href="../tag-wn.css" rel="stylesheet" type="text/css">
    <script src="../tag-wn.js" language="javascript"></script>
    <script src='../jquery.js' language='javascript'></script>
    <script src='../js/scrolltotop.js' language='javascript'></script>
    <script src='../js/showex.js' language='javascript'></script>
    <script>
       $( document ).ready(page_init);
    </script>


    <script type="text/javascript">

    function sizeFrame(framename) {
        var F = document.getElementById(framename);
        F.height = 0;
        if(F.contentDocument) {
            F.height = F.contentDocument.documentElement.scrollHeight+30; //FF 3.0.11, Opera 9.63, and Chrome
            if (F.height > 900) {
                F.height = 900;
            }
        } else {
            F.height = F.contentWindow.document.body.scrollHeight+30; //IE6, IE7 and Chrome
            if (F.height > 900) {
                F.height = 900;
            }
        }
    }

    function resizeAllFrames(){
        var frames2resize = ["tag-lexiframe", "logiframe","omwiframe"];
        for (i = 0; i < frames2resize.length; i++) {
        var framename = frames2resize[i];
        // alert(framename);
        sizeFrame(framename);
        }
    }

    // document.onload = alert("Before calling resizeAllFrames()");
    document.onload = resizeAllFrames(); 
    </script>


    <title>NTUMC Annotation Tool %s</title>
 </head>
 <body>

 """ % version )


# ; padding:15px;
print("""<table style="width:100%;">
<tr>
  <td valign="top" style="width:50%">""")
 
print("""</td> <td align="right" style="width:50%">""")

### USER COOKIE
try:
    usrname = user_cookie['user_name'].value

    if usrname in valid_usernames:
        pass

    else:
        print("""<strong>NTUMC Annotation Tools</strong>""")
        print """<br><strong>A valid user has not been defined or it has expired.</strong><br>"""
        print """Please choose a valid username to continue!"""
        print """<form method = post action = "%s"> username:<input type ="text" name="usrname_cgi"> 
                 <input type = "submit" value = "Change"> </form> """ % wncgi

except KeyError:
    print("""<strong>NTUMC Annotation Tools</strong>""")
    print """<br><strong>I couldn't find a username in the cookie!</strong><br>"""
    print """Please choose a valid username to continue!"""
    print """<form method = post action = "%s"> username:<input type ="text" name="usrname_cgi"> 
                 <input type = "submit" value = "Change"> </form> """ % wncgi


print(""" </td> </tr>""") # closes first row 

# No Username No Page!
if usrname not in valid_usernames:
    print("""</td> <td style="width:55%"> <br><br> </td> </tr> </table>""") # closes first row 

else:
    # Print user status
    print """<tr>""" + HTML.show_change_user_bttn(usrname)

    print("""<td valign="top" style="width:55%; border-right: 1px solid black">""") # second row
    print("""<iframe name="tagging" src="%s?corpus=%s&lemma=%s&ss=%s&lang=%s&lim=%d&com_all=%s&lmss=%s&sfcorpus=%s&usrname=%s"
              frameborder="0" width="100%%" id="tag-lexiframe" onload="resizeAllFrames()"></iframe>
          """ % (tagcgi, corpus, lemma, ss, lang, lim, com_all, lmss, sfcorpus, usrname))

    print("""</td>""") # closes first column of second row


    print(""" <td valign="top" style="width:45%%"> <table style="width:100%%"><tr><td>
    <iframe name="wn" id="omwiframe" src="%s?ss=%s&lang=%s&lemma=%s&usrname=%s&gridmode=ntumcgrid" frameborder="0" 
     width="100%%" onload="resizeAllFrames()" ></iframe></td></tr>
         """ % (omwcgi, ss, lang, lemma, usrname))


    print("""<tr> 
             <td valign="top" style="width:45%"><hr>
             <iframe name="log" id="logiframe" frameborder="0"
              width="100%" onload="resizeAllFrames()" ></iframe>
             </td></tr></table>
             </td></tr></table>""")


### Footer
print """<span style="text-align:right;">
         <p><a href='%s'>More detail about the %s (%s)</a>
      """ % (wnurl, wnnam, wnver)

print """<p>Maintainer: <a href="http://www3.ntu.edu.sg/home/fcbond/">Francis Bond</a>
         &lt;<a href="mailto:bond@ieee.org">bond@ieee.org</a>&gt;</span>"""

print "  </body>"
print "</html>"
