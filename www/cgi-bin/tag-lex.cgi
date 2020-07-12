#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###
### This is a simple cgi-script for searching for items in the corpus


### Copyright Francis Bond 2013 <bond@ieee.org>
### This is released under the CC BY license
### (http://creativecommons.org/licenses/by/3.0/)
### bugfixes and enhancements gratefuly received

import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import re, sqlite3, collections
import operator
from collections import defaultdict as dd
from ntumc_util import *
from ntumc_webkit import *
## Reading parameters

form = cgi.FieldStorage()

#synset = form.getfirst("synset", "")
lemma = form.getfirst("lemma", "")
lemma = lemma.strip()
lang = form.getfirst("lang", "cmn")
ss = form.getfirst("ss", "")
com_all = form.getfirst("com_all", "")
lim = form.getfirst("lim", 80)
corpus = form.getfirst("corpus", "cmn")
try:
    sfcorpus = int(form.getfirst("sfcorpus", -1))
except:
    sfcorpus = -1
jilog(">>> sfcorpus = %s" % sfcorpus)
###################################################################################################
# CONSTANTS
###################################################################################################
lims = { 10:10, 20:20, 40:40, 80:80, 200:200, 400:400, -1:'All'}

#
# Aggregating comments of all listed sentences to show on top of the page
#
all_comments = {}

def store_comment(comment):
    if comment is None or comment == '' or comment == 'unk':
        # Nah, we don't care about empty comment for now
        pass
    elif not comment in all_comments:
        all_comments[comment] = 1
    else:
        all_comments[comment] += 1

####################################################################
# DATABASE ACCESS
####################################################################

### Connect to and update the database
con = sqlite3.connect("../db/%s.db" % corpus)
cur = con.cursor()
wcon = sqlite3.connect(wndb)
wcur = wcon.cursor()

###############

# totag query
def select_concept():
    lems = list(expandlem(lemma))
    query = """
      SELECT sid, cid, clemma, tag, ntag, tags, comment 
      FROM concept WHERE clemma in (%s) 
      ORDER BY tag, sid, cid 
      LIMIT ?
    """ % placeholders_for(lems)
    #print query 
    cur.execute(query, lems + [int(lim)])
    tm.stop().log("Job = selecting concepts")
    return cur.fetchall()

def select_cwlink():
    query = """
        SELECT sid, wid, cid 
        FROM cwl
        WHERE sid IN (
            SELECT sid FROM concept 
            WHERE clemma IN (%s) 
            ORDER BY tag, sid, cid 
            LIMIT ?)
    """ % placeholders_for(lems)
    return cur.execute(query, lems + [int(lim)]).fetchall()

def select_tag_distribution():
    query = """
        SELECT count(tag), tag 
        FROM concept 
        WHERE clemma in (%s) 
        GROUP BY tag 
        ORDER BY count(tag) DESC;
    """ % placeholders_for(lems)
    jilog('Executing query: %s' % query)
    jilog('Values: %s' % str(lems))
    cur.execute(query, lems)
    return cur.fetchall()

def select_word():
    query = """
        SELECT wid, word, pos, lemma, sid 
        FROM word WHERE sid IN (
            SELECT sid FROM concept 
            WHERE clemma IN (%s) 
            ORDER BY tag, sid, cid 
            LIMIT ?) 
        ORDER BY sid, wid
    """ % placeholders_for(lems)
    return cur.execute(query, lems + [int(lim)]).fetchall()

def select_sentence_id(lemma):
    query = """
        SELECT DISTINCT sid FROM word 
        WHERE lemma LIKE ? OR word LIKE ?
    """
    return cur.execute(query, [str(lemma), str(lemma)]).fetchall()

def select_word_from_sentence(sids):
    query = """
        SELECT sid, wid, word, lemma FROM word 
        WHERE sid IN (%s) ORDER BY sid, wid
    """ % placeholders_for(sids)
    return cur.execute(query).fetchall()

# 2014-06-30 [Tuan Anh]
# fix 500 items limitation
def select_other_concept(lems):
    all_sids_query = """
        SELECT DISTINCT sid FROM concept 
        WHERE clemma IN (%s) 
        ORDER BY tag, sid, cid LIMIT ?
    """ % placeholders_for(lems)
    all_cids_query = """
        SELECT DISTINCT cid FROM concept 
        WHERE clemma in (%s) 
        ORDER BY tag, sid, cid LIMIT %d
    """ % placeholders_for(lems)
    query = """
        SELECT b.cid, b.sid, b.wid, c.clemma, c.tag, c.tags, c.comment  
            FROM concept AS z
            JOIN cwl AS a ON  z.sid=a.sid AND z.cid=a.cid 
            JOIN cwl AS b ON a.sid=b.sid AND a.wid=b.wid 
            JOIN concept as c ON b.sid=c.sid AND b.cid=c.cid 
            WHERE z.sid in (%s) 
                AND z.cid IN (%s) 
                AND z.clemma IN (%s)
    """  % (all_sids_query, all_cids_query, placeholders_for(lems))
    jilog("Find other concept: %s [lemma = %s]" % (query, lems))
    lim = [int(lim)]
    return cur.execute(query, lems + lim + lems + lim + lems).fetchall()

## 2014-07-01 [Tuan Anh]
# Add filter
def select_corpus(lang):
    query = """SELECT * FROM corpus WHERE language=?;"""
    results = cur.execute(query, (lang,)).fetchall()
    return results
    

## ACCESS [WORDNET]

def select_wordnet_freq(all_synsets):
    a_query = """
        SELECT lemma, freq, synset 
        FROM sense 
        LEFT JOIN word ON word.wordid = sense.wordid 
        WHERE synset IN (%s) 
            AND sense.lang = ? 
        ORDER BY synset, freq DESC
    """ % placeholders_for("'%s'" % x for x in all_synsets)
    params = [str(x) for x in all_synsets] + ['eng']
    jilog("I'm selecting %s" % a_query)
    tm.start()
    results = wcur.execute(a_query, params).fetchall()
    tm.stop().log("task = select word left join sense")
    return results

def select_synset_def(all_synsets):
    a_query = """
        SELECT def, synset 
        FROM synset_def 
        WHERE synset IN (%s) 
            AND lang = ? 
        ORDER BY synset, sid
    """ % placeholders_for("'%s'" % x for x in all_synsets)
    params = [str(x) for x in all_synsets] + ['eng']
    jilog("I'm selecting %s\n" % a_query)
    tm.start()
    results = wcur.execute(a_query, params).fetchall()
    tm.stop().log("task = select synset_def")
    return results

def select_synset_def_ex(all_synsets):
    a_query = """
        SELECT def, synset 
        FROM synset_ex 
        WHERE synset IN (%s) 
            AND lang = ? 
        ORDER BY synset, sid
    """ % placeholders_for("'%s'" % x for x in all_synsets)
    params = [str(x) for x in all_synsets] + ['eng']
    jilog("I'm selecting %s\n" % a_query)
    tm.start()
    results = wcur.execute(a_query, params).fetchall()
    tm.stop().log("task = synset_ex")
    return results
####################################################################
# END OF DB ACCESS CODE
####################################################################

# Add more tags in
mtags = [ 'e', 'x', 'w' ] + ["org", "loc", "per", "dat", "oth", "num", "dat:year"]
mtags_short = { "e":"e", 
              "x":"x", 
              "w":"w", 
              'org' : 'Org', 
              'loc': 'Loc', 
              'per': 'Per', 
              'dat': 'Dat',
              'oth': 'Oth', 
              'num': 'Num', 
              'dat:year': 'Year',
              '' : 'Not tagged',
              None : 'Not tagged'
}
mtags_human = { "e":"e", 
              "x":"x", 
              "w":"w", 
              'org' : 'Organization', 
              'loc': 'Location', 
              'per': 'Person', 
              'dat': 'Date/Time',
              'oth': 'Other', 
              'num': 'Number', 
              'dat:year': 'Date: Year',
              '' : 'Not tagged',
              None : 'Not tagged'
}

sss = ss.split()


def tagbox(sss, cid, wp, tag, ntag, com):
    """Create the box for tagging entries"""
    print("<span style='background-color: #eeeeee;'>")  ### FIXME cute css div
    for i, t in enumerate(sss):
        # 2012-06-25 [Tuan Anh]
        # Prevent funny wordwrap where label and radio button are placed on different lines
        print("<span style='white-space: nowrap;background-color: #dddddd'><input type='radio' name='cid_%s' value='%s'" % (cid, t),)
        if (t == tag):
            print(" CHECKED ")
        if wp == t[-1]:
            print(" />%d<sub><font color='DarkRed' size='-2'>%s</font></sub></span>\n" % (i+1, t[-1]))
        else:
            print(" />%d<sub><font size='-2'>%s</font></sub></span>\n" % (i+1, t[-1]))
    for tk in mtags:
        # 2012-06-25 [Tuan Anh]
        # Friendlier tag value display
        tv = mtags_human[tk]
        print("<span style='white-space: nowrap;background-color:#dddddd'><input type='radio' name='cid_%s' title='%s' value='%s'" % (cid, tv, tk))
        if (tk == tag):
            print(" CHECKED ")
        show_text = mtags_short[tk] if tk in mtags_short else tk
        print(" /><span title='%s'>%s</span></span>\n" % (tv, show_text))
    tagv = ''
    if str(tag) != str(ntag):
        tagv = ntag
    if tagv:
        print("""<span style='background-color: #dddddd;white-space: nowrap;border: 1px solid black'>%s</span>""" % tagv)
#     print """
# <input style='font-size:12px; background-color: #ececec;' 
#  title='tag' type='text' name='ntag_%s' value='%s' size='%d'
#  pattern ="loc|org|per|dat|oth|[<>=~!]?[0-9]{8}-[avnr]"
#  />""" % (cid, tagv, 8)
    comv = com if com is not None else '';
    print("""  <textarea style='font-size:12px; height: 18px; width: 150px;
  background-color: #ecffec;' 
  title= 'comment' name='com_%s'>%s</textarea>""" % (cid, comv))

    print("</span>")  ### FIXME cute css div




### Header

print("Content-type: text/html; charset=utf-8\n")
print("<html>")
print("  <head>")
print("    <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>")
print("    <meta http-equiv='content-language' content='zh'>")
print("    <title>%s %s %s</title>" % (lemma, corpus,lang))
print("    <script src='../tag-wid.js' language='javascript'></script>")
# 2014-06-10 [Tuan Anh]
# Added CSS & JQuery support
print("    <script src='../jquery.js' language='javascript'></script>")
# 2014-07-02 [Tuan Anh]
# Add jquery-ui support
print("    <script src='../jquery-ui.js' language='javascript'></script>")
print("    <link rel='stylesheet' type='text/css' href='../css/ui-lightness/jquery-ui-1.10.4.custom.min.css'>")
print("    <link rel='stylesheet' type='text/css' href='../common.css'>")
# 2014-06-11 [Tuan Anh]
# Make synset clickable
print("    <script src='../tag_lex.js' language='javascript'></script>")
print("""
  <script>
     $( document ).ready(page_init);
  </script>
""")
print("  </head>")
print("  <body>")
#print "    <h4>%s in %s (%s)</h4>" % (lemma, corpus,lang)


if re.match('(\d+)-[avnr]',lemma):
    ### synset
    print("Looking for synset %s" % lemma)
    print("Not actually implemented yet")
else:
    ### Find the concepts for the lemmas
    tm = Timer()
    tm.start()
    jilog("Selecting concepts...")
    lems = list(expandlem(lemma))
    totag = select_concept() ## all the results
    if totag:
        ###
        ### We have something to tag
        ###
        ###
        ### Form
        ###
        print(u"""
        <form method="get" action="%s" target='_parent'>   
          <strong>«&#8239;%s&#8239;» in %s (%s)</strong>: 
          <input type='hidden' name='corpus' value='%s'>
          <input type='hidden' name='lang' value='%s'>
          <input type="text" style='font-size:14px;' name="lemma" value="%s" size=8 maxlength=30>
          <input type="submit" name="Query" value="Search">
          <select name="lim">
        """ % (taglcgi, lemma, corpus, lang, corpus,lang,lemma))
        
        for key in sorted(lims.keys()):
            if key == int(lim):
                print("    <option value='%s' selected>%s</option>" % (key, lims[key]))
            else:
                print("    <option value='%s'>%s</option>" % (key, lims[key]))
        print(u"""
          </select>
          <a href="multidict.cgi?lg1=%s&lemma1=%s" target="_blank"><button type="button">Multidict</button></a>
        """ % (lang, lemma))
        ### documentation
        print("""<a href='../tagdoc.html' target='_blank'><button type="button">?</button></a>""")

        # [FILTER]
        # print """<button type='button' id='btnToolbox'>Advanced</button>"""

        # print """<input type="button" 
        #           onclick="window.location = '../tagdoc.html';">"""

        all_corpus = select_corpus(lang)
        filter_corpus_values = [ ('', 'All') ] + [ (_corpusID, _title) for (_corpusID, _corpus, _title, _language) in all_corpus]
        # print """<div id='toolboxdiv' class='toolboxdiv'>"""
        # print """Corpus: %s """ % HTML.dropdownbox('sfcorpus', filter_corpus_values, sfcorpus)
        # print """<input type="submit" name="Query" value="Search">"""
        # print "</div>"
        print("</form>")
        # print "<script>alert('%s');</script>" % sfcorpus;
        ## [HEADER]
        
    
        # 2014-06-12 [Tuan Anh]
        # Pull concept-word link information out for highlighting concepts
        all_cwlink = select_cwlink()
        cwl_map = {} # To store all concept-word link key = (sid, cid), values is a list of wid
        all_sids = [] # This is stored for debug purpose (keep all sid pulled out)
        all_synsets = [] # A list of synsets need to be select
        #words_map = {}
        for (sid, wid, cid) in all_cwlink:
            # if not (sid, wid) in words_map:
            #     words_map[(sid, wid)] = []
            if not (sid, cid) in cwl_map:
                cwl_map[(sid, cid)] = []
            if sid not in all_sids:
                all_sids.append(sid)
            cwl_map[(sid, cid)].append(wid)
            #words_map[(sid, wid)].append(cid)
        show = dd(lambda: dd(lambda: dict()))
        #cwids = dd(list)
        ### store by tag, sid, cid: groups wids by cid
        for (sid, cid, clemma, tag, ntag, tags, comment) in totag:
            if tag and re.match('(\d+)-[avnr]',tag) and tag not in all_synsets:
                all_synsets.append(tag)
            store_comment(comment)
            store_comment(ntag)
            sid = int(sid)
            #wid=int(wid)
            cid=int(cid)
            ## show[tag][sid][cid] = (wids, clemma, nlemma, tag, ntag, tags, comment)
            #cwids[cid].append(wid)  ### for MWEs just write over with the new values
            show[tag][sid][cid] = [cwl_map[(sid, cid)], clemma, ntag, tags, comment]
        ## store the concept ids 
        ## [Tuan Anh]: 2014-06-10 (to identify a concept, we need both sentence ID and concept ID)
        cids = u" ".join(["%s|%s" % (str(r[0]), str(r[1])) for r in totag])  ### all the cids
        ## store the concepts (sid, cid) so we can check for other tags semi-efficiently
        cidsids = [(r[0], r[1]) for r in totag]
        others = dd(list)
        ## find other concepts with the same ids
        ## get too many back, filter later
        for (d_cid, d_sid, d_wid, d_clemma, d_tag, d_tags, d_comment) in select_other_concept(lems):
            jilog('%s\t%s\t%s' %(d_sid, d_cid, d_wid))
            # store_comment(r[5])
            ##print r
            if (d_sid, d_cid) not in cidsids:
                others[(int(d_sid), int(d_wid))].append((d_clemma, d_tag, d_tags, d_comment, d_cid))
                ###print "<br>", d_sid, d_wid, d_cid, d_clemma, d_tag, d_tags, d_comment
        jilog("OTHER = %s" % str(others))

        # 2014-06-21 [Tuan Anh]
        # Summarise tag distribution
        tag_freqs_order = []
        tag_freqs = {}
        tag_count = 0
        for (freq, tag) in select_tag_distribution():
            tag_freqs_order.append(tag)
            tag_count += freq
            tag_freqs[tag] = freq
        if tag_count > 0:
            for tag in tag_freqs_order:
                tag_freqs[tag] = '%d%%' % ((tag_freqs[tag] * 100) / tag_count)

        ##
        ## Start the form
        ##
        print("""
    <form name='tag' method="post" action="%s" target='_parent'>   
      <input type='hidden' name='corpus' value='%s'>
      <input type='hidden' name='lang' value='%s'>
      <input type='hidden' name='lemma' value='%s'>
      <input type='hidden' name='cids' value='%s'>
      <input type='hidden' name='lim' value='%s'>
    """ % (taglcgi,  corpus, lang, lemma, cids, lim))
    
        ### default values
        print("<a id='bookmark_PAGE_TOP'/>")
        print("<p><strong>Default</strong>:")
        tagbox(sss, 'all', '', '', '', com_all)
        print("<input type='submit' name='Query' value='tag'>")

        all_synset_group = sorted(show.keys()) 
        jilog("all_synset_group = %s" % all_synset_group)
       
        # 2014-06-21 [Tuan Anh]
        print('<hr/> Distribution (%d): ' % tag_count)
        # for (k, v) in tag_freqs.iteritems():
        #     print '%s => %s<br/>' % (k,v)
        text_items = []
        item_text_by_tag = {}
        # 2014-07-02 [Tuan Anh]
        # add bookmark jump
        for i, t in enumerate(sss):
            display_text = t if not t in mtags_human else mtags_human[t]
            freq = '0%' if not t in tag_freqs else tag_freqs[t]
            item_text_by_tag[t] = u"""<span title='%s'>%d<sub><font color='DarkRed' size='-2'>%s</font></sub></span>""" % (display_text, i+1, t[-1])
            if str(t) in all_synset_group:
                #jilog("%s is IN %s" % (t, all_synset_group))
                text_items.append("<a href='bookmark_%s'>%s <font size='-1'>(%s)</font></a>" % (t, item_text_by_tag[t], freq))
                pass
            else:
                #jilog("%s is not in %s" % (t, all_synset_group))
                text_items.append("%s <font size='-1'>(%s)</font>" % (item_text_by_tag[t], freq))
        for t in mtags:
            display_text = t if not t in mtags_human else mtags_human[t]
            item_text_by_tag[t] = display_text
            freq = '0%' if not t in tag_freqs else tag_freqs[t]
            if str(t) in all_synset_group:
                #jilog("%s is IN %s" % (t, all_synset_group))
                text_items.append (u"""<a href='bookmark_%s'>%s <font size='-1'>(%s)</font></a>"""%(t, t, freq) )
                pass
            else:
                #jilog("%s is not in %s" % (t, all_synset_group))
                text_items.append (u"""%s <font size='-1'>(%s)</font>"""%( t, freq) )
        # We don't need this for now
        #print(u' - '.join(text_items))
        #print('<hr/>')
        text_items = []
        for a_tag in tag_freqs_order:
            if a_tag in item_text_by_tag and a_tag in tag_freqs:
                text_items.append("<a href='#bookmark_%s'>%s <font size='-1'>(%s)</font></a>" % (a_tag, item_text_by_tag[a_tag], tag_freqs[a_tag]))
        if len(text_items) > 0:
            print(' - '.join(text_items))

        
        # 2014-06-10 [Tuan Anh]
        # Add comment summary box
        if len(all_comments) > 0:
            all_comments_text = ''
            for a_pair in reversed(sorted(all_comments.items(), key=operator.itemgetter(1, 0))):
                all_comments_text += "<tr> <td>%s</td> <td>%s</td> </tr>" % a_pair
            # 2014-06-11 [Tuan Anh]
            # Make the synsets clickable
            # This version is for popup, but Shan want to display them in the right panel
            #all_comments_text = re.sub(r'([0-9]{8}-[varn])', r"""<a href='#' onclick='popup(synset_to_url("\1"), "\1");'>\1</a>""", all_comments_text)
            # 2014-06-12 [Tuan Anh]... So I change the target from popup window to right panel
            all_comments_text = re.sub(r'([0-9]{8}-[varn])', r"""<a href='wn-gridx.cgi?synset=\1' target='wn'>\1</a> [wn_list_loc(\1)]""", all_comments_text)
    
            # 2014-06-15 [Tuan Anh]
            # Shan needs to have item number to be shown for each synset found in comment (easy to check)
            for i, t in enumerate(sss):
                all_comments_text = all_comments_text.replace('[wn_list_loc(%s)]' % t, """(%d<sub><font color='DarkRed' size='-2'>%s</font></sub>)"""%( i+1, t[-1]))
            # remove any not found synset
            all_comments_text = re.sub(r'(\[wn_list_loc\([0-9]{8}-[varn]\)\])', '(NITL)', all_comments_text)
            print("""
            <br/>
            <button id="btnToggle" type="button">All Comments</button>
            <div id="CommentSummary" class="CommentSummary"><table border='1'><tr><td>Comment</td><td>freq</td></tr>%s</table></div>
            """ % (all_comments_text))
    
        ### per sentence values
    
        # 2014-06-12 [Tuan Anh]
        # We will select all words of all sentences
        results = select_word() # select all words of listed sentences 
        sentences_words = {}
        for (wid, word, pos, lemma, sid) in results:
            if not sid in sentences_words:
                sentences_words[int(sid)] = []
            sentences_words[int(sid)].append([wid, word, pos, lemma])
        # Now we don't have to select inside the for-loop using multiple queries any more
    
        # 2014-06-12 [Tuan Anh]
        # We should hit wordnet DB once only. This should improve the performance
        jilog("Working with wordnet")
        #a_query = "select lemma, freq, synset from word left join sense on word.wordid = sense.wordid where synset in (%s) and sense.lang = ? ORDER BY synset, freq DESC" % ','.join(["'%s'" % x for x in all_synsets] )
        # 2014-06-12 [Tuan Anh] Wrong join direction, sense left join word is much much faster. This query should use < 0.01 sec now ^^ Thank me? You are welcome
        lemma_freq_dict = {}
        for lemma, freq, synset  in select_wordnet_freq(all_synsets):
            if not synset in lemma_freq_dict:
                lemma_freq_dict[synset] = []
            lemma_freq_dict[synset].append((lemma, freq))
        # all defs
        
        synset_def_dict = {}
        for a_def, synset  in select_synset_def(all_synsets):
            if not synset in synset_def_dict:
                synset_def_dict[synset] = []
            synset_def_dict[synset].append(a_def)           
        # all synset_ex
        
        synset_ex_dict = {}
        for a_def, synset in select_synset_def_ex(all_synsets):
            if not synset in synset_ex_dict:
                synset_ex_dict[synset] = []
            synset_ex_dict[synset].append(a_def)  
        # A bit of debugging here
        jilog("synset_def_dict = %s\n" % repr(synset_def_dict))
        jilog("synset_ex_dict = %s\n" % repr(synset_ex_dict))
        jilog("lemma_freq_dict = %s\n" % repr(lemma_freq_dict))
        jilog("End Wordnet touch")
        # OK, that's all we need from wordnet, lol [Tuan Anh]
        # 2014-07-02 [Tuan Anh] Add a navigator bar
        navigator_bar_html = "<a href='#bookmark_PAGE_TOP' class='bookmark_top' alt='Top'></a> <a href='#bookmark_PAGE_BOTTOM' class='bookmark_bottom'></a> "
        for ltag in all_synset_group:
            ### print the tag (and if it is a synset, information about it)
            print("<hr/>")
            print("<p>")
            # [SYNSETGROUP] each synset group has a header. (synset-id, definition, etc)
            # 2014-07-02 [Tuan Anh]
            # Add bookmark jump
            tag_bookmark_name = "bookmark_" + str(ltag)
            print ("<a id='%s'/>" % tag_bookmark_name)
            if ltag and re.match('(\d+)-[avnr]',ltag):
                print(navigator_bar_html)
                # lemmas and freq
                if str(ltag) in lemma_freq_dict:
                    for r in lemma_freq_dict[str(ltag)]:
                        print("<font color='green'><b><i>%s</i></b></font><sub><font size='-2'>%d</font></sub> " % (r[0], int(r[1] or 0)))
                ## synset ID
                print("(<a style='color: Navy;' href='%s?synset=%s' target='wn'>%s</a>)" %(wncgi, ltag, ltag))

                if ltag in synset_def_dict:
                    print("<font size='-1'>%s</font>" % "; ".join(synset_def_dict[ltag]))

                if ltag in synset_ex_dict:
                    print("<i><font size='-1'>%s</font></i>" % "; ".join(synset_ex_dict[ltag]))

            elif ltag in mtags_human:
                print("<p>")
                print(navigator_bar_html)
                print("<strong>%s</strong>" %(mtags_human[ltag]))
            else:
                print("<p>")
                print(navigator_bar_html)
                print("<strong>%s</strong>" %(ltag))
    
            for lsid in sorted(show[ltag].keys()):
                for lcid in show[ltag][lsid]:
                    ## Concepts, grouped by sentence
                    print("<br><a class='sid' href='%s?corpus=%s&sid=%d&lemma=%s' target='_blank'>%d</a>" % (showsentcgi, 
                                                                                        corpus, lsid, clemma, lsid))
                    (cwds, clemma, ntag, tags, com) = show[ltag][lsid][lcid]
                    # 2014-06-12 [Tuan Anh]
                    # I changed this part of code to improve the performance
                    # This query should be executed only once per sentence
                    # d. execute("select wid, word, pos, lemma from word where sid =? order by sid, wid", (lsid,) )
                    print("<br>")
                    if not ntag:
                        ntag=ltag
                    if not ltag:
                        ntag =''
                    wp = '' # wordnet POS   
                    #for (wid, word, pos, lemma) in d:
    
                    if not int(lsid) in sentences_words:
                        jilog("It seems that I can't really find %s all_sids=%s, sentences_words=%s...\n" % (lsid, repr(sorted(all_sids)), repr(sorted(sentences_words.keys()))))
                    for wid, word, pos, lemma in sentences_words[int(lsid)]:
                        if wid in cwds:
                            wp = pos2wn(pos,lang)  ### remember the pos of the (last) selected word
                            # 2014-06-26 [Tuan Anh] tag-text doesn't work so let make a search in tag-tex instead
                            # tt = '%s?corpus=%s&sid=%d&wid=%d&ss=%s' %(tagwcgi, corpus, lsid, wid, tags)
                            tt = '%s?lemma=%s' %(taglcgi, lemma)
                            ttt = cgi.escape('%d:%s:%s&#013;%s:%s' % (wid, pos, lemma, ntag, com))
                            print("<a style='color: Green;' title = '%s' href='%s' target='_parent'>%s</a><sub><font size='-2'>%s</font></sub>" % (ttt, tt, word, wp))
                        else:
                            print("<span title='%d:%s:%s'>%s</span> " % (wid, pos, lemma, word))
                    ## 
                    ## Tags
                    ##
                    print("<br>")  ### FIXME cute css div
                    tagbox(sss, "%s_%s" % (lsid, lcid), wp, ltag, ntag, com)
                    #print "<br>"  ### FIXME cute css div
                    oth = list()
                    for cwd in cwds:
                        oth += others[(lsid, cwd)]
                    if oth:
                        print("(")
                        for (clemma, tag, tags, com, cwid) in oth:
                            t = ''
                            if com:
                                t = "title='%s'" % cgi.escape(com)
                            print("""
    <a style='color: Green;' %s
    href='%s?corpus=%s&lang=%s&lemma=%s&lim=%d' 
    target='_blank'>%s</a><sub>
    <font size='-2'>%s</font></sub>""" % (t, taglcgi, corpus, lang, clemma, int(lim),
                                          clemma, tag))
                        print(")<br>")
    
        print("<a id='bookmark_PAGE_BOTTOM'/>")
        print("""
           <div align='right'><input type="submit" name="Query" value="tag"></div>
        </form>""")
    elif not lemma:
        print(u"""<h4>Please enter a lemma to tag in %s (%s)</h4>
        <form method="get" action="%s" target='_parent'>   
          <input type='hidden' name='corpus' value='%s'>
          <input type='hidden' name='lang' value='%s'>
          <input type="text" style='font-size:14px;' name="lemma" value="%s" size=8 maxlength=30>
          <input type="submit" name="Query" value="Search">
          <select name="lim">
        """ % (corpus, lang, taglcgi, corpus,lang,lemma))
        for key in sorted(lims.keys()):
            if key == lim:
                print("    <option value='%s' selected>%s</option>" % (key, lims[key]))
            else:
                print("    <option value='%s'>%s</option>" % (key, lims[key]))
        print(u"""
          </select>
        </form>
        """)
    else:
        ### 
        ### No concept!  
        ### let's add it
        ### 
        print(u"<h4>«&#8239;%s&#8239;» is not stored as a concept in the corpus</h4>" % lemma)
        print(u"""
      <form method="get" action="%s" target='_parent'>   
          <input type="submit" name="Query" value="Add">«&#8239;%s&#8239;» to %s?
          <input type='hidden' name='addme' value='%s'>
          <input type='hidden' name='lemma' value='%s'>
          <input type='hidden' name='corpus' value='%s'>
          <input type='hidden' name='lang' value='%s'>
          <input type=hidden name="lim" value ='%s'> 
      </form>
        """ % (taglcgi, lemma, corpus, lemma, lemma, corpus, lang,  lim))

        ls = re.split(r' |_|∥', lemma) if lemma else ''
        sids = [str(s[0]) for s in select_sentence_id(ls[0])] if ls else []
        if sids and len(sids) > 0:
            sents = dd(lambda:dd(list))
            for (sid, wid, word, lem) in select_word_from_sentence(sids):
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
                            if i+j <= sentlength and ls[j] in sents[sid][i+j]:
                               matched.append(i+j) 
                        if len(matched) == len(ls):
                            matches[sid].append(matched)
            if matches:
                print(u"<p>It appears in the following sentences:")
                for sid in matches:
                    print("<br><b>%s</b>: " % sid)
                    for wid in sents[sid]:
                        if any((wid in wids) for wids in matches[sid]):
                            print("<b><font color='green'>%s</font></b>" % sents[sid][wid][0],)
                        else:
                            print(sents[sid][wid][0],)
                        print()
        print(u"""
        <form method="get" action="%s" target='_parent'>   
          <strong>«&#8239;%s&#8239;» in %s (%s)</strong>: 
          <input type='hidden' name='corpus' value='%s'>
          <input type='hidden' name='lang' value='%s'>
          <input type="text" style='font-size:14px;' name="lemma" value="%s" size=8 maxlength=30>
          <input type="submit" name="Query" value="Search">
          <select name="lim">
        """ % (taglcgi, lemma, corpus, lang, corpus,lang,lemma))
        for key in sorted(lims.keys()):
            if key == lim:
                print("    <option value='%s' selected>%s</option>" % (key, lims[key]))
            else:
                print("    <option value='%s'>%s</option>" % (key, lims[key]))
        print(u"""
          </select>
        </form>
        """)
            

### Ending Information


print('<hr><p>Maintainer: <a href="http://www3.ntu.edu.sg/home/fcbond/">Francis Bond</a> ')
print('&lt;<a href="mailto:bond@ieee.org">bond@ieee.org</a>&gt;')

print("  </body>")
print("</html>")

