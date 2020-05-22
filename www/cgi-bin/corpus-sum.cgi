#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
import cgitb; cgitb.enable()  # for troubleshooting

import sqlite3
from collections import defaultdict as dd

import nltk
from nltk.corpus import wordnet as pwn


form = cgi.FieldStorage()




########
# HTML
########

# Header
print(u"""Content-type: text/html; charset=utf-8\n
         <!DOCTYPE html>\n
           <html>\n
           <head>
<title>NTU-MC Corpus Statistics</title>
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

print("""<h1>Summary of the NTU-MC</h1>\n """)  ## add date?

# print("""<form action="" method="post" >
#          <span id="search">
#          <select id="search" name="search">""")

# datedrop = """<option value ='' selected>Select</option>
#               <option value ='e'>e</option>
#               <option value ='w'>w</option>
#               <option value ='ew'>w/e</option>
#               <option value ='ebylemma'>e (by lemma)</option>
#               <option value ='wbylemma'>w (by lemma)</option>
#               <option value ='ewbylemma'>e/w (by lemma)</option>"""
# print(datedrop)
# print("""</select>
# sid_from:<input type="text" size="7" name="sid_from" value="%s"/>
# sid_to:<input type="text" size="7" name="sid_to" value="%s"/>
# <input type="submit" value="Search"/></form>""" % (sid_from, sid_to))
dbdir='/var/www/ntumc/db'
langs =  ['eng', 'cmn', 'ind']
for lang in langs:
    dbfile = "%s/%s.db" % (dbdir, lang)
    ##print("%s" % dbfile)
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    c.execute('select corpusID, corpus, title from corpus')
    corpora = c.fetchall()
    print("<table>\n<caption>Corpora for %s</caption>" % lang)
    print("<tr><th>Corpus</th><th>ID</th><th>Sentences</th><th>Words</th><th>Concepts</th><th>Range</th></tr>")  
    for (corpusID, corpus, title) in corpora:
        c.execute("""select count(sent) from sent 
 where docid in (select docid from doc where corpusID=?)""", (corpusID,))
        sents = c.fetchone()[0]
        c.execute("""select min(sid), max(sid) from sent 
where docid in (select docid from doc where corpusID = ?)""", (corpusID,))
        srange = c.fetchone()
        c.execute("""select count(word) from word 
where sid in (select sid from sent 
where (docid in (select docid from doc where corpusID=?)))""", (corpusID,))
        words=c.fetchone()[0]
        c.execute("""select count(cid) from concept 
where tag not in ('e', 'x') 
and sid in (select sid from sent 
where (docid in (select docid from doc where corpusID=?)))""", (corpusID,))
        concepts=c.fetchone()[0]
        print("<tr><td>%s</td><td>%s</td>" \
                  "<td align='right'>%d</td><td align='right'>%d</td>"\
                  "<td align='right'>%d</td><td align='center'>%d&ndash;%d</td>" \
                  " </tr>" % (title, corpus, 
                              sents, words, concepts, 
                              int(srange[0] or 0), 
                              int(srange[1] or 0))) 

    print("</table>")

print("""<h4>Current known Issues</h4>
<p>not all the data is up
<p>yoursing is from ver 3, ver 5 (with headers) is available)
<hr>
<p><a href="http://compling.hss.ntu.edu.sg/ntumc/">More Information about the Corpus</a>
""")

print("""</body></html>\n""")
