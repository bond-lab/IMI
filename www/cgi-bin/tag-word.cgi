#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi, urllib, http.cookies, os
import cgitb; cgitb.enable()  # for troubleshooting
import re, sqlite3, collections
from collections import defaultdict as dd
from ntumc_util import taglcgi, wndb, wncgi, check_corpusdb, all_corpusdb
from ntumc_util import  expandlem, lem2ss, pos2wn,  tbox, Timer
from ntumc_webkit import HTML, wnnam, wnver, wnurl
from lang_data_toolkit import valid_usernames, pos_tags
from ntumc_gatekeeper import concurs, placeholders_for
from html import escape

# Fixes encoding issues when reading cookies from os.environ
import os, sys
from importlib import reload
sys.getfilesystemencoding = lambda: 'utf-8'
reload(os)

################################################################################
# CGI FIELD STORAGE & CONSTANTS
################################################################################
cgiself = "tag-word.cgi"
wndb="wn-ntumc" # NOT "../db/wn-ntumc.db"

form = cgi.FieldStorage()
version = form.getfirst("version", "0.1")
lemma = form.getfirst("lemma", "")
lemma = lemma.strip()
gridmode = form.getfirst("gridmode", "ntumc-noedit")

#lang = form.getfirst("lang", "cmn")
corpus = form.getfirst("corpus", "cmn")
corpus = form.getfirst("corpus", "cmn")
(dbexists, dbversion, dbmaster, dblang, dbpath) = check_corpusdb(corpus)
if not dbexists:
    print("""Content-type: text/html; charset=utf-8\n\n""")
    print (f"""<html>
<body>No such corpus: <strong>{corpus}</strong>, try again</body>
</html>""")
    quit()
else:    
    lang = dblang


tsid = int(form.getfirst("sid", 10000)) #default to sentence 1000
twid = int(form.getfirst("wid", 0)) #default to first word

window = int(form.getfirst("window", 4)) #default context of four sentences
if window > 200:
    window = 200

textSize = form.getfirst("textSize", '120%')

################################################################################


################################################################################
# MASTER COOKIE
################################################################################
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
################################################################################


################################################################################
# CONNECT TO DATABASES
################################################################################
conn, c = concurs(corpus, dbpath)
wn, w = concurs(wndb, dbpath)


# GET WORDS
wds = dd(lambda: dd(tuple))
query="""SELECT sid, wid, word, pos, lemma  
         FROM word 
         WHERE sid IN (SELECT DISTINCT sid 
                       FROM word WHERE sid > ? limit ?) 
         ORDER BY sid, wid"""
c.execute(query,  (tsid - window, 2 * window -1))

for (sid, wid, word, pos, lemma) in c:
    wds[int(sid)][int(wid)] = (word, pos, lemma)

if twid == 0:
    twid = min(wds[tsid])
tword = wds[tsid][twid][0]  ### target word
twp = pos2wn(wds[tsid][twid][1],lang) ### target wn pos
tlemma = wds[tsid][twid][2] ### target lemma

if tlemma ==  wds[tsid][twid][0]:
    html =  """<h3>Tagging %s (%d:%d %s)</h3>""" % (tlemma,sid,wid,corpus)
else: ## word !=lemma
    html =  "<h3>Tagging %s " % (tlemma)
    html += """(%d:%d %s --- %s)</h3>""" % (sid,wid,corpus,
                                            escape(wds[tsid][twid][0]))

# GET CONCEPTS
query = """SELECT cwl.sid, cwl.wid,  cwl.cid, clemma, tag, tags, comment 
           FROM cwl 
           LEFT JOIN concept 
           ON concept.sid =cwl.sid AND concept.cid=cwl.cid
           WHERE cwl.sid in (%s)""" % placeholders_for(wds.keys())
c.execute(query, list(wds.keys()))

tags = dd(lambda: dd(dict))
for (sid, wid, cid, clemma, tag, tgs, comment) in c:
    ##print "<BR>", sid, wid, cid, clemma, tag, tgs, comment
    tags[int(sid)][int(wid)][int(cid)] = (clemma, tag, tgs, comment)
tsss=''
tcid=0
clem=''
#print "<br>tags", tags[tsid][twid].keys(), tags[tsid][twid].keys()[0], tags[tsid][twid][4]
if tags[tsid][twid]:
    tcid = list(tags[tsid][twid].keys())[0]
    clem = tags[tsid][twid][tcid][0]
    tsss= ' '.join(lem2ss(w, clem,lang))
### FIXME screwing up tagging






try:
    # GET SENTIMENT SCORES
    query = """SELECT sentiment.sid, sentiment.cid, sentiment.score 
           FROM sentiment
           WHERE sentiment.sid in (%s)
           """ % placeholders_for(wds.keys())
    c.execute(query, list(wds.keys()))

    # sentiment = {sid: {cid :  score}} 
    sentiment = dd(lambda: dd(int))
    for (sid, cid, score) in c:
        sentiment[int(sid)][int(cid)] = score
except:
    sentiment = dd(lambda: dd(int))



################################################################################



################################################################################
# HTML FUNCTIONAL BLOCKS
################################################################################
def tag_head(ver,typ):
    return """<html>
  <head>
    <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
    <link href="../common.css" rel="stylesheet" type="text/css">
    <link href="../tag-wn.css" rel="stylesheet" type="text/css">
    <script src="../tag-wn.js" language="javascript"></script>
    <script src='../jquery.js' language='javascript'></script>


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

    <!-- KICKSTART -->
    <script src="../HTML-KickStart-master/js/kickstart.js"></script>
    <link rel="stylesheet" href="../HTML-KickStart-master/css/kickstart.css" 
     media="all" /> 

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

 <style>
  hr{
    padding: 0px;
    margin: 5px;    
  }
 </style>

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



  <script>  // THIS SNIPPET IS USED TO CHECK KEYS PRESSED
  window.addEventListener("keydown", keysPressed, false);
  window.addEventListener("keyup", keysReleased, false);
  var keys = [];
  function keysPressed(e) {
      // store an entry for every key pressed
      keys[e.keyCode] = true;

      // Sentiment 1
      if (keys[90] && keys[49]) {
          // alert("1 was pressed");
          var x = document.getElementsByName("senti_score");
          for (var i = 0; i < x.length; i++) {
             x[i].value = -95;
          }
          var forms = document.getElementsByName("senti_score_form");
          for (var i = 0; i < forms.length; i++) {
             forms[i].submit();
          }
      }

      // Sentiment 2
      if (keys[90] && keys[50]) {
          // alert("2 was pressed");
          var x = document.getElementsByName("senti_score");
          for (var i = 0; i < x.length; i++) {
             x[i].value = -64;
          }
          var forms = document.getElementsByName("senti_score_form");
          for (var i = 0; i < forms.length; i++) {
             forms[i].submit();
          }
      }

      // Sentiment 3
      if (keys[90] && keys[51]) { // key '3'
          var x = document.getElementsByName("senti_score");
          for (var i = 0; i < x.length; i++) {
             x[i].value = -34;
          }
          var forms = document.getElementsByName("senti_score_form");
          for (var i = 0; i < forms.length; i++) {
             forms[i].submit();
          }
      }

      // Sentiment 4
      if (keys[90] && keys[52]) { // key '4'
          var x = document.getElementsByName("senti_score");
          for (var i = 0; i < x.length; i++) {
             x[i].value = 0;
          }
          var forms = document.getElementsByName("senti_score_form");
          for (var i = 0; i < forms.length; i++) {
             forms[i].submit();
          }
      }


      // Sentiment 5
      if (keys[90] && keys[53]) { // key '5'
          var x = document.getElementsByName("senti_score");
          for (var i = 0; i < x.length; i++) {
             x[i].value = 34;
          }
          var forms = document.getElementsByName("senti_score_form");
          for (var i = 0; i < forms.length; i++) {
             forms[i].submit();
          }
      }

      // Sentiment 6
      if (keys[90] && keys[54]) { // key '6'
          var x = document.getElementsByName("senti_score");
          for (var i = 0; i < x.length; i++) {
             x[i].value = 64;
          }
          var forms = document.getElementsByName("senti_score_form");
          for (var i = 0; i < forms.length; i++) {
             forms[i].submit();
          }
      }

      // Sentiment 7
      if (keys[90] && keys[55]) { // key '7'
          var x = document.getElementsByName("senti_score");
          for (var i = 0; i < x.length; i++) {
             x[i].value = 95;
          }
          var forms = document.getElementsByName("senti_score_form");
          for (var i = 0; i < forms.length; i++) {
             forms[i].submit();
          }
      }



      // Ctrl + f
      if (keys[17] && keys[70]) {
          // do something
          // prevent default browser behavior
          e.preventDefault(); 
      }
  }
  function keysReleased(e) {
      // mark keys that were released
      keys[e.keyCode] = false;
  }

  function isZKeyPressed(sid) {
      if (keys[90]) { // The Z key!
          keys[keys[90]] = false; 
          return false;

          window.open("fix-corpus.cgi?db_edit=../db/%s.db&sid_edit=" + sid, "_blank")

          //window.location.reload();
          //alert("The Z key was pressed!" + sid);

      } else {
          //  alert("The Z key was NOT pressed!" + sid);
      }
  }
  </script>



""" % (ver, typ, corpus)


def show_sents(c, tsid, twid):
    html = '<h6>'
    html += HTML.status_bar(userID, position="right")
    if tlemma ==  tword:
        html +=  """Tagging %s (%d:%d %s)</h6><p>""" % (tlemma,tsid,
                                                        twid,corpus)
    else: ## word !=lemma
        html +=  """Tagging %s (%d:%d %s --- %s)</h6><p>""" % (tlemma,tsid,
                                                               twid,corpus,
                                                               tword)
    ### go through each sentence
    for sid in sorted(wds.keys()):
        html += "<div lang='zh' style='font-size:%s;line-height: 150%%;'>" % textSize  
        #fixme above dynamicly according to lang
        html += """<span style="font-size:80%">"""
        html += "%s" % \
            HTML.show_sid_bttn(corpus, sid, tlemma)
        # html += HTML.edit_sid_bttn(lang,sid)
        html += "&nbsp;</span>"

        for wid in sorted(wds[sid].keys()):
            cids = ['c%s_%s' % (sid,cd) for cd in tags[sid][wid]]
            # sid:wid:pos:lemma
            title= escape("%d:%d:%s:%s" % (sid, wid, 
                                               wds[sid][wid][1], 
                                               wds[sid][wid][2]))


            # TRY TO SORT OUT SENTIMENT VALUES HERE
            # tags[int(sid)][int(wid)][int(cid)] = (clemma, tag, tgs, comment)
            # FIXME!!! Add sentiment scores for each concept
            senti_style = ""
            concept_count = 0
            total_score = 0
            if tags[sid][wid]:
                for cid in tags[sid][wid]:
                    if cid in sentiment[sid].keys():
                        concept_count += 1
                        total_score += sentiment[sid][cid]
            
            if concept_count > 0: # CHECK IF DB HAD SCORES (EVEN IF 0)
                db_senti_score = True
            else:
                db_senti_score = False

            concept_count = 1 if concept_count == 0 else concept_count
            if db_senti_score and total_score == 0:
                senti_style = "border-bottom: 2px solid grey;"
            elif (total_score / concept_count) > 0:
                senti_style = "border-bottom: 2px solid green;"
            elif (total_score / concept_count) < 0:
                senti_style = "border-bottom: 2px solid red;"
            


            ## selected word
            word = wds[sid][wid][0]
            clss = ' '.join(['tagme'] + cids)
            if sid == tsid and wid==twid:
                html += """<span class='%s' style="%s"
                title='%s'>%s</span> """ % (clss, senti_style, title, word)


            ## needs to be tagged  (then no sentiment)
            elif any(tags[sid][wid][cid][1] == None for cid in tags[sid][wid]):
                clss = ' '.join(['notag'] + cids)
                
                html += """\
<a href = '%s?gridmode=%s&corpus=%s&lang=%s&sid=%s&wid=%s&window=%s&textSize=%s' 
   target='_parent' title='%s' class='%s'>%s</a>
""" %(cgiself, gridmode, corpus, lang, sid, wid, 
      window,textSize, title, clss,word)

            ## tagged
            elif tags[sid][wid]:
                for cid in tags[sid][wid]:

                    if tags[sid][wid][cid][3]: ## has a comment
                        title +='&#013;%s: %s (%s)' % (
                            tags[sid][wid][cid][0],
                            tags[sid][wid][cid][1],
                            escape(tags[sid][wid][cid][3],quote=True))

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
<a href = '%s?gridmode=%s&corpus=%s&lang=%s&sid=%s&wid=%s&window=%s&textSize=%s' 
   target='_parent' title='%s' class='%s' style="%s" >%s</a>
""" %(cgiself, gridmode, corpus, lang, sid, 
      wid, window, textSize,title, clss, senti_style, word)

            ## function word: FIXME --- allow you to tag it anyway              
            else:
                html += "<span title='%s'>%s</span> " % (title, word)
        html += "</div>\n"

    ############################################################################
    # TAGGING BOXES
    ############################################################################
    sentihtml = ""
    html += """<form id='tagword' name='tag' method="get" action="%s" 
               target='log' onsubmit="setTimeout('parent.location.reload()',
               500); return true;" >
               <input type='hidden' name='cgi_mode' value='tagword'>
               <input type='hidden' name='corpus' value='%s'>
               <input type='hidden' name='lang' value='%s'>
               <input type='hidden' name='lemma' value='%s'>
               <input type='hidden' name='sid' value='%d'>
               <input type='hidden' name='wid' value='%d'>
               <input type='hidden' name='cids' value='%s'>
               <input type='hidden' name='usrname' value='%s'>
            """ % ('edit-corpus.cgi',  corpus, lang, tlemma, tsid, twid, 
                   ' '.join(["%d|%d" % (tsid, c) for c in tags[tsid][twid]]),
                   userID)
    html+= "<br>"
    for cid in tags[tsid][twid]:
        if tags[tsid][twid][cid]:
            clem = tags[tsid][twid][cid][0]
            ss = lem2ss(w, clem, lang)
            sss= ' '.join(ss)
            html += """<a
                       href='wn-gridx.cgi?gridmode=%s&lang=%s&ss=%s&lemma=%s' 
                       style="font-size:100%%;text-decoration:none;" 
                       target='wn'>%s</a>&nbsp;&nbsp;
                    """ % (gridmode,lang, sss, clem, clem)
        ##print 'ss', ss, wds[tsid][twid][1],  pos2wn(wds[tsid][twid][1], lang)
        ### fixme: back off to English
        ##print tags[tsid][twid][cid]
            html += tbox(ss, "%d|%d" % (tsid,cid), pos2wn(wds[tsid][twid][1], 
                        lang), tags[tsid][twid][cid][1], #tag
                        tags[tsid][twid][cid][3])       #comment


            html += "<hr style='margin-top:5px;margin-bottom:5px;'/>"


            ####################################################################
            # SENTIMENT (TRIAL)
            ####################################################################
            if tags[tsid][twid][cid][1] != "x":
                unique_id = "%s%s%s" % (tsid, twid, cid)
                sentihtml += """%s (sentiment:  %s)<form id="senti%s"  method="get" name="senti_score_form"
                action="%s" target='log' style="display: inline;">
                <input type='hidden' name='cgi_mode' value='sentiment'>
                <input type='hidden' name='corpus' value='%s'>
                <input type='hidden' name='lang' value='%s'>
                <input type='hidden' name='senti_lemma' value='%s'>
                <input type='hidden' name='senti_sid' value='%d'>
                <input type='hidden' name='senti_cid' value='%s'>
                <input type='hidden' name='usrname' value='%s'>
                """ % (clem, sentiment[tsid][cid], unique_id, 'edit-corpus.cgi',  corpus, 
                       lang, clem, tsid, cid, userID)
                tag = tags[tsid][twid][cid][1]
                sentihtml += """<br><input name="senti_score" type="range" 
                style="width:200px" min="-100" max="100" value="%d"
                onchange="document.getElementById('senti%s').submit();">

                   <table style="width:200px; height:10px; font-size:8px;">
                         <tr><td bgcolor="#CD2626">1</td>
                             <td bgcolor="#E26262">2</td>
                             <td bgcolor="#EEA6A6">3</td>
                             <td>4</td>
                             <td bgcolor="#94D994">5</td>
                             <td bgcolor="#40B640">6</td>
                             <td bgcolor="#228B22">7</td>
                         </tr>
                   </table>
                </form>
                """ % (sentiment[tsid][cid], unique_id)
            ####################################################################



    # There is no need for a submit button anymore!
    # html += """<span style='float:right'><button class="small">
    #              <a href="javascript:{}"
    #              onclick="document.getElementById('tagword').submit(); 
    #              return false;"><span title="Tag Word">
    #              <span style="color: #4D99E0;font-size:15px">
    #              <i class='icon-tag'></i>Tag</span></span></a>
    #            </button></span>"""

    html += """</form> """



    # PRINT SENTIMENT (TRIAL II)
    html += sentihtml
    html += "<hr style='margin-top:5px;margin-bottom:5px;'/>"

    return html



def tag_word(corpus, sid, wid):

    selSize = "<select name ='textSize'>"
    for size in ['100%','110%','120%','130%','140%','150%']:
        if textSize == size:
            selSize += """<option value='%s' selected>%s</option>""" % (size, size)
        else:
            selSize += """<option value='%s'>%s</option>""" % (size, size)
    selSize += "</select>"


    searchbox = """
<form id='input' name ='input' method='get' action='%s' 
style="display:inline-block; vertical-align:middle" target='_parent'>
<input type='hidden' name='corpus' value='%s'>
<input type='hidden' name='lang' value='%s'>
<input type='hidden' name='gridmode' value='%s'>

<span style="display:inline-block; vertical-align:middle">
<table style="padding:0;margin:0;font-size:85%%;">
<tr><td style="padding:0">Goto</td></tr>
<tr><td style="padding:0;">sid:</td></tr></table>
</span>
<input type='text' name='sid' value='%d' size=3/>

<span style="display:inline-block; vertical-align:middle">
<table style="padding:0;margin:0;font-size:85%%;">
<tr><td style="padding:0">Sentence</td></tr>
<tr><td style="padding:0;">context:</td></tr></table>
</span>
<input type='text' name='window' value='%s' style="width:2em" />


<span style="display:inline-block; vertical-align:middle">
<table style="padding:0;margin:0;font-size:85%%;">
<tr><td style="padding:0">Text</td></tr>
<tr><td style="padding:0;">size:</td></tr></table>
</span>
%s


<button class="small"> <a href="javascript:{}"
 onclick="document.getElementById('input').submit(); 
 return false;"><span title="Search">
 <span style="color: #4D99E0;"><i class='icon-search'></i>
 </span></span></a>
</button>

</form>

<form title='Tag all instances of this lemma' name ='input' method='get' action='tag-lexs.cgi' 
   style="display:inline-block; vertical-align:middle; float: right;" target='_blank'>
<input type='hidden' name='corpus' value='%s'>
<input type='hidden' name='lang' value='%s'>
<input type='hidden' name='gridmode' value='%s'>

<span style="display:inline-block; vertical-align:middle">
<table style="padding:0;margin:0;font-size:85%%;">
<tr><td style="padding:0">Lookup</td></tr>
<tr><td style="padding:0;">word:</td></tr></table>
</span>
 <input type='text' name='lemma' placeholder='lemma' value='%s' size=8/>
</form>
<br><span style='float: right;'>%s</span><br><br><br><br><br><br><br><br> 
</p>""" % (cgiself, corpus, lang, gridmode, sid, window, selSize,
           ## second form (lemma)
           corpus, lang, gridmode, tlemma, HTML.ntumc_tagdoc())
     
    return  """%s %s""" % (show_sents(c, tsid, twid), searchbox,)





###
### Main
###

########## HTML
print("""Content-type: text/html; charset=utf-8\n\n""")

# Header
print(tag_head(version,'sequential'))
#taglog= process_tags(c)

# No Username No Page!
if userID not in valid_usernames:
    print(HTML.status_bar(userID, position="center"))
    print("""You need to have an active username 
             to be able to modify the database.""")

##
## single word tagging is in here; wn-gridx is an iframe
##
else:

    print(""" <table style="width:100%%">
    <tr> <td valign="top" style="width:55%%;
             border-right: 1px solid black">%s</td>

         <td valign="top" style="width:45%%">
         <table style="width:100%%">
           <tr> <td valign="top" style="width:45%%"> 
           <iframe name="wn" id="omwiframe" 
               src="%s?lang=%s&ss=%s&lemma=%s&pos=%s&gridmode=%s" 
               frameborder="0" width="100%%"
               onload="resizeAllFrames()">wordnet
           </iframe></td></tr>
           <tr> <td> 

           </td> </tr>
         </table>
     </tr>
   </table>
"""% (tag_word(corpus, tsid, twid), 
      wncgi, lang, tsss, tlemma, twp, gridmode))


# <hr>
#            <iframe name="log" id="logiframe" frameborder="0"
#                    width="100%%" onload="resizeAllFrames()">
#            </iframe> width="400%" 

    # BOTTOM LOG (breaks make sure the div has space)
    print("""<span style="position:fixed; 
                      bottom:1px; left:3px;">""")
    print("""<iframe name="log" id="logiframe" frameborder="0"
                onload="resizeAllFrames()" width="400%"
              style="transform: scale(0.7); transform-origin: 0 0;">
           </iframe>""")
    print("""</span> """)

print("  </body>")
print("</html>"
)
