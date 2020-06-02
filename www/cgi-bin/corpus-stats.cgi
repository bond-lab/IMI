#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
import cgitb; cgitb.enable()  # for troubleshooting

import sqlite3, codecs
from collections import defaultdict as dd

import nltk
from nltk.corpus import wordnet as pwn

form = cgi.FieldStorage()

# It allows selecting what part of the corpus to compare
sid_from = form.getfirst("sid_from", 11000)
sid_to = form.getfirst("sid_to", 11609)

# Tags to look for
search = form.getfirst("search")

# It allows to compare up to 4 databases
dba = form.getfirst("dba", "../db/enga.db")
dbb = form.getfirst("dbb", "../db/engb.db")
dbc = form.getfirst("dbc", "../db/engc.db")
dbd = form.getfirst("dbd", "../db/engd.db")  # old eng.db (renamed to engd.db)

usr = form.getfirst("usr", "")  # if it finds a user, will use it in links

def norm(tag):
    """This function was used to normalize tags used to tag concepts. 
       FIXME!(some of these are not used anymore)"""
    if tag is None:
        return 'N'
    elif tag in ['s', 'u']:
        return 'w'
    elif tag in ['m', 'p']:
        return 'x'
    return tag

# wncgi = 'http://172.21.174.40/~bond/cgi-bin/wn-msa.cgi?synset='
# wnwcgi = 'http://172.21.174.40/~bond/cgi-bin/wn-msa.cgi?term='
# wnsidcgi='http://172.21.174.40/~bond/cgi-bin/tagz/tag-text.cgi?corpus=eng-story-gold&sid='

wncgi = "wn-gridx.cgi?gridmode=ntumc-noedit&synset="
wncgi_lemma = "wn-gridx.cgi?gridmode=ntumc-noedit&lang=eng&lemma="

tag_sidA = "http://172.21.174.40/ntumc/cgi-bin/tag-word.cgi?corpus=enga&lang=eng&usrname_cgi=%s&gridmode=ntumc-noedit&sid=" % usr
tag_sidB = "http://172.21.174.40/ntumc/cgi-bin/tag-word.cgi?corpus=engb&lang=eng&usrname_cgi=%s&gridmode=ntumc-noedit&sid=" % usr
tag_sidC = "http://172.21.174.40/ntumc/cgi-bin/tag-word.cgi?corpus=engc&lang=eng&usrname_cgi=%s&gridmode=ntumc-noedit&sid=" % usr

tag_sidENG = "http://172.21.174.40/ntumc/cgi-bin/tag-word.cgi?corpus=eng&lang=eng&usrname_cgi=%s&gridmode=ntumc-noedit&sid=" % usr  # this is not database D, this is a link to the new db


def s_color(num):
    """This functions takes a float number, 
    trims it to n decimals places without rounding it,  
    and assigns color according to it."""
    
    n = 2
    if num < 0.5:
        return ('<span style="color:red">%.*f</span>' % (n + 1, num))[:-1]
    elif num < 0.7:
        return ('<span style="color:orange">%.*f</span>' % (n + 1, num))[:-1]
    elif num < 1:
        return ('<span style="color:blue">%.*f</span>' % (n + 1, num))[:-1]
    else:  # #008000 = green
        return ('<span style="color:#008000">%.*f</span>' % (n + 1, num))[:-1]


# FIXME! The definition is not working in my local machine!
def link(tag, ref):
    """This function transforms a tag into a link to the wn-gridx
       It takes a tag (ideally a synset), and a ref (???) as argument"""
    title = '';
    href = '';
    tag = norm(tag)

    if tag and len(tag) == 10:  # Check if tag looks like a synset
        href = " class='fancybox fancybox.iframe' href='%s%s' "  % (wncgi, tag)
# fancybox fancybox.iframe
        try:
            ss = pwn.of2ss(tag)
        except:
            pass
        else:
            title = " title='%s'" % ss.definition

    if ref and tag == ref:  # #008000 = green
        return "<a style='color:#008000;'%s%s>%s</a>" % (href, title, tag)  # ref & tag match = Green
    elif ref:
        return "<a style='color:crimson;'%s%s>%s</a>" % (href, title, tag)  # if ref = red
    else:
        return "<a style='color:black;'%s%s>%s</a>" % (href, title, tag)  # else black?

def linkw(word):
    """This function turns a word into a link for a lemma search in the wordnet"""
    return """<a class='fancybox fancybox.iframe' style='color:black;text-decoration:none;' 
              href='%s%s'>%s</a>""" % (wncgi_lemma, word, word)


##########################
# FETCH sentences BY sid
##########################
conn_dba = sqlite3.connect(dba)
a = conn_dba.cursor()

sent = dict()
a.execute( """SELECT sid, sent
              FROM  sent
              WHERE sid >= ? AND sid <= ?""", (sid_from, sid_to) )
for (sid, s) in a:
    sent[sid] = s

######################
# FETCH concept tags
######################

# DATA stores the tags for comparison!
data = dd(lambda: dd(lambda: dd(lambda: dd(str))))  # agregates data by sentence
data_ag = dd(lambda: dd(lambda: dd(lambda: dd(str))))  # agreegates all data
ag_scores = dd(lambda: dd(int))  # e.g. {sid: {'AvsS' : 0.8} }

# TAGGER 
tagger = dict()

concept_query = """SELECT sid, cid, clemma, tag, tags, 
                          comment, usrname 
                   FROM concept 
                   WHERE sid >= ? AND sid <= ? 
                   ORDER BY sid, cid"""



# DATABASE A (connected on Sentences)
a.execute(concept_query, (sid_from, sid_to))
for (sid, cid, clemma, tag, tags, comment, usrname) in a:
    data[sid][cid]['a']['tag'] = str(tag).strip()
    data[sid][cid]['a']['tags'] = str(tags).strip()
    data[sid][cid]['a']['clem'] = str(clemma).strip()
    data[sid][cid]['a']['com'] = comment
    data[sid][cid]['a']['usr'] = usrname

    sidcid = str(sid) + '_' + str(cid)
    data_ag['all'][sidcid]['a']['tag'] = str(tag).strip()
    data_ag['all'][sidcid]['a']['clem'] = str(clemma).strip()


# DATABASE B
connb = sqlite3.connect(dbb)
b = connb.cursor()
b.execute(concept_query, (sid_from, sid_to))

for (sid, cid, clemma, tag, tags, comment, usrname) in b:
    data[sid][cid]['b']['tag'] = str(tag).strip()
    data[sid][cid]['b']['tags'] = str(tags).strip()
    data[sid][cid]['b']['clem'] = str(clemma).strip()
    data[sid][cid]['b']['com'] = comment
    data[sid][cid]['b']['usr'] = usrname

    sidcid = str(sid) + '_' + str(cid)
    data_ag['all'][sidcid]['b']['tag'] = str(tag).strip()
    data_ag['all'][sidcid]['b']['clem'] = str(clemma).strip()


# DATABASE C
connc = sqlite3.connect(dbc)
c = connc.cursor()
c.execute(concept_query, (sid_from, sid_to))

for (sid, cid, clemma, tag, tags, comment, usrname) in c:
    data[sid][cid]['c']['tag'] = str(tag).strip()
    data[sid][cid]['c']['tags'] = str(tags).strip()
    data[sid][cid]['c']['clem'] = str(clemma).strip()
    data[sid][cid]['c']['com'] = comment
    data[sid][cid]['c']['usr'] = usrname

    sidcid = str(sid) + '_' + str(cid)
    data_ag['all'][sidcid]['c']['tag'] = str(tag).strip()
    data_ag['all'][sidcid]['c']['clem'] = str(clemma).strip()


# DATABASE D
conng = sqlite3.connect(dbd)
g = conng.cursor()
g.execute(concept_query, (sid_from, sid_to))

for (sid, cid, clemma, tag, tags, comment, usrname) in g:
    data[sid][cid]['g']['tag'] = str(tag).strip()
    data[sid][cid]['g']['tags'] = str(tags).strip()
    data[sid][cid]['g']['clem'] = str(clemma).strip()
    data[sid][cid]['g']['com'] = comment
    data[sid][cid]['g']['usr'] = usrname

    sidcid = str(sid) + '_' + str(cid)
    data_ag['all'][sidcid]['g']['tag'] = str(tag).strip()
    data_ag['all'][sidcid]['g']['clem'] = str(clemma).strip()




sidcid_ew = dd(list) # e.g. {sid: cid}
sidcid_e = dd(list) # e.g. {sid: cid}
sidcid_w = dd(list) # e.g. {sid: cid}
lemma_sidcid_ew = dd(list)
lemma_sidcid_e  = dd(list)
lemma_sidcid_w  = dd(list)
for sid in sorted(data.keys()):  # for sentence in selected range
    for cid in data[sid].keys():  # for each concept in the sentence

        atag = str(data[sid][cid]['a']['tag']).strip()
        btag = str(data[sid][cid]['b']['tag']).strip()
        ctag = str(data[sid][cid]['c']['tag']).strip()
        gtag = str(data[sid][cid]['g']['tag']).strip()
        lemma = str(data[sid][cid]['a']['clem']).strip()
        tagset = set([atag, btag, ctag, gtag])
        sidcid = str(sid) + '_' + str(cid)

        if 'e' in tagset:
            if cid not in sidcid_ew[sid]:
                sidcid_ew[sid].append(cid)
            if cid not in sidcid_e[sid]:
                sidcid_e[sid].append(cid)
            if sidcid not in lemma_sidcid_ew[lemma]:
                lemma_sidcid_ew[lemma].append(sidcid)
            if sidcid not in lemma_sidcid_e[lemma]:
                lemma_sidcid_e[lemma].append(sidcid)

        if 'w' in tagset:
            if cid not in sidcid_ew[sid]:
                sidcid_ew[sid].append(cid)
            if cid not in sidcid_w[sid]:
                sidcid_w[sid].append(cid)
            if sidcid not in lemma_sidcid_ew[lemma]:
                lemma_sidcid_ew[lemma].append(sidcid)
            if sidcid not in lemma_sidcid_w[lemma]:
                lemma_sidcid_w[lemma].append(sidcid)


bylemma = False
if search == "ew":
    searchdict = sidcid_ew
elif search == "ewbylemma":
    searchdict = lemma_sidcid_ew
    bylemma = True
elif search == "ebylemma":
    searchdict = lemma_sidcid_e
    bylemma = True
elif search == "wbylemma":
    searchdict = lemma_sidcid_w
    bylemma = True
elif search == "e":
    searchdict = sidcid_e
elif search == "w":
    searchdict = sidcid_w
else:
    searchdict = dict()


# SILVER DATA (May be failing to pass values on data_ag!!!)
for sid in sent.keys():
    for cid in data[sid].keys():  # each concept used in sentence

        tags = [data[sid][cid]['a']['tag'],
                data[sid][cid]['b']['tag'],
                # data[sid][cid]['c']['tag'],
                data[sid][cid]['g']['tag']]
        mx = max(tags.count(t) for t in tags)

        if mx > 1:  # IF THERE WAS A MINIMUM AGREEMENT
            majtag =  [t for t in tags if tags.count(t) == mx][0]

            if majtag == "None":
                majtag = '?'

            data[sid][cid]['s']['tag'] = majtag

            sidcid = str(sid) + '_' + str(cid)
            data_ag['all'][sidcid]['s']['tag'] = majtag

        else:
            data[sid][cid]['s']['tag'] = '?'  # NO AGREEMENT
            data_ag['all'][sidcid]['s']['tag'] = '?'



########
# HTML
########

# Header
print(u"""Content-type: text/html; charset=utf-8\n
         <!DOCTYPE html>\n
           <html>\n
           <head>

	<!-- Add jQuery library -->
	<script type="text/javascript" src="../fancybox/lib/jquery-1.10.1.min.js"></script>

	<!-- Add mousewheel plugin (this is optional) -->
	<script type="text/javascript" src="../fancybox/lib/jquery.mousewheel-3.0.6.pack.js"></script>

	<!-- Add fancyBox main JS and CSS files -->
	<script type="text/javascript" src="../fancybox/source/jquery.fancybox.js?v=2.1.5"></script>
	<link rel="stylesheet" type="text/css" href="../fancybox/source/jquery.fancybox.css?v=2.1.5" media="screen" />

	<!-- Add Button helper (this is optional) -->
	<link rel="stylesheet" type="text/css" href="../fancybox/source/helpers/jquery.fancybox-buttons.css?v=1.0.5" />
	<script type="text/javascript" src="../fancybox/source/helpers/jquery.fancybox-buttons.js?v=1.0.5"></script>

	<!-- Add Thumbnail helper (this is optional) -->
	<link rel="stylesheet" type="text/css" href="../fancybox/source/helpers/jquery.fancybox-thumbs.css?v=1.0.7" />
	<script type="text/javascript" src="../fancybox/source/helpers/jquery.fancybox-thumbs.js?v=1.0.7"></script>

	<!-- Add Media helper (this is optional) -->
	<script type="text/javascript" src="../fancybox/source/helpers/jquery.fancybox-media.js?v=1.0.6"></script>

	<script type="text/javascript">
		$(document).ready(function() {
			/*
			 *  Simple image gallery. Uses default settings
			 */

			$('.fancybox').fancybox();

                        $("a.lightbox").fancybox({
                            'showCloseButton': false,
                            'width': 500,
                            'height': 300,
                            'type': 'iframe',
                            'fitToView': false, // for v2.1.x
                            'autoSize': false, // for v2.1.x
                            'padding': 0,
                            'margin': 0
                        }).hover(function() {
                            $(this).click();
                            $(".fancybox").mouseout(function() {
                                $.fancybox.close();
                            });
                        });


                        $(".test").fancybox();
                        $(".test").hover(function() {
                            $(this).click();
                            $("#fancybox-overlay").remove(); //remove the overlay so you can close when hover off.
                        }, function() {
                            $.fancybox.close();
                        });


			/*
			 *  Different effects
			 */

			// Change title type, overlay closing speed
			$(".fancybox-effects-a").fancybox({
				helpers: {
					title : {
						type : 'outside'
					},
					overlay : {
						speedOut : 0
					}
				}
			});

			// Disable opening and closing animations, change title type
			$(".fancybox-effects-b").fancybox({
				openEffect  : 'none',
				closeEffect	: 'none',

				helpers : {
					title : {
						type : 'over'
					}
				}
			});

			// Set custom style, close if clicked, change title type and overlay color
			$(".fancybox-effects-c").fancybox({
				wrapCSS    : 'fancybox-custom',
				closeClick : true,

				openEffect : 'none',

				helpers : {
					title : {
						type : 'inside'
					},
					overlay : {
						css : {
							'background' : 'rgba(238,238,238,0.85)'
						}
					}
				}
			});

			// Remove padding, set opening and closing animations, close if clicked and disable overlay
			$(".fancybox-effects-d").fancybox({
				padding: 0,

				openEffect : 'elastic',
				openSpeed  : 150,

				closeEffect : 'elastic',
				closeSpeed  : 150,

				closeClick : true,

				helpers : {
					overlay : null
				}
			});

			/*
			 *  Button helper. Disable animations, hide close button, change title type and content
			 */

			$('.fancybox-buttons').fancybox({
				openEffect  : 'none',
				closeEffect : 'none',

				prevEffect : 'none',
				nextEffect : 'none',

				closeBtn  : false,

				helpers : {
					title : {
						type : 'inside'
					},
					buttons	: {}
				},

				afterLoad : function() {
					this.title = 'Image ' + (this.index + 1) + ' of ' + this.group.length + (this.title ? ' - ' + this.title : '');
				}
			});


			/*
			 *  Thumbnail helper. Disable animations, hide close button, arrows and slide to next gallery item if clicked
			 */

			$('.fancybox-thumbs').fancybox({
				prevEffect : 'none',
				nextEffect : 'none',

				closeBtn  : false,
				arrows    : false,
				nextClick : true,

				helpers : {
					thumbs : {
						width  : 50,
						height : 50
					}
				}
			});

			/*
			 *  Media helper. Group items, disable animations, hide arrows, enable media and button helpers.
			*/
			$('.fancybox-media')
				.attr('rel', 'media-gallery')
				.fancybox({
					openEffect : 'none',
					closeEffect : 'none',
					prevEffect : 'none',
					nextEffect : 'none',

					arrows : false,
					helpers : {
						media : {},
						buttons : {}
					}
				});

			/*
			 *  Open manually
			 */

		});
</script>
</head>
<body>\n""")

print("""<h1>Annotation Stats: %s-%s </h1>\n """ % (sid_from, sid_to))

print("""<form action="" method="post" >
         <span id="search">
         <select id="search" name="search">""")

datedrop = """<option value ='' selected>Select</option>
              <option value ='e'>e</option>
              <option value ='w'>w</option>
              <option value ='ew'>w/e</option>
              <option value ='ebylemma'>e (by lemma)</option>
              <option value ='wbylemma'>w (by lemma)</option>
              <option value ='ewbylemma'>e/w (by lemma)</option>"""
print(datedrop)
print("""</select>
sid_from:<input type="text" size="7" name="sid_from" value="%s"/>
sid_to:<input type="text" size="7" name="sid_to" value="%s"/>
<input type="submit" value="Search"/></form>""" % (sid_from, sid_to))


if bylemma == True:
    for lemma, l in sorted(searchdict.items(), key=lambda x: len(x[1]), reverse=True):
        print("<hr>")
        print("<b>Lemma:</b> '%s' [%d times]" % (linkw(lemma), len(l)))

        print("""<table cellpadding="10">""")

        for sidcid in l:  # for each concept in the sentence

            sid = sidcid.split('_')[0]
            cid = sidcid.split('_')[1]
            print("""<tr>
                     <th>cid</th><th>A</th><th>B</th>
                     <th>C</th><th>D</th><th>MajTag</th>
                     <th>Comments</th><th>Sentence</th> 
                     </tr>""")

            lemma = linkw(data_ag['all'][sidcid]['a']['clem'].strip())
            majtag = str(data[int(sid)][int(cid)]['s']['tag']).strip()
            atag = link(str(data[int(sid)][int(cid)]['a']['tag']).strip(), majtag)
            btag = link(str(data[int(sid)][int(cid)]['b']['tag']).strip(), majtag)
            ctag = link(str(data[int(sid)][int(cid)]['c']['tag']).strip(), majtag)
            gtag = link(str(data[int(sid)][int(cid)]['g']['tag']).strip(), majtag)
            majtag = link(majtag, None)

            acom = data[int(sid)][int(cid)]['a']['com']
            if acom:
                acom = "<b>A:</b>" + acom + "; "
            else:
                acom = ""
            bcom = data[int(sid)][int(cid)]['b']['com']
            if bcom:
                bcom = "<b>B:</b>" + bcom + "; "
            else:
                bcom = ""
            ccom = data[int(sid)][int(cid)]['c']['com']
            if ccom:
                ccom = "<b>C:</b>" + ccom + "; "
            else:
                ccom = ""
            comms = acom + bcom + ccom


            s = """<a href='%s%s' style='color:black;text-decoration:none;' 
                      target='_blank'>(SID:%s)</a> %s
                   """ % (tag_sidENG, sid, sid, sent[int(sid)])

            print(u"""<tr><td><nobr>%s</nobr></td><td><nobr>%s</nobr></td><td><nobr>%s</nobr></td>
                         <td><nobr>%s</nobr></td><td><nobr>%s</nobr></td><td><nobr>%s</nobr></td>
                      <td>%s</td><td>%s</td>
                  """ % (cid, atag, btag, ctag, gtag, majtag, comms, s) )
            print("</tr>")

        print("</table>")


else:
    for sid in sorted(searchdict.keys()):
        print("<hr>")
        print("""(<a href='%s%d' target='_blank' >SID:%s</a>) <strong>%s</strong> 
             """ % (tag_sidENG, sid, sid, sent[sid]))

        print("""<table cellpadding="10">""")
        print("""<tr><th>cid</th><th>lemma</th><th>A</th><th>B</th><th>C</th>
                     <th>D</th><th>MajTag</th><th>Comments</th>""")


        for cid in searchdict[sid]:  # for each concept in the sentence

            lemma = linkw(data[sid][cid]['a']['clem'].strip())
            majtag = str(data[sid][cid]['s']['tag']).strip()
            atag = link(str(data[sid][cid]['a']['tag']).strip(), majtag)
            btag = link(str(data[sid][cid]['b']['tag']).strip(), majtag)
            ctag = link(str(data[sid][cid]['c']['tag']).strip(), majtag)
            gtag = link(str(data[sid][cid]['g']['tag']).strip(), majtag)
            majtag = link(majtag, None)


            acom = data[sid][cid]['a']['com']
            if acom:
                acom = "<b>A:</b>" + acom
            else:
                acom = ""
            bcom = data[sid][cid]['b']['com']
            if bcom:
                bcom = "<b>B:</b>" + bcom
            else:
                bcom = ""
            ccom = data[sid][cid]['c']['com']
            if ccom:
                ccom = "<b>C:</b>" + ccom
            else:
                ccom = ""
            comms = acom + bcom + ccom


            print(u"""<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                         <td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                  """ % (cid, lemma, atag, btag, ctag, gtag, majtag, comms) )
            print("</tr>")

        print("</table>")


print("""</body></html>\n""")
a.close()
b.close()
c.close()
g.close()
