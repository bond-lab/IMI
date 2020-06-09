#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# tag-lexs.cgi - version 2.0 alpha

###
### This is a simple cgi-script for searching for items in the corpus

### Copyright Francis Bond 2013 <bond@ieee.org>
### This is released under the CC BY license
### (http://creativecommons.org/licenses/by/3.0/)
### bugfixes and enhancements gratefuly received

# FIXME(Wilson): line 543-ish, undefined variable 'ma' leftover from legacy code


# 2014-09-16 [Tuan Anh] I'm adding Jinja template engine support to 
# NTU-MC tagging tool so this version won't work with previous tag-lex.cgi anymore

import cgi, urllib, http.cookies, os
import cgitb; cgitb.enable()  # for troubleshooting
import re, sqlite3, collections
from collections import defaultdict as dd
from collections import OrderedDict as od
from collections import namedtuple as ntu
import operator
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
# usrname_cgi = form.getvalue("usrname_cgi")
lemma = form.getfirst("lemma", "")
lemma = lemma.strip()
# usrname = form.getfirst("usrname", "unknown")
lang = form.getfirst("lang", "cmn")
corpus = form.getfirst("corpus", "cmn")
sid_from = form.getfirst("sid_from", 0)
sid_to = form.getfirst("sid_to", 1000000)
lim = int(form.getfirst("lim", 499))
gridmode= form.getfirst("gridmode", "ntumcgrid")
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
# dntag = form.getfirst("ntag_all", None)
dcom = form.getfirst("com_all", None)
addme = form.getfirst("addme", "")
addme = addme.strip()
tgs = dd(lambda: [None, None]) 



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

if userID in valid_usernames:
    cookie_text = C
else:
    cookie_text = None
    HTML.redirect('dashboard.cgi')


##########################################################################
# Local variables
##########################################################################

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


################################################################################
# ADDME WAS ACTUALLY NOT WORKING ANYMORE... 
# I'LL LEAVE IT HERE FOR NOW, BUT DON'T WORRY
################################################################################
# if addme:
#     ### add this as a concept
#     ls = re.split(ur' |_|∥', addme)
#     c.execute("select distinct sid from word where lemma like ? or word like ?", ('%s' % ls[0],ls[0]))
#     sids = ",".join(str(s[0]) for s in c.fetchall())
#     ##print sids
#     if sids:
#         sents = dd(lambda:dd(list))
#         c.execute("select sid, wid, word, lemma from word where sid in (%s) order by sid, wid" % sids) 
#         for (sid, wid, word, lem) in c:
#             sents[sid][wid] = (word,lem)
#             #print word
#         matches = dd(list)
#         for sid in sents:
#             matched = []
#             sentlengt=len(sents[sid])
#             for i in sents[sid]:
#                 if sents[sid][i][0] == ls[0] or sents[sid][i][1] == ls[0]:
#                     matched = [i]
#                     ### matched first word
#                     for j in range(1,len(ls)):  ## no skip for now
#                         if i+j < sentlength and ls[j] in sents[sid][i+j]:
#                             matched.append(i+j) 
#                     if len(matched) == len(ls):
#                         matches[sid].append(matched)
#         for sid in matches:
#             for wids in matches[sid]:
#                 ###
#                 ### Add the concept
#                 ###
#                 c.execute("select max(cid) from concept where sid = ?", (int(sid),))
#                 (maxcid,) = c.fetchone()
#                 newcid = maxcid + 1
#                 c.execute("INSERT INTO concept(sid, cid, tag, clemma, comment, usrname) VALUES (?,?,?,?,?,?)",
#                           (sid, newcid, None, addme, None, usrname))
#                 for wid in wids:
#                     c.execute("""INSERT INTO cwl(sid, wid, cid, usrname) 
#                                  VALUES (?,?,?,?)""",
#                               (sid, wid, newcid, usrname))
################################################################################
################################################################################



con.commit()







# Select data if needed
com_all=''
sss = lem2ss(w, lemma, lang)
##
## Fixme --- backoff to non-English
##
# lang1='ind'
# if not sss and lang != lang1:   ### Fixme --- backoff to non-English
#     sss = lem2ss(w, lemma, lang1)
#     com_all='FW:%s' % lang1
lmss = "\\".join("%s" % l  for l in lems)
tsss= ' '.join(sss)


# Store fields in template value map
template_data.update({
    'status_bar':HTML.status_bar(userID),
    'version':version,
    'lemma': lemma,
    'corpus': corpus,
    'lang': lang,
    'lim': lim,
    'sid_from': sid_from,
    'sid_to': sid_to,
    'usrname_logout': userID,
    'wn_src': '%s?gridmode=%s&lang=%s&lemma=%s&ss=%s' % \
        (wncgi, gridmode, lang,lemma,tsss)
})


### Find the concepts for the lemmas
tm.start()
jilog("Selecting concepts...")
lems = list(expandlem(lemma))
totag = select_concept(cur, lems, lim, sid_from, sid_to) ## all the results #FIXME [DBACCESS]
tm.stop()

#if totag:
    #template_data['message'] = 'Found something to tag'

##########################################################################
# Application logic code (process queries, access database, etc.)
##########################################################################



################################################################################
# CASE 1: THE CLEMMA WAS FOUND IN AT LEAST ONE CONCEPT
################################################################################
if totag:
    if re.match('(\d+)-[avnr]',lemma): # Search by synset instead of lemma
        template_data['message'] = """Looking for synset %s is not 
                                      actually implemented yet""" % lemma

    # 2014-06-12 [Tuan Anh]
    # Pull concept-word link information out for highlighting concepts
    all_cwlink = select_cwlink(cur, lems, lim) #FIXME [DBACCESS]
    cwl_map = {} # Stores concept-word links key = (sid, cid), values is a list of wid
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
    for (sid, cid, clemma, tag, tags, comment) in totag:
        if tag and re.match('(\d+)-[avnr]',tag) and tag not in all_synsets:
            all_synsets.append(tag)
        store_comment(comment)

        # store_comment(ntag)

        sid = int(sid)
        #wid=int(wid)
        cid=int(cid)
        ## show[tag][sid][cid] = (wids, clemma, nlemma, tag, ntag, tags, comment)
        #cwids[cid].append(wid)  ### for MWEs just write over with the new values
        show[tag][sid][cid] = [cwl_map[(sid, cid)], clemma, tags, comment]
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



    ############################################################################
    # COMMENT SUMMARY (TO SHOW ON TOP OF THE PAGE)
    ############################################################################
    # 2014-06-10 [Tuan Anh]
    # Add comment summary box
    template_data['comment_summary'] = ''
    if len(all_comments) > 0:
        com_sum = ''
        for a_pair in reversed(sorted(all_comments.items(), 
                                      key=operator.itemgetter(1, 0))):
            com_sum += "<tr> <td>%s</td> <td>%s</td> </tr>" % a_pair

        # If it looks like a synset, it becomes clickable 
        # the target is the right (wn) panel
        com_sum = re.sub(r'([0-9]{8}-[varn])', 
                 r"""<a href='wn-gridx.cgi?synset=\1&gridmode=%s' 
                     target='wn'>\1</a> [wn_list_loc(\1)]
                  """ % gridmode, com_sum)

        # 2014-06-15 [Tuan Anh]
        # Shan needs to have item number to be shown for each 
        # synset found in comment (easy to check)
        for i, t in enumerate(sss):
            com_sum = com_sum.replace('[wn_list_loc(%s)]' % t, 
                    """(%d<sub><font color='DarkRed' 
                        size='-2'>%s</font></sub>)""" % ( i+1, t[-1]))

        # remove any not found synset
        com_sum = re.sub(r'(\[wn_list_loc\([0-9]{8}-[varn]\)\])', 
                         '(NITL)', com_sum)
    ############################################################################
        template_data['comment_summary'] = com_sum
    ############################################################################







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
    navigator_bar_html = """<a href='#bookmark_PAGE_TOP' class='bookmark_top' 
                               alt='Top'></a>"""
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
            tmp_lex_group.append("(<a href='%s?synset=%s&gridmode=ntumcgrid' target='wn'>%s</a>)" %(wncgi, ltag, ltag))

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
                tmp_lex_group.append("<p>")
                tmp_lex_group.append(HTML.show_sid_bttn(corpus, lsid, clemma) +\
                                     "&nbsp;"),

                (cwds, clemma, tags, com) = show[ltag][lsid][lcid]



                # 2014-06-12 [Tuan Anh]
                # I changed this part of code to improve the performance
                # This query should be executed only once per sentence
#                tmp_lex_group.append("<br>")
                # if not ntag:
                #     ntag=ltag
                # if not ltag:
                #     ntag =''
                wp = '' # wordnet POS   
                #for (wid, word, pos, lemma) in d:

                if not int(lsid) in sentences_words:
                    jilog("""It seems that I can't really find %s 
                             all_sids=%s, sentences_words=%s...\n
                          """ % (lsid, repr(sorted(all_sids)),
                                 repr(sorted(sentences_words.keys()))))

                # PRINT SENTENCE (BY WORD)
                tmp_lex_group.append("""<span style="font-size:120%">""")

                for wid, word, pos, lemma in sentences_words[int(lsid)]:

                    if wid in cwds: # IF IT IS PART OF THE CONCEPT TAGGING

                        wp = pos2wn(pos,lang)  # POS of the selected word

                        # LINK TO TAG-WORD (FOR SELECTED WORD ONLY)
                        tt = """%s?lemma=%s&corpus=%s&lang=%s"""
                        tt += """&gridmode=%s&sid=%d&wid=%d""" 
                        tt = tt % ("tag-word.cgi", lemma,  corpus, 
                                   lang, gridmode, lsid, wid)
                        ttt = cgi.escape("""%d:%s:%s&#013;%s""" % (wid, 
                                    pos, lemma, com), quote = True)
                        tmp_lex_group.append("""<a style='color: Green;' 
                                 title = '%s' href='%s' target='_parent'
                                 >%s</a><sub><font size='-2'>%s</font></sub>
                                 """ % (ttt, tt, word, wp))

                    else: # OTHER WORDS 
                        # FIXME(Wilson): Undefined variable 'ma'
                        tmp_lex_group.append("""<span 
                                                title='%d:%s:%s'>%s</span>
                                             """ % (wid, pos, ma, word))

                tmp_lex_group.append("""</span>""")

                # PRINT THE TAG BOXES (THIS IS SHARED WITH TAG-WORD)
                tmp_lex_group.append("<br>")
                tmp_lex_group.append(tbox(sss, "%s_%s" % (lsid, lcid), 
                                          wp, ltag, com))

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
    template_data['tagbox_default'] = tbox(sss, 'all', '', '', com_all)
    template_data['cids'] = cids
    HTML.render_template('tag-lexs.htm', template_data, cookie_text)
    # end of totag = True

################################################################################
# CASE 2: THE CLEMMA WAS NOT FOUND (AND, OF COURSE, IT BELONGS TO NO CONCEPT)
################################################################################
elif not lemma:
    # not totag and not lemma => show search form
    HTML.render_template('tag-lexs-search.htm', template_data, cookie_text)


################################################################################
# CASE 3: THE CLEMMA WAS FOUND BUT IT DOES NOT BELONG TO A CONCEPT (ADD?)
################################################################################
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
    HTML.render_template('tag-lexs-add.htm', template_data, cookie_text)

