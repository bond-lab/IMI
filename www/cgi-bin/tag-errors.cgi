#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, http.cookies 
import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import sqlite3, codecs
from collections import defaultdict as dd
import sys

from ntumc_webkit import *
from lang_data_toolkit import *


################################################################################
# This cgi is aimed at language learner analysis. 
# It allows to tagging a set of errors at word/phrase level.
# It currently works only monolingually, for Mandarin. 
################################################################################

error_set = dd(lambda: dd(str)) # dd[errgroup][error][human label]


# THE ERROR STRUCTURE WILL BE INJECTED IF IT DIDN'T EXIST
def create_error_sql(c):
    """This function is triggered if the database does not yet have
    the necessary strucutre for error level analysis. 
    It will add new tables and triggers."""

    # CREATE ERROR TABLE
    c.execute("""CREATE TABLE IF NOT EXISTS error (
                   sid INTEGER, 
                   eid INTEGER, 
                   label TEXT,
                   comment TEXT, 
                   username TEXT, 
                   PRIMARY KEY (sid, eid),
                   FOREIGN KEY(sid) REFERENCES sent(sid))""")

    # CREATE ERROR_LOG TABLE (FOR TRIGGERS)
    c.execute("""CREATE TABLE IF NOT EXISTS error_log (
                   sid_new INTEGER, 
                   sid_old INTEGER,
                   eid_new INTEGER, 
                   eid_old INTEGER,
                   label_new TEXT, 
                   label_old TEXT,
                   comment_new TEXT, 
                   comment_old TEXT,
                   username_new TEXT, 
                   username_old TEXT,
                   date_update DATE)""")

    # CREATE ERROR-WORD-LINKS TABLE
    c.execute("""CREATE TABLE IF NOT EXISTS ewl (
                   sid INTEGER, 
                   wid INTEGER, 
                   eid INTEGER,
                   username TEXT, 
                   PRIMARY KEY (sid, wid, eid),
                   FOREIGN KEY(sid) REFERENCES sent(sid),
                   FOREIGN KEY(wid) REFERENCES word(wid),
                   FOREIGN KEY(eid) REFERENCES error(eid))""")

    # CREATE ERROR-WORD-LINKS LOG TABLE (FOR TRIGGERS)
    c.execute("""CREATE TABLE IF NOT EXISTS ewl_log (
                   sid_new INTEGER, 
                   sid_old INTEGER,
                   wid_new INTEGER, 
                   wid_old INTEGER,
                   eid_new INTEGER, 
                   eid_old INTEGER,
                   username_new TEXT, 
                   username_old TEXT,
                   date_update DATE)""")

    html_log = """The SQL structure for error level 
                   analysis was created."""
    return html_log



################################################################################
# FETCH DATA FROM FORM
################################################################################

form = cgi.FieldStorage()
sid = form.getfirst("sid", 1)

corpusdb = form.getfirst("corpusdb")
if corpusdb == "cmn_mal_edu":
    error_set["Accept Sentence"]["OK"] = "OK"
    error_set["Core"]["1"] = "Adjective predicate sentence"
    error_set["Core"]["2"] = "Adjective predicate sentence with 不"
    error_set["Core"]["3"] = "Adjective predicate sentence without adverbials"
    error_set["Core"]["4"] = "Adjective modifier without degree adverbials"
    error_set["Core"]["5"] = "姓 used as a verb"
    error_set["Core"]["6"] = "Syntactic position of a noun Modifier"
    error_set["Core"]["7"] = "Usage of 和 vs. 也"
    error_set["Core"]["8"] = "Syntactic position of 也 (e.g. before the subject, after the verb)"
    error_set["Core"]["9"] = "有点儿 vs. 一点儿 mix-up"
    error_set["Core"]["10"] = "Syntactic position of adverbial clause"
    error_set["Core"]["11"] = "Emphasizing sentence 是...的..."
    error_set["Core"]["12"] = "Usage of 不 vs. 没有"
    error_set["Core"]["13"] = "Usage of 二 vs. 两"
    error_set["Core"]["14"] = "Syntactic order of multiple adverbials 不, 都, 也, etc."
    error_set["Core"]["15"] = "Missing Measure word after 几"
    error_set["Core"]["16"] = "Incorrect measure word"
    error_set["Core"]["17"] = "吗redundancy (V 不 V, 几, etc.)"
    error_set["Core"]["18"] = "中国 vs 中文"
    error_set["Core"]["19"] = "Numerical phrase predicate sentence"
    error_set["Core"]["20"] = "Bad Pinyin / Tone"
    error_set["Others"]["Oth"] = "Oth - Other errors requiring correction"

else:
    error_set["Accept Sentence"]["OK"] = "OK"
    error_set["Verbs"]["VTense"] = "VTense - Verb tense"
    error_set["Verbs"]["VMod"] = "VMod - Missing, inappropriate or unnecessary modal"
    error_set["Verbs"]["VMiss"] = "VMiss - Missing verb"
    error_set["Verbs"]["VForm"] = "VForm - Wrong form of the verb"
    error_set["Verbs"]["VVoice"] = "VVoice - Wrong choice of active or passive voice"

    error_set["Articles, Determiners"]["AMiss"] = "AMiss - Missing article/determiner"
    error_set["Articles, Determiners"]["ACh"] = "ACh - Wrong choice of article/determiner"
    error_set["Articles, Determiners"]["AUnn"] = "AUnn - Unnecessary article/determiner"

    error_set["Nouns"]["NNum"] = "NNum - Wrong choice of singular/plural form of the noun"
    error_set["Nouns"]["NCount"] = "NCount - Wrong form of countable/uncountable noun"
    error_set["Nouns"]["NPoss"] = "NPoss - Wrong choice of possessive form"

    error_set["Subject-Verb Agreement"]["SubVA"] = "SubVA - Subject and verb do not agree in number and/or person"

    error_set["Pronouns"]["ProCh"] = "ProCh - Wrong choice of pronoun"
    error_set["Pronouns"]["ProRef"] = "ProRef - Unclear reference for pronoun"
    error_set["Pronouns"]["ProAgr"] = "ProAgr - Pronoun and reference do not agree in number/person/gender"
    error_set["Pronouns"]["ProMiss"] = "ProMiss - Missing pronoun"
    error_set["Pronouns"]["ProUnn"] = "ProUnn - Unnecessary pronoun"

    error_set["Prepositions"]["PreCh"] = "PreCh - Wrong choice of preposition"
    error_set["Prepositions"]["PreMiss"] = "PreMiss - Missing preposition"
    error_set["Prepositions"]["PreUnn"] = "PreUnn - Unnecessary preposition"

    error_set["Words"]["WCh"] = "WCh - Wrong choice of word"
    error_set["Words"]["WForm"] = "WForm - Wrong form of the word"
    error_set["Words"]["WMiss"] = "WMiss - Missing words"
    error_set["Words"]["WUnn"] = "WUnn - Unnecessary words"
    error_set["Words"]["WColloc"] = "WColloc - Words do not collocate"
    #error_set["Words"]["WInf"] = "WInf - Inappropriate word in terms of formality"

    error_set["Word Order"]["PosW"] = "PosW - Incorrect word order"
    error_set["Word Order"]["PosAd"] = "PosAd - Wrong position of adjective/adverb"

    error_set["Transitions"]["TCh"] = "TCh - Wrong choice of link words/phrases"
    error_set["Transitions"]["TUnn"] = "TUnn - Unnecessary link words/phrases"
    error_set["Transitions"]["TMiss"] = "TMiss - Missing link words/phrases"

    error_set["Sentence structure"]["SRun"] = "SRun - Run-on sentence"
    error_set["Sentence structure"]["SComS"] = "SComS - Comma splice"
    error_set["Sentence structure"]["SFrag"] = "SFrag - Sentence fragment"
    error_set["Sentence structure"]["SMMod"] = "SMMod - Misplaced modifier"
    error_set["Sentence structure"]["SDMod"] = "SDMod - Dangling modifier"
    error_set["Sentence structure"]["SPar"] = "SPar - Parallelism missing"
    error_set["Sentence structure"]["SSub"] = "SSub - Problematic subordinate clause"
    error_set["Sentence structure"]["SLong"] = "SLong - Overly long sentence"
    error_set["Sentence structure"]["SConv"] = "SConv - Convoluted sentence"

    # error_set["Style"]["StyC"] = "CHANGE ME (StyC)" #StyC - Casual style
    error_set["Style"]["StyF"] = "StyF - Overly formal words or expressions"
    # error_set["Style"]["StySh"] = "CHANGE ME (StySh)" #StySh - Style shift (e.g. from formal to informal and vice versa)
    error_set["Style"]["StyContr"] = "StyContr - Contractions"
    error_set["Style"]["StyWch"] = "StyWch - Casual or colloquial words or expressions"
    error_set["Style"]["StyMood"] = "StyMood - Style mood"
    error_set["Style"]["StyPron"] = "StyPron - Pronoun choice"


    error_set["Expression"]["ExpUC"] = "ExpUC - Unclear expression"
    error_set["Expression"]["ExpAw"] = "ExpAw - Awkward expression"

    error_set["Mechanics"]["MPunc"] = "MPunc - Punctuation error"
    error_set["Mechanics"]["MCase"] = "MCase - Wrong use of upper or lower case"
    error_set["Mechanics"]["MSpel"] = "MSpel - Spelling error"
    error_set["Mechanics"]["MSpace"] = "MSpace - Missing or unnecessary space"

    error_set["Citation"]["CitForm"] = "CitForm - Incorrect citation form"
    error_set["Citation"]["CitMiss"] = "CitMiss - Missing citation"

    error_set["Others"]["Oth"] = "Oth - Other errors requiring correction"

    


log_message = form.getfirst("log_message", "")

# langs = [('eng','English'), ('cmn','Chinese'),
#          ('ind','Indonesian'),('jpn','Japanese'),
#          ('ita','Italian')]

################################################################################
# FIND AND CONNECT TO THE DATABASES
################################################################################
if corpusdb:
    (dbexists, dbversion, dbmaster, dblang, dbpath) = check_corpusdb(corpusdb)

    lang = dblang

    if dbexists:
        conn = sqlite3.connect(dbpath)
        curs = conn.cursor()

else:
    corpusdb = None

################################################################################
sents = dd(lambda: dd(str)) # sents[lang][sid] = sent
words = dd(lambda: dd(lambda: dd(tuple))) # ws[lang][sid][wid]=(word,pos,lemma)
concepts = dd(lambda: dd(lambda: dd(tuple))) # cs[lang][sid][cid]=(clemma,tag)
wcls = dd(lambda: dd(lambda: dd(set))) # wcls[lang][sid][wid]=set(cid)
cwls = dd(lambda: dd(lambda: dd(set))) # cwls[lang][sid][cid]=set(wid)
chunks = dd(lambda: dd(lambda: dd(set))) # chunks[lang][sid][xid]=set(wids)
# chunks_senti = dd(lambda: dd(lambda: dd(int))) # chunks_sen[lang][sid][xid]= score
error_labels = dd(lambda: dd(lambda: dd(int))) # chunks_sen[lang][sid][xid]= score

chunks_comm = dd(lambda: dd(lambda: dd(str))) # chunks_sen[lang][sid][xid]= comment
docID = None
docN = None

if corpusdb != None:
    ############################################################################
    # FETCH SENTENCE
    ############################################################################
    fetch_sents = """SELECT sid, sent, doc.docID, doc.doc 
                     FROM sent 
                     JOIN doc 
                     WHERE sid = ? 
                     AND doc.docID = sent.docID """

    curs.execute(fetch_sents, [int(sid)])
    rows = curs.fetchall()
    for r in rows:
        (sid, sent, doc_id, doc) = (r[0],r[1], r[2], r[3])
        sents[lang][sid] = sent
        docID = doc_id
        docN = doc
    ############################################################################

    ############################################################################
    # FETCH WORDS
    ############################################################################
    fetch_words = """ SELECT sid, wid, word, pos, lemma
                      FROM word
                      WHERE sid = ?"""

    curs.execute(fetch_words, [int(sid)])
    rows = curs.fetchall()
    full_wid_set = set()
    for r in rows:
        (sid, wid, word, pos, lemma) = (r[0],r[1],r[2],r[3],r[4])
        words[lang][sid][wid] = (word,pos,lemma)
        full_wid_set.add(wid)
    ############################################################################

    ############################################################################
    # FETCH CONCEPTS
    ############################################################################
    fetch_concepts = """ SELECT sid, cid, clemma, tag 
                         FROM concept
                         WHERE sid =  ? """
    curs.execute(fetch_concepts, [int(sid)])
    rows = curs.fetchall()
    for r in rows:
        (sid, cid, clemma, tag) = (r[0],r[1],r[2],r[3])
        concepts[lang][sid][cid]=(clemma,tag)
    ############################################################################

    ############################################################################
    # FETCH CWL/WCL
    ############################################################################
    fetch_cwls = """SELECT sid, wid, cid 
                    FROM cwl 
                    WHERE sid = ? """
    curs.execute(fetch_cwls, [int(sid)])
    rows = curs.fetchall()
    for r in rows:
        (sid, wid, cid) = (r[0],r[1],r[2])
        wcls[lang][sid][wid].add(cid)
        cwls[lang][sid][cid].add(wid)
    ############################################################################


    ############################################################################
    # FETCH ERRORS
    ############################################################################
    used_wids = set()
    used_eids = set()
    try:
        fetch_errors = """SELECT e.sid, e.eid, e.label, 
                                 ewl.wid, e.comment
                       FROM error as e
                       LEFT JOIN ewl
                       WHERE e.sid = ?
                       AND e.sid = ewl.sid
                       AND e.eid = ewl.eid
                    """
        curs.execute(fetch_errors, [int(sid)])
        rows = curs.fetchall()
        for r in rows:
            (sid, eid, label, wid, comm) = (r[0],r[1],r[2],r[3],r[4])
            chunks[lang][sid][eid].add(wid)
            # chunks_senti[lang][sid][eid] = label
            error_labels[lang][sid][eid] = label
            chunks_comm[lang][sid][eid] = comm
            used_wids.add(wid)

        # CHECK IF CHUNKS HAVE BEEN USED
        for eid_a in chunks[lang][sid]:
            chunk_set_a = chunks[lang][sid][eid_a]

            for eid_b in chunks[lang][sid]:
                chunk_set_b = chunks[lang][sid][eid_b]
                if eid_a != eid_b and chunk_set_a <= chunk_set_b:
                    used_eids.add(eid_a)
    except:
        log_message += "It wasn't possible to fetch chunks from the database.<br>"
        log_message += create_error_sql(curs)
        log_message += "Try again now..."


        
    ############################################################################
    # FETCH SENTIMENT SCORES BY WORD
    ############################################################################

    # senti_wid = dd(lambda: dd(int))
    # try:
    #     query = """SELECT sentiment.sid, cwl.wid, score 
    #                FROM sentiment 
    #                JOIN cwl WHERE sentiment.sid = cwl.sid 
    #                AND sentiment.cid = cwl.cid 
    #                AND sentiment.sid = ?"""
    #     curs.execute(query, [sid])

    #     # sentiment = {sid: {wid :  score}} 
    #     for (sid, wid, score) in curs:
    #         senti_wid[int(sid)][int(wid)] = score
    # except:
    #     log_message += "It wasn't possible to fetch word-level sentiment from the database.<br>"

    ############################################################################




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

try: # Last Chunk ID
    lc = str(sid) + str(max(chunks[lang][sid].keys()))
except: # IN CASE NO CHUNKS EXIST
    lc = ""







################################################################################
# GUIDELINES
################################################################################
guidelines = """<div class="info floatRight">
<a class="info"><span style="color: #4D99E0;">
<i class="icon-info-sign"></i>ReadMe</a>

<div class="show_info">
<h5>Guidelines:</h5>
<p>This interface was designed to allow tagging of text chunks. Words (not necessarily contiguous) can be linked together to form chunks of text. Existing chunks can be further linked with words or between themselves to form new chunks.
<p>A set of labels and a comment box is provided for each created chunk of text.

<p>Key Shortcuts:<br>
Space Bar - Creates a new chunk (i.e. a phrase or a word) from previously selected elements on the page;<br>
Z Key - Resets any selection made until that moment;<br>
A Key - Creates a chunk with every word in the sentence to be tagged;
Backspace - Confirms the deletion of chunks after they have been targeted for deletion (using the cross on the right of each comment box);<br>

</div></div>"""
################################################################################



################################################################################
# HTML
################################################################################
print(u"""Content-type: text/html; charset=utf-8\n
<!DOCTYPE html>
  <html>
  <head>

  <!-- IMPORT NTUMC COMMON STYLES -->
  <link href="http://compling.hss.ntu.edu.sg/ntumc-unipi/ntumc-common.css" rel="stylesheet" type="text/css">

   <!-- IMPORT FONT AWESOME -->
   <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.4.0/css/font-awesome.min.css">


    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
    <script src="http://compling.hss.ntu.edu.sg/ntumc-unipi//HTML-KickStart-master/js/kickstart.js"></script> <!-- KICKSTART -->
    <link rel="stylesheet" href="http://compling.hss.ntu.edu.sg/ntumc-unipi/HTML-KickStart-master/css/kickstart.css" media="all" /> <!-- KICKSTART -->


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
.hoverTable td:hover {
background-color: #c0dcc0;
}

/* lightrow is a faded yellow background*/
.lightrow {
background-color: #c0dcc0;
}

/* deleteRed is a faded red background*/
.deleteRed {
background-color: #E06666;
}

/* final is a faded green background used to mark completion*/
.final {
background-color: #c0dcc0;;
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



<script>
/*
 This snippet of code is to create new phrases.
 It should allow selection of any number of words and,
 on clicking 'P', create a new phrase. 'R' should reset
 all selections until now.
*/

function isInArray(value, array) {
  return array.indexOf(value) > -1;
} // isInArray(1, [1,2,3]); == True

var isSelected = [];
function addToBucket(id){ 
  // This function keeps adding words to isSelected
  var current_data = document.getElementById(id).dataset.value;
  if (isInArray(current_data, isSelected)) {
  } else {
    isSelected.push(current_data); 
    addClass(document.getElementById(id), 'lightrow');
  }
}


var toDelete = [];
function addToDelBucket(id){ 
  // This function keeps adding words to toDelete 

  // First clear other selections
  for (index = 0; index < isSelected.length; index++) {
    removeClass(document.getElementById(isSelected[index]), 'lightrow');
  }
  isSelected = [];

  // We need a special case for the final class
  var final = document.getElementsByClassName("final");

  var current_data = document.getElementById(id).dataset.value;

  try {
    if (final[0].dataset.value == current_data) {
    removeClass(final[0], 'final');
    }
  }
  catch(err) {
      // final[0] will often be undefined
      // alert("Err is " + err);
  }

  if (isInArray(current_data, toDelete)) {
  } else {
    toDelete.push(current_data); 
    addClass(document.getElementById(id), 'deleteRed');
  }
}


function addNewPhrase(selectedWordIDs) {
  var container = document.getElementById('linkContainer');
  var newDiv = document.createElement('div');
  var newText = document.createElement('input');
  var headed = document.createElement('input');

  newText.type = "text";
  newText.name = "new_chunk";
  newText.required = "Yes";
  newText.value = selectedWordIDs;
  newText.style.visibility= "hidden"

  newDiv.appendChild(newText);
  container.appendChild(newDiv);

  document.linking.submit() // submit the form!
}



function deleteChunks(selectedChunkIDs) {
  var container = document.getElementById('XlinkContainer');
  var newDiv = document.createElement('div');
  var newText = document.createElement('input');

  newText.type = "text";
  newText.name = "del_chunk";
  newText.required = "Yes";
  newText.value = selectedChunkIDs;
  newText.style.visibility= "hidden"

  newDiv.appendChild(newText);
  container.appendChild(newDiv);

  document.delete_chunks.submit() // submit the form!
}

</script>



<script>  
/*
 This snippet of code is used to check keys. It allows checking 
 multiple pressed keys by using conditionals like:
 (...) if (keys[90] && keys[49]) {...}
*/

var keysEnabled = true;

function disableKeys() {
  keysEnabled = false;
}
function enableKeys() {
  keysEnabled = true;
}


window.addEventListener("keydown", keysPressed, false);
window.addEventListener("keyup", keysReleased, false);
var keys = [];
function keysPressed(e) {
  // store an entry for every key pressed
  keys[e.keyCode] = true;


  if(keys[90] && keysEnabled) { // Z for Reset Selection
    e.preventDefault();
    // alert('Pressed R');
    for (i = 0; i < isSelected.length; i++) {
      removeClass(document.getElementById(isSelected[i]),'lightrow');
    }
    for (i = 0; i < toDelete.length; i++) {
      removeClass(document.getElementById(toDelete[i]),'deleteRed');
    }
    isSelected = [];
    toDelete = [];
  }


  if(keys[32] && keysEnabled) { // SPACE FOR CREATE CHUNK
    e.preventDefault();
    for (i = 0; i < isSelected.length; i++) {
      removeClass(document.getElementById(isSelected[i]), 'lightrow');
    }
    if(isSelected.length > 0) {
      addNewPhrase(isSelected)
    } else {
      keys[32] = false;
      alert('You must select at least one things to create an error.');
    }
    isSelected = [];
  }


  if(keys[8] && keysEnabled) { // BackSpace FOR DELETE CHUNKS
    e.preventDefault();
    if(toDelete.length > 0) {
      deleteChunks(toDelete)
    } else {
      keys[8] = false;
      alert('Select at least 1 thing to be able to delete!');
    }
  }


  if(keys[65] && keysEnabled) { // A - FOR 'ALL'
    e.preventDefault();
    var other = document.getElementsByClassName("unused");
    for (i = 0; i < other.length; i++) {
        current_data = other[i].dataset.value;
        isSelected.push(current_data); 
    }
    if(isSelected.length > 1) {
      addNewPhrase(isSelected)
    } else {
      keys[65] = false;
      alert('There is nothing else to link.');
    }
    isSelected = [];
  }


}
function keysReleased(e) {
    // mark keys that were released
    keys[e.keyCode] = false;
}


// this function allucinates a keyboard event
function triggerKeyboardEvent(el, keyCode) {
    var eventObj = document.createEventObject ?
        document.createEventObject() : document.createEvent("Events");
  
    if(eventObj.initEvent){
      eventObj.initEvent("keydown", true, true);
    }
  
    eventObj.keyCode = keyCode;
    eventObj.which = keyCode;
    
    el.dispatchEvent ? el.dispatchEvent(eventObj) : el.fireEvent("onkeydown", eventObj);
} 

</script>""")



print(HTML.status_bar(userID))
if userID not in valid_usernames:
    print("""<i class="icon-user-md pull-left icon-4x"></i> """)
    print("""We're sorry, but you need to have an active username 
             to be able to access this area.<br>
             Please click the Home button, on the right and 
             proceed to login.<br>""")
    print("</body>")
    print("</html>")
    sys.exit(0)


print("""<h4>Learner Corpus' Tagger</h4>\n """)
print(guidelines)

################################################################################
# SEARCH FORM
################################################################################
print("""<form id="goto" action="" method="post" 
          style="display:inline-block">""")
print("""<b>CorpusDB:</b>""")
print("""<select style='font-size:16px;' id="corpusdb" name="corpusdb">""")
corpusdb_in = False
for db in all_corpusdb():
    if db[0] == corpusdb:
        print("<option value ='%s' selected>%s</option>" % db)
        corpusdb_in = True
    else:
        print("<option value ='%s'>%s</option>" % db)
# This allows linking to a specific (not listed) CorpusDB
if corpusdb_in == False:
    print("<option value ='%s' selected>%s</option>" % (corpusdb,corpusdb))
print("""</select>""")
print("""<input type="text" name="sid" value="%s" size="9"
         pattern="[0-9]{1,}" onfocus="disableKeys();" 
         onblur="enableKeys();"/>""" % sid)
print("""</form>""")


# GO TO TAG-WORD
# print("""<form id="tagwords" action="tag-word.cgi" method="post" 
#          target="_blank" style="display:inline-block">""")
# print("""<input type="hidden" name="lang" value="%s"/>""" % lang)
# print("""<input type="hidden" name="corpus" value="%s"/>""" % corpusdb)
# print("""<input type="hidden" name="sid" value="%d"/>""" % int(sid))
# print("""<span><button class="small"><a href="javascript:{}"
#           onclick="document.getElementById('tagwords').submit();return false;"
#           style="text-decoration:none">
#          <span style="color: #4D99E0;font-size:15px;">Retag</span></a>
#          </button></span>""")
# print("""</form>""")


# PREVIOUS BUTTON
print("""<form id="prev_doc" action="" method="post" 
      style="display:inline-block">""")
print("""<input type="hidden" name="corpusdb" value="%s"/>""" % corpusdb)
print("""<input type="hidden" name="sid" value="%d"/>""" % ((int(sid) - 1)))
print("""<span><button class="small"><a href="javascript:{}"
          onclick="document.getElementById('prev_doc').submit();return false;"
          style="text-decoration:none">
         <span style="color: #4D99E0;font-size:15px;">Prev</span></a>
         </button></span>""")
print("""</form>""")

# NEXT BUTTON
print("""<form id="next_doc" action="" method="post" 
      style="display:inline-block">""")
print("""<input type="hidden" name="corpusdb" value="%s"/>""" % corpusdb)
print("""<input type="hidden" name="sid" value="%d"/>""" % (int(sid) + 1))
print("""<span><button class="small"><a href="javascript:{}"
          onclick="document.getElementById('next_doc').submit();return false;"
          style="text-decoration:none">
         <span style="color: #4D99E0;font-size:15px;">Next</span></a>
         </button></span>""")
print("""</form>""")


if docID is not None:
    # print("<a href='reader.cgi?docName={}&corpusdb={}' target='_blank'>".format(docN,corpusdb))
    print("[Document: " + str(docID) + "]")
    # print("</a>")






# NEW CHUNK
print("<br><br>")
print("""<span><button class="small"><a href="javascript:{}"
          onclick="triggerKeyboardEvent(document.body, 32);"
          style="text-decoration:none">
         <span style="color: #4D99E0;font-size:15px;">New Error</span></a>
         </button></span>""")

# Full Sentence
print("""<span><button class="small"><a href="javascript:{}"
          onclick="triggerKeyboardEvent(document.body, 65);"
          style="text-decoration:none">
         <span style="color: #4D99E0;font-size:15px;">Full Sentence</span></a>
         </button></span>""")

# Unselect
print("""<span><button class="small"><a href="javascript:{}"
          onclick="triggerKeyboardEvent(document.body, 90);"
          style="text-decoration:none">
         <span style="color: #4D99E0;font-size:15px;">Unselect</span></a>
         </button></span>""")

# Confirm Deletion
print("""<span><button class="small"><a href="javascript:{}"
          onclick="triggerKeyboardEvent(document.body, 8);"
          style="text-decoration:none">
         <span style="color: #4D99E0;font-size:15px;">Confirm Deletion</span></a>
         </button></span>""")



print("<hr style='margin-top:10px;margin-bottom:10px;'/>")





################################################################################
# SENTENCE / SENTIMENT FORM
################################################################################
for sid in sorted(sents[lang].keys()):

    # PRINT SENTENCE
    print("""<div style="line-height: 120%;">""")

    print("<b>Sentence:</b>")
    print(sents[lang][sid])
    print("<hr style='margin-top:10px;margin-bottom:10px;'/>")
    for wid in words[lang][sid].keys():
        (word,pos,lemma) = words[lang][sid][wid]

        # if senti_wid[sid][wid] > 0:
        #     wid_senti_style = """ style='border-bottom: 2px solid green;' """
        #     tooltip = """ class='tooltip' title='senti:%s' """ % senti_wid[sid][wid]
        # elif senti_wid[sid][wid] < 0:
        #     wid_senti_style = """ style='border-bottom: 2px solid red;' """
        #     tooltip = """ class='tooltip' title='senti:%s' """ % senti_wid[sid][wid]
        # else:

        wid_senti_style = ""
        tooltip = ""



        # if wid in used_wids:
        #     print("""<span style="color:green;">  <span %s %s>%s</span></span>
        #           """ % (wid_senti_style, tooltip, word))
        # else:
        Xid = 'wid' + str(wid)
        print("""<span class="unused" id='%s' data-value="%s"
                       onclick="addToBucket('%s');">
                  """ % (Xid,Xid,Xid))
        print("""<span %s %s >%s</span></span>""" %(wid_senti_style, tooltip, word))

    print("</div>")
    print("<hr style='margin-top:10px;margin-bottom:10px;'/>")
    # print("<hr>")



    print("""<table class="tight">""")
    for xid in chunks[lang][sid].keys():
        ####################################################################
        # SENTIMENT (TRIAL)
        ####################################################################
        # if chunks_senti[lang][sid][xid]:
        #     senti_score = chunks_senti[lang][sid][xid]
        if error_labels[lang][sid][xid]:
            error_lbl = error_labels[lang][sid][xid]
        else:
            error_lbl = None

        sentihtml = ""
        unique_id = "%s%s" % (sid, xid)
        sentihtml += """<form id="error_label_form%s"  method="get" 
        name="error_label_form" action="%s" style="display:inline;">

        <input type='hidden' name='cgi_mode' value='error_label'>

        <input type='hidden' name='corpus' value='%s'>
        <input type='hidden' name='lang' value='%s'>
        <input type='hidden' name='sid' value='%d'>
        <input type='hidden' name='eid' value='%d'>
        """ % (unique_id, 'edit-corpus.cgi', 
               corpusdb, lang, sid, xid)


        sentihtml += """<select style='font-size:15px;'
                         name="error_label"
                         onchange="document.getElementById('error_label_form%s').submit();">
                        <option value=''></option>""" % unique_id 

        for errgroup in sorted(error_set.keys()):
            sentihtml += "<optgroup label='{}'>".format(errgroup)
            for lbl in sorted(error_set[errgroup].keys()):
                if lbl == error_lbl:
                    sentihtml += """<option value="{}" selected>{}</option>
                             """.format(lbl, error_set[errgroup][lbl])
                else:
                    sentihtml += """<option value="{}">{}</option>
                             """.format(lbl, error_set[errgroup][lbl])
            sentihtml += "</optgroup>"
        sentihtml += "</select> </form>"





        # tag = tags[tsid][twid][cid][1]
        # sentihtml += u"""<input id="senti_score%s" 
        # name="senti_score" type="range" 
        # style="width:200px" min="-100" max="100" value="%d"
        # onchange="document.getElementById('senti_score_form%s').submit();">

        #    <table  class="tight" style="width:200px; height:10px; font-size:8px;">
        #          <tr><td bgcolor="#CD2626">1</td>
        #              <td bgcolor="#E26262">2</td>
        #              <td bgcolor="#EEA6A6">3</td>
        #              <td bgcolor="#FFFFFF">4</td>
        #              <td bgcolor="#94D994">5</td>
        #              <td bgcolor="#40B640">6</td>
        #              <td bgcolor="#228B22">7</td>
        #          </tr>
        #    </table>
        # </form>
        # """ % ( unique_id, senti_score, unique_id)
        ####################################################################


        Xid = 'eid' + str(xid)

        # IF THE CHUNK IS A SUBSET OF ANOTHER CHUNK
        # if xid in used_eids:
        #     print("""<tr id='%s' data-value="%s" >""" % (Xid,Xid))
        #     print("""<td>""")
        #     print("""<span style="color:green">""")
        #     for wid in sorted(chunks[lang][sid][xid]):
        #         print(words[lang][sid][wid][0])
        #     print("""</td>""")

        # # IF THE CHUNK MATCHES THE FULL SENTENCE
        # elif chunks[lang][sid][xid] == full_wid_set: 
        #     print("""<tr class="final" id='%s' data-value="%s" >
        #           """% (Xid,Xid))
        #     print("""<td>""")
        #     print("""<span>""")
        #     for wid in sorted(chunks[lang][sid][xid]):
        #         print(words[lang][sid][wid][0])
        #     print("""</span> """)
        #     print("""</td>""")

        # else:
        print("""<tr data-value="%s" id='%s' 
                       onclick="addToBucket('%s');">
                  """% (Xid,Xid,Xid))
        print("""<td>""")
        print("""<span>""")
        for wid in sorted(chunks[lang][sid][xid]):
            print(words[lang][sid][wid][0])
        print("""</span>""")
        print("""</td>""")


        # SENTIMENT COLUMN
        print("""<td style="width:300px">""")
        print(sentihtml)
        print("""</td>""")


        # COMMENT COLUMN
        print("""<td style="width:180px">""")
        print("""<form name="comment" id="comment%s" 
           style="display: inline;" action="edit-corpus.cgi" method="post">
           <input type="hidden" name="cgi_mode" value="error_comment"/>
           <input type="hidden" name="lang" value="%s"/>
           <input type="hidden" name="corpus" value="%s"/>
           <input type="hidden" name="sid" value="%s"/>
           <input type="hidden" name="eid" value="%s"/>
              """ %(xid,lang,corpusdb,sid,xid))

        if chunks_comm[lang][sid][xid]:
            comm = chunks_comm[lang][sid][xid]
        else:
            comm = ""

        print("""<span title="Comment"><textarea 
              style="width:150px;height:30px;" name="comment" 
              onfocus="disableKeys();" onblur="enableKeys();
              document.getElementById('comment%s').submit();"
              >%s</textarea>
              </span>""" %(xid,comm))

        print("""</form>""")
        print("""</td>""")


        # DELETE BUTTON
        print("""<td id='%s' onclick="addToDelBucket('%s');" 
                   style="width:30px" data-value="%s">
              """ % (Xid,Xid,Xid))
        print("""<i class="fa fa-times"></i>""")
        print("""</td>""")



        print("""</tr>""")
    print("""</table>""")



# (CREATE) NEW-ERROR (FORM)
print("""
<form name="linking" id="linking" 
   action="edit-corpus.cgi" method="post">
  <input type="hidden" name="cgi_mode" value="new_error"/>
  <input type="hidden" name="lang" value="%s"/>
  <input type="hidden" name="corpus" value="%s"/>
  <input type="hidden" name="sid" value="%s"/>
  <span id="linkContainer"></span>
</form></p>""" %(lang,corpusdb,sid))


# DELETE-ERRORS (FORM)
print("""
<form name="delete_chunks" id="delete_chunks" 
   action="edit-corpus.cgi" method="post">
  <input type="hidden" name="cgi_mode" value="delete_errors"/>
  <input type="hidden" name="lang" value="%s"/>
  <input type="hidden" name="corpus" value="%s"/>
  <input type="hidden" name="sid" value="%s"/>
  <span id="XlinkContainer"></span>
</form></p>""" %(lang,corpusdb,sid))


# BOTTOM LOG (breaks make sure there is enough space)
print("<br><br><br><br><br>")
print("""<span style="background-color: #FFFFFF;position:fixed; bottom:5px; right:5px;">""")
print("""%s""" % log_message)
print("""</span> """)



print("""</body></html>\n""")
