dbdir=/var/www/ntumc/db


for db in jpn ita ind zsm
do
    command="ALTER TABLE meta ADD COLUMN lang TEXT;"
    command="$command ALTER TABLE meta ADD COLUMN version TEXT;"
    command="$command ALTER TABLE meta ADD COLUMN master TEXT;"
    #sqlite3 "$dbdir"/"$db" "
    update="UPDATE meta SET title='NTU-MC', license='CC BY 4.0', lang='$db', version='master', master='$db';" 
    sqlite3 "$dbdir/$db.db" " $command "
    sqlite3 "$dbdir/$db.db" " $update  "
    sqlite3 "$dbdir/$db.db" "SELECT * from META"
done
