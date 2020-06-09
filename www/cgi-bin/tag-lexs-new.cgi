#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# tag-lexs.cgi - version 2.0 alpha

###
### This is a simple cgi-script for searching for items in the corpus

### Copyright Francis Bond 2013 <bond@ieee.org>
### This is released under the CC BY license
### (http://creativecommons.org/licenses/by/3.0/)
### bugfixes and enhancements gratefuly received

# FIXME(Wilson): line 274: missing args for select_concept(): sid_from, sid_to

# 2014-09-16 [Tuan Anh] I'm adding Jinja template engine support to 
# NTU-MC tagging tool so this version won't work with previous tag-lex.cgi anymore

import cgi, urllib, os
import cgitb; cgitb.enable()  # for troubleshooting
import re, sqlite3, collections
from collections import defaultdict as dd
from collections import OrderedDict as od
from collections import namedtuple as ntu
from ntumc_util import *
from ntumc_webkit import *
from lang_data_toolkit import *
from ntumc_tagdb import *
import time


##########################################################################
# CONSTANTS
##########################################################################
lims = { 10:10, 20:20, 40:40, 80:80, 200:200, 400:400, -1:'All'}

### working corpus.db
corpusdb = "../db/cmn.db"

# Add more tags in

taglcgi = 'tag-lexs-new.cgi' # FOR TESTING PURPOSE
template_data = {
    'wnnam':wnnam,
    'wnver':wnver,
    'wnurl':wnurl,
    'type':'sequential',
    'taglcgi': taglcgi,
    'lims': lims
}

##########################################################################
# Get fields from CGI
##########################################################################
form = cgi.FieldStorage()
##------------------------
version = form.getfirst("version", "0.1")
usrname_cgi = form.getvalue("usrname_cgi")
lemma = form.getfirst("lemma", "")
lemma = lemma.strip()
usrname = form.getfirst("usrname", "unknown")
lang = form.getfirst("lang", "cmn")
corpus = form.getfirst("corpus", "cmn")
lim = int(form.getfirst("lim", 499))
try:
    sfcorpus = int(form.getfirst("sfcorpus", -1))
except:
    sfcorpus = -1
com_all = form.getfirst("com_all", "")
tsid = int(form.getfirst("sid", 10000)) #default to sentence 1000
twid = int(form.getfirst("wid", 0)) #default to first word
window = int(form.getfirst("window", 4)) #default context of four sentences
if window > 200:
    window = 200

# tag-lex fields
cids = form.getfirst("cids", '')
jilog("cids=%s" % (cids,))
dtag = form.getfirst("cid_all", None)
dntag = form.getfirst("ntag_all", None)
dcom = form.getfirst("com_all", None)
addme = form.getfirst("addme", "")
addme = addme.strip()
tgs = dd(lambda: [None, None]) 
##########################################################################
# Get fields from Cookies
##########################################################################
# Look for the username cookie (if it can't find, it will use 'unknown' as default)
user_cookie = NTUMC_Cookies.read_user_cookie(usrname_cgi)
usrname = user_cookie['user_name'].value

##########################################################################
# Local variables
##########################################################################

# Store fields in template value map
template_data.update({
    'version':version,
    'lemma': lemma,
    'corpus': corpus,
    'lang': lang,
    'lim': lim,
    'wn_src': '%s?usrname=%s&gridmode=ntumcgrid&lang=%s&lemma=%s' % (wncgi, usrname,lang,lemma)
})

# Local variables
lems = list(expandlem(lemma))
lms = ",".join("'%s'" % l  for l in lems)
tm = Timer()


# Create database pointers
con = sqlite3.connect("../db/%s.db" % corpus)
c = con.cursor() # cursor to corpus database
cur = con.cursor() # cursor to corpus database
wcon = sqlite3.connect(wndb)
wcur = wcon.cursor()
wn = sqlite3.connect(wndb)
w = wn.cursor()

##########################################################################
# Utilities functions
##########################################################################
Sentence = ntu('Sentence', ['sid', 'words'])
# Build a tagbox
def tagbox(sss, cid, wp, tag, ntag, com):
    """Create the box for tagging entries"""
    tagbox_text = []
    tagbox_text.append("<span style='background-color: #eeeeee;'>")  ### FIXME cute css div
    for i, t in enumerate(sss):
        # 2012-06-25 [Tuan Anh]
        # Prevent funny wordwrap where label and radio button are placed on different lines
        tagbox_text.append("<span style='white-space: nowrap;background-color: #dddddd'><input type='radio' name='cid_%s' value='%s'" % (cid, t))
        if (t == tag):
            tagbox_text.append(" CHECKED ")
        if wp == t[-1]:
            tagbox_text.append(" />%d<sub><font color='DarkRed' size='-2'>%s</font></sub></span>\n" % (i+1, t[-1]))
        else:
            tagbox_text.append(" />%d<sub><font size='-2'>%s</font></sub></span>\n" % (i+1, t[-1]))
    for tk in mtags:
        # 2012-06-25 [Tuan Anh]
        # Friendlier tag value display
        tv = mtags_human[tk]
        tagbox_text.append("<span style='white-space: nowrap;background-color:#dddddd'><input type='radio' name='cid_%s' title='%s' value='%s'" % (cid, tv, tk))
        if (tk == tag):
            tagbox_text.append(" CHECKED ")
        show_text = mtags_short[tk] if tk in mtags_short else tk
        tagbox_text.append(" /><span title='%s'>%s</span></span>\n" % (tv, show_text))
    tagv=''
    if str(tag) != str(ntag):
        tagv=ntag
    if tagv:
        tagbox_text.append("""<span style='background-color: #dddddd;white-space: nowrap;border: 1px solid black'>%s</span>""" % tagv)
#     print """
# <input style='font-size:12px; background-color: #ececec;' 
#  title='tag' type='text' name='ntag_%s' value='%s' size='%d'
#  pattern ="loc|org|per|dat|oth|[<>=~!]?[0-9]{8}-[avnr]"
#  />""" % (cid, tagv, 8)
    comv = com if com is not None else '';
    tagbox_text.append("""  <textarea style='font-size:12px; height: 18px; width: 150px; 
               background-color: #ecffec;' 
               title= 'comment' name='com_%s'>%s</textarea>""" % (cid, comv))
    tagbox_text.append("</span>")  ### FIXME cute css div
    return ''.join(tagbox_text)

##########################################################################
# Application logic code (process queries, access database, etc.)
##########################################################################

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

### process the tags
for cd in cids.split(' '): ### prefer local ntag
    jilog("im tagging cdis=%s" % (cids,))
    if not cd:
        continue
    cdparts = cd.split('|')
    sid = int(cdparts[0])
    cid = int(cdparts[1])
    tag =  form.getfirst("cid_%d_%d" % (sid, cid), None)
    jilog('im tagging - tag=%s' % tag)
    com =  form.getfirst("com_%d_%d" % (sid, cid), None)
    if com:
        com = com.strip()
    ntag = form.getfirst("ntag_%d_%d" % (sid, cid), None)

    if tag: ### then local tag
        c.execute("update concept set tag=?, usrname=? where tag IS NOT ? and sid=? and cid=?", (tag, usrname, tag, sid, cid))
        set_others_x (c, usrname, sid, cid,)
        jilog('im tagging tag=%s - sid=%s - cid=%s' % (tag, sid, cid))
    elif dtag: ### then default tag
        #log.write("dtag\n")
        c.execute("update concept set tag=?, usrname=? where sid=? and cid=?", (dtag, usrname, sid, cid))
        set_others_x (c, usrname, sid, cid,)
        jilog('ntag - sid=%s - cid=%s' % (sid, cid))
    ### don't do anything otherwise
    ### always update the comment
    c.execute("update concept set comment=?, usrname=? where comment IS NOT ? and sid=? and cid=?", (com, usrname, com, sid, cid))
if addme:
    ### add this as a concept
    ls = re.split(r' |_|∥', addme)
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

# Select data if needed
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
lmss = "\\".join("%s" % l  for l in lems)

### Find the concepts for the lemmas
tm.start()
jilog("Selecting concepts...")
lems = list(expandlem(lemma))
totag = select_concept(cur, lems, lim) ## all the results #FIXME [DBACCESS]
tm.stop()

#if totag:
    #template_data['message'] = 'Found something to tag'

##########################################################################
# Application logic code (process queries, access database, etc.)
##########################################################################

if totag:
    if re.match('(\d+)-[avnr]',lemma): # Search by synset instead of lemma ...
        template_data['message'] = "Looking for synset %s is not actually implemented yet" % lemma

    # 2014-06-12 [Tuan Anh]
    # Pull concept-word link information out for highlighting concepts
    all_cwlink = select_cwlink(cur, lems, lim) #FIXME [DBACCESS]
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
    for (d_cid, d_sid, d_wid, d_clemma, d_tag, d_tags, d_comment) in select_other_concept(cur, lems, lim): #FIXME [DBACCESS]
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
    for (freq, tag) in select_tag_distribution(cur, lems):
        tag_freqs_order.append(tag)
        tag_count += freq
        tag_freqs[tag] = freq
    if tag_count > 0:
        for tag in tag_freqs_order:
            tag_freqs[tag] = '%d%%' % ((tag_freqs[tag] * 100) / tag_count)

    template_data['tag_count'] = tag_count
    all_synset_group = sorted(show.keys())

    # 2014-06-21 [Tuan Anh]
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
    text_items = []
    for a_tag in tag_freqs_order:
        if a_tag in item_text_by_tag and a_tag in tag_freqs:
            text_items.append("<a href='#bookmark_%s'>%s <font size='-1'>(%s)</font></a>" % (a_tag, item_text_by_tag[a_tag], tag_freqs[a_tag]))
    
    template_data['distribution_text'] = ''
    if len(text_items) > 0:
        template_data['distribution_text'] = ' - '.join(text_items)

    # 2014-06-10 [Tuan Anh]
    # Add comment summary box
    template_data['comment_summary'] = ''
    if len(all_comments) > 0:
        all_comments_text = ''
        for a_pair in reversed(sorted(all_comments.items(), key=operator.itemgetter(1, 0))):
            all_comments_text += "<tr> <td>%s</td> <td>%s</td> </tr>" % a_pair
        # 2014-06-11 [Tuan Anh]
        # Make the synsets clickable
        # This version is for popup, but Shan want to display them in the right panel
        #all_comments_text = re.sub(r'([0-9]{8}-[varn])', r"""<a href='#' onclick='popup(synset_to_url("\1"), "\1");'>\1</a>""", all_comments_text)
        # 2014-06-12 [Tuan Anh]... So I change the target from popup window to right panel
        all_comments_text = re.sub(r'([0-9]{8}-[varn])', r"""<a href='wn-gridx.cgi?synset=\1&gridmode=ntumcgrid' target='wn'>\1</a> [wn_list_loc(\1)]""", all_comments_text)

        # 2014-06-15 [Tuan Anh]
        # Shan needs to have item number to be shown for each synset found in comment (easy to check)
        for i, t in enumerate(sss):
            all_comments_text = all_comments_text.replace('[wn_list_loc(%s)]' % t, """(%d<sub><font color='DarkRed' size='-2'>%s</font></sub>)"""%( i+1, t[-1]))
        # remove any not found synset
        all_comments_text = re.sub(r'(\[wn_list_loc\([0-9]{8}-[varn]\)\])', '(NITL)', all_comments_text)
        template_data['comment_summary'] = all_comments_text
    # End of comment box

    # 2014-06-12 [Tuan Anh]
    # We will select all words of all sentences
    results = select_word(cur, lems, lim) # select all words of listed sentences  #FIXME [DBACCESS]
    sentences_words = {}
    for (wid, word, pos, lemma, sid) in results:
        if not sid in sentences_words:
            sentences_words[int(sid)] = []
        sentences_words[int(sid)].append([wid, word, pos, lemma])
    # Now we don't have to select inside the for-loop using multiple queries any more

    # 2014-06-12 [Tuan Anh]
    # We should hit wordnet DB once only. This should improve the performance
    jilog("Working with wordnet")
    lemma_freq_dict = {}
    for lemma, freq, synset  in select_wordnet_freq(wcur, all_synsets): #FIXME [DBACCESS]
        if not synset in lemma_freq_dict:
            lemma_freq_dict[synset] = []
        lemma_freq_dict[synset].append((lemma, freq))
    # all defs

    synset_def_dict = {}
    for a_def, synset  in select_synset_def(wcur, all_synsets): #FIXME [DBACCESS]
        if not synset in synset_def_dict:
            synset_def_dict[synset] = []
        synset_def_dict[synset].append(a_def)           
    # all synset_ex

    synset_ex_dict = {}
    for a_def, synset in select_synset_def_ex(wcur, all_synsets): #FIXME [DBACCESS]
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
    navigator_bar_html = "<a href='#bookmark_PAGE_TOP' class='bookmark_top' alt='Top'></a> <a href='#bookmark_PAGE_BOTTOM' class='bookmark_bottom'></a>"
    lex_groups = []
    for ltag in all_synset_group:
        ### print the tag (and if it is a synset, information about it)
        #print "<hr/>"
        #print "<p>"
        # [SYNSETGROUP] each synset group has a header. (synset-id, definition, etc)
        # 2014-07-02 [Tuan Anh]
        # Add bookmark jump
        tmp_lex_group = []
        #tag_bookmark_name = "bookmark_" + str(ltag)
        tmp_lex_group.append(("<a id='bookmark_%s'></a>" % (str(ltag),)))
        if ltag and re.match('(\d+)-[avnr]',ltag):
            tmp_lex_group.append( navigator_bar_html)
            # lemmas and freq
            if str(ltag) in lemma_freq_dict:
                for r in lemma_freq_dict[str(ltag)]:
                    tmp_lex_group.append("<font color='green'><b><i>%s</i></b></font><sub><font size='-2'>%d</font></sub> " % (r[0], int(r[1] or 0)))
            ## synset ID
            tmp_lex_group.append("(<a style='color: Navy;' href='%s?synset=%s&gridmode=ntumcgrid' target='wn'>%s</a>)" %(wncgi, ltag, ltag))

            if ltag in synset_def_dict:
                tmp_lex_group.append("<font size='-1'>%s</font>" % "; ".join(synset_def_dict[ltag]))

            if ltag in synset_ex_dict:
                tmp_lex_group.append("<i><font size='-1'>%s</font></i>" % "; ".join(synset_ex_dict[ltag]))

        elif ltag in mtags_human:
            tmp_lex_group.append("<p>")
            tmp_lex_group.append(navigator_bar_html)
            tmp_lex_group.append("<strong>%s</strong>" %(mtags_human[ltag]))
        else:
            tmp_lex_group.append("<p>")
            tmp_lex_group.append(navigator_bar_html)
            tmp_lex_group.append("<strong>%s</strong>" %(ltag))

        for lsid in sorted(show[ltag].keys()):
            for lcid in show[ltag][lsid]:
                ## Concepts, grouped by sentence
                tmp_lex_group.append("<br><a class='sid' href='%s?corpus=%s&sid=%d&lemma=%s' target='log'>%d</a>" % (showsentcgi, 
                                                                                    corpus, lsid, clemma, lsid))
                (cwds, clemma, ntag, tags, com) = show[ltag][lsid][lcid]
                # 2014-06-12 [Tuan Anh]
                # I changed this part of code to improve the performance
                # This query should be executed only once per sentence
                tmp_lex_group.append("<br>")
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
                        tt = '%s?lemma=%s' %(taglcgi, lemma)
                        ttt = cgi.escape('%d:%s:%s&#013;%s:%s' % (wid, pos, lemma, ntag, com))
                        tmp_lex_group.append("<a style='color: Green;' title = '%s' href='%s' target='_parent'>%s</a><sub><font size='-2'>%s</font></sub>" % (ttt, tt, word, wp))
                    else:
                        tmp_lex_group.append("<span title='%d:%s:%s'>%s</span> " % (wid, pos, lemma, word))
                ## 
                ## Tags
                ##
                tmp_lex_group.append("<br>")  ### FIXME cute css div
                tmp_lex_group.append(tagbox(sss, "%s_%s" % (lsid, lcid), wp, ltag, ntag, com))
                #print "<br>"  ### FIXME cute css div
                oth = list()
                for cwd in cwds:
                    oth += others[(lsid, cwd)]
                if oth:
                    tmp_lex_group.append("(")
                    for (clemma, tag, tags, com, cwid) in oth:
                        t = ''
                        if com:
                            t = "title='%s'" % cgi.escape(com)
                        tmp_lex_group.append("""
<a style='color: Green;' %s
href='%s?corpus=%s&lang=%s&lemma=%s&lim=%d' 
target='_blank'>%s</a><sub>
<font size='-2'>%s</font></sub>""" % (t, taglcgi, corpus, lang, clemma, int(lim),
                                      clemma, tag))
                    tmp_lex_group.append(")<br>")
        lex_groups.append(u'\n'.join(['' if x is None else x for x in tmp_lex_group]))
    template_data['lex_groups'] = lex_groups
    # Now we can render tag-lexs
    template_data['tagbox_default'] = tagbox(sss, 'all', '', '', '', com_all)
    template_data['cids'] = cids
    HTML.render_template('tag-lexs.htm', template_data, user_cookie)
    # end of totag = True

elif not lemma:
    # not totag and not lemma => show search form
    HTML.render_template('tag-lexs-search.htm', template_data, user_cookie)

else:
    ### 
    ### We have lemma but no totag => No concept!  
    ### let's add it, first we need to find the 
    ### 
    ls = re.split(r' |_|∥', lemma) if lemma else ''
    sids = [str(s[0]) for s in select_sentence_id(cur, ls[0])] if ls else []
    # The list of Sentence structure will be stored here and passed to template_data to render
    matched_sentences = [] 
    if sids and len(sids) > 0:
        sents = dd(lambda:dd(list))
        for (sid, wid, word, lem) in select_word_from_sentence(cur, sids): #FIXME [DBACCESS]
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
            for sid in matches:
                words = []
                #print "<br><b>%s</b>: " % sid
                for wid in sents[sid]:
                    if any((wid in wids) for wids in matches[sid]):
                        words.append(u"<b><font color='green'>%s</font></b>" % sents[sid][wid][0],)
                    else:
                        words.append(sents[sid][wid][0],)
                matched_sentences.append(Sentence(sid, words))

    # Now we have a list of matched sentences, let's pass it to the template and render it
    # The structure of the template is 
    # [ 
    #   Sentence(sid=1, words=[word1, word2, word3]), 
    #   Sentence(sid=2, words=[word1, word2]) 
    # ...]
    template_data['matched_sentences'] = matched_sentences
    HTML.render_template('tag-lexs-add.htm', template_data, user_cookie)

