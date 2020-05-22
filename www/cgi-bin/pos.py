#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict as dd
from lang_data_toolkit import *

###########################################################
# This script takes in the POS to UPOS mapping that exists 
# in lang_data_toolkit and outputs the string for an dict
# that maps from the UPOS to POS (for search purposes)
###########################################################

upos_name = dd(lambda: dd(lambda: str()))
upos_name['ADJ']['eng'] = 'adjective'
upos_name['ADJ']['jpn'] = u'形容词'

upos_name['ADP']['eng'] = 'adposition'
upos_name['ADP']['jpn'] = u'方位词'

upos_name['ADV']['eng'] = 'adverb'
upos_name['ADV']['jpn'] = u'副词'

upos_name['AUX']['eng'] = 'auxiliary verb'
upos_name['AUX']['jpn'] = u'助動詞'

upos_name['CONJ']['eng'] = 'coordinating conjunction'
upos_name['CONJ']['jpn'] = u'连词' #!!! check

upos_name['DET']['eng'] = 'determiner'
upos_name['DET']['jpn'] = u'代词'

upos_name['INTJ']['eng'] = 'interjection'
upos_name['INTJ']['jpn'] = u'間投詞' #!!! check

upos_name['NOUN']['eng'] = 'noun'
upos_name['NOUN']['jpn'] = u'名词'

upos_name['NUM']['eng'] = 'numeral'
upos_name['NUM']['jpn'] = u'数词'

upos_name['PRT']['eng'] = 'particle'
upos_name['PRT']['jpn'] = u'助词'

upos_name['PRON']['eng'] = 'pronoun'
upos_name['PRON']['jpn'] = u'代名词'

upos_name['PROPN']['eng'] = 'proper noun'
upos_name['PROPN']['jpn'] = u'固有名詞'

upos_name['PUNCT']['eng'] = 'punctuation'
upos_name['PUNCT']['jpn'] = u'标点符号'

upos_name['SCONJ']['eng'] = 'subordinating conjunction'
upos_name['SCONJ']['jpn'] = 'subordinating conjunction' #!!! check

upos_name['SYM']['eng'] = 'symbol'
upos_name['SYM']['jpn'] = 'symbol' #!!! check

upos_name['VERB']['eng'] = 'verb'
upos_name['VERB']['jpn'] = u'动词'

upos_name['X']['eng'] = 'other'
upos_name['X']['jpn'] = u'其他'


upos_tags = dd(lambda: dd(lambda: dd(lambda: list())))

langlist = ['ita']
for lang in langlist:
    for tag in pos_tags[lang].keys():
        upos = pos_tags[lang][tag]['upos']
        upos_tags[lang][upos]['pos'].append(tag)
        # print tag + "	" + upos  #print the tab separated values

for lang in upos_tags.keys():
    print("\n\n\n")
    for upos in upos_tags[lang].keys():
        stringlist = ""
        for postag in upos_tags[lang][upos]['pos']:
            stringlist += "u'" + postag + "',"

        print("upos_tags['" + lang + "']['" +  upos + "']['pos'] = [" + stringlist[:-1] +"]")

        if lang in upos_name[upos].keys():
            print("upos_tags['" + lang + "']['" +  upos + "']['def'] = u'" + upos_name[upos][lang] + "'")
        else:
            print("upos_tags['" + lang + "']['" +  upos + "']['def'] = u'" + upos_name[upos]['eng'] + "'")
            
        print("upos_tags['" + lang + "']['" +  upos + "']['eng_def'] = u'" + upos_name[upos]['eng'] + "'")
