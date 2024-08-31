from collections import defaultdict as dd
import sqlite3
import toml
from datetime import date    
today = date.today().isoformat

###
###  Create 10 folds, balanced by number of words 
###  Folds should start on a header or the beginning of a paragraph.
###  Create a train/dev/test split (60/20/20)
###  output as toml
###
###
###  By fcbond with help from GPT-4
###


corpusdb='/home/bond/git/IMI/scripts/eng-new.db'

conn = sqlite3.connect(corpusdb)
c = conn.cursor()

#docid, doc = 441, 'danc'
docid, doc = 440, 'spec'

# c.execute("""select min(sid), max(sid) from sent 
# where docid=? """, (docid,))


# print (sid_min, sid_max)

sent = dict()

c.execute("""SELECT sid, comment
FROM sent 
WHERE docid = ?
ORDER BY sent.sid""",
          (docid,))



for (sid, comment) in c:
    stype = None
    if comment and '<h>' in comment:
        stype = 'h1'
    elif comment and '<p>' in comment:
        stype = 'p'
    sent[sid] = stype


c.execute("""SELECT sid,  max(wid) 
FROM word 
WHERE sid >= ? AND sid <= ?
GROUP BY sid 
ORDER BY sid""",
          (min(sent), max(sent)))

for (sid, words) in c:
    sent[sid]  =  (sent[sid], words + 1)



  
def find_optimal_partitions(sent, k = 10):
    # Get sentence ids, lengths, and types in the order they appear in the dictionary
    # order into k partitions
    #
    sids = list(sent.keys())
    print ('Total Sentences:', len(sids))
    
    lengths = [sent[sid][1] for sid in sids]

    print ('Total Words:', sum(lengths))
    
    types = [sent[sid][0] for sid in sids]

    
    n = len(lengths)

    # DP table: dp[i][j] will store the minimum of the maximum partition size
    dp = [[float('inf')] * (k + 1) for _ in range(n + 1)]
    dp[0][0] = 0

    # Cumulative sum array to make range sum calculation efficient
    cumulative_sum = [0] * (n + 1)
    for i in range(1, n + 1):
        cumulative_sum[i] = cumulative_sum[i - 1] + lengths[i - 1]

    # Fill the DP table
    for i in range(1, n + 1):  # i is the end index of the current sentence sequence
        for j in range(1, k + 1):  # j is the number of partitions
            for m in range(i):  # m is the start index of the last partition
                if types[m] in ('p', 'h1'):  # Ensure partition starts with 'p' or 'h'
                    # Calculate the sum of the last partition
                    last_partition_sum = cumulative_sum[i] - cumulative_sum[m]
                    # Update the DP value to the minimum of the max partition sum found
                    dp[i][j] = min(dp[i][j], max(dp[m][j - 1], last_partition_sum))

    # Backtrack to find the partitions
    partitions = []
    last_index = n
    for j in range(k, 0, -1):
        for i in range(last_index):
            if types[i] in ('p', 'h') and dp[last_index][j] == max(dp[i][j - 1], cumulative_sum[last_index] - cumulative_sum[i]):
                partitions.append(sids[i:last_index])
                last_index = i
                break
    # If the first partition was not formed, ensure we add it
    if last_index > 0:
        partitions.append(sids[:last_index])
        
    # Reverse the partitions since we backtracked
    partitions.reverse()

    # Convert list of lists to dictionary format for each partition
    partitions_dict = [{sid: sent[sid] for sid in partition}
                       for partition in partitions]

    return partitions_dict


# sent = {
#     101: ('p', 100),
#     102: ('h', 200),
#     103: ('p', 50),
#     104: ('h', 150),
#     105: ('p', 120),
#     106: ('h', 300),
#     107: (None, 80),
#     108: ('p', 90),
#     109: ('h', 100),
#     110: (None, 110),
#     111: ('p', 130)
# }


partitions = find_optimal_partitions(sent)
#print (partitions)
for i, partition in enumerate(partitions):
    print(i+1, min(partition.keys()),  max(partition.keys()))
    #print(partition)
    print(f"Total length: {sum(length for _, length in partition.values())}\n")


data = dd(dict)
data['meta']['doc'] = doc
data['meta']['docid'] = docid
data['meta']['length'] = sum(sent[sid][1] for sid in sent)
data['meta']['first'] = min(sent)
data['meta']['last'] =  max(sent)
data['meta']['split'] =  "60/20/20 -- split on paragraphs so lengths are slightly uneven"
data['meta']['dcterms:created'] =  date.today().isoformat()


data['train']['first'] = min(partitions[0])
data['train']['last'] = max(partitions[5])
data['train']['length'] = sum(sum(length for _, length in partitions[i].values()) for i in range(0,6)) 


data['dev']['first'] = min(partitions[6])
data['dev']['last'] = max(partitions[7])
data['dev']['length'] = sum(sum(length for _, length in partitions[i].values()) for i in range(6,8)) 


data['test']['first'] = min(partitions[8])
data['test']['last'] = max(partitions[9])
data['test']['length'] = sum(sum(length for _, length in partitions[i].values()) for i in range(8,10)) 


for i, partition in enumerate(partitions):
    data[f'fold{i}']['first'] = min(partition)
    data[f'fold{i}']['last'] = max(partition)
    data[f'fold{i}']['length'] = sum(length for _, length in partition.values())


output_file_name = f"{doc}-split.toml"
with open(output_file_name, "w") as toml_file:
    toml.dump(data, toml_file)

