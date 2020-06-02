#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, http.cookies
import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import sqlite3, codecs
from collections import defaultdict as dd
from ntumc_utils import placeholders_for
from ntumc_webkit import *
from lang_data_toolkit import *


form = cgi.FieldStorage()

docName = form.getfirst("docName")
log_message = form.getfirst("log_message", "")
langs = [('eng','English'), ('cmn','Chinese'),
         ('ind','Indonesian'),('jpn','Japanese'),
         ('zsm','Malay'),('ita','Italian'),('kor','Korean')]

fl_docID = 0
tl_docID = 0

################################################################################
# FIND AND CONNECT TO THE DATABASES
################################################################################
l1 = form.getfirst("l1", 'eng')
l2 = form.getfirst("l2", 'cmn')
fl = l1
tl = l2

if l1 != None and l2 != None and os.path.isfile('../db/'+l1+'-'+l2+'.db'):
    db = '../db/'+l1+'-'+l2+'.db'
    fldb = '../db/'+l1+'.db'
    tldb = '../db/'+l2+'.db'

elif l1 != None and l2 != None and os.path.isfile('../db/'+l2+'-'+l1+'.db'):
    db = '../db/'+l2+'-'+l1+'.db'
    tldb = '../db/'+l1+'.db'
    fldb = '../db/'+l2+'.db'
    fl = l2
    tl = l1

else:
    db = None
    fldb = None
    tldb = None
    fl = None
    tl = None


if db != None:
    conn = sqlite3.connect(db)
    curs = conn.cursor()
    conn_fl = sqlite3.connect(fldb)
    curs_fl = conn_fl.cursor()
    conn_tl = sqlite3.connect(tldb)
    curs_tl = conn_tl.cursor()

################################################################################
# FETCH INFORMATION ABOUT THE DOCUMENTS IN THE DB
################################################################################
docs = []
engconn = sqlite3.connect("../db/eng.db")
engc = engconn.cursor()
engc.execute("""SELECT doc, title, docid FROM doc""")
rows = engc.fetchall()
for r in rows:
    (doc, title, docid) = (r[0],r[1],r[2])
    docs.append((doc, title, docid))


################################################################################
sents = dd(lambda: dd(str))
sents_links = dd(lambda: dd(set))

if db != None:
    ############################################################################
    # FETCH THE DOC_ID FROM THE DOC_NAME
    fetch_docID = """SELECT docid FROM doc WHERE doc=? """
    curs_fl.execute(fetch_docID, [docName])
    rows = curs_fl.fetchall()
    for r in rows:
        fl_docID = r[0]
    curs_tl.execute(fetch_docID, [docName])
    rows = curs_tl.fetchall()
    for r in rows:
        tl_docID = r[0]
    ############################################################################

    ############################################################################
    fetch_sents = """SELECT sid, sent FROM sent 
                     WHERE docID = ? """
    
    curs_fl.execute(fetch_sents, [int(fl_docID)])
    rows = curs_fl.fetchall()
    for r in rows:
        (sid, sent) = (r[0],r[1])
        sents[fl][sid] = sent        

    curs_tl.execute(fetch_sents, [int(tl_docID)])
    rows = curs_tl.fetchall()
    for r in rows:
        (sid, sent) = (r[0],r[1])
        sents[tl][sid] = sent
    ############################################################################

    ############################################################################
    fl_sids = placeholders_for(sents[fl].keys())
    fetch_all = """SELECT slid, fsid, tsid
                   FROM slink
                   WHERE fsid in (%s) """ % fl_sids
    curs.execute(fetch_all, list(sents[fl].keys()))
    rows = curs.fetchall()
    for r in rows:
        (slid, fsid, tsid) = (r[0],r[1],r[2])

        sents_links[fl][fsid].add(tsid)
        sents_links[tl][tsid].add(fsid)
    ############################################################################

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
# HTML
################################################################################
print(u"""Content-type: text/html; charset=utf-8\n
         <!DOCTYPE html>\n
           <html>\n
           <head>

    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
    <script src="../HTML-KickStart-master/js/kickstart.js"></script> <!-- KICKSTART -->
    <link rel="stylesheet" href="../HTML-KickStart-master/css/kickstart.css" media="all" /> <!-- KICKSTART -->


<script>
function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    ev.dataTransfer.setData("Text", ev.target.dataset.value);
}

function drop(ev) {
    var data = ev.dataTransfer.getData("Text");
    ev.target.appendChild(document.getElementById(data));
    ev.preventDefault();
}

function dropfill(ev, linkid) {
    var data = ev.dataTransfer.getData("Text");
    document.getElementById(linkid).value=data
    ev.preventDefault();
}

</script>


<style>
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

/* lightrow is a faded yellow */
.lightrow {
background-color: #FFFFCC;
}
</style>



<script>
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



<script>
function addNewRel(link) {
  var container = document.getElementById('linkContainer');
  var newDiv = document.createElement('div');
  var newText = document.createElement('input');
  newText.type = "text";
  newText.name = "new_sent_link";
  newText.required = "Yes";
  newText.placeholder = "New Link";
  newText.value = link;
  newText.style.visibility= "hidden"

  newDiv.appendChild(newText);
  container.appendChild(newDiv);

  document.linking.submit() // submit the form!
}
</script>



<script>

function spoil(id){
    var divid = document.getElementById(id);
    divid.scrollIntoView(true);
    return false;
}


var prev_click = null;
var prev_click_id = null;
var prev_data = null;

function scm(id){
  var something = document.getElementById(id).innerHTML;
  var current_data = document.getElementById(id).dataset.value;
  // alert(current_data)
  // alert(previous)
  // alert(something)


  // if there is a previous sentence, and the previous sentence
  // is not the same sentence as the one just selected
  if (prev_click != null && prev_data != current_data ){

    var link = current_data + "|||" + prev_data;
    addNewRel(link);

    // alert("NEW link!");
    removeClass(prev_click_id, 'lightrow');
    removeClass(document.getElementById(id), 'lightrow');

    prev_click_id = null;
    prev_click = null;
    prev_data = null;
    // the form should submit here!

    document.getElementById('langselection').submit();

  } else {

    if (prev_data == current_data) {
      prev_click_id = null;
      prev_click = null;
      prev_data = null;
      removeClass(document.getElementById(id), 'lightrow');
      spoil('b'+id)

    } else {
      addClass(document.getElementById(id), 'lightrow');
      prev_click_id = document.getElementById(id);
      prev_click = something;
      prev_data = document.getElementById(id).dataset.value;
      }
  }
}
</script>


</head>
<body>\n""")



print(HTML.status_bar(userID))
if userID not in valid_usernames:
    print("""<i class="icon-user-md pull-left icon-4x"></i> """)
    print("""We're sorry %s, but you need to have an active username 
             to be able to access this area.<br>
             Please click the Home button, on the right and 
             proceed to login.<br>""" % userID)
    print("</body>")
    print("</html>")
    sys.exit(0)


if docName:
    print("""<h5>Crosslingual Sentence Linking (docID:%s)</h5>\n """ % docName)
else:
    print("""<h5>Crosslingual Sentence Linking</h5>\n """)
    
################################################################################
# SEARCH FORM
################################################################################
print("""<form id="goto" action="" method="post" style="display:inline-block">""")
print("""<b>L1:</b>""")
print("""<select id="l1" name="l1">""")
for l in langs:
    if l[0] == l1:
        print("<option value ='%s' selected>%s</option>" % l)
    else:
        print("<option value ='%s'>%s</option>" % l)
print("""</select>""")

print("""<b>L2:</b>""")
print("""<select id="l2" name="l2">""")
for l in langs:
    if l[0] == l2:
        print("<option value ='%s' selected>%s</option>" % l)
    else:
        print("<option value ='%s'>%s</option>" % l)
print("""</select>""")

print("""<select name="docName">""")
print("<option value ='' selected>Select Document</option>")

next_docName = docs[0][0]
for current_doc_i, d in enumerate(docs):
    if d[0] == docName:
        try:
            next_docName = docs[current_doc_i + 1][0]
        except: # there is no 'next'
            next_docName = docs[current_doc_i][0]
        print("<option value ='%s' selected>%s (%d)</option>""" % d)
    else:
        print("<option value ='%s'>%s (%d)</option>""" % d)
print("""</select>""")

print("""<span><button class="small"><a href="javascript:{}"
          onclick="document.getElementById('goto').submit();return false;"
          style="text-decoration:none">
         <span style="color: #4D99E0;font-size:15px;">Go</span></a>
         </button></span>""")
print("""</form>""")


# NEXT BUTTON HERE
print("""<form id="next_doc" action="" method="post" 
      style="display:inline-block">""")
print("""<input type="hidden" name="l1" value="%s"/>""" % l1)
print("""<input type="hidden" name="l2" value="%s"/>""" % l2)
print("""<input type="hidden" name="docName" value="%s"/>""" % next_docName)
print("""<span><button class="small"><a href="javascript:{}"
          onclick="document.getElementById('next_doc').submit();return false;"
          style="text-decoration:none">
         <span style="color: #4D99E0;font-size:15px;">Next</span></a>
         </button></span>""")
print("""</form>""")


print("<hr style='margin-top:10px;margin-bottom:10px;'/>")


################################################################################
# PARALLEL LANGUAGE DIVS
################################################################################
for lang in (l1, l2):
    if lang == l1:
        print("""<div style="height:250px; width:50%;
                  overflow-y:scroll; float:left">""")
    else:
        print("""<div style="height:250px; width:50%;
                  overflow-y:scroll;">""")

    print("""<table class="tight hoverTable">""")
    for s in sorted(sents[lang].keys()):
        unq_id = lang+str(s)
        l = """<tr>"""

        if len(sents_links[lang][s]) == 0:
            markunlinked = """ style="color:red" """
        else:
            markunlinked = ""

        if lang == l1:
            l += u"""<td style="margin:0;padding:0;">
                     <a href="#b%s" style="text-decoration:none">⬇</a></td>
                  """ % unq_id


        l += """<td id='%s' onclick="scm('%s');" 
                  data-value="%s"  %s>""" % (str(unq_id), str(unq_id), 
                                              str(unq_id), markunlinked)
        l += """<span title='%s'>%s</span>""" % (s, sents[lang][s]) 
        l += """</td>"""

        if lang == l2:
            l += u"""<td style="margin:0;padding:5px;">
                     <a href="#b%s" style="text-decoration:none">⬇</a>
                     </td>
                  """ % unq_id

        l += """</tr>"""

        print(l)
    print("""</table>""")
    print("""</div>""")
print("<hr>")


################################################################################
# SHOW EXISTENT LINKS
################################################################################
print("""<div style="height:400px;overflow-y:scroll;">""")
print("""<table class="tight hoverTable">""")

for l1_sid in sorted(sents_links[l1].keys()):

    line_l1 = u"""<tr><td width="1%%" id="b%s%s" style="margin:0;padding:0;">
               <a href="#%s%s" style="text-decoration:none">⬆</a></td>
               """ % (l1, l1_sid, l1, l1_sid) 
    line_l1 += """<td width="49%">"""
    line_l1 += """<span title='%s' onclick="spoil('%s%s');"
                  >%s</span>""" % (l1_sid,  l1, l1_sid, 
                                   cgi.escape(sents[l1][l1_sid]))
    line_l1 += "</td>"

    line = u"<td><a href='edit-linkedcorpus.cgi?edit_mode=del_sentence_link"
    line += u"&lang_from=%s&lang_to=%s&linked_db=%s" % (fl,tl,db)
    line += u"&username=%s&lang1=%s&lang2=%s" % (userID,l1,l2)
    line += u"&docName=%s" % (docName)
    line += u"&delete_sent_link=%s' "
    line += u" style='text-decoration:none' title='Delete link'>"
    line += u"<span style='color:red'>❌</span></a></td>"

    for tsid in sorted(sents_links[l1][l1_sid]):
        line_per_l = line_l1
        line_per_l += line % (l1 + str(l1_sid) + '|||' + l2 + str(tsid))

        line_per_l += """<td><span title='%s' onclick="spoil('%s%s');"
                         >%s</span></td>""" % (tsid, l2, tsid, sents[l2][tsid]) 
        line_per_l += u"""<td width="1%%" id="b%s%s" 
                       style="margin:0;padding:0;">
                       <a href="#%s%s" style="text-decoration:none">⬆</a></td>
                       """ % (l2, tsid, l2, tsid) 

        line_per_l += "</tr>"
        print(line_per_l)

print("</table>")
print("</div>")

# PRINTING  FORM
print("""<p>
<form name="linking" id="linking" action="edit-linkedcorpus.cgi"  method="post">
  <input type="hidden" name="edit_mode" value="sentence_link"/>
  <input type="hidden" name="lang_from" value="%s"/>
  <input type="hidden" name="lang_to" value="%s"/>
  <input type="hidden" name="linked_db" value="%s"/>
  <input type="hidden" name="username" value="%s"/>

  <input type="hidden" name="lang1" value="%s"/>
  <input type="hidden" name="lang2" value="%s"/>
  <input type="hidden" name="docName" value="%s"/>

  <span id="linkContainer"></span>
</form></p>""" %(fl,tl,db,userID,l1,l2,docName))



# BOTTOM LOG (breaks make sure the div has space)
print("""<span style="position:fixed; bottom:3px; right:15px;">""")
print("""%s""" % log_message)
print("""</span> """)

print("""</body></html>\n""")
