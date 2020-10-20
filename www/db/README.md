This should have the databases:


File		Description
---------------------------------------------
cmn.db		Chinese Corpus
eng.db		English Corpus
ind.db		Indonesian Corpus	
jpn.db		Japanese Corpus
zsm.db		Malay Corpus
cmn-jpn.db	Chinese-Japanese Alignments
cmn-zsm.db
eng-cmn.db
eng-ind.db
eng-ita.db
ind-cmn.db
ind-zsm.db
jpn-ind.db
jpn-zsm.db
wn-ntumc.db	NTU Multilingual Wordnet


It also has files for mfs tagging and merging annotations
see Notes in Semantics-and-Pragmatics
---------------------------------------------------------
tag-mfs.py		tag with MFS
merge.tsv		sentiment scores for MFS tagging
assign-majtag.py	merge annotation from eng[A-E].db into eng.db
