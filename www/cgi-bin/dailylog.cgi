#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FIXME(Wilson 18Mar2020): L356: Undefined variable 'sellangs' (undefined-variable)
FIXME(Wilson 18Mar2020): L358: Undefined variable 'lang' (undefined-variable)
FIXME(Wilson 18Mar2020): Using variable 'defs' before assignment
"""

import cgi, urllib
import cgitb; cgitb.enable()  # for troubleshooting
import re, sqlite3, collections
from collections import defaultdict as dd

import sys, codecs



form = cgi.FieldStorage()
mode = form.getfirst("mode", ()) # viewing mode
source = form.getfirst("source", "ntumc") # choose source, default is ntmuc
datefrom = form.getfirst("datefrom", ()) # start date
dateto = form.getfirst("dateto", ()) # end date
searchlang = form.getfirst("searchlang", "all") # language to specify search 
version = form.getfirst("version", "0.1")


### reference to self (.cgi)
wncgi = "dailylog.cgi"

### working .db (should be the extended OMW
wndb = "../db/wn-ntumc.db"

### reference to wn-grid (search .cgi)
omwcgi = "wn-gridx.cgi"


### Connect to and update the database
con = sqlite3.connect(wndb)
c = con.cursor()


### Languages

### from projects
langs = (
"eng", "ind", "jpn", "cmn", 

 # "zsm", "qcn",
     
 # "fas", "arb", "heb", "tha", "slv",
 # "ita", "por", "nob", "nno", "dan", 
 # "swe", "fra", "fin", "ell", "glg", 
 # "cat", "spa", "eus", "als", "pol",  
 
 
 
### from wikt & cldr
 # 'aar', 'afr', 'aka', 'als', 'amh', 
 # 'ang', 'arz', 'asm', 'ast', 'aze', 
 # 'bam', 'bel', 'ben', 'bod', 'bos', 
 # 'bre', 'bul', 'ces', 'chr', 'cor', 
 # 'cym', 'deu', 'dzo', 'epo', 'est', 
 # 'ewe', 'fao', 'fry', 'ful', 'fur', 
 # 'gla', 'gle', 'glv', 'grc', 'guj', 
 # 'hat', 'hau', 'hbs', 'hin', 'hrv', 
 # 'hun', 'hye', 'ibo', 'ido', 'iii', 
 # 'ina', 'isl', 'jer', 'kal', 'kan',
 # 'kat', 'kaz', 'khm', 'kik', 'kin', 
 # 'kir', 'kor', 'kur', 'lao', 'lat', 
 # 'lav', 'lin', 'lit', 'ltg', 'ltz', 
 # 'lub', 'lug', 'mal', 'mar', 'mkd', 
 # 'mlg', 'mlt', 'mon', 'mri', 'mya', 
 # 'nan', 'nav', 'nbl', 'nde', 'nep', 
 # 'nld', 'oci', 'ori', 'orm', 'pan', 
 # 'pol', 'pus', 'roh', 'ron', 'run', 
 # 'rup', 'rus', 'sag', 'san', 'scn', 
 # 'sin', 'slk', 'slv', 'sme', 'sna', 
 # 'som', 'sot', 'srd', 'srp', 'ssw', 
 # 'swa', 'tam', 'tat', 'tel', 'tgk', 
 # 'tgl', 'tir', 'ton', 'tsn', 'tso', 
 # 'tuk', 'tur', 'ukr', 'urd', 'uzb', 
 # 'ven', 'vie', 'vol', 'xho', 'yid', 
 # 'yor', 'yue', 'zul'
)

t = dd(lambda: dd(str))
## thing, lang, = label
t['eng']['eng'] = 'English'
t['eng']['ind'] = 'Inggeris'
t['eng']['zsm'] = 'Inggeris'
t['ind']['eng'] = 'Indonesian'
t['ind']['ind'] = 'Bahasa Indonesia'
t['ind']['zsm'] = 'Bahasa Indonesia'
t['zsm']['eng'] = 'Malaysian'
t['zsm']['ind'] = 'Bahasa Malaysia'
t['zsm']['zsm'] = 'Bahasa Malaysia'
t['msa']['eng'] = 'Malay'

t["swe"]["eng"] = "Swedish";
t["ell"]["eng"] = "Greek";
t["cmn"]["eng"] = "Chinese (simplified)";
t["qcn"]["eng"] = "Chinese (traditional)";
t['eng']['cmn'] = u'英语'
t['cmn']['cmn'] = u'汉语'
t['qcn']['cmn'] = u'漢語'
t['cmn']['qcn'] = u'汉语'
t['qcn']['qcn'] = u'漢語'
t['jpn']['cmn'] = u'日语'
t['jpn']['qcn'] = u'日语'


t['als']['eng'] = 'Albanian'
t['arb']['eng'] = 'Arabic'
t['cat']['eng'] = 'Catalan'
t['dan']['eng'] = 'Danish'
t['eus']['eng'] = 'Basque'
t['fas']['eng'] = 'Farsi'
t['fin']['eng'] = 'Finnish'
t['fra']['eng'] = 'French'
t['glg']['eng'] = 'Galician'
t['heb']['eng'] = 'Hebrew'
t['ita']['eng'] = 'Italian'
t['jpn']['eng'] = 'Japanese'
t['mkd']['eng'] = 'Macedonian'
t['nno']['eng'] = 'Nynorsk'
t['nob']['eng'] =  u'Bokmål'
t['pol']['eng'] = 'Polish'
t['por']['eng'] = 'Portuguese'
t['slv']['eng'] = 'Slovene'
t['spa']['eng'] = 'Spanish'
t['tha']['eng'] = 'Thai'


# wikt / cldr languages
t['aar']['eng'] = 'Afar'
t['afr']['eng'] = 'Afrikaans'
t['aka']['eng'] = 'Akan'
t['amh']['eng'] = 'Amharic'
t['ang']['eng'] = 'Old English (ca. 450-1100)'
t['arz']['eng'] = 'Egyptian Arabic'
t['asm']['eng'] = 'Assamese'
t['ast']['eng'] = 'Asturian'
t['aze']['eng'] = 'Azerbaijani'
t['bam']['eng'] = 'Bambara'
t['bel']['eng'] = 'Belarusian'
t['ben']['eng'] = 'Bengali'
t['bod']['eng'] = 'Tibetan'
t['bos']['eng'] = 'Bosnian'
t['bre']['eng'] = 'Breton'
t['bul']['eng'] = 'Bulgarian'
t['ces']['eng'] = 'Czech'
t['chr']['eng'] = 'Cherokee'
t['cor']['eng'] = 'Cornish'
t['cym']['eng'] = 'Welsh'
t['deu']['eng'] = 'German'
t['dzo']['eng'] = 'Dzongkha'
t['epo']['eng'] = 'Esperanto'
t['est']['eng'] = 'Estonian'
t['ewe']['eng'] = 'Ewe'
t['fao']['eng'] = 'Faroese'
t['fry']['eng'] = 'Western Frisian'
t['ful']['eng'] = 'Fulah'
t['fur']['eng'] = 'Friulian'
t['gla']['eng'] = 'Scottish Gaelic'
t['gle']['eng'] = 'Irish'
t['glv']['eng'] = 'Manx'
t['grc']['eng'] = 'Ancient Greek (to 1453)'
t['guj']['eng'] = 'Gujarati'
t['hat']['eng'] = 'Haitian'
t['hau']['eng'] = 'Hausa'
t['hbs']['eng'] = 'Serbo-Croatian'
t['hin']['eng'] = 'Hindi'
t['hrv']['eng'] = 'Croatian'
t['hun']['eng'] = 'Hungarian'
t['hye']['eng'] = 'Armenian'
t['ibo']['eng'] = 'Igbo'
t['ido']['eng'] = 'Ido'
t['iii']['eng'] = 'Sichuan Yi'
t['ina']['eng'] = 'Interlingua'
t['isl']['eng'] = 'Icelandic'
t['jer']['eng'] = 'Jere'
t['kal']['eng'] = 'Kalaallisut'
t['kan']['eng'] = 'Kannada'
t['kat']['eng'] = 'Georgian'
t['kaz']['eng'] = 'Kazakh'
t['khm']['eng'] = 'Central Khmer'
t['kik']['eng'] = 'Kikuyu'
t['kin']['eng'] = 'Kinyarwanda'
t['kir']['eng'] = 'Kirghiz'
t['kor']['eng'] = 'Korean'
t['kur']['eng'] = 'Kurdish'
t['lao']['eng'] = 'Lao'
t['lat']['eng'] = 'Latin'
t['lav']['eng'] = 'Latvian'
t['lin']['eng'] = 'Lingala'
t['lit']['eng'] = 'Lithuanian'
t['ltg']['eng'] = 'Latgalian'
t['ltz']['eng'] = 'Luxembourgish'
t['lub']['eng'] = 'Luba-Katanga'
t['lug']['eng'] = 'Ganda'
t['mal']['eng'] = 'Malayalam'
t['mar']['eng'] = 'Marathi'
t['mlg']['eng'] = 'Malagasy'
t['mlt']['eng'] = 'Maltese'
t['mon']['eng'] = 'Mongolian'
t['mri']['eng'] = 'Maori'
t['mya']['eng'] = 'Burmese'
t['nan']['eng'] = 'Min Nan Chinese'
t['nav']['eng'] = 'Navajo'
t['nbl']['eng'] = 'South Ndebele'
t['nde']['eng'] = 'North Ndebele'
t['nep']['eng'] = 'Nepali (macrolanguage)'
t['nld']['eng'] = 'Dutch'
t['oci']['eng'] = 'Occitan (post 1500)'
t['ori']['eng'] = 'Oriya (macrolanguage)'
t['orm']['eng'] = 'Oromo'
t['pan']['eng'] = 'Panjabi'
t['pus']['eng'] = 'Pushto'
t['roh']['eng'] = 'Romansh'
t['ron']['eng'] = 'Romanian'
t['run']['eng'] = 'Rundi'
t['rup']['eng'] = 'Macedo-Romanian'
t['rus']['eng'] = 'Russian'
t['sag']['eng'] = 'Sango'
t['san']['eng'] = 'Sanskrit'
t['scn']['eng'] = 'Sicilian'
t['sin']['eng'] = 'Sinhala'
t['slk']['eng'] = 'Slovak'
t['sme']['eng'] = 'Northern Sami'
t['sna']['eng'] = 'Shona'
t['som']['eng'] = 'Somali'
t['sot']['eng'] = 'Southern Sotho'
t['srd']['eng'] = 'Sardinian'
t['srp']['eng'] = 'Serbian'
t['ssw']['eng'] = 'Swati'
t['swa']['eng'] = 'Swahili (macrolanguage)'
t['tam']['eng'] = 'Tamil'
t['tat']['eng'] = 'Tatar'
t['tel']['eng'] = 'Telugu'
t['tgk']['eng'] = 'Tajik'
t['tgl']['eng'] = 'Tagalog'
t['tir']['eng'] = 'Tigrinya'
t['ton']['eng'] = 'Tonga (Tonga Islands)'
t['tsn']['eng'] = 'Tswana'
t['tso']['eng'] = 'Tsonga'
t['tuk']['eng'] = 'Turkmen'
t['tur']['eng'] = 'Turkish'
t['ukr']['eng'] = 'Ukrainian'
t['urd']['eng'] = 'Urdu'
t['uzb']['eng'] = 'Uzbek'
t['ven']['eng'] = 'Venda'
t['vie']['eng'] = 'Vietnamese'
t['vol']['eng'] = u'Volapük'
t['xho']['eng'] = 'Xhosa'
t['yid']['eng'] = 'Yiddish'
t['yor']['eng'] = 'Yoruba'
t['yue']['eng'] = 'Yue Chinese'
t['zul']['eng'] = 'Zulu'


t['hype']['eng'] = u'Hypernym:'
t['hypo']['eng'] = u'Hyponym:'
t['mprt']['eng'] = u'Meronym–Part:'
t['hprt']['eng'] = u'Holonym–Part:'
t['hmem']['eng'] = u'Holonym–Member:'
t['mmem']['eng'] = u'Meronym–Member:'
t['msub']['eng'] = u'Meronym–Substance:'
t['hsub']['eng'] = u'Holonym–Substance:'
t['dmnc']['eng'] = u'Domain–Category:'
t['dmtc']['eng'] = u'In Domain–Category:'
t['dmnu']['eng'] = u'Domain–Usage:'
t['dmtu']['eng'] = u'In Domain–Usage:'
t['dmnr']['eng'] = u'Domain–Region:'
t['dmtr']['eng'] = u'In Domain–Region:'
t['inst']['eng'] = u'Instance:'
t['hasi']['eng'] = u'Type:'
t['enta']['eng'] = u'Entails'
t['caus']['eng'] = u'Causes'
t['also']['eng'] = u'See also:'
t['sim']['eng']  = u'Similar to:'
t['attr']['eng'] = u'Attributes:'
t['eqls']['eng'] = u'Equals'
t['ants']['eng'] = u'Antonym:'
t['qant']['eng'] = u'Quantifies'
t['hasq']['eng'] = u'Quantifier:'



### translates language and link codes to human readable strings
def trans (word, lang = "eng"):
    if (t[word][lang]):
        return t[word][lang]
    elif (t[word]['eng']):
        return t[word]['eng']
    else:
        return word

# If searched has the form of a synset, 
# erase the lemma field and use it as a synset
if re.match('(\d+)-[avnr]', lemma):
    synset = lemma
    lemma = ''



### Language Selection File

# # List with values of selected languages
# sellangs = form.getlist('sellangs')

# # Stored in a txt file
# sellangs_path = 'sellangs.txt'

# # if there is no languages on sellang list, 
# if len(sellangs) == 0:
#     sellangs = []

#     # Create the file (if it doesn't already exist)
#     lastselected = open(sellangs_path, 'a+')
#     lastselected.close()

#     # Read selection stored in file
#     notes = open(sellangs_path).read()
#     for line in notes.split('\n'):
#         sellangs.append(line)
#     sellangs.remove("")    # delete any empty string in the list

# # (if some selection was made), overwrite lastselected file with these values
# else:
#     lastselected = open(sellangs_path, 'w')
#     for l in sellangs:
#         lastselected.write(l)
#         lastselected.write("\n")
#     lastselected.close()





########## HTML

### Header

print(u"""Content-type: text/html; charset=utf-8\n
<html>
 <head>
 <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
 <link href="../tag-wn.css" rel="stylesheet" type="text/css">
 <script src="../tag-wn.js" language="javascript"></script>
 <title>NTUMC Daily Logs %s</title>
 </head>
 <body>
""" % version)

### Javascript functions

# this creates the code to use as a language selection dropdown box
langdrop = ""
for l in sellangs:
    if l == "cmn": # pre-select cmn
        langdrop = langdrop + "<option value ='%s' selected>%s</option>" % (l, trans(l, lang))
    else:
        langdrop = langdrop + "<option value ='%s'>%s</option>" % (l, trans(l, lang))


linkdrop = "<option value =''>Change Me!</option>" # this is an html dropdown menu of all synlinks available

synlinks = ["hypo", "also", "hype", "inst", "hasi", "mmem", "msub", "mprt", "hmem", "hsub", "hprt", 
        "attr", "sim", "enta", "caus", "dmnc", "dmnu", "dmnr", "dmtc", "dmtu", "dmtr", "eqls","ants","qant", "hasq"]

for l in synlinks:
    linkdrop += "<option value ='%s'>%s</option>" %(l, trans(l))


print("""<script type="text/javascript">

function btn_reset() { window.parent.search.location.reload(); /* window.location.reload(); */ }

function addNewLemma() {
    var container = document.getElementById('lemmaContainer');
    var newDiv = document.createElement('div');
    var newText = document.createElement('input');
    newText.type = "text";
    newText.name = "lemmalst[]";
    newText.placeholder = "lemma";
        newText.required = "Yes";
    newText.size = "10";
        var selectLang = document.createElement('select');
        selectLang.innerHTML = "%s";
        selectLang.name = "lemmalangs[]";
    var newDelButton = document.createElement('input');
    newDelButton.type = "button";
    newDelButton.value = "-";
    newDiv.appendChild(selectLang);
    newDiv.appendChild(newText);
    newDiv.appendChild(newDelButton);
    container.appendChild(newDiv);
    newDelButton.onclick = function() { container.removeChild(newDiv); }
}
function addNewDef() {
    var container = document.getElementById('defContainer');
    var newDiv = document.createElement('div');
    var newText = document.createElement('textarea');
        newText.style.verticalAlign = "middle";
    newText.name = "deflst[]";
    newText.rows = "1";
        newText.cols = "20";
        newText.required = "Yes";
    newText.placeholder = "definition";
        var selectLang = document.createElement('select');
        selectLang.innerHTML = "%s";
        selectLang.name = "deflangs[]";
    var newDelButton = document.createElement('input');
    newDelButton.type = "button";
    newDelButton.value = "-";
    newDiv.appendChild(selectLang);
    newDiv.appendChild(newText);
    newDiv.appendChild(newDelButton);
    container.appendChild(newDiv);
    newDelButton.onclick = function() { container.removeChild(newDiv); }
}
function addNewEg() {
    var container = document.getElementById('egContainer');
    var newDiv = document.createElement('div');
    var newText = document.createElement('textarea');
        newText.style.verticalAlign = "middle";
    newText.name = "eglst[]";
    newText.rows = "1";
        newText.cols = "20";
        newText.required = "Yes";
    newText.placeholder = "example";
        var selectLang = document.createElement('select');
        selectLang.innerHTML = "%s";
        selectLang.name = "eglangs[]";
    var newDelButton = document.createElement('input');
    newDelButton.type = "button";
    newDelButton.value = "-";
    newDiv.appendChild(selectLang);
    newDiv.appendChild(newText);
    newDiv.appendChild(newDelButton);
    container.appendChild(newDiv);
    newDelButton.onclick = function() { container.removeChild(newDiv); }
}

function addNewRel() {
    var container = document.getElementById('synlinkContainer');
    var newDiv = document.createElement('div');
    var newText = document.createElement('input');
    newText.type = "text";
    newText.name = "linkedsyn[]";
        var selectRel = document.createElement('select');
        selectRel.innerHTML = "%s";
        selectRel.name = "synlink[]";
        selectRel.required = "Yes";
        newText.pattern = "[0-9]{8}-[avnr]";
    newText.placeholder = "linked synset";
        newText.title = "xxxxxxxx-a/v/n/r"
    newText.size = "10";
        newText.required = "Yes";
    var newDelButton = document.createElement('input');
    newDelButton.type = "button";
    newDelButton.value = "-";
        newDiv.appendChild(selectRel);
        newDiv.appendChild(newText);
    newDiv.appendChild(newDelButton);
    container.appendChild(newDiv);
    newDelButton.onclick = function() { container.removeChild(newDiv); }
}


function subandref(){ 
    document.forms[''].action='sellangs.cgi';
    document.forms[''].target='_new';
    document.forms[''].submit();
    setTimeout("window.parent.prog.location.reload();", 0);
    //return true;
}
</script>
""" % (langdrop, langdrop, langdrop, linkdrop))

### Fetch Everything Old & New from the database


# CREATE TABLE synset (synset text primary key,
#                   pos text,
#                      name text,
#              src text);
# CREATE TABLE synset_def (synset text,
#                          lang text,
#              def text,
#                          sid text);
# CREATE TABLE synset_ex (synset text,
#             lang text,
#             def text,
#                         sid text);



### Fetching Synsets

c.execute(""" SELECT synset, pos, name, src FROM synset 
              WHERE src in (?) """, [source] )

rows = c.fetchall()

ssdict = collections.defaultdict(list)

for r in rows:
    ssdict[r[0]] = []
           
    if r[0] in sellangs:
        if r[2] != "old":
            defs[r[0]].append(r[1].replace('"', '&quot;'))
            




if (synset): 

### get data
    ## Defs
    c.execute("SELECT lang, def, status FROM synset_def WHERE synset = ?", (synset,))
    rows = c.fetchall()

    defs = collections.defaultdict(list)
    for r in rows:
        if r[0] in sellangs:
            if r[2] != "old":
                defs[r[0]].append(r[1].replace('"', '&quot;'))

    ## Examples
    c.execute("SELECT lang, def, status FROM synset_ex WHERE synset = ?", (synset,))
    rows = c.fetchall()

    exes = collections.defaultdict(list)
    for r in rows:
        if r[0] in sellangs:
            if r[2] != "old":
                exes[r[0]].append(r[1].replace('"', '&quot;'))
    ## Words
    c.execute(""" select sense.lang, lemma, freq, sense.status, confidence from word 
                      left join sense on word.wordid = sense.wordid where synset = ? ORDER BY freq DESC """, (synset,))
    rows = c.fetchall()

    words = collections.defaultdict(list)

    for r in rows:  # [lang][i] = (lemma, freq)
        if r[0] in sellangs:
            if r[3] != "old":
                words[r[0]].append((r[1], r[2],r[4]))

    ## relations
    c.execute("""select link, synset2, name, synlink.status from synlink 
                  left join synset on synlink.synset2 = synset.synset where synset1 = ?""", 
          (synset,))
    rows = c.fetchall()
    rels = collections.defaultdict(list)
    for r in rows:  # [link][i] = (synset, name)
        if r[3] != "old":
            rels[r[0]].append((r[1], r[2]))


### Prints Fetched Data:

    print("""<h2>Synset <a href="wn-gridx.cgi?synset=%s">%s</a></h3> """ % (synset, synset))


### Add new information to the WN (!= correcting existing entries)

    print("""<hr>
        <p><strong>Add new information to this entry:</strong>
    <p><form action="editwordnet.cgi" method="post" target="cgenesis"  onsubmit="setTimeout('location.reload()',500); return true;" >
    <input type="hidden" name="deleteyn" value="add"/>
    <input type="hidden" name="synset" value="%s"/>
    <select id="lemmalang" name="lemmalangs[]">
    """ % synset)

    for l in sellangs:
        if l  == "cmn":  ### label things with the query's own language label
            print(""" <option value ="%s" selected> %s """ % (l, trans(l, lang)))
        else:
            print(""" <option value ="%s"> %s """ % (l, trans(l, lang)))
    print("""</select><!--
    --><span id="lemmaContainer"><span><input type="text" name="lemmalst[]" placeholder="lemma" size="10" /><!--
        --><input type="button" value="+" onClick="addNewLemma()"></span></span>



    <div id="defContainer"><div>
    <select id="deflang" name="deflangs[]">""")
    for l in sellangs:
        if lang == l:  ### label things with the query's own language label
            print("    <option value ='%s' selected>%s" % (l, trans(l, lang)))
        else:
            print("    <option value ='%s'>%s" % (l, trans(l, lang)))
    print("""</select><!--
              --><textarea rows="1" cols="20" name="deflst[]" style="vertical-align:middle" placeholder="definition" ></textarea><!--
        --><input type="button" value="+" onClick="addNewDef()"></div></div>



    <div id="egContainer"><div>
    <select id="eglang" name="eglangs[]">""")

    for l in sellangs:
        if lang == l:  ### label things with the query's own language label
            print("    <option value ='%s' selected>%s" % (l, trans(l, lang)))
        else:
            print("    <option value ='%s'>%s" % (l, trans(l, lang)))
    print("""</select><!--
        --><textarea rows="1" cols="20" name="eglst[]" style="vertical-align:middle" placeholder="example" ></textarea><!--
        --><input type="button" value="+" onClick="addNewEg()"></div></div>


         <div id="synlinkContainer"><select id="synlink" name="synlink[]"> 

         <option value =''>Change Me!</option>""" )

    synlinks = ["hypo", "also", "hype", "inst", "hasi", "mmem", "msub", "mprt", "hmem", "hsub", "hprt", 
            "attr", "sim", "enta", "caus", "dmnc", "dmnu", "dmnr", "dmtc", "dmtu", "dmtr", "eqls","ants","qant","hasq"]

    for l in synlinks:
        print("<option value ='%s'>%s</option>" %(l, trans(l)))

    print("""</select><!--
           --><input type="text" name="linkedsyn[]" placeholder="linked synset" 
              pattern="[0-9]{8}-[avnr]" title = "xxxxxxxx-a/v/n/r" size="10"/><!--
              --><input type="button" value="+" onClick="addNewRel()"></div><div></div>
              """)

    print("""<input type="submit" value="Add to synset"/>
             </form><hr>
              """)


    # ### Images
    # for sid in defs['img']:
    #     print "<img align='right' width=200 src ='../wn-ocal/img/%s.png' alt='%s'>" % (defs['img'][sid], defs['img'][sid])

    
    ### Words (Lemmas)
    print("<h4>Lemmas</h4>")
    print("""<table>""")
    for l in words:

        print("<tr> \n  <td><strong> %s </strong></td>" % trans(l, lang) )

        print("""  <form action="editwordnet.cgi" method="post" target="cgenesis"  
                           onsubmit="setTimeout('location.reload()',500); return true;">
                   <input type="hidden" name="synset" value="%s"/> \n  
                           <input type="hidden" name="lang" value="%s" /> \n  
                           <input type="hidden" name="deleteyn" value="mod"/>
                      """ % (synset, l))


        ws = list()   # list to store html entries of each word

        # for (word, frequency) in the list of lemmas per language (l)
        for (w,f,c) in words[l]:

            # append html code of each lemma as a text input form
            ws.append("""<input type="hidden" name="lemmao[]" value="%s"/>
                                     <input type="hidden" name="confo[]" value="%f"/><!--
                                     --><nobr><span title="Lemma"><!--
                                     --><input type="text" size="%d" name="lemman[]" value="%s"/></span><!--
                                     --><span title="Confidence"><!--
                                     --><input type="text" size="3" name="confn[]" value="%0.2f"
                                      pattern="(0(\.[0-9]*)?)|1(\.[0]*)?" title="A number between 0.0 and 1.0" "/></span><!--
                                  """ %(w, c, len(w)+1, w, c))


            # append frequency information (if there is some)
            if f: 
                ws.append("""--><span style="font-size:80%%" title="Frequency"><sub>%d</sub></span><!--""" % f)
                
                deleteme = "✘"
            # delete me button
            ws.append("""--><span style="font-size:85%%" title="Delete lemma"><!--
                       --><a href="editwordnet.cgi?deleteyn=mod&synset=%s&lang=%s&lemmao[]=%s&lemman[]=delete!&confo[]=%s&confn[]=%s"                                                             style="color:red" target="_blank"
                                               onClick="setTimeout('location.reload()',500)">%s</a></span></nobr>;&nbsp;&nbsp;&nbsp;
                                   """ % (synset, l, urllib.parse.quote(w), c, c,deleteme))

        # prints the html list of lemmas 
        print("""  <td><i> \n %s \n </i></td>""" % ("\n  ".join(ws)))
        
        print("""   <td><input type="submit" value="Update"/></td>\n  </form>
                    </tr> <tr><td></td></tr> <tr><td></td></tr> <tr><td></td></tr>
                            <tr><td></td></tr> <tr><td></td></tr> <tr><td></td></tr>
                      """)
    # closes word(lemmas) table
    print("</table>")


    ### Definitions
    print("<hr>")
    print("<h4>Definitions</h4>")
    print("<dl>")
    for l in defs.keys():
        if l == 'img':
            continue
        print("<dt><strong>%s</strong>" % trans(l, lang) )
        print("<dd>")
        print(""" <form action="editwordnet.cgi" method="post" target="cgenesis" onsubmit="setTimeout('location.reload()',500); return true;">""")
        print(""" <input type="hidden" name="synset" value="%s"/>\n  
                          <input type="hidden" name="lang" value="%s"/>\n  
                          <input type="hidden" name="deleteyn" value="mod"/>
                      """ %(synset,l))

        for d in defs[l]:
            print("""  <input type="hidden" name="defo[]" value="%s"/>
                                   <input type="hidden" name="defelangs[]" value="%s"/>
                                   <textarea rows="2" cols="30" name="defn[]">%s</textarea>
 				  """ %(d,l,d))
        print("""  <input type="submit" value="Update"/>\n  </form>""")
    print("</dl>")

    ### Examples
    print("<hr>")
    print("<h4>Examples</h4>")
    print("<dl>")
    for l in exes.keys():
        if l == 'img':
            continue
        print("<dt><strong>%s</strong>" % trans(l, lang) )
        print("<dd>")
        print("""<form action="editwordnet.cgi" method="post" target="cgenesis" onsubmit="setTimeout('location.reload()',500); return true;">""")
        print("""<input type="hidden" name="synset" value="%s"/>
                         <input type="hidden" name="lang" value="%s"/>
                         <input type="hidden" name="deleteyn" value="mod"/>""" %(synset,l))

        for d in exes[l]:
            print(""" <input type="hidden" name="exeo[]" value="%s"/>
                                  <input type="hidden" name="exeelangs[]" value="%s"/>
                                  <textarea rows="1" cols="30" name="exen[]">%s</textarea>
                             """ %(d,l,d))
        print("""  <input type="submit" value="Update"/>\n  </form>""")
    print("</dl>")


    ### Relations
    if rels: # rels {link {synset2, name}}
        print("<hr>")
        print("<h4>Relations</h4>")
        print("<table>")

        print("""  <form action="editwordnet.cgi" method="post" target="cgenesis" onsubmit="setTimeout('location.reload()',500); return true;">""")
        print("""  <input type="hidden" name="synset" value="%s"/>
                           <input type="hidden" name="lang" value="%s"/>
                           <input type="hidden" name="deleteyn" value="mod"/>""" %(synset,l))

        print(""" <div id="synlinkContainer2"> """)

        synlinks = ["also", "hype", "inst", "hypo", "hasi", "mmem", "msub", "mprt", "hmem", "hsub", "hprt", 
                "attr", "sim", "enta", "caus", "dmnc", "dmnu", "dmnr", "dmtc", "dmtu", "dmtr", "eqls","ants","qant","hasq"]

        deleteme = "✘"

        for r in rels:
            for (osynset, name) in rels[r]:
                print("""<tr></td>""")
                print("""<nobr><select id="synlink" name="synlink[]">""")
                for l in synlinks:
                    if r == l:
                        print("""<option value ='%s' selected>%s</option>""" %(l, trans(l)))
                    else:
                        print("""<option value ='%s'>%s</option>""" %(l, trans(l)))
                print("""</select><input type="hidden" name="synlinko[]" value="%s"/><!--""" % r)

                print("""--><span title= %s><input type="hidden" name="linkedsyno[]" value="%s"/><!--
                                         --><input type="text" size="9" name="linkedsyn[]" 
                                           pattern="[0-9]{8}-[avnr]" title="xxxxxxxx-a/v/n/r" value="%s"/></span><!--
                                         --></td></tr><!--""" % (name, osynset, osynset))

                print("""--><span style="font-size:85%%" title="Delete link"><!--
           --><a href="editwordnet.cgi?deleteyn=mod&synset=%s&lang=%s&synlinko[]=%s&synlink[]=delete!&linkedsyn[]=%s&linkedsyno[]=%s"                            style="color:red" onClick="setTimeout('location.reload()',500)" target="_blank">%s</a></span></nobr>;&nbsp;&nbsp;&nbsp;
                                      """ % (synset, l, r, osynset, osynset, deleteme))


        print("</table>")
        print("""  <input type="submit" value="Update"/></form> """ )






### Add new information to the WN (!= correcting existing entries)

    # print """<hr>
        # <p><strong>Add new information to this entry:</strong>
    # <p><form action="editwordnet.cgi" method="post" target="cgenesis">
    # <input type="hidden" name="deleteyn" value="add"/>
    # <input type="hidden" name="synset" value="%s"/>
    # <select id="lemmalang" name="lemmalangs[]">
    # """ %synset

    # for l in sellangs:
    #     if lang == l:  ### label things with the query's own language label
    #         print "    <option value ='%s' selected>%s" % (l, trans(l, lang))
    #     else:
    #         print "    <option value ='%s'>%s" % (l, trans(l, lang))
    # print """</select><!--
    # --><span id="lemmaContainer"><span><input type="text" name="lemmalst[]" placeholder="lemma" size="10" /><!--
        # --><input type="button" value="+" onClick="addNewLemma()"></span></span>



    # <div id="defContainer"><div>
    # <select id="deflang" name="deflangs[]">"""
    # for l in sellangs:
    #     if lang == l:  ### label things with the query's own language label
    #         print "    <option value ='%s' selected>%s" % (l, trans(l, lang))
    #     else:
    #         print "    <option value ='%s'>%s" % (l, trans(l, lang))
    # print """</select><!--
        # --><input type="text" name="deflst[]" placeholder="definition" size="20" /><!--
        # --><input type="button" value="+" onClick="addNewDef()"></div></div>



    # <div id="egContainer"><div>
    # <select id="eglang" name="eglangs[]">"""
    # for l in sellangs:
    #     if lang == l:  ### label things with the query's own language label
    #         print "    <option value ='%s' selected>%s" % (l, trans(l, lang))
    #     else:
    #         print "    <option value ='%s'>%s" % (l, trans(l, lang))
    # print """</select><!--
        # --><input type="text" name="eglst[]" placeholder="example" size="20" /><!--
        # --><input type="button" value="+" onClick="addNewEg()"></div></div>


        #   <div id="synlinkContainer"><select id="synlink" name="synlink[]">""" 

    # synlinks = ["also", "hype", "inst", "hypo", "hasi", "mmem", "msub", "mprt", "hmem", "hsub", "hprt", 
    #         "attr", "sim", "enta", "caus", "dmnc", "dmnu", "dmnr", "dmtc", "dmtu", "dmtr"]

    # for l in synlinks:
    #     print "<option value ='%s'>%s</option>" %(l, trans(l))

    # print """</select><!--
     #       --><input type="text" name="linkedsyn[]" placeholder="linked synset" size="10"/><!--
        #       --><input type="button" value="+" onClick="addNewRel()"></div><div></div>
        #       """

      # print """<input type="submit" value="Add to synset"/>
    # </form>
    # """



### THE INPUT SHOULD NEVER BE A LEMMA

# ### If the input was a lemma

# elif (lemma):   ## Show all the entries for this lemma, in this language
#     print u"<h2>Results for «&#8239;%s&#8239;» (%s)</h2>\n" % (lemma, lang)
#     ## note the use of narrow non-breaking spaces

#     ## order the synsets by sense frequency
#     c.execute("SELECT synset, freq FROM word LEFT JOIN sense ON word.wordid = sense.wordid WHERE lemma = ? AND sense.lang = ? ORDER BY freq DESC", (lemma.strip(), lang))  ## lemma, lang

#     row = c.fetchall()
#     if row:
#         print "<table>"
#         for s in row:
#             synset = s[0]
#             print "  <tr>"

#             ## Image
#             print "   <td>"
#             c.execute("SELECT def FROM synset_def WHERE synset = ? AND lang = ?", (synset, 'img'))
#             imgs = c.fetchone()
#             if (imgs):
#                 img = imgs[0]
#                 print "<img align=top  height=40 src ='../wn-ocal/img/%s.png' alt='%s'>" % (img, img)
#                 print "    </td>";

#             ## Synset (with a link to search for this synset)
#             print "    <td valign='top'><a href='%s?synset=%s&lang=%s'>%s" %  (wncgi, synset, lang, synset)
#             print "</a></td>"
#             print "    <td valign='top'>"
#             if s[1] > 0: ### frequency
#                 print "(%d)" %  s[1] 
#             print "    </td>"


#             ## Words
#             ## order the lemmas by sense frequency
#             c.execute("SELECT lemma FROM word JOIN sense ON word.wordid = sense.wordid WHERE synset = ? AND sense.lang = ? ORDER BY freq DESC", 
#                   (synset, lang))
#             words = [w[0] for w in c.fetchall()]
#             print "<td valign='top'><i>",
#             print ", ".join(words)
#             print "</i></td>";

#             ## defs
#             print "   <td>"
#             c.execute("SELECT sid, def FROM synset_def WHERE synset = ? AND lang = ? ORDER BY sid", (synset, lang))
#             defs = [d[1] for d in c.fetchall()]
#             if (defs):
#                 print "<td  valign='top'>",
#                 print "; ".join(defs)
#                 print "</td>";

#             print "  </tr>"
#         print "</table>"
#     else:
#         print u"<p>No synsets found containing «&#8239;%s&#8239;» (%s) in the wordnets!" % (lemma, lang) 


### If there is no input (or it is left blank), print the welcome message
else:
    print("<h2>Welcome to the Open Multi-lingual Wordnet (%s)</h2>\n" % version)




### Search Form (always visible below)

# Runs wncgi script with new lemma and lang values
print("""
<hr><p>
  <form method="get" action="%s">

    <strong>Lookup Word (or Synset):</strong>
      <input type="text" name="lemma" value="%s" size=10 maxlength=30>

    <strong>Language</strong>: 
      <select name="lang" size="1">

""" % (omwcgi, lemma))

# For every lang (language code) in the sellang file, 
# Allow searching the wordnet with it

for l in sellangs:
    if lang == l:  # label things with the query's own language label
        print("    <option value ='%s' selected>%s" % (l, trans(l, lang)))
    else:
        print("    <option value ='%s'>%s" % (l, trans(l, lang)))

print("""
</select>
<input type="submit" name="Query" value="Search Wordnet">
  </form></p>
""")



### Language Selection Form

# Runs wncgi with updated language selection (sellangs)
print("""
<hr><p>
  <form action='%s' method="post">
     <strong>Language Selection:</strong><br>
""" % (wncgi))

# Show each language in langs list as a checkbox (most are commented out!)
for l in langs:
    print('<input type="checkbox" name="sellangs" value="%s"' %l)

    # if a language was previously on sellangs, show these languages as checked
    if l in sellangs:
        print('checked="checked"')

    # the translation is what it is printed to the html
    print('>%s' %trans(l, lang))

# Submit button
print("""
<br><input type="submit" value="Update Language Selection"/>
</form>
</p>
""")



### General Info (always visible below)
print("""
<hr><p>
<a href='http://compling.hss.ntu.edu.sg/omw/'>More detail about the wordnets</a>, 
including links to the data, licenses and statistics about the wordnets.
<br> Maintainer: <a href="http://www3.ntu.edu.sg/home/fcbond/">Francis Bond</a>
&lt;<a href="mailto:bond@ieee.org">bond@ieee.org</a>&gt;
""")



### Close HTML
print("""  
</body>
</html>
""")

