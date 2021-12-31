###
### one off script to fix some issues with sentiment
###
### If a concept is marked as don't tag (x)
### then it should have no sentiment
### so delete it
###
### It should be Ok to call this anytime,
### if no such concepts exist
### the nothing happens
###


import sqlite3

dbdir = '/var/www/ntumc/db/'

### check which dbs

dbs = [ 'eng.db', 'jpn.db', 'ind.db' ]

for db in dbs:
    conn = sqlite3.connect(dbdir + db)
    c = conn.cursor()
    c.execute("""select c.sid, c.cid from sentiment as s 
                 left join concept as c 
                 on s.sid=c.sid and s.cid =c.cid 
                 where tag = 'x'""")

    donttag = c.fetchall()

    c.executemany("""DELETE from sentiment
    WHERE sid=? and cid=?""", donttag)

    conn.commit()
     

