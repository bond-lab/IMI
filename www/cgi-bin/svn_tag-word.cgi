#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi, urllib, http.cookies, os
import cgitb; cgitb.enable()  # for troubleshooting
import re, sqlite3, collections
from collections import defaultdict as dd
from collections import OrderedDict as od
from ntumc_util import *
from ntumc_webkit import *
from lang_data_toolkit import *
import time

cgiself = "tag-word.cgi"
wnnam = "Open Multilingual Wordnet"
wnver = "1.0"
wnurl = "http://compling.hss.ntu.edu.sg/omw/index.html"
wndb="../db/wn-ntumc.db"

form = cgi.FieldStorage()

version = form.getfirst("version", "0.1")
usrname_cgi = form.getvalue("usrname_cgi")

#synset = form.getfirst("synset", "")
lemma = form.getfirst("lemma", "")
lemma = lemma.strip()

usrname = form.getfirst("usrname", "unknown")
gridmode = form.getfirst("gridmode", "ntumc-noedit")

lang = form.getfirst("lang", "cmn")
corpus = form.getfirst("corpus", "cmn")
# jilog(">>> corpus = %s" % corpus)
#ss = form.getfirst("ss", "")
lim = int(form.getfirst("lim", 499))
sfcorpus = form.getfirst("sfcorpus", "")
tsid = int(form.getfirst("sid", 10000)) #default to sentence 1000
twid = int(form.getfirst("wid", 0)) #default to first word
window = int(form.getfirst("window", 4)) #default context of four sentences
if window > 200:
    window = 200
#log=open('log.txt', 'w')  codecs.open


# Look for the username cookie (if it can't find, it will use 'unknown' as default)
user_cookie = NTUMC_Cookies.read_user_cookie(usrname_cgi)
usrname = user_cookie['user_name'].value


###
### Process tags
###
con = sqlite3.connect("../db/%s.db" % corpus) ###
c = con.cursor()

# def process_tags(c):
#     cids = form.getfirst("cids", '')
#     for cd in cids.split(' '): ### prefer local ntag
#         if not cd:
#             continue
#         print cd
#         cdparts = cd.split('|')
#         sid = int(cdparts[0])
#         cid = int(cdparts[1])
#         tag =  form.getfirst("cid_%s" % (cd,), None)
#         com =  form.getfirst("com_%s" % (cd,), None)
#         c.execute("""UPDATE concept SET tag=?, usrname=? 
#                    WHERE tag IS NOT ? 
#                    AND sid=? and cid=?""", 
#                   (tag, usrname, tag, sid, cid))

#         set_rest_x(c, usrname, sid, cid)

#         c.execute("""UPDATE concept SET comment=?, usrname=? 
#                    WHERE comment IS NOT ? 
#                    AND sid=? AND cid=?""", 
#                   (com, usrname, com, sid, cid))
#         print tag, com
#         con.commit()
#         ### FIXME --- log; add usrname; show in log window


def tag_head(ver,typ):
    return u"""<html>
  <head>
    <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
    <link href="../common.css" rel="stylesheet" type="text/css">
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
        var frames2resize = ["omwiframe", "logiframe"];
        for (i = 0; i < frames2resize.length; i++) {
        var framename = frames2resize[i];
        // alert(framename);
        sizeFrame(framename);
        }
    }

    // document.onload = alert("Before calling resizeAllFrames()");
    document.onload = resizeAllFrames(); 
    </script>
    <title>NTUMC Annotation Tool (%s: %s)</title>
 </head>
 <body>
<script type="text/javascript">
$(document).ready(function() {
$(".c60639_21").on('mouseover', function() {
  $(".c60639_21").addClass("match");
});

$(".c60639_21").on('mouseout', function() {
  $(".c60639_21").removeClass("match");
});
});
</script>
 """ % (ver, typ)
### FIXME do fo everything

########## HTML

### The cookie was created above; needs to be printed before html
### ('unknown' will be de default usrname) 
print(user_cookie)

print(u"""Content-type: text/html; charset=utf-8\n\n""")
#print valid_usernames

try:
    usrname = user_cookie['user_name'].value

    if usrname in valid_usernames:
        pass

    else:
        print("""<strong>NTUMC Annotation Tools</strong>""")
        print("""<br>Welcome %s!</strong><br>""" % usrname)
        print("""<br><strong>A valid user has not been defined.</strong><br>""")
        print("""Please choose a valid username to continue!""")
        print("""<form method = post action = "%s"> username:<input type ="text" name="usrname_cgi"> 
                 <input type = "submit" value = "Change"> </form> """ % cgiself)

except KeyError:
    print("""<strong>NTUMC Annotation Tools</strong>""")
    print("""<br><strong>A valid user has not been defined or it has expired.</strong><br>""")
    print("""Please choose a valid username to continue!""")
    print("""<form method = post action = "%s"> username:<input type ="text" name="usrname_cgi"> 
                 <input type = "submit" value = "Change"> </form> """ % cgiself)


wn = sqlite3.connect(wndb)
w = wn.cursor()

    
### get the words
wds = dd(lambda: dd(tuple))
query = """
    SELECT sid, wid, word, pos, lemma  FROM word 
    WHERE sid IN (
        SELECT DISTINCT sid 
        FROM word WHERE sid > ? limit ?) 
    ORDER BY sid, wid"""
c.execute(query,  (tsid - window, 2 * window -1))
for (sid, wid, word, pos, lemma) in c:
    wds[int(sid)][int(wid)] = (word, pos, lemma)
tword = wds[tsid][twid][0]  ### target word
twp = pos2wn(wds[tsid][twid][1],lang) ### target wn pos
tlemma = wds[tsid][twid][2] ### target lemma
if tlemma ==  wds[tsid][twid][0]:
    html =  """<h3>Tagging %s (%d:%d %s)</h3>""" % (tlemma,sid,wid,corpus)
else: ## word !=lemma
    html =  """<h3>Tagging %s (%d:%d %s --- %s)</h3>""" % (tlemma,sid,wid,corpus,
                                                               wds[tsid][twid][0])

    ### get the concepts
query = """
    SELECT cwl.sid, cwl.wid,  cwl.cid, clemma, tag, tags, comment 
    FROM cwl 
    LEFT JOIN concept ON concept.sid =cwl.sid AND concept.cid=cwl.cid
    WHERE cwl.sid in (%s)""" % placeholders_for(wds.keys())
c.execute(query, wds.keys())
tags = dd(lambda: dd(dict))
for (sid, wid, cid, clemma, tag, tgs, comment) in c:
    ##print "<BR>", sid, wid, cid, clemma, tag, tgs, comment
    tags[int(sid)][int(wid)][int(cid)] = (clemma, tag, tgs, comment)
tsss=''
tcid=0
clem=''
#print "<br>tags", tags[tsid][twid].keys(), tags[tsid][twid].keys()[0], tags[tsid][twid][4]
if tags[tsid][twid]:
    tcid = tags[tsid][twid].keys()[0]
    clem = tags[tsid][twid][tcid][0]
    tsss= ' '.join(lem2ss(w, clem,lang))
### FIXME screwing up tagging

def show_sents(c, tsid, twid):
    
    if tlemma ==  tword:
        html =  """<h3>Tagging %s (%d:%d %s)</h3>""" % (tlemma,tsid,
                                                        twid,corpus)
    else: ## word !=lemma
        html =  """<h3>Tagging %s (%d:%d %s --- %s)</h3>""" % (tlemma,tsid,
                                                               twid,corpus,
                                                               tword)
    ### go through each sentence    
    for sid in sorted(wds.keys()):
        html += "<div lang='zh'>"  #fixme dynamicly according to lang
        html += "%s&nbsp;&nbsp;&nbsp" % \
            HTML.show_sid_bttn(corpus, sid, tlemma)
        for wid in sorted(wds[sid].keys()):
            cids = ['c%s_%s' % (sid,cd) for cd in tags[sid][wid]]
            # sid:wid:pos:lemma
            title= cgi.escape("%d:%d:%s:%s" % (sid, wid, 
                                               wds[sid][wid][1], wds[sid][wid][2]))
            ## selected word
            word = wds[sid][wid][0]
            clss = ' '.join(['tagme'] + cids)
            if sid == tsid and wid==twid:
                html += "<span class='%s' title='%s'>%s</span> " % (clss, 
                                                                  title, word)
            ## needs to be tagged
            elif any(tags[sid][wid][cid][1] == None for cid in tags[sid][wid]):
                clss = ' '.join(['notag'] + cids)
                
                html += """\
<a href = '%s?gridmode=%s&corpus=%s&lang=%s&sid=%s&wid=%s' 
   target='_parent' title='%s' class='%s'>%s</a>
""" %(cgiself, gridmode, corpus, lang, sid, wid,  title, clss,word)
            ## tagged
            elif tags[sid][wid]:
                for cid in tags[sid][wid]:
                    if tags[sid][wid][cid][3]: ## has a comment
                        title +='&#013;%s: %s (%s)' % (tags[sid][wid][cid][0],
                                                       tags[sid][wid][cid][1],
                                                       tags[sid][wid][cid][3])
                    else:
                        title +='&#013;%s: %s' % (tags[sid][wid][cid][0],
                                                  tags[sid][wid][cid][1])
                    ## fixme look up synset name and definition
                if all(tags[sid][wid][cid][1] == 'x' 
                       for cid in tags[sid][wid]):
                    clss = ' '.join(['ignore'] + cids)
                elif any(tags[sid][wid][cid][1] == 'w' 
                         for cid in tags[sid][wid]):
                    clss = ' '.join(['missing'] + cids)
                elif any(tags[sid][wid][cid][1] == 'e' 
                         for cid in tags[sid][wid]):
                    clss = ' '.join(['error'] + cids)
                else:
                    clss = ' '.join(['hastag'] + cids)
                    
                html += """\
<a href = '%s?gridmode=%s&corpus=%s&lang=%s&sid=%s&wid=%s' 
   target='_parent' title='%s' class='%s'>%s</a>
""" %(cgiself, gridmode, corpus, lang, sid, wid, title, clss,word)
            ## function word: FIXME --- allow you to tag it anyway              
            else:
                html += "<span title='%s'>%s</span> " % (title, word)
        html += "</div>\n"
    ###
    ### show the tagboxs
    ###
    ## Start the form
    html += """\
<form name='tag' method="get" action="%s" target='log'
onsubmit="setTimeout('parent.location.reload()',500); return true;" >
<input type='hidden' name='corpus' value='%s'>
<input type='hidden' name='lang' value='%s'>
<input type='hidden' name='lemma' value='%s'>
<input type='hidden' name='sid' value='%d'>
<input type='hidden' name='wid' value='%d'>
<input type='hidden' name='cids' value='%s'>
<input type='hidden' name='usrname' value='%s'>
""" % ('edit-corpus.cgi',  corpus, lang, tlemma, 
           tsid, twid, ' '.join(["%d|%d" % (tsid, c) for c in tags[tsid][twid]]),
           usrname)
    
    for cid in tags[tsid][twid]:
        if tags[tsid][twid][cid]:
            clem = tags[tsid][twid][cid][0]
            ss = lem2ss(w, clem, lang)
            sss= ' '.join(ss)
            html += """\
<br><a href='wn-gridx.cgi?gridmode=%s&lang=%s&ss=%s&lemma=%s&usrname=%s' 
 class='match' target='wn'>%s</a>&nbsp;&nbsp;""" % (gridmode,lang, sss, 
                                                    clem, usrname, clem)
        ##print 'ss', ss, wds[tsid][twid][1],  pos2wn(wds[tsid][twid][1], lang)
        ### fixme: back off to English
        ##print tags[tsid][twid][cid]
            html += tbox(ss, "%d|%d" % (tsid,cid), pos2wn(wds[tsid][twid][1], lang), 
                         tags[tsid][twid][cid][1], '',   #tag, ntag
                         tags[tsid][twid][cid][3])       #comment
    html += """\
<div align='right'><input type="submit" name="Query" value="tag"></div></form> """

    return html

def tag_word(corpus, sid, wid):
    searchbox = """<table>
<tr><td>
<form name ='input' method='get' action='tag-word.cgi' target='_parent'>
<input type='hidden' name='corpus' value='%s'>
<input type='hidden' name='lang' value='%s'>
<input type='hidden' name='gridmode' value='%s'>
Goto sid: <input type='text' name='sid' value='%d' size=6/>
</form></td>
<td><form name ='input' method='get' action='tag-lexs.cgi' target='_blank'>
<input type='hidden' name='corpus' value='%s'>
<input type='hidden' name='lang' value='%s'>
<input type='hidden' name='gridmode' value='%s'>
Lookup word: <input type='text' name='lemma' placeholder='lemma' value='%s' size=12/>
</form></tr></table>
<span style='float: right;'><a target='_blank' href='../tagdoc.html'>Documentation</a></span>
</p>""" % (corpus, lang, gridmode, sid, 
           ## second form (lemma)
           corpus, lang, gridmode, tlemma)
     
    return  """%s<br><hr>%s""" % (show_sents(c, tsid, twid), searchbox,)





###
### Main
###

# Header
print(tag_head(version,'sequential'))
#taglog= process_tags(c)
# No Username No Page!
if usrname not in valid_usernames:
    print("""</td> <td style="width:55%"> Invalid Username<br><br> </td> </tr> </table>""") # closes first row 
##
## single word tagging is in here; wn-gridx is an iframe
##
else:

    # Print user status
    print("""<tr>""" + HTML.show_change_user_bttn(usrname, cgiself))

    print( u""" <table style="width:100%%"> 
    <tr> <td valign="top" style="width:55%%; 
             border-right: 1px solid black">%s</td>

         <td valign="top" style="width:45%%">
         <table style="width:100%%">
           <tr> <td valign="top" style="width:45%%"> 
           <iframe name="wn" id="omwiframe" 
               src="%s?usrname=%s&lang=%s&ss=%s&lemma=%s&pos=%s&gridmode=%s" 
               frameborder="0" width="100%%"
               onload="resizeAllFrames()">wordnet
           </iframe></td></tr>
           <tr> <td> <hr>
           <iframe name="log" id="logiframe" frameborder="0"
                   width="100%%" onload="resizeAllFrames()">
           </iframe> </td> </tr>
         </table>
     </tr>
   </table>
"""% (tag_word(corpus, tsid, twid), 
      wncgi, usrname, lang, tsss, tlemma, twp, gridmode))

print("  </body>")
print("</html>")

 
