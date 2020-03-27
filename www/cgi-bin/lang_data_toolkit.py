#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict as dd

#mtags values
mtags = [ 'e', 'x', 'w' ] + ["org", "loc", "per", "dat", "oth", "num", "dat:year"]

# mtags short form (to be displayed on tag list?)
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

valid_usernames = ['fcbond','lmorgado','letuananh','wangshan',
                   'rosechen','gbonansinga',

                   'tanzhixin','seayujie','wangwenjie',
                   'lewxuhong','eshleygao',

                   'gohrachael','wongsining','liutianli',
                   'nurizdihar', 'violaow','hojiaqian',
                   'sandrasoh']


corpuslangs = ['eng','cmn','jpn','ind']

# old users: 'yuehuiting', 'honxuemin',

wnnam = "Open Multilingual Wordnet"
wnver = "1.0"
wnurl = "http://compling.hss.ntu.edu.sg/omw/index.html"


####################################################################
# We're mapping to the Universal POS tags by Petrov, Das & McDonald
# http://universaldependencies.github.io/docs/u/pos/index.html
# As only mappings for old versions of the tagset existed, we 
# remapped the tagsets taking a few changes (e.g. for ENG & CMN)
####################################################################
pos_tags = dd(lambda: dd(lambda: dd(unicode)))
pos_tags['eng']['CC']['def'] = "coordinating conjunction"
pos_tags['eng']['CC']['eng_def'] = "coordinating conjunction"
pos_tags['eng']['CC']['upos'] = "CONJ"
pos_tags['eng']['CD']['def'] = "cardinal number"
pos_tags['eng']['CD']['eng_def'] = "cardinal number"
pos_tags['eng']['CD']['upos'] = "NUM"
pos_tags['eng']['DT']['def'] = "determiner"
pos_tags['eng']['DT']['eng_def'] = "determiner"
pos_tags['eng']['DT']['upos'] = "DET"
pos_tags['eng']['EX']['def'] = "existential there"
pos_tags['eng']['EX']['eng_def'] = "existential there"
pos_tags['eng']['EX']['upos'] = "PRON"
pos_tags['eng']['FW']['def'] = "foreign word"
pos_tags['eng']['FW']['eng_def'] = "foreign word"
pos_tags['eng']['FW']['upos'] = "X"
pos_tags['eng']['Fat']['def'] = "exclamation point"
pos_tags['eng']['Fat']['eng_def'] = "exclamation point"
pos_tags['eng']['Fat']['upos'] = "PUNCT"
pos_tags['eng']['Fc']['def'] = "comma"
pos_tags['eng']['Fc']['eng_def'] = "comma"
pos_tags['eng']['Fc']['upos'] = "PUNCT"
pos_tags['eng']['Fd']['def'] = "colon"
pos_tags['eng']['Fd']['eng_def'] = "colon"
pos_tags['eng']['Fd']['upos'] = "PUNCT"
pos_tags['eng']['Fe']['def'] = "quote(s)"
pos_tags['eng']['Fe']['eng_def'] = "quote(s)"
pos_tags['eng']['Fe']['upos'] = "PUNCT"
pos_tags['eng']['Fg']['def'] = "dash"
pos_tags['eng']['Fg']['eng_def'] = "dash"
pos_tags['eng']['Fg']['upos'] = "PUNCT"
pos_tags['eng']['Fh']['def'] = "slash"
pos_tags['eng']['Fh']['eng_def'] = "slash"
pos_tags['eng']['Fh']['upos'] = "PUNCT"
pos_tags['eng']['Fit']['def'] = "question mark"
pos_tags['eng']['Fit']['eng_def'] = "question mark"
pos_tags['eng']['Fit']['upos'] = "PUNCT"
pos_tags['eng']['Fp']['def'] = "period"
pos_tags['eng']['Fp']['eng_def'] = "period"
pos_tags['eng']['Fp']['upos'] = "PUNCT"
pos_tags['eng']['Fpa']['def'] = "left parenthesis"
pos_tags['eng']['Fpa']['eng_def'] = "left parenthesis"
pos_tags['eng']['Fpa']['upos'] = "PUNCT"
pos_tags['eng']['Fpt']['def'] = "right parenthesis"
pos_tags['eng']['Fpt']['eng_def'] = "right parenthesis"
pos_tags['eng']['Fpt']['upos'] = "PUNCT"
pos_tags['eng']['Fs']['def'] = "ellipsis"
pos_tags['eng']['Fs']['eng_def'] = "ellipsis"
pos_tags['eng']['Fs']['upos'] = "PUNCT"
pos_tags['eng']['Fx']['def'] = "semicolon"
pos_tags['eng']['Fx']['eng_def'] = "semicolon"
pos_tags['eng']['Fx']['upos'] = "PUNCT"
pos_tags['eng']['Fz']['def'] = "ellipsis"
pos_tags['eng']['Fz']['eng_def'] = "ellipsis"
pos_tags['eng']['Fz']['upos'] = "PUNCT"
pos_tags['eng']['IN']['def'] = "preposition or subordinating conjunction"
pos_tags['eng']['IN']['eng_def'] = "preposition or subordinating conjunction"
pos_tags['eng']['IN']['upos'] = "ADP"
pos_tags['eng']['JJ']['def'] = "adjective"
pos_tags['eng']['JJ']['eng_def'] = "adjective"
pos_tags['eng']['JJ']['upos'] = "ADJ"
pos_tags['eng']['JJR']['def'] = "adjective, comparative"
pos_tags['eng']['JJR']['eng_def'] = "adjective, comparative"
pos_tags['eng']['JJR']['upos'] = "ADJ"
pos_tags['eng']['JJS']['def'] = "adjective, superlative"
pos_tags['eng']['JJS']['eng_def'] = "adjective, superlative"
pos_tags['eng']['JJS']['upos'] = "ADJ"
pos_tags['eng']['MD']['def'] = "modal"
pos_tags['eng']['MD']['eng_def'] = "modal"
pos_tags['eng']['MD']['upos'] = "AUX"
pos_tags['eng']['NN']['def'] = "noun, singular or mass"
pos_tags['eng']['NN']['eng_def'] = "noun, singular or mass"
pos_tags['eng']['NN']['upos'] = "NOUN"
pos_tags['eng']['NNP']['def'] = "proper noun, singular"
pos_tags['eng']['NNP']['eng_def'] = "proper noun, singular"
pos_tags['eng']['NNP']['upos'] = "NOUN"
pos_tags['eng']['NNS']['def'] = "noun, plural"
pos_tags['eng']['NNS']['eng_def'] = "noun, plural"
pos_tags['eng']['NNS']['upos'] = "NOUN"
pos_tags['eng']['NNPS']['def'] = "proper noun, plural"
pos_tags['eng']['NNPS']['eng_def'] = "proper noun, plural"
pos_tags['eng']['NNPS']['upos'] = "NOUN"
pos_tags['eng']['PDT']['def'] = "predeterminer"
pos_tags['eng']['PDT']['eng_def'] = "predeterminer"
pos_tags['eng']['PDT']['upos'] = "ADV"
pos_tags['eng']['POS']['def'] = "possessive ending"
pos_tags['eng']['POS']['eng_def'] = "possessive ending"
pos_tags['eng']['POS']['upos'] = "PRT"
pos_tags['eng']['PRP']['def'] = "personal pronoun"
pos_tags['eng']['PRP']['eng_def'] = "personal pronoun"
pos_tags['eng']['PRP']['upos'] = "PRON"
pos_tags['eng']['PRP$']['def'] = "possessive pronoun"
pos_tags['eng']['PRP$']['eng_def'] = "possessive pronoun"
pos_tags['eng']['PRP$']['upos'] = "PRON"
pos_tags['eng']['RB']['def'] = "adverb"
pos_tags['eng']['RB']['eng_def'] = "adverb"
pos_tags['eng']['RB']['upos'] = "ADV"
pos_tags['eng']['RBR']['def'] = "adverb, comparative"
pos_tags['eng']['RBR']['eng_def'] = "adverb, comparative"
pos_tags['eng']['RBR']['upos'] = "ADV"
pos_tags['eng']['RBS']['def'] = "adverb, superlative"
pos_tags['eng']['RBS']['eng_def'] = "adverb, superlative"
pos_tags['eng']['RBS']['upos'] = "ADV"
pos_tags['eng']['RP']['def'] = "particle"
pos_tags['eng']['RP']['eng_def'] = "particle"
pos_tags['eng']['RP']['upos'] = "PRT"
pos_tags['eng']['TO']['def'] = "to"
pos_tags['eng']['TO']['eng_def'] = "to"
pos_tags['eng']['TO']['upos'] = "PRT"
pos_tags['eng']['UH']['def'] = "Interjection"
pos_tags['eng']['UH']['eng_def'] = "Interjection"
pos_tags['eng']['UH']['upos'] = "INTJ"
pos_tags['eng']['VAX']['def'] = "auxiliary verb"
pos_tags['eng']['VAX']['eng_def'] = "auxiliary verb"
pos_tags['eng']['VAX']['upos'] = "AUX"
pos_tags['eng']['VB']['def'] = "verb, base form"
pos_tags['eng']['VB']['eng_def'] = "verb, base form"
pos_tags['eng']['VB']['upos'] = "VERB"
pos_tags['eng']['VBD']['def'] = "verb, past tense"
pos_tags['eng']['VBD']['eng_def'] = "verb, past tense"
pos_tags['eng']['VBD']['upos'] = "VERB"
pos_tags['eng']['VBG']['def'] = "verb, gerund or present participle"
pos_tags['eng']['VBG']['eng_def'] = "verb, gerund or present participle"
pos_tags['eng']['VBG']['upos'] = "VERB"
pos_tags['eng']['VBN']['def'] = "verb, past participle"
pos_tags['eng']['VBN']['eng_def'] = "verb, past participle"
pos_tags['eng']['VBN']['upos'] = "VERB"
pos_tags['eng']['VBP']['def'] = "verb, non-3rd person singular present"
pos_tags['eng']['VBP']['eng_def'] = "verb, non-3rd person singular present"
pos_tags['eng']['VBP']['upos'] = "VERB"
pos_tags['eng']['VBZ']['def'] = "verb, 3rd person singular present"
pos_tags['eng']['VBZ']['eng_def'] = "verb, 3rd person singular present"
pos_tags['eng']['VBZ']['upos'] = "VERB"
pos_tags['eng']['WDT']['def'] = "wh-determiner"
pos_tags['eng']['WDT']['eng_def'] = "wh-determiner"
pos_tags['eng']['WDT']['upos'] = "DET"
pos_tags['eng']['WP']['def'] = "wh-pronoun"
pos_tags['eng']['WP']['eng_def'] = "wh-pronoun"
pos_tags['eng']['WP']['upos'] = "PRON"
pos_tags['eng']['WP$']['def'] = "possessive wh-pronoun"
pos_tags['eng']['WP$']['eng_def'] = "possessive wh-pronoun"
pos_tags['eng']['WP$']['upos'] = "PRON"
pos_tags['eng']['WRB']['def'] = "wh-adverb"
pos_tags['eng']['WRB']['eng_def'] = "wh-adverb"
pos_tags['eng']['WRB']['upos'] = "ADV"
pos_tags['eng']['Z']['def'] = "number"
pos_tags['eng']['Z']['eng_def'] = "number"
pos_tags['eng']['Z']['upos'] = "NUM" #!!! There are a lot of things going here!
pos_tags['eng']['Zm']['def'] = "number (money)"
pos_tags['eng']['Zm']['eng_def'] = "number (money)"
pos_tags['eng']['Zm']['upos'] = "NUM" #!!! This is money, it's on the guidelines
pos_tags['eng']['Zp']['def'] = "number (percentage)"
pos_tags['eng']['Zp']['eng_def'] = "number (percentage)"
pos_tags['eng']['Zp']['upos'] = "NUM" #!!! This is percentage, should be similar to money
pos_tags['eng']['Zu']['def'] = "number (unit)"
pos_tags['eng']['Zu']['eng_def'] = "number (unit)"
pos_tags['eng']['Zu']['upos'] = "NUM" #!!! Are all these tokenization errors

# CHINESE POS TAGS
pos_tags['cmn']['AD']['def'] = "adverb"
pos_tags['cmn']['AD']['eng_def'] = "adverb"
pos_tags['cmn']['AD']['upos'] = "ADV"
pos_tags['cmn']['AD2']['def'] = "adverb (reduplication)"
pos_tags['cmn']['AD2']['eng_def'] = "adverb (reduplication)"
pos_tags['cmn']['AD2']['upos'] = "ADV"
pos_tags['cmn']['AS']['def'] = "aspect particle"
pos_tags['cmn']['AS']['eng_def'] = "aspect particle"
pos_tags['cmn']['AS']['upos'] = "PRT"
pos_tags['cmn']['BA']['def'] = "ba3 in ba-construction"
pos_tags['cmn']['BA']['eng_def'] = "ba3 in ba-construction"
pos_tags['cmn']['BA']['upos'] = "PRT"
pos_tags['cmn']['CC']['def'] = "coordinating conjunction"
pos_tags['cmn']['CC']['eng_def'] = "coordinating conjunction"
pos_tags['cmn']['CC']['upos'] = "CONJ"
pos_tags['cmn']['CD']['def'] = "cardinal number"
pos_tags['cmn']['CD']['eng_def'] = "cardinal number"
pos_tags['cmn']['CD']['upos'] = "NUM"
pos_tags['cmn']['CS']['def'] = "subordinating conjunction"
pos_tags['cmn']['CS']['eng_def'] = "subordinating conjunction"
pos_tags['cmn']['CS']['upos'] = "SCONJ"
pos_tags['cmn']['DEC']['def'] = "de5 as a complementizer or a nominalizer"
pos_tags['cmn']['DEC']['eng_def'] = "de5 as a complementizer or a nominalizer"
pos_tags['cmn']['DEC']['upos'] = "PRT"
pos_tags['cmn']['DEG']['def'] = "de5 as a genitive marker and an associative marker"
pos_tags['cmn']['DEG']['eng_def'] = "de5 as a genitive marker and an associative marker"
pos_tags['cmn']['DEG']['upos'] = "PRT"
pos_tags['cmn']['DER']['def'] = "resultative de5"
pos_tags['cmn']['DER']['eng_def'] = "resultative de5"
pos_tags['cmn']['DER']['upos'] = "PRT"
pos_tags['cmn']['DEV']['def'] = "manner de5"
pos_tags['cmn']['DEV']['eng_def'] = "manner de5"
pos_tags['cmn']['DEV']['upos'] = "PRT"
pos_tags['cmn']['DT']['def'] = "determiner"
pos_tags['cmn']['DT']['eng_def'] = "determiner"
pos_tags['cmn']['DT']['upos'] = "DET"
pos_tags['cmn']['ETC']['def'] = "ETC (deng3 and deng3deng3)"
pos_tags['cmn']['ETC']['eng_def'] = "ETC (deng3 and deng3deng3)"
pos_tags['cmn']['ETC']['upos'] = "ADJ"
pos_tags['cmn']['FW']['def'] = "foreign word"
pos_tags['cmn']['FW']['eng_def'] = "foreign word"
pos_tags['cmn']['FW']['upos'] = "X"
pos_tags['cmn']['IJ']['def'] = "interjection"
pos_tags['cmn']['IJ']['eng_def'] = "interjection"
pos_tags['cmn']['IJ']['upos'] = "INTJ"
pos_tags['cmn']['JJ']['def'] = "other noun modifier"
pos_tags['cmn']['JJ']['eng_def'] = "other noun modifier"
pos_tags['cmn']['JJ']['upos'] = "ADJ"
pos_tags['cmn']['JJ2']['def'] = "other noun modifier (reduplication)"
pos_tags['cmn']['JJ2']['eng_def'] = "other noun modifier (reduplication)"
pos_tags['cmn']['JJ2']['upos'] = "ADJ"
pos_tags['cmn']['LB']['def'] = "bei4 in long bei-construction"
pos_tags['cmn']['LB']['eng_def'] = "bei4 in long bei-construction"
pos_tags['cmn']['LB']['upos'] = "PRT"
pos_tags['cmn']['LC']['def'] = "localizer"
pos_tags['cmn']['LC']['eng_def'] = "localizer"
pos_tags['cmn']['LC']['upos'] = "ADP"
pos_tags['cmn']['M']['def'] = "measure word"
pos_tags['cmn']['M']['eng_def'] = "measure word"
pos_tags['cmn']['M']['upos'] = "NOUN"
pos_tags['cmn']['M2']['def'] = "measure word (reduplication)"
pos_tags['cmn']['M2']['eng_def'] = "measure word (reduplication)"
pos_tags['cmn']['M2']['upos'] = "NOUN"
pos_tags['cmn']['MSP']['def'] = "other particle"
pos_tags['cmn']['MSP']['eng_def'] = "other particle"
pos_tags['cmn']['MSP']['upos'] = "PRT"
pos_tags['cmn']['NN']['def'] = "other noun"
pos_tags['cmn']['NN']['eng_def'] = "other noun"
pos_tags['cmn']['NN']['upos'] = "NOUN"
pos_tags['cmn']['NN2']['def'] = "other noun (reduplication)"
pos_tags['cmn']['NN2']['eng_def'] = "other noun (reduplication)"
pos_tags['cmn']['NN2']['upos'] = "NOUN"
pos_tags['cmn']['NR']['def'] = "proper noun"
pos_tags['cmn']['NR']['eng_def'] = "proper noun"
pos_tags['cmn']['NR']['upos'] = "PROPN"
pos_tags['cmn']['NT']['def'] = "temporal noun"
pos_tags['cmn']['NT']['eng_def'] = "temporal noun"
pos_tags['cmn']['NT']['upos'] = "ADV"
pos_tags['cmn']['OD']['def'] = "ordinal number"
pos_tags['cmn']['OD']['eng_def'] = "ordinal number"
pos_tags['cmn']['OD']['upos'] = "NUM"
pos_tags['cmn']['ON']['def'] = "onomatopeia"
pos_tags['cmn']['ON']['eng_def'] = "onomatopeia"
pos_tags['cmn']['ON']['upos'] = "X"
pos_tags['cmn']['P']['def'] = "preposition"
pos_tags['cmn']['P']['eng_def'] = "preposition"
pos_tags['cmn']['P']['upos'] = "ADP"
pos_tags['cmn']['PN']['def'] = "pronoun"
pos_tags['cmn']['PN']['eng_def'] = "pronoun"
pos_tags['cmn']['PN']['upos'] = "PRON"
pos_tags['cmn']['PN2']['def'] = "pronoun (reduplication)"
pos_tags['cmn']['PN2']['eng_def'] = "pronoun (reduplication)"
pos_tags['cmn']['PN2']['upos'] = "PROPN"
pos_tags['cmn']['PU']['def'] = "punctuation"
pos_tags['cmn']['PU']['eng_def'] = "punctuation"
pos_tags['cmn']['PU']['upos'] = "PUNCT"
pos_tags['cmn']['SB']['def'] = "bei4 in short bei-construction"
pos_tags['cmn']['SB']['eng_def'] = "bei4 in short bei-construction"
pos_tags['cmn']['SB']['upos'] = "PRT"
pos_tags['cmn']['SP']['def'] = "sentence-final particle"
pos_tags['cmn']['SP']['eng_def'] = "sentence-final particle"
pos_tags['cmn']['SP']['upos'] = "PRT"
pos_tags['cmn']['URL']['def'] = "url"
pos_tags['cmn']['URL']['eng_def'] = "url"
pos_tags['cmn']['URL']['upos'] = "SYM"
pos_tags['cmn']['VA']['def'] = "predicative adjective"
pos_tags['cmn']['VA']['eng_def'] = "predicative adjective"
pos_tags['cmn']['VA']['upos'] = "ADJ"
pos_tags['cmn']['VA2']['def'] = "predicative adjective (reduplication)"
pos_tags['cmn']['VA2']['eng_def'] = "predicative adjective (reduplication)"
pos_tags['cmn']['VA2']['upos'] = "ADJ"
pos_tags['cmn']['VC']['def'] = "copula"
pos_tags['cmn']['VC']['eng_def'] = "copula"
pos_tags['cmn']['VC']['upos'] = "VERB"
pos_tags['cmn']['VE']['def'] = "you3 as the main verb"
pos_tags['cmn']['VE']['eng_def'] = "you3 as the main verb"
pos_tags['cmn']['VE']['upos'] = "VERB"
pos_tags['cmn']['VV']['def'] = "other verb"
pos_tags['cmn']['VV']['eng_def'] = "other verb"
pos_tags['cmn']['VV']['upos'] = "VERB"
pos_tags['cmn']['VV2']['def'] = "other verb (reduplication)"
pos_tags['cmn']['VV2']['eng_def'] = "other verb (reduplication)"
pos_tags['cmn']['VV2']['upos'] = "VERB"


# JAPANESE POS TAGS
pos_tags['jpn'][u'語断片']['def'] = u"語断片"
pos_tags['jpn'][u'語断片']['eng_def'] = u"fragment"
pos_tags['jpn'][u'語断片']['upos'] = u"X"
pos_tags['jpn'][u'非言語音']['def'] = u"非言語音"
pos_tags['jpn'][u'非言語音']['eng_def'] = u"nonlinguistic sound"
pos_tags['jpn'][u'非言語音']['upos'] = u"X"
pos_tags['jpn'][u'記号']['def'] = u"記号"
pos_tags['jpn'][u'記号']['eng_def'] = u"symbol"
pos_tags['jpn'][u'記号']['upos'] = u"X"
pos_tags['jpn'][u'記号-アルファベット']['def'] = u"記号 アルファベット"
pos_tags['jpn'][u'記号-アルファベット']['eng_def'] = u"symbol aphabetic"
pos_tags['jpn'][u'記号-アルファベット']['upos'] = u"X"
pos_tags['jpn'][u'記号-一般']['def'] = u"記号 一般"
pos_tags['jpn'][u'記号-一般']['eng_def'] = u"symbol normal"
pos_tags['jpn'][u'記号-一般']['upos'] = u"PUNCT"
pos_tags['jpn'][u'記号-句点']['def'] = u"記号 句点"
pos_tags['jpn'][u'記号-句点']['eng_def'] = u"full stop"
pos_tags['jpn'][u'記号-句点']['upos'] = u"PUNCT"
pos_tags['jpn'][u'記号-括弧閉']['def'] = u"記号 括弧閉"
pos_tags['jpn'][u'記号-括弧閉']['eng_def'] = u"symbol right parenthesis"
pos_tags['jpn'][u'記号-括弧閉']['upos'] = u"PUNCT"
pos_tags['jpn'][u'記号-括弧開']['def'] = u"記号 括弧開"
pos_tags['jpn'][u'記号-括弧開']['eng_def'] = u"symbol left paranthesis"
pos_tags['jpn'][u'記号-括弧開']['upos'] = u"PUNCT"
pos_tags['jpn'][u'記号-空白']['def'] = u"記号-空白"
pos_tags['jpn'][u'記号-空白']['eng_def'] = u"symbol space"
pos_tags['jpn'][u'記号-空白']['upos'] = u"PUNCT"
pos_tags['jpn'][u'記号-読点']['def'] = u"記号 読点"
pos_tags['jpn'][u'記号-読点']['eng_def'] = u"comma"
pos_tags['jpn'][u'記号-読点']['upos'] = u"PUNCT"
pos_tags['jpn'][u'接頭詞']['def'] = u"接頭詞"
pos_tags['jpn'][u'接頭詞']['eng_def'] = u"prefix"
pos_tags['jpn'][u'接頭詞']['upos'] = u"NOUN"
pos_tags['jpn'][u'接頭詞-動詞接続']['def'] = u"接頭詞 動詞接続"
pos_tags['jpn'][u'接頭詞-動詞接続']['eng_def'] = u"prefix verbal"
pos_tags['jpn'][u'接頭詞-動詞接続']['upos'] = u"VERB"
pos_tags['jpn'][u'接頭詞-名詞接続']['def'] = u"接頭詞 名詞接続"
pos_tags['jpn'][u'接頭詞-名詞接続']['eng_def'] = u"prefix nominal"
pos_tags['jpn'][u'接頭詞-名詞接続']['upos'] = u"NOUN"
pos_tags['jpn'][u'接頭詞-形容詞接続']['def'] = u"接頭詞 形容詞接続"
pos_tags['jpn'][u'接頭詞-形容詞接続']['eng_def'] = u"prefix adjectival"
pos_tags['jpn'][u'接頭詞-形容詞接続']['upos'] = u"ADJ"
pos_tags['jpn'][u'接頭詞-数接続']['def'] = u"接頭詞 数接続"
pos_tags['jpn'][u'接頭詞-数接続']['eng_def'] = u"prefix numerical"
pos_tags['jpn'][u'接頭詞-数接続']['upos'] = u"NUM"
pos_tags['jpn'][u'接続詞']['def'] = u"接続詞"
pos_tags['jpn'][u'接続詞']['eng_def'] = u"conjunction"
pos_tags['jpn'][u'接続詞']['upos'] = u"CONJ"
pos_tags['jpn'][u'形容詞']['def'] = u"形容詞"
pos_tags['jpn'][u'形容詞']['eng_def'] = u"adjective"
pos_tags['jpn'][u'形容詞']['upos'] = u"ADJ"
pos_tags['jpn'][u'形容詞-自立']['def'] = u"形容詞 自立"
pos_tags['jpn'][u'形容詞-自立']['eng_def'] = u"adjective main"
pos_tags['jpn'][u'形容詞-自立']['upos'] = u"ADJ"
pos_tags['jpn'][u'形容詞-接尾']['def'] = u"形容詞 接尾"
pos_tags['jpn'][u'形容詞-接尾']['eng_def'] = u"adjective suffix"
pos_tags['jpn'][u'形容詞-接尾']['upos'] = u"ADJ"
pos_tags['jpn'][u'形容詞-非自立']['def'] = u"形容詞 非自立"
pos_tags['jpn'][u'形容詞-非自立']['eng_def'] = u"adjective aux"
pos_tags['jpn'][u'形容詞-非自立']['upos'] = u"ADJ"
pos_tags['jpn'][u'感動詞']['def'] = u"感動詞"
pos_tags['jpn'][u'感動詞']['eng_def'] = u"exclamation"
pos_tags['jpn'][u'感動詞']['upos'] = u"X"
pos_tags['jpn'][u'名詞']['def'] = u"名詞"
pos_tags['jpn'][u'名詞']['eng_def'] = u"noun"
pos_tags['jpn'][u'名詞']['upos'] = u"NOUN"
pos_tags['jpn'][u'名詞-サ変接続']['def'] = u"名詞 サ変接続"
pos_tags['jpn'][u'名詞-サ変接続']['eng_def'] = u"noun verbal" # Nouns that can appear before 'suru' and related verbs
pos_tags['jpn'][u'名詞-サ変接続']['upos'] = u"NOUN"
pos_tags['jpn'][u'名詞-ナイ形容詞語幹']['def'] = u"名詞 ナイ形容詞語幹"
pos_tags['jpn'][u'名詞-ナイ形容詞語幹']['eng_def'] = u"noun nai_adjective"
pos_tags['jpn'][u'名詞-ナイ形容詞語幹']['upos'] = u"NOUN"
pos_tags['jpn'][u'名詞-一般']['def'] = u"名詞 一般"
pos_tags['jpn'][u'名詞-一般']['eng_def'] = u"noun common"
pos_tags['jpn'][u'名詞-一般']['upos'] = u"NOUN"
pos_tags['jpn'][u'名詞-副詞可能']['def'] = u"名詞 副詞可能"
pos_tags['jpn'][u'名詞-副詞可能']['eng_def'] = u"noun adverbial"
pos_tags['jpn'][u'名詞-副詞可能']['upos'] = u"NOUN"
pos_tags['jpn'][u'名詞-動詞非自立的']['def'] = u"名詞 動詞非自立的"
pos_tags['jpn'][u'名詞-動詞非自立的']['eng_def'] = u"noun verbal_aux"
pos_tags['jpn'][u'名詞-動詞非自立的']['upos'] = u"VERB"
pos_tags['jpn'][u'名詞-代名詞']['def'] = u"名詞 代名詞"
pos_tags['jpn'][u'名詞-代名詞']['eng_def'] = u"noun pronoun"
pos_tags['jpn'][u'名詞-代名詞']['upos'] = u"PRON"
pos_tags['jpn'][u'名詞-代名詞-一般']['def'] = u"名詞 代名詞 一般"
pos_tags['jpn'][u'名詞-代名詞-一般']['eng_def'] = u"noun pronoun normal"
pos_tags['jpn'][u'名詞-代名詞-一般']['upos'] = u"PRON"
pos_tags['jpn'][u'名詞-代名詞-縮約']['def'] = u"名詞 代名詞 縮約"
pos_tags['jpn'][u'名詞-代名詞-縮約']['eng_def'] = u"noun pronoun contraction"
pos_tags['jpn'][u'名詞-代名詞-縮約']['upos'] = u"PRON"
pos_tags['jpn'][u'名詞-固有名詞']['def'] = u"名詞 固有名詞"
pos_tags['jpn'][u'名詞-固有名詞']['eng_def'] = u"noun proper"
pos_tags['jpn'][u'名詞-固有名詞']['upos'] = u"PROPN"
pos_tags['jpn'][u'名詞-固有名詞-一般']['def'] = u"名詞 固有名詞 一般"
pos_tags['jpn'][u'名詞-固有名詞-一般']['eng_def'] = u"noun proper normal"
pos_tags['jpn'][u'名詞-固有名詞-一般']['upos'] = u"PROPN"
pos_tags['jpn'][u'名詞-固有名詞-人名']['def'] = u"名詞 固有名詞 人名"
pos_tags['jpn'][u'名詞-固有名詞-人名']['eng_def'] = u"noun proper person"
pos_tags['jpn'][u'名詞-固有名詞-人名']['upos'] = u"PROPN"
pos_tags['jpn'][u'名詞-固有名詞-人名-一般']['def'] = u"名詞 固有名詞 人名 一般"
pos_tags['jpn'][u'名詞-固有名詞-人名-一般']['eng_def'] = u"noun proper person normal"
pos_tags['jpn'][u'名詞-固有名詞-人名-一般']['upos'] = u"PROPN"
pos_tags['jpn'][u'名詞-固有名詞-人名-名']['def'] = u"名詞 固有名詞 人名 名"
pos_tags['jpn'][u'名詞-固有名詞-人名-名']['eng_def'] = u"noun proper person given_name"
pos_tags['jpn'][u'名詞-固有名詞-人名-名']['upos'] = u"PROPN"
pos_tags['jpn'][u'名詞-固有名詞-人名-姓']['def'] = u"名詞 固有名詞 人名 姓"
pos_tags['jpn'][u'名詞-固有名詞-人名-姓']['eng_def'] = u"noun proper person surname"
pos_tags['jpn'][u'名詞-固有名詞-人名-姓']['upos'] = u"PROPN"
pos_tags['jpn'][u'名詞-固有名詞-地域']['def'] = u"名詞 固有名詞 地域"
pos_tags['jpn'][u'名詞-固有名詞-地域']['eng_def'] = u"noun proper place"
pos_tags['jpn'][u'名詞-固有名詞-地域']['upos'] = u"PROPN"
pos_tags['jpn'][u'名詞-固有名詞-地域-一般']['def'] = u"名詞 固有名詞 地域 一般"
pos_tags['jpn'][u'名詞-固有名詞-地域-一般']['eng_def'] = u"noun proper place normal"
pos_tags['jpn'][u'名詞-固有名詞-地域-一般']['upos'] = u"PROPN"
pos_tags['jpn'][u'名詞-固有名詞-地域-国']['def'] = u"名詞 固有名詞 地域 国"
pos_tags['jpn'][u'名詞-固有名詞-地域-国']['eng_def'] = u"noun proper place country"
pos_tags['jpn'][u'名詞-固有名詞-地域-国']['upos'] = u"PROPN"
pos_tags['jpn'][u'名詞-固有名詞-組織']['def'] = u"名詞 固有名詞 組織"
pos_tags['jpn'][u'名詞-固有名詞-組織']['eng_def'] = u"noun proper place organization"
pos_tags['jpn'][u'名詞-固有名詞-組織']['upos'] = u"PROPN"
pos_tags['jpn'][u'名詞-接尾']['def'] = u"名詞 接尾"
pos_tags['jpn'][u'名詞-接尾']['eng_def'] = u"noun suffix"
pos_tags['jpn'][u'名詞-接尾']['upos'] = u"NOUN"
pos_tags['jpn'][u'名詞-接尾-サ変接続']['def'] = u"名詞 接尾 サ変接続"
pos_tags['jpn'][u'名詞-接尾-サ変接続']['eng_def'] = u"noun suffix verbal"
pos_tags['jpn'][u'名詞-接尾-サ変接続']['upos'] = u"NOUN"
pos_tags['jpn'][u'名詞-接尾-一般']['def'] = u"名詞 接尾 一般"
pos_tags['jpn'][u'名詞-接尾-一般']['eng_def'] = u"noun suffix normal"
pos_tags['jpn'][u'名詞-接尾-一般']['upos'] = u"NOUN"
pos_tags['jpn'][u'名詞-接尾-人名']['def'] = u"名詞 接尾 人名"
pos_tags['jpn'][u'名詞-接尾-人名']['eng_def'] = u"noun suffix peron"
pos_tags['jpn'][u'名詞-接尾-人名']['upos'] = u"NOUN"
pos_tags['jpn'][u'名詞-接尾-助動詞語幹']['def'] = u"名詞 接尾 助動詞語幹"
pos_tags['jpn'][u'名詞-接尾-助動詞語幹']['eng_def'] = u"noun suffix aux"
pos_tags['jpn'][u'名詞-接尾-助動詞語幹']['upos'] = u"NOUN"
pos_tags['jpn'][u'名詞-接尾-助数詞']['def'] = u"名詞 接尾 助数詞"
pos_tags['jpn'][u'名詞-接尾-助数詞']['eng_def'] = u"noun suffix classifier"
pos_tags['jpn'][u'名詞-接尾-助数詞']['upos'] = u"NOUN"
pos_tags['jpn'][u'名詞-接尾-地域']['def'] = u"名詞 接尾 地域"
pos_tags['jpn'][u'名詞-接尾-地域']['eng_def'] = u"noun suffix place"
pos_tags['jpn'][u'名詞-接尾-地域']['upos'] = u"NOUN"
pos_tags['jpn'][u'名詞-接尾-形容動詞語幹']['def'] = u"名詞 接尾 形容動詞語幹"
pos_tags['jpn'][u'名詞-接尾-形容動詞語幹']['eng_def'] = u"noun suffix adjective"
pos_tags['jpn'][u'名詞-接尾-形容動詞語幹']['upos'] = u"ADJ"
pos_tags['jpn'][u'名詞-接尾-特殊']['def'] = u"名詞 接尾 特殊"
pos_tags['jpn'][u'名詞-接尾-特殊']['eng_def'] = u"noun suffix special"
pos_tags['jpn'][u'名詞-接尾-特殊']['upos'] = u"NOUN"
pos_tags['jpn'][u'名詞-接続詞的']['def'] = u"名詞 接続詞的"
pos_tags['jpn'][u'名詞-接続詞的']['eng_def'] = u"noun suffix conjunctive"
pos_tags['jpn'][u'名詞-接続詞的']['upos'] = u"CONJ"
pos_tags['jpn'][u'名詞-数']['def'] = u"名詞 数"
pos_tags['jpn'][u'名詞-数']['eng_def'] = u"noun numeral"
pos_tags['jpn'][u'名詞-数']['upos'] = u"NUM"
pos_tags['jpn'][u'名詞-特殊']['def'] = u"名詞 特殊"
pos_tags['jpn'][u'名詞-特殊']['eng_def'] = u"noun special"
pos_tags['jpn'][u'名詞-特殊']['upos'] = u"NOUN"
pos_tags['jpn'][u'名詞-特殊-助動詞語幹']['def'] = u"名詞 特殊 助動詞語幹"
pos_tags['jpn'][u'名詞-特殊-助動詞語幹']['eng_def'] = u"noun special aux"
pos_tags['jpn'][u'名詞-特殊-助動詞語幹']['upos'] = u"NOUN"
pos_tags['jpn'][u'連体詞']['def'] = u"連体詞"
pos_tags['jpn'][u'連体詞']['eng_def'] = u"adnominal"
pos_tags['jpn'][u'連体詞']['upos'] = u"DET"
pos_tags['jpn'][u'名詞-引用文字列']['def'] = u"名詞 引用文字列"
pos_tags['jpn'][u'名詞-引用文字列']['eng_def'] = u"noun quote"
pos_tags['jpn'][u'名詞-引用文字列']['upos'] = u"PROPN"
pos_tags['jpn'][u'名詞-形容動詞語幹']['def'] = u"名詞 形容動詞語幹" # The base form of adjectives: words that appear before な
pos_tags['jpn'][u'名詞-形容動詞語幹']['eng_def'] = u"noun adjective"
pos_tags['jpn'][u'名詞-形容動詞語幹']['upos'] = u"ADJ"
pos_tags['jpn'][u'名詞-接尾-副詞可能']['def'] = u"名詞 接尾 副詞可能"
pos_tags['jpn'][u'名詞-接尾-副詞可能']['eng_def'] = u"noun suffix adverbal"
pos_tags['jpn'][u'名詞-接尾-副詞可能']['upos'] = u"ADV"
pos_tags['jpn'][u'名詞-非自立']['def'] = u"名詞 非自立"
pos_tags['jpn'][u'名詞-非自立']['eng_def'] = u"noun affix"
pos_tags['jpn'][u'名詞-非自立']['upos'] = u"NOUN"
pos_tags['jpn'][u'名詞-非自立-一般']['def'] = u"名詞 非自立 一般"
pos_tags['jpn'][u'名詞-非自立-一般']['eng_def'] = u"noun affix normal"
pos_tags['jpn'][u'名詞-非自立-一般']['upos'] = u"NOUN"
pos_tags['jpn'][u'名詞-非自立-副詞可能']['def'] = u"名詞 非自立 副詞可能"
pos_tags['jpn'][u'名詞-非自立-副詞可能']['eng_def'] = u"noun affix adverbial"
pos_tags['jpn'][u'名詞-非自立-副詞可能']['upos'] = u"ADV"
pos_tags['jpn'][u'名詞-非自立-助動詞語幹']['def'] = u"名詞 非自立 助動詞語幹"
pos_tags['jpn'][u'名詞-非自立-助動詞語幹']['eng_def'] = u"noun affix aux"
pos_tags['jpn'][u'名詞-非自立-助動詞語幹']['upos'] = u"AUX"
pos_tags['jpn'][u'名詞-非自立-形容動詞語幹']['def'] = u"名詞 非自立 形容動詞語幹"
pos_tags['jpn'][u'名詞-非自立-形容動詞語幹']['eng_def'] = u"noun affix adjective"
pos_tags['jpn'][u'名詞-非自立-形容動詞語幹']['upos'] = u"ADJ"
pos_tags['jpn'][u'動詞']['def'] = u"動詞"
pos_tags['jpn'][u'動詞']['eng_def'] = u"verb"
pos_tags['jpn'][u'動詞']['upos'] = u"VERB"
pos_tags['jpn'][u'動詞-接尾']['def'] = u"動詞 接尾"
pos_tags['jpn'][u'動詞-接尾']['eng_def'] = u"verb suffix"
pos_tags['jpn'][u'動詞-接尾']['upos'] = u"AUX"
pos_tags['jpn'][u'動詞-自立']['def'] = u"動詞 自立"
pos_tags['jpn'][u'動詞-自立']['eng_def'] = u"verb main"
pos_tags['jpn'][u'動詞-自立']['upos'] = u"VERB"
pos_tags['jpn'][u'動詞-非自立']['def'] = u"動詞 非自立"
pos_tags['jpn'][u'動詞-非自立']['eng_def'] = u"verb aux"
pos_tags['jpn'][u'動詞-非自立']['upos'] = u"AUX"
pos_tags['jpn'][u'助動詞']['def'] = u"助動詞"
pos_tags['jpn'][u'助動詞']['eng_def'] = u"aux"
pos_tags['jpn'][u'助動詞']['upos'] = u"AUX"
pos_tags['jpn'][u'助詞']['def'] = u"助詞"
pos_tags['jpn'][u'助詞']['eng_def'] = u"particle"
pos_tags['jpn'][u'助詞']['upos'] = u"PRT"
pos_tags['jpn'][u'助詞-並立助詞']['def'] = u"助詞 並立助詞"
pos_tags['jpn'][u'助詞-並立助詞']['eng_def'] = u"particle coordinate"
pos_tags['jpn'][u'助詞-並立助詞']['upos'] = u"CONJ"
pos_tags['jpn'][u'助詞-係助詞']['def'] = u"助詞 係助詞"
pos_tags['jpn'][u'助詞-係助詞']['eng_def'] = u"particle dependency"
pos_tags['jpn'][u'助詞-係助詞']['upos'] = u"ADP"
pos_tags['jpn'][u'助詞-副助詞']['def'] = u"助詞 副助詞"
pos_tags['jpn'][u'助詞-副助詞']['eng_def'] = u"particle adverbial"
pos_tags['jpn'][u'助詞-副助詞']['upos'] = u"PRT"
pos_tags['jpn'][u'助詞-副助詞／並立助詞／終助詞']['def'] = u"助詞 副助詞／並立助詞／終助詞"
pos_tags['jpn'][u'助詞-副助詞／並立助詞／終助詞']['eng_def'] = u"particle adverbial/conjunctive/final"
pos_tags['jpn'][u'助詞-副助詞／並立助詞／終助詞']['upos'] = u"PRT"
pos_tags['jpn'][u'助詞-副詞化']['def'] = u"助詞 副詞化"
pos_tags['jpn'][u'助詞-副詞化']['eng_def'] = u"particle adverbializer"
pos_tags['jpn'][u'助詞-副詞化']['upos'] = u"ADP"
pos_tags['jpn'][u'助詞-接続助詞']['def'] = u"助詞 接続助詞"
pos_tags['jpn'][u'助詞-接続助詞']['eng_def'] = u"particle conjuctive"
pos_tags['jpn'][u'助詞-接続助詞']['upos'] = u"CONJ"
pos_tags['jpn'][u'助詞-格助詞']['def'] = u"助詞 格助詞"
pos_tags['jpn'][u'助詞-格助詞']['eng_def'] = u"particle case"
pos_tags['jpn'][u'助詞-格助詞']['upos'] = u"PRT"
pos_tags['jpn'][u'助詞-格助詞-一般']['def'] = u"助詞 格助詞 一般"
pos_tags['jpn'][u'助詞-格助詞-一般']['eng_def'] = u"particle case normal"
pos_tags['jpn'][u'助詞-格助詞-一般']['upos'] = u"PRT"
pos_tags['jpn'][u'助詞-格助詞-引用']['def'] = u"助詞 格助詞 引用"
pos_tags['jpn'][u'助詞-格助詞-引用']['eng_def'] = u"particle case quote"
pos_tags['jpn'][u'助詞-格助詞-引用']['upos'] = u"PRT"
pos_tags['jpn'][u'助詞-格助詞-連語']['def'] = u"助詞 格助詞 連語"
pos_tags['jpn'][u'助詞-格助詞-連語']['eng_def'] = u"particle case compound"
pos_tags['jpn'][u'助詞-格助詞-連語']['upos'] = u"PRT"
pos_tags['jpn'][u'助詞-特殊']['def'] = u"助詞 特殊"
pos_tags['jpn'][u'助詞-特殊']['eng_def'] = u"particle special"
pos_tags['jpn'][u'助詞-特殊']['upos'] = u"PRT"
pos_tags['jpn'][u'助詞-終助詞']['def'] = u"助詞 終助詞"
pos_tags['jpn'][u'助詞-終助詞']['eng_def'] = u"particle final"
pos_tags['jpn'][u'助詞-終助詞']['upos'] = u"PRT"
pos_tags['jpn'][u'助詞-連体化']['def'] = u"助詞 連体化"
pos_tags['jpn'][u'助詞-連体化']['eng_def'] = u"particle adnominalizer"
pos_tags['jpn'][u'助詞-連体化']['upos'] = u"ADP"
pos_tags['jpn'][u'助詞-間投助詞']['def'] = u"助詞 間投助詞"
pos_tags['jpn'][u'助詞-間投助詞']['eng_def'] = u"particle interjective"
pos_tags['jpn'][u'助詞-間投助詞']['upos'] = u"PRT"
pos_tags['jpn'][u'副詞']['def'] = u"副詞"
pos_tags['jpn'][u'副詞']['eng_def'] = u"adverb"
pos_tags['jpn'][u'副詞']['upos'] = u"ADV"
pos_tags['jpn'][u'副詞-一般']['def'] = u"副詞 一般"
pos_tags['jpn'][u'副詞-一般']['eng_def'] = u"adverb normal"
pos_tags['jpn'][u'副詞-一般']['upos'] = u"ADV"
pos_tags['jpn'][u'副詞-助詞類接続']['def'] = u"副詞 助詞類接続"
pos_tags['jpn'][u'副詞-助詞類接続']['eng_def'] = u"adverb particle attaching"
pos_tags['jpn'][u'副詞-助詞類接続']['upos'] = u"ADV"
pos_tags['jpn'][u'フィラー']['def'] = u"フィラー"
pos_tags['jpn'][u'フィラー']['eng_def'] = u"filler"
pos_tags['jpn'][u'フィラー']['upos'] = u"X"
pos_tags['jpn'][u'その他']['def'] = u"その他"
pos_tags['jpn'][u'その他']['eng_def'] = u"other"
pos_tags['jpn'][u'その他']['upos'] = u"X"
pos_tags['jpn'][u'その他-間投']['def'] = u"その他 間投"
pos_tags['jpn'][u'その他-間投']['eng_def'] = u"other interjection"
pos_tags['jpn'][u'その他-間投']['upos'] = u"X"
pos_tags['jpn'][u'未知語']['def'] = u"未知語"
pos_tags['jpn'][u'未知語']['eng_def'] = u"unknown word"
pos_tags['jpn'][u'未知語']['upos'] = u"X"

# INDONESIAN POS
pos_tags['ind'][u'cc']['def'] = u"coordinate conjunction"
pos_tags['ind'][u'cc']['eng_def'] = u"coordinate conjunction"
pos_tags['ind'][u'cc']['upos'] = u"CONJ"
pos_tags['ind'][u'vbi']['def'] = u"transitive verb"
pos_tags['ind'][u'vbi']['eng_def'] = u"transitive verb"
pos_tags['ind'][u'vbi']['upos'] = u"VERB"
pos_tags['ind'][u'vbt']['def'] = u"intransitive verb"
pos_tags['ind'][u'vbt']['eng_def'] = u"intransitive verb"
pos_tags['ind'][u'vbt']['upos'] = u"VERB"
pos_tags['ind'][u'rp']['def'] = u"particle"
pos_tags['ind'][u'rp']['eng_def'] = u"particle"
pos_tags['ind'][u'rp']['upos'] = u"PRT"
pos_tags['ind'][u'sc']['def'] = u"subordinate conjunction"
pos_tags['ind'][u'sc']['eng_def'] = u"subordinate conjunction"
pos_tags['ind'][u'sc']['upos'] = u"SCONJ"
pos_tags['ind'][u'rb']['def'] = u"adverb"
pos_tags['ind'][u'rb']['eng_def'] = u"adverb"
pos_tags['ind'][u'rb']['upos'] = u"ADV"
pos_tags['ind'][u'prp']['def'] = u"personal pronoun"
pos_tags['ind'][u'prp']['eng_def'] = u"personal pronoun"
pos_tags['ind'][u'prp']['upos'] = u"PRON"
pos_tags['ind'][u'prn']['def'] = u"number pronoun"
pos_tags['ind'][u'prn']['eng_def'] = u"number pronoun"
pos_tags['ind'][u'prn']['upos'] = u"NUM" #!!! needs David's revision
pos_tags['ind'][u'prl']['def'] = u"locative pronoun"
pos_tags['ind'][u'prl']['eng_def'] = u"locative pronoun"
pos_tags['ind'][u'prl']['upos'] = u"ADV" #!!! needs David's revision
pos_tags['ind'][u'wp']['def'] = u"wh-pronoun"
pos_tags['ind'][u'wp']['eng_def'] = u"wh-pronoun"
pos_tags['ind'][u'wp']['upos'] = u"PRON"
pos_tags['ind'][u'wp2']['def'] = u"wh-pronoun (reduplication)"
pos_tags['ind'][u'wp2']['eng_def'] = u"wh-pronoun (reduplication)"
pos_tags['ind'][u'wp2']['upos'] = u"PRON"
pos_tags['ind'][u'cdc']['def'] = u"collective cardinal number"
pos_tags['ind'][u'cdc']['eng_def'] = u"collective cardinal number"
pos_tags['ind'][u'cdc']['upos'] = u"NUM"
pos_tags['ind'][u'cdi']['def'] = u"irregular cardinal number"
pos_tags['ind'][u'cdi']['eng_def'] = u"irregular cardinal number"
pos_tags['ind'][u'cdi']['upos'] = u"NUM"
pos_tags['ind'][u'cdo']['def'] = u"ordinal cardinal number"
pos_tags['ind'][u'cdo']['eng_def'] = u"ordinal cardinal number"
pos_tags['ind'][u'cdo']['upos'] = u"NUM"
pos_tags['ind'][u'cdp']['def'] = u"primary cardinal number"
pos_tags['ind'][u'cdp']['eng_def'] = u"primary cardinal number"
pos_tags['ind'][u'cdp']['upos'] = u"NUM"
pos_tags['ind'][u'nn']['def'] = u"common noun"
pos_tags['ind'][u'nn']['eng_def'] = u"common noun"
pos_tags['ind'][u'nn']['upos'] = u"NOUN"
pos_tags['ind'][u'nn2']['def'] = u"common noun (reduplication)"
pos_tags['ind'][u'nn2']['eng_def'] = u"common noun (reduplication)"
pos_tags['ind'][u'nn2']['upos'] = u"NOUN"
pos_tags['ind'][u'nnc']['def'] = u"countable common noun"
pos_tags['ind'][u'nnc']['eng_def'] = u"countable common noun"
pos_tags['ind'][u'nnc']['upos'] = u"NOUN"
pos_tags['ind'][u'nnc2']['def'] = u"countable common noun (reduplication)"
pos_tags['ind'][u'nnc2']['eng_def'] = u"countable common noun (reduplication)"
pos_tags['ind'][u'nnc2']['upos'] = u"NOUN"
pos_tags['ind'][u'nng']['def'] = u"genitive common noun"
pos_tags['ind'][u'nng']['eng_def'] = u"genitive common noun"
pos_tags['ind'][u'nng']['upos'] = u"NOUN"
pos_tags['ind'][u'nnp']['def'] = u"proper noun"
pos_tags['ind'][u'nnp']['eng_def'] = u"proper noun"
pos_tags['ind'][u'nnp']['upos'] = u"PROPN"
pos_tags['ind'][u'nns2']['def'] = u"???"
pos_tags['ind'][u'nns2']['eng_def'] = u"???"
pos_tags['ind'][u'nns2']['upos'] = u"X" #!!! needs David's revision
pos_tags['ind'][u'nnu']['def'] = u"uncountable common noun"
pos_tags['ind'][u'nnu']['eng_def'] = u"uncountable common noun"
pos_tags['ind'][u'nnu']['upos'] = u"NOUN"
pos_tags['ind'][u'jj']['def'] = u"adjective"
pos_tags['ind'][u'jj']['eng_def'] = u"adjective"
pos_tags['ind'][u'jj']['upos'] = u"ADJ"
pos_tags['ind'][u'jj2']['def'] = u"adjective (reduplication)"
pos_tags['ind'][u'jj2']['eng_def'] = u"adjective (reduplication)"
pos_tags['ind'][u'jj2']['upos'] = u"ADJ"
pos_tags['ind'][u'fw']['def'] = u"foreign word"
pos_tags['ind'][u'fw']['eng_def'] = u"foreign word"
pos_tags['ind'][u'fw']['upos'] = u"X"
pos_tags['ind'][u'in']['def'] = u"preposition"
pos_tags['ind'][u'in']['eng_def'] = u"preposition"
pos_tags['ind'][u'in']['upos'] = u"ADP"
pos_tags['ind'][u'md']['def'] = u"modal or auxiliary verb"
pos_tags['ind'][u'md']['eng_def'] = u"modal or auxiliary verb"
pos_tags['ind'][u'md']['upos'] = u"AUX"
pos_tags['ind'][u'neg']['def'] = u"negation"
pos_tags['ind'][u'neg']['eng_def'] = u"negation"
pos_tags['ind'][u'neg']['upos'] = u"PRT"
pos_tags['ind'][u'wrb']['def'] = u"???"
pos_tags['ind'][u'wrb']['eng_def'] = u"???"
pos_tags['ind'][u'wrb']['upos'] = u"X" #!!! needs David's revision
pos_tags['ind'][u'dt']['def'] = u"???"
pos_tags['ind'][u'dt']['eng_def'] = u"???"
pos_tags['ind'][u'dt']['upos'] = u"X" #!!! needs David's revision
pos_tags['ind'][u'dt2']['def'] = u"???"
pos_tags['ind'][u'dt2']['eng_def'] = u"???"
pos_tags['ind'][u'dt2']['upos'] = u"X" #!!! needs David's revision
pos_tags['ind'][u'pu(']['def'] = u"opening parenthesis"
pos_tags['ind'][u'pu(']['eng_def'] = u"opening parenthesis"
pos_tags['ind'][u'pu(']['upos'] = u"PUNCT"
pos_tags['ind'][u'pu)']['def'] = u"closing parenthesis"
pos_tags['ind'][u'pu)']['eng_def'] = u"closing parenthesis"
pos_tags['ind'][u'pu)']['upos'] = u"PUNCT"
pos_tags['ind'][u'pu!']['def'] = u"exclamation point"
pos_tags['ind'][u'pu!']['eng_def'] = u"exclamation point"
pos_tags['ind'][u'pu!']['upos'] = u"PUNCT"
pos_tags['ind'][u'.']['def'] = u"???"
pos_tags['ind'][u'.']['eng_def'] = u"???"
pos_tags['ind'][u'.']['upos'] = u"X" #!!! needs David's revision
pos_tags['ind'][u'pu"']['def'] = u"quotation mark"
pos_tags['ind'][u'pu"']['eng_def'] = u"quotation mark"
pos_tags['ind'][u'pu"']['upos'] = u"PUNCT"
pos_tags['ind'][u'pu,']['def'] = u"comma"
pos_tags['ind'][u'pu,']['eng_def'] = u"comma"
pos_tags['ind'][u'pu,']['upos'] = u"PUNCT"
pos_tags['ind'][u'pu&']['def'] = u"&"
pos_tags['ind'][u'pu&']['eng_def'] = u"&"
pos_tags['ind'][u'pu&']['upos'] = u"PUNCT"
pos_tags['ind'][u'pu-']['def'] = u"dash"
pos_tags['ind'][u'pu-']['eng_def'] = u"dash"
pos_tags['ind'][u'pu-']['upos'] = u"PUNCT"
pos_tags['ind'][u'pu.']['def'] = u"."
pos_tags['ind'][u'pu.']['eng_def'] = u"."
pos_tags['ind'][u'pu.']['upos'] = u"PUNCT"
pos_tags['ind'][u'pu/']['def'] = u"/"
pos_tags['ind'][u'pu/']['eng_def'] = u"/"
pos_tags['ind'][u'pu/']['upos'] = u"PUNCT"
pos_tags['ind'][u'pu:']['def'] = u":"
pos_tags['ind'][u'pu:']['eng_def'] = u":"
pos_tags['ind'][u'pu:']['upos'] = u"PUNCT"
pos_tags['ind'][u'pu;']['def'] = u";"
pos_tags['ind'][u'pu;']['eng_def'] = u";"
pos_tags['ind'][u'pu;']['upos'] = u"PUNCT"
pos_tags['ind'][u'pu>']['def'] = u">"
pos_tags['ind'][u'pu>']['eng_def'] = u">"
pos_tags['ind'][u'pu>']['upos'] = u"PUNCT"
pos_tags['ind'][u'pu?']['def'] = u"?"
pos_tags['ind'][u'pu?']['eng_def'] = u"?"
pos_tags['ind'][u'pu?']['upos'] = u"PUNCT"
pos_tags['ind'][u'pu©']['def'] = u"©"
pos_tags['ind'][u'pu©']['eng_def'] = u"©"
pos_tags['ind'][u'pu©']['upos'] = u"PUNCT"
pos_tags['ind'][u'pu–']['def'] = u"m dash"
pos_tags['ind'][u'pu–']['eng_def'] = u"m dash"
pos_tags['ind'][u'pu–']['upos'] = u"PUNCT"
pos_tags['ind'][u'pu“']['def'] = u"opening quotes"
pos_tags['ind'][u'pu“']['eng_def'] = u"opening quotes"
pos_tags['ind'][u'pu“']['upos'] = u"PUNCT"
pos_tags['ind'][u'pu”']['def'] = u"closing quotes"
pos_tags['ind'][u'pu”']['eng_def'] = u"closing quotes"
pos_tags['ind'][u'pu”']['upos'] = u"PUNCT"
pos_tags['ind'][u'pu•']['def'] = u"•"
pos_tags['ind'][u'pu•']['eng_def'] = u"•"
pos_tags['ind'][u'pu•']['upos'] = u"PUNCT"


# UPOS TAGS
upos_tags = dd(lambda: dd(lambda: dd(unicode)))

upos_tags['ind']['ADV']['pos'] = [u'prl',u'rb']
upos_tags['ind']['ADV']['def'] = u'adverb'
upos_tags['ind']['ADV']['eng_def'] = u'adverb'
upos_tags['ind']['NOUN']['pos'] = [u'nnc',u'nnu',u'nn',u'nng',u'nnc2',u'nn2']
upos_tags['ind']['NOUN']['def'] = u'noun'
upos_tags['ind']['NOUN']['eng_def'] = u'noun'
upos_tags['ind']['ADP']['pos'] = [u'in']
upos_tags['ind']['ADP']['def'] = u'adposition'
upos_tags['ind']['ADP']['eng_def'] = u'adposition'
upos_tags['ind']['PRON']['pos'] = [u'wp2',u'prp',u'wp']
upos_tags['ind']['PRON']['def'] = u'pronoun'
upos_tags['ind']['PRON']['eng_def'] = u'pronoun'
upos_tags['ind']['SCONJ']['pos'] = [u'sc']
upos_tags['ind']['SCONJ']['def'] = u'subordinating conjunction'
upos_tags['ind']['SCONJ']['eng_def'] = u'subordinating conjunction'
upos_tags['ind']['PROPN']['pos'] = [u'nnp']
upos_tags['ind']['PROPN']['def'] = u'proper noun'
upos_tags['ind']['PROPN']['eng_def'] = u'proper noun'
upos_tags['ind']['PUNCT']['pos'] = [u'pu,',u'pu-',u'pu.',u'pu/',u'pu(',u'pu)',u'pu&',u'pu>',u'pu?',u'pu:',u'pu”',u'pu©',u'pu“',u'pu•',u'pu–',u'pu;',u'pu!',u'pu"']
upos_tags['ind']['PUNCT']['def'] = u'punctuation'
upos_tags['ind']['PUNCT']['eng_def'] = u'punctuation'
upos_tags['ind']['NUM']['pos'] = [u'cdc',u'cdo',u'cdi',u'cdp',u'prn']
upos_tags['ind']['NUM']['def'] = u'numeral'
upos_tags['ind']['NUM']['eng_def'] = u'numeral'
upos_tags['ind']['PRT']['pos'] = [u'rp',u'neg']
upos_tags['ind']['PRT']['def'] = u'particle'
upos_tags['ind']['PRT']['eng_def'] = u'particle'
upos_tags['ind']['AUX']['pos'] = [u'md']
upos_tags['ind']['AUX']['def'] = u'auxiliary verb'
upos_tags['ind']['AUX']['eng_def'] = u'auxiliary verb'
upos_tags['ind']['X']['pos'] = [u'nns2',u'.',u'dt2',u'fw',u'wrb',u'dt']
upos_tags['ind']['X']['def'] = u'other'
upos_tags['ind']['X']['eng_def'] = u'other'
upos_tags['ind']['CONJ']['pos'] = [u'cc']
upos_tags['ind']['CONJ']['def'] = u'coordinating conjunction'
upos_tags['ind']['CONJ']['eng_def'] = u'coordinating conjunction'
upos_tags['ind']['ADJ']['pos'] = [u'jj2',u'jj']
upos_tags['ind']['ADJ']['def'] = u'adjective'
upos_tags['ind']['ADJ']['eng_def'] = u'adjective'
upos_tags['ind']['VERB']['pos'] = [u'vbi',u'vbt']
upos_tags['ind']['VERB']['def'] = u'verb'
upos_tags['ind']['VERB']['eng_def'] = u'verb'




upos_tags['cmn']['ADV']['pos'] = [u'AD2',u'NT',u'AD']
upos_tags['cmn']['ADV']['def'] = u'adverb'
upos_tags['cmn']['ADV']['eng_def'] = u'adverb'
upos_tags['cmn']['NOUN']['pos'] = [u'M2',u'NN',u'M',u'NN2']
upos_tags['cmn']['NOUN']['def'] = u'noun'
upos_tags['cmn']['NOUN']['eng_def'] = u'noun'
upos_tags['cmn']['NUM']['pos'] = [u'CD',u'OD']
upos_tags['cmn']['NUM']['def'] = u'numeral'
upos_tags['cmn']['NUM']['eng_def'] = u'numeral'
upos_tags['cmn']['ADP']['pos'] = [u'LC',u'P']
upos_tags['cmn']['ADP']['def'] = u'adposition'
upos_tags['cmn']['ADP']['eng_def'] = u'adposition'
upos_tags['cmn']['PUNCT']['pos'] = [u'PU']
upos_tags['cmn']['PUNCT']['def'] = u'punctuation'
upos_tags['cmn']['PUNCT']['eng_def'] = u'punctuation'
upos_tags['cmn']['SCONJ']['pos'] = [u'CS']
upos_tags['cmn']['SCONJ']['def'] = u'subordinating conjunction'
upos_tags['cmn']['SCONJ']['eng_def'] = u'subordinating conjunction'
upos_tags['cmn']['PROPN']['pos'] = [u'PN2',u'NR']
upos_tags['cmn']['PROPN']['def'] = u'proper noun'
upos_tags['cmn']['PROPN']['eng_def'] = u'proper noun'
upos_tags['cmn']['DET']['pos'] = [u'DT']
upos_tags['cmn']['DET']['def'] = u'determiner'
upos_tags['cmn']['DET']['eng_def'] = u'determiner'
upos_tags['cmn']['SYM']['pos'] = [u'URL']
upos_tags['cmn']['SYM']['def'] = u'symbol'
upos_tags['cmn']['SYM']['eng_def'] = u'symbol'
upos_tags['cmn']['INTJ']['pos'] = [u'IJ']
upos_tags['cmn']['INTJ']['def'] = u'interjection'
upos_tags['cmn']['INTJ']['eng_def'] = u'interjection'
upos_tags['cmn']['PRT']['pos'] = [u'SP',u'BA',u'DER',u'DEV',u'MSP',u'DEC',u'DEG',u'AS',u'LB',u'SB']
upos_tags['cmn']['PRT']['def'] = u'particle'
upos_tags['cmn']['PRT']['eng_def'] = u'particle'
upos_tags['cmn']['VERB']['pos'] = [u'VC',u'VE',u'VV2',u'VV']
upos_tags['cmn']['VERB']['def'] = u'verb'
upos_tags['cmn']['VERB']['eng_def'] = u'verb'
upos_tags['cmn']['X']['pos'] = [u'FW',u'ON']
upos_tags['cmn']['X']['def'] = u'other'
upos_tags['cmn']['X']['eng_def'] = u'other'
upos_tags['cmn']['CONJ']['pos'] = [u'CC']
upos_tags['cmn']['CONJ']['def'] = u'coordinating conjunction'
upos_tags['cmn']['CONJ']['eng_def'] = u'coordinating conjunction'
upos_tags['cmn']['PRON']['pos'] = [u'PN']
upos_tags['cmn']['PRON']['def'] = u'pronoun'
upos_tags['cmn']['PRON']['eng_def'] = u'pronoun'
upos_tags['cmn']['ADJ']['pos'] = [u'JJ2',u'ETC',u'JJ',u'VA2',u'VA']
upos_tags['cmn']['ADJ']['def'] = u'adjective'
upos_tags['cmn']['ADJ']['eng_def'] = u'adjective'




upos_tags['eng']['ADV']['pos'] = [u'RB',u'WRB',u'PDT',u'RBS',u'RBR']
upos_tags['eng']['ADV']['def'] = u'adverb'
upos_tags['eng']['ADV']['eng_def'] = u'adverb'
upos_tags['eng']['NOUN']['pos'] = [u'NN',u'NNS',u'NNP',u'NNPS']
upos_tags['eng']['NOUN']['def'] = u'noun'
upos_tags['eng']['NOUN']['eng_def'] = u'noun'
upos_tags['eng']['NUM']['pos'] = [u'Zm',u'CD',u'Z',u'Zu',u'Zp']
upos_tags['eng']['NUM']['def'] = u'numeral'
upos_tags['eng']['NUM']['eng_def'] = u'numeral'
upos_tags['eng']['ADP']['pos'] = [u'IN']
upos_tags['eng']['ADP']['def'] = u'adposition'
upos_tags['eng']['ADP']['eng_def'] = u'adposition'
upos_tags['eng']['PUNCT']['pos'] = [u'Fpa',u'Fit',u'Fpt',u'Fp',u'Fs',u'Fx',u'Fz',u'Fat',u'Fc',u'Fd',u'Fe',u'Fg',u'Fh']
upos_tags['eng']['PUNCT']['def'] = u'punctuation'
upos_tags['eng']['PUNCT']['eng_def'] = u'punctuation'
upos_tags['eng']['DET']['pos'] = [u'WDT',u'DT']
upos_tags['eng']['DET']['def'] = u'determiner'
upos_tags['eng']['DET']['eng_def'] = u'determiner'
upos_tags['eng']['INTJ']['pos'] = [u'UH']
upos_tags['eng']['INTJ']['def'] = u'interjection'
upos_tags['eng']['INTJ']['eng_def'] = u'interjection'
upos_tags['eng']['PRON']['pos'] = [u'PRP$',u'WP',u'PRP',u'EX',u'WP$']
upos_tags['eng']['PRON']['def'] = u'pronoun'
upos_tags['eng']['PRON']['eng_def'] = u'pronoun'
upos_tags['eng']['VERB']['pos'] = [u'VBN',u'VBP',u'VBZ',u'VBG',u'VBD',u'VB']
upos_tags['eng']['VERB']['def'] = u'verb'
upos_tags['eng']['VERB']['eng_def'] = u'verb'
upos_tags['eng']['PRT']['pos'] = [u'RP',u'POS',u'TO']
upos_tags['eng']['PRT']['def'] = u'particle'
upos_tags['eng']['PRT']['eng_def'] = u'particle'
upos_tags['eng']['AUX']['pos'] = [u'VAX',u'MD']
upos_tags['eng']['AUX']['def'] = u'auxiliary verb'
upos_tags['eng']['AUX']['eng_def'] = u'auxiliary verb'
upos_tags['eng']['X']['pos'] = [u'FW']
upos_tags['eng']['X']['def'] = u'other'
upos_tags['eng']['X']['eng_def'] = u'other'
upos_tags['eng']['CONJ']['pos'] = [u'CC']
upos_tags['eng']['CONJ']['def'] = u'coordinating conjunction'
upos_tags['eng']['CONJ']['eng_def'] = u'coordinating conjunction'
upos_tags['eng']['ADJ']['pos'] = [u'JJ',u'JJS',u'JJR']
upos_tags['eng']['ADJ']['def'] = u'adjective'
upos_tags['eng']['ADJ']['eng_def'] = u'adjective'




upos_tags['jpn']['ADV']['pos'] = [u'副詞',u'副詞-助詞類接続',u'名詞-接尾-副詞可能',u'名詞-非自立-副詞可能',u'副詞-一般']
upos_tags['jpn']['ADV']['def'] = u'副词'
upos_tags['jpn']['ADV']['eng_def'] = u'adverb'
upos_tags['jpn']['NOUN']['pos'] = [u'名詞-特殊-助動詞語幹',u'名詞-サ変接続',u'名詞-接尾-人名',u'名詞-非自立-一般',u'名詞-一般',u'名詞-副詞可能',u'名詞-接尾',u'名詞-接尾-特殊',u'名詞-接尾-一般',u'名詞-接尾-地域',u'接頭詞-名詞接続',u'名詞-非自立',u'名詞-ナイ形容詞語幹',u'接頭詞',u'名詞-接尾-サ変接続',u'名詞-接尾-助数詞',u'名詞',u'名詞-特殊',u'名詞-接尾-助動詞語幹']
upos_tags['jpn']['NOUN']['def'] = u'名词'
upos_tags['jpn']['NOUN']['eng_def'] = u'noun'
upos_tags['jpn']['ADP']['pos'] = [u'助詞-連体化',u'助詞-係助詞',u'助詞-副詞化']
upos_tags['jpn']['ADP']['def'] = u'方位词'
upos_tags['jpn']['ADP']['eng_def'] = u'adposition'
upos_tags['jpn']['PRT']['pos'] = [u'助詞-副助詞',u'助詞-特殊',u'助詞-格助詞-引用',u'助詞-格助詞-一般',u'助詞-終助詞',u'助詞-間投助詞',u'助詞-格助詞',u'助詞-副助詞／並立助詞／終助詞',u'助詞-格助詞-連語',u'助詞']
upos_tags['jpn']['PRT']['def'] = u'助词'
upos_tags['jpn']['PRT']['eng_def'] = u'particle'
upos_tags['jpn']['PROPN']['pos'] = [u'名詞-固有名詞-一般',u'名詞-固有名詞-人名-姓',u'名詞-固有名詞-人名-一般',u'名詞-固有名詞-地域-一般',u'名詞-固有名詞-組織',u'名詞-固有名詞-地域-国',u'名詞-固有名詞-人名',u'名詞-固有名詞-地域',u'名詞-引用文字列',u'名詞-固有名詞',u'名詞-固有名詞-人名-名']
upos_tags['jpn']['PROPN']['def'] = u'固有名詞'
upos_tags['jpn']['PROPN']['eng_def'] = u'proper noun'
upos_tags['jpn']['DET']['pos'] = [u'連体詞']
upos_tags['jpn']['DET']['def'] = u'代词'
upos_tags['jpn']['DET']['eng_def'] = u'determiner'
upos_tags['jpn']['PRON']['pos'] = [u'名詞-代名詞-縮約',u'名詞-代名詞',u'名詞-代名詞-一般']
upos_tags['jpn']['PRON']['def'] = u'代名词'
upos_tags['jpn']['PRON']['eng_def'] = u'pronoun'
upos_tags['jpn']['NUM']['pos'] = [u'名詞-数',u'接頭詞-数接続']
upos_tags['jpn']['NUM']['def'] = u'数词'
upos_tags['jpn']['NUM']['eng_def'] = u'numeral'
upos_tags['jpn']['PUNCT']['pos'] = [u'記号-括弧閉',u'記号-空白',u'記号-括弧開',u'記号-句点',u'記号-読点',u'記号-一般']
upos_tags['jpn']['PUNCT']['def'] = u'标点符号'
upos_tags['jpn']['PUNCT']['eng_def'] = u'punctuation'
upos_tags['jpn']['AUX']['pos'] = [u'動詞-接尾',u'動詞-非自立',u'助動詞',u'名詞-非自立-助動詞語幹']
upos_tags['jpn']['AUX']['def'] = u'助動詞'
upos_tags['jpn']['AUX']['eng_def'] = u'auxiliary verb'
upos_tags['jpn']['X']['pos'] = [u'その他-間投',u'フィラー',u'感動詞',u'未知語',u'その他',u'非言語音',u'記号',u'記号-アルファベット',u'語断片']
upos_tags['jpn']['X']['def'] = u'其他'
upos_tags['jpn']['X']['eng_def'] = u'other'
upos_tags['jpn']['CONJ']['pos'] = [u'名詞-接続詞的',u'助詞-接続助詞',u'接続詞',u'助詞-並立助詞']
upos_tags['jpn']['CONJ']['def'] = u'连词'
upos_tags['jpn']['CONJ']['eng_def'] = u'coordinating conjunction'
upos_tags['jpn']['ADJ']['pos'] = [u'形容詞',u'名詞-接尾-形容動詞語幹',u'名詞-非自立-形容動詞語幹',u'形容詞-接尾',u'接頭詞-形容詞接続',u'形容詞-自立',u'名詞-形容動詞語幹',u'形容詞-非自立']
upos_tags['jpn']['ADJ']['def'] = u'形容词'
upos_tags['jpn']['ADJ']['eng_def'] = u'adjective'
upos_tags['jpn']['VERB']['pos'] = [u'動詞-自立',u'名詞-動詞非自立的',u'動詞',u'接頭詞-動詞接続']
upos_tags['jpn']['VERB']['def'] = u'动词'
upos_tags['jpn']['VERB']['eng_def'] = u'verb'


################ OLD WORKING DIFFERENT STRUCTURE OF DICT
# pos_tags['eng']['CC'] = "coordinating conjunction"
# pos_tags['eng']['CD'] = "cardinal number"
# pos_tags['eng']['DT'] = "determiner"
# pos_tags['eng']['EX'] = "existential there"
# pos_tags['eng']['FW'] = "foreign word"
# pos_tags['eng']['Fat'] = "???"
# pos_tags['eng']['Fc'] = "[,]comma"
# pos_tags['eng']['Fd'] = "???"
# pos_tags['eng']['Fe'] = "???"
# pos_tags['eng']['Fg'] = "???"
# pos_tags['eng']['Fh'] = "???"
# pos_tags['eng']['Fit'] = "???"
# pos_tags['eng']['Fp'] = "[.]period"
# pos_tags['eng']['Fpa'] = "???"
# pos_tags['eng']['Fpt'] = "???"
# pos_tags['eng']['Fs'] = "???"
# pos_tags['eng']['Fx'] = "???"
# pos_tags['eng']['Fz'] = "???"
# pos_tags['eng']['IN'] = "preposition or subordinating conjunction"
# pos_tags['eng']['JJ'] = "adjective"
# pos_tags['eng']['JJR'] = "adjective, comparative"
# pos_tags['eng']['JJS'] = "adjective, superlative"
# pos_tags['eng']['MD'] = "modal"
# pos_tags['eng']['NN'] = "noun, singular or mass"
# pos_tags['eng']['NNP'] = "proper noun, singular"
# pos_tags['eng']['NNS'] = "noun, plural"
# pos_tags['eng']['NNPS'] = "proper noun, plural"
# pos_tags['eng']['PDT'] = "predeterminer"
# pos_tags['eng']['POS'] = "possessive ending"
# pos_tags['eng']['PRP'] = "personal pronoun"
# pos_tags['eng']['PRP$'] = "possessive pronoun"
# pos_tags['eng']['RB'] = "adverb"
# pos_tags['eng']['RBR'] = "adverb, comparative"
# pos_tags['eng']['RBS'] = "adverb, superlative"
# pos_tags['eng']['RP'] = "particle"
# pos_tags['eng']['TO'] = "to"
# pos_tags['eng']['UH'] = "Interjection"
# pos_tags['eng']['VAX'] = "???"
# pos_tags['eng']['VB'] = "verb, base form"
# pos_tags['eng']['VBD'] = "verb, past tense"
# pos_tags['eng']['VBG'] = "verb, gerund or present participle"
# pos_tags['eng']['VBN'] = "verb, past participle"
# pos_tags['eng']['VBP'] = "verb, non-3rd person singular present"
# pos_tags['eng']['VBZ'] = "verb, 3rd person singular present"
# pos_tags['eng']['WDT'] = "wh-determiner"
# pos_tags['eng']['WP'] = "wh-pronoun"
# pos_tags['eng']['WP$'] = "possessive wh-pronoun"
# pos_tags['eng']['WRB'] = "wh-adverb"
# pos_tags['eng']['Z'] = "???"
# pos_tags['eng']['Zm'] = "???"
# pos_tags['eng']['Zp'] = "???"
# pos_tags['eng']['Zu'] = "???"

# pos_tags['cmn']['AD'] = "adverb"
# pos_tags['cmn']['AD2'] = "adverb (reduplication)"
# pos_tags['cmn']['AS'] = "aspect particle"
# pos_tags['cmn']['BA'] = "ba3 in ba-construction"
# pos_tags['cmn']['CC'] = "coordinating conjunction"
# pos_tags['cmn']['CD'] = "cardinal number"
# pos_tags['cmn']['CS'] = "subordinating conjunction"
# pos_tags['cmn']['DEC'] = "de5 as a complementizer or a nominalizer"
# pos_tags['cmn']['DEG'] = "de5 as a genitive marker and an associative marker"
# pos_tags['cmn']['DER'] = "resultative de5"
# pos_tags['cmn']['DEV'] = "manner de5"
# pos_tags['cmn']['DT'] = "determiner"
# pos_tags['cmn']['ETC'] = "ETC (deng3 and deng3deng3)"
# pos_tags['cmn']['FW'] = "foreign word"
# pos_tags['cmn']['IJ'] = "interjection"
# pos_tags['cmn']['JJ'] = "other noun modifier"
# pos_tags['cmn']['JJ2'] = "other noun modifier (reduplication)"
# pos_tags['cmn']['LB'] = "bei4 in long bei-construction"
# pos_tags['cmn']['LC'] = "localizer"
# pos_tags['cmn']['M'] = "measure word"
# pos_tags['cmn']['M2'] = "measure word (reduplication)"
# pos_tags['cmn']['MSP'] = "other particle"
# pos_tags['cmn']['NN'] = "other noun"
# pos_tags['cmn']['NN2'] = "other noun (reduplication)"
# pos_tags['cmn']['NR'] = "proper noun"
# pos_tags['cmn']['NT'] = "temporal noun"
# pos_tags['cmn']['OD'] = "ordinal number"
# pos_tags['cmn']['ON'] = "onomatopeia"
# pos_tags['cmn']['P'] = "preposition"
# pos_tags['cmn']['PN'] = "pronoun"
# pos_tags['cmn']['PN2'] = "pronoun (reduplication)"
# pos_tags['cmn']['PU'] = "punctuation"
# pos_tags['cmn']['SB'] = "bei4 in short bei-construction"
# pos_tags['cmn']['SP'] = "sentence-final particle"
# pos_tags['cmn']['URL'] = "url"
# pos_tags['cmn']['VA'] = "predicative adjective"
# pos_tags['cmn']['VA2'] = "predicative adjective (reduplication)"
# pos_tags['cmn']['VC'] = "copula"
# pos_tags['cmn']['VE'] = "you3 as the main verb"
# pos_tags['cmn']['VV'] = "other verb"
# pos_tags['cmn']['VV2'] = "other verb (reduplication)"

# pos_tags['jpn'][u'連体詞'] = u"???"
# pos_tags['jpn'][u'接頭詞'] = u"???"
# pos_tags['jpn'][u'接頭詞-形容詞接続'] = u"「お高い」「クソ高い」「まっ赤」"
# pos_tags['jpn'][u'接頭詞-数接続'] = u"あとに数値がくるもの。"
# pos_tags['jpn'][u'接頭詞-動詞接続'] = u"あとに動詞がくるもの。「ぶったたく」"
# pos_tags['jpn'][u'接頭詞-名詞接続'] = u"あとに名詞がくるもの。"
# pos_tags['jpn'][u'名詞'] = u"???"
# pos_tags['jpn'][u'名詞-引用文字列'] = u"???"
# pos_tags['jpn'][u'名詞-サ変接続'] = u"「～する」の形をとれるもの。"
# pos_tags['jpn'][u'名詞-ナイ形容詞語幹'] = u"「～ない」の形をとれるもの。"
# pos_tags['jpn'][u'名詞-形容動詞語幹'] = u"「～な」の形をとれるもの。"
# pos_tags['jpn'][u'名詞-動詞非自立的'] = u"「～してごらん」「～してちょうだい」"
# pos_tags['jpn'][u'名詞-副詞可能'] = u"おもに時相名詞。"
# pos_tags['jpn'][u'名詞-一般'] = u"一般名詞。"
# pos_tags['jpn'][u'名詞-数'] = u"数値。"
# pos_tags['jpn'][u'名詞-接続詞的'] = u"???"
# pos_tags['jpn'][u'名詞-固有名詞'] = u"???"
# pos_tags['jpn'][u'名詞-固有名詞-一般'] = u"下のカテゴリにあてはまらないもの。山・川・商品名など。"
# pos_tags['jpn'][u'名詞-固有名詞-人名'] = u"???"
# pos_tags['jpn'][u'名詞-固有名詞-人名-一般'] = u"芸能人名など。"
# pos_tags['jpn'][u'名詞-固有名詞-人名-姓'] = u"???"
# pos_tags['jpn'][u'名詞-固有名詞-人名-名'] = u"???"
# pos_tags['jpn'][u'名詞-固有名詞-組織'] = u"???"
# pos_tags['jpn'][u'名詞-固有名詞-地域'] = u"???"
# pos_tags['jpn'][u'名詞-固有名詞-地域-一般'] = u"???"
# pos_tags['jpn'][u'名詞-固有名詞-地域-国'] = u"???"
# pos_tags['jpn'][u'名詞-接尾'] = u"???"
# pos_tags['jpn'][u'名詞-接尾-サ変接続'] = u"「巨大化」「キャンプ入り」"
# pos_tags['jpn'][u'名詞-接尾-一般'] = u"???"
# pos_tags['jpn'][u'名詞-接尾-形容動詞語幹'] = u"???"
# pos_tags['jpn'][u'名詞-接尾-助数詞'] = u"単位。"
# pos_tags['jpn'][u'名詞-接尾-助動詞語幹'] = u"「～してそう」「～そうだ」で使われる。"
# pos_tags['jpn'][u'名詞-接尾-人名'] = u"???"
# pos_tags['jpn'][u'名詞-接尾-地域'] = u"???"
# pos_tags['jpn'][u'名詞-接尾-特殊'] = u"???"
# pos_tags['jpn'][u'名詞-接尾-副詞可能'] = u"???"
# pos_tags['jpn'][u'名詞-代名詞'] = u"???"
# pos_tags['jpn'][u'名詞-代名詞-一般'] = u"???"
# pos_tags['jpn'][u'名詞-代名詞-縮約'] = u"???"
# pos_tags['jpn'][u'名詞-非自立'] = u"???"
# pos_tags['jpn'][u'名詞-非自立-一般'] = u"???"
# pos_tags['jpn'][u'名詞-非自立-形容動詞語幹'] = u"???"
# pos_tags['jpn'][u'名詞-非自立-助動詞語幹'] = u"???"
# pos_tags['jpn'][u'名詞-非自立-副詞可能'] = u"???"
# pos_tags['jpn'][u'名詞-特殊'] = u"???"
# pos_tags['jpn'][u'名詞-特殊-助動詞語幹'] = u"???"
# pos_tags['jpn'][u'動詞'] = u"???"
# pos_tags['jpn'][u'動詞-自立'] = u"???"
# pos_tags['jpn'][u'動詞-接尾'] = u"???"
# pos_tags['jpn'][u'動詞-非自立'] = u"「行ってしまう」「やっちゃったね」「ご遠慮願う」"
# pos_tags['jpn'][u'形容詞'] = u"???"
# pos_tags['jpn'][u'形容詞-自立'] = u"???"
# pos_tags['jpn'][u'形容詞-接尾'] = u"???"
# pos_tags['jpn'][u'形容詞-非自立'] = u"「聞きづらい」「見よい」"
# pos_tags['jpn'][u'副詞'] = u"???"
# pos_tags['jpn'][u'副詞-一般'] = u"???"
# pos_tags['jpn'][u'副詞-助詞類接続'] = u"同一文節内に付属語がこれるもの。"
# pos_tags['jpn'][u'接続詞'] = u"???"
# pos_tags['jpn'][u'助詞'] = u"???"
# pos_tags['jpn'][u'助詞-格助詞'] = u"???"
# pos_tags['jpn'][u'助詞-格助詞-一般'] = u"???"
# pos_tags['jpn'][u'助詞-格助詞-引用'] = u"???"
# pos_tags['jpn'][u'助詞-格助詞-連語'] = u"解析ミスを防ぐためのマクロ。"
# pos_tags['jpn'][u'助詞-係助詞'] = u"???"
# pos_tags['jpn'][u'助詞-終助詞'] = u"???"
# pos_tags['jpn'][u'助詞-接続助詞'] = u"???"
# pos_tags['jpn'][u'助詞-特殊'] = u"「せにゃならん」 これ以外の用途は不明。"
# pos_tags['jpn'][u'助詞-副詞化'] = u"???"
# pos_tags['jpn'][u'助詞-副助詞'] = u"???"
# pos_tags['jpn'][u'助詞-副助詞／並立助詞／終助詞'] = u"???"
# pos_tags['jpn'][u'助詞-並立助詞'] = u"???"
# pos_tags['jpn'][u'助詞-連体化'] = u"???"
# pos_tags['jpn'][u'助動詞'] = u"「そうでございます」"
# pos_tags['jpn'][u'感動詞'] = u"???"
# pos_tags['jpn'][u'記号'] = u"???"
# pos_tags['jpn'][u'記号-句点'] = u"???"
# pos_tags['jpn'][u'記号-読点'] = u"???"
# pos_tags['jpn'][u'記号-空白'] = u"???"
# pos_tags['jpn'][u'記号-アルファベット'] = u"???"
# pos_tags['jpn'][u'記号-一般'] = u"???"
# pos_tags['jpn'][u'記号-括弧開'] = u"???"
# pos_tags['jpn'][u'記号-括弧閉'] = u"???"
# pos_tags['jpn'][u'フィラー'] = u"(たぶん)音声認識用。"
# pos_tags['jpn'][u'その他'] = u"???"
# pos_tags['jpn'][u'その他-間投'] = u"「そんなぁ」"
# pos_tags['jpn'][u'未知語'] = u"???"


# pos_tags['ind'][u'cc'] = u"coordinate conjunction"
# pos_tags['ind'][u'vbi'] = u"transitive verb"
# pos_tags['ind'][u'vbt'] = u"intransitive verb"
# pos_tags['ind'][u'rp'] = u"particle"
# pos_tags['ind'][u'sc'] = u"subordinate conjunction"
# pos_tags['ind'][u'rb'] = u"adverb"
# pos_tags['ind'][u'prp'] = u"personal pronoun"
# pos_tags['ind'][u'prn'] = u"number pronoun"
# pos_tags['ind'][u'prl'] = u"locative pronoun"
# pos_tags['ind'][u'wp'] = u"wh-pronoun"
# pos_tags['ind'][u'wp2'] = u"wh-pronoun (reduplication)"
# pos_tags['ind'][u'cdc'] = u"collective cardinal number"
# pos_tags['ind'][u'cdi'] = u"irregular cardinal number"
# pos_tags['ind'][u'cdo'] = u"ordinal cardinal number"
# pos_tags['ind'][u'cdp'] = u"primary cardinal number"
# pos_tags['ind'][u'nn'] = u"common noun"
# pos_tags['ind'][u'nn2'] = u"common noun (reduplication)"
# pos_tags['ind'][u'nnc'] = u"countable common noun"
# pos_tags['ind'][u'nnc2'] = u"countable common noun (reduplication)"
# pos_tags['ind'][u'nng'] = u"genitive common noun"
# pos_tags['ind'][u'nnp'] = u"proper noun"
# pos_tags['ind'][u'nns2'] = u"???"
# pos_tags['ind'][u'nnu'] = u"uncountable common noun"
# pos_tags['ind'][u'jj'] = u"adjective"
# pos_tags['ind'][u'jj2'] = u"adjective (reduplication)"
# pos_tags['ind'][u'fw'] = u"foreign word"
# pos_tags['ind'][u'in'] = u"preposition"
# pos_tags['ind'][u'md'] = u"modal or auxiliary verb"
# pos_tags['ind'][u'neg'] = u"negation"
# pos_tags['ind'][u'wrb'] = u"???"
# pos_tags['ind'][u'dt'] = u"???"
# pos_tags['ind'][u'dt2'] = u"???"
# pos_tags['ind'][u'pu('] = u"opening parenthesis"
# pos_tags['ind'][u'pu)'] = u"closing parenthesis"
# pos_tags['ind'][u'pu!'] = u"exclamation point"
# pos_tags['ind'][u'.'] = u"???"
# pos_tags['ind'][u'pu"'] = u"quotation mark"
# pos_tags['ind'][u'pu,'] = u"comma"
# pos_tags['ind'][u'pu&'] = u"&"
# pos_tags['ind'][u'pu-'] = u"dash"
# pos_tags['ind'][u'pu.'] = u"."
# pos_tags['ind'][u'pu/'] = u"/"
# pos_tags['ind'][u'pu:'] = u":"
# pos_tags['ind'][u'pu;'] = u";"
# pos_tags['ind'][u'pu>'] = u">"
# pos_tags['ind'][u'pu?'] = u"?"
# pos_tags['ind'][u'pu©'] = u"©"
# pos_tags['ind'][u'pu–'] = u"m dash"
# pos_tags['ind'][u'pu“'] = u"opening quotes"
# pos_tags['ind'][u'pu”'] = u"closing quotes"
# pos_tags['ind'][u'pu•'] = u"•"





t = dd(lambda: dd(unicode))
# thing, lang, = label
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

t["swe"]["eng"] = "Swedish"
t["ell"]["eng"] = "Greek"
t["cmn"]["eng"] = "Chinese (simplified)"
t["qcn"]["eng"] = "Chinese (traditional)"
t['eng']['cmn'] = u'英语'
t['cmn']['cmn'] = u'汉语'
t['qcn']['cmn'] = u'漢語'
t['cmn']['qcn'] = u'汉语'
t['qcn']['qcn'] = u'漢語'
t['jpn']['cmn'] = u'日语'
t['jpn']['qcn'] = u'日语'

t['eng']['jpn'] = u'英語'
t['jpn']['jpn'] = u'日本語'


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
t['nob']['eng'] = u'Bokmål'
t['pol']['eng'] = 'Polish'
t['por']['eng'] = 'Portuguese'
t['slv']['eng'] = 'Slovene'
t['spa']['eng'] = 'Spanish'
t['tha']['eng'] = 'Thai'
t['bul']['eng'] = 'Bulgarian'


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
t['sim']['eng'] = u'Similar to:'
t['attr']['eng'] = u'Attributes:'
t['eqls']['eng'] = u'Equals'
t['ants']['eng'] = u'Antonym:'
t['qant']['eng'] = u'Quantifies'
t['hasq']['eng'] = u'Quantifier:'


def fun_x():
    pass


class omwlang:

    @staticmethod
    def trans(word, lang):
        if (t[word][lang]):
            return t[word][lang]
        elif (t[word]['eng']):
            return t[word]['eng']
        else:
            return word

    @staticmethod
    def ntumclist():
        langsntumc = ("eng", "ind", "zsm",  "jpn", "cmn", "qcn")
        return langsntumc

    @staticmethod
    def humanprojectslist():
        langsprojects = (
            # From Projects	(used by NTUMC)
            "eng", "ind", "zsm",  "jpn", "cmn", "qcn",

            # From Projects
            "fas", "arb", "heb", "tha", "slv",
            "ita", "por", "nob", "nno", "dan",
            "swe", "fra", "fin", "ell", "glg",
            "cat", "spa", "eus", "als", "pol",
            "bul")
        return langsprojects

    @staticmethod
    def alllangslist():

        langs = (
            # From Projects	(used by NTUMC)
            "eng", "ind", "zsm",  "jpn", "cmn", "qcn",
            
            # From Projects
            "fas", "arb", "heb", "tha", "slv",
            "ita", "por", "nob", "nno", "dan",
            "swe", "fra", "fin", "ell", "glg",
            "cat", "spa", "eus", "als", "pol",
            "bul",
            
            # From WIKT & CLDR
            'aar', 'afr', 'aka', 'als', 'amh',
            'ang', 'arz', 'asm', 'ast', 'aze',
            'bam', 'bel', 'ben', 'bod', 'bos',
            'bre', 'bul', 'ces', 'chr', 'cor',
            'cym', 'deu', 'dzo', 'epo', 'est',
            'ewe', 'fao', 'fry', 'ful', 'fur',
            'gla', 'gle', 'glv', 'grc', 'guj',
            'hat', 'hau', 'hbs', 'hin', 'hrv',
            'hun', 'hye', 'ibo', 'ido', 'iii',
            'ina', 'isl', 'jer', 'kal', 'kan',
            'kat', 'kaz', 'khm', 'kik', 'kin',
            'kir', 'kor', 'kur', 'lao', 'lat',
            'lav', 'lin', 'lit', 'ltg', 'ltz',
            'lub', 'lug', 'mal', 'mar', 'mkd',
            'mlg', 'mlt', 'mon', 'mri', 'mya',
            'nan', 'nav', 'nbl', 'nde', 'nep',
            'nld', 'oci', 'ori', 'orm', 'pan',
            'pol', 'pus', 'roh', 'ron', 'run',
            'rup', 'rus', 'sag', 'san', 'scn',
            'sin', 'slk', 'slv', 'sme', 'sna',
            'som', 'sot', 'srd', 'srp', 'ssw',
            'swa', 'tam', 'tat', 'tel', 'tgk',
            'tgl', 'tir', 'ton', 'tsn', 'tso',
            'tuk', 'tur', 'ukr', 'urd', 'uzb',
            'ven', 'vie', 'vol', 'xho', 'yid',
            'yor', 'yue', 'zul'
            )

        return langs
