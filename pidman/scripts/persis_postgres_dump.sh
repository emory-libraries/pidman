#!/bin/bash


set -x 
#if [ 1 -eq 0 ];then
while getopts ":d:D:h:l:u:" option;do
   case $option in    
     d) dir=$OPTARG;;
     D) DB=$OPTARG;;
     h) host=$OPTARG;;
     l) tablelist=$OPTARG;;
     u) user=$OPTARG;;
     ?) exit;;
   esac
done
#
[ -z "$dir" ] && dir="$(pwd)"
seq='pid_pid_pid_seq'
let new_nextval=0
orphans="delete_orphans.mysql"
tablelist="/tmp/persis_tablelist.$$"
echo "\dt;" | psql -h $host -U${user} $DB | grep 'public' | awk 'BEGIN {FS="|"} {print $2}' > $tablelist

nextval=$(echo "select * from ${seq};" | psql -t -h $host -U${user} $DB | grep $seq | awk 'BEGIN {FS="|"} {print $2}' | sed 's/ //g')
let new_nextval=$nextval+100
echo "ALTER TABLE pid_pid AUTO_INCREMENT = $new_nextval;" > ${dir}/alter-pid_pid.mysql

cat $tablelist |\
while read table;do
    dumpfile=
    [ -n "$dir" ] && dumpfile="$dir/"
    dumpfile="${dumpfile}${table}_dump.sql"
    cmd="pg_dump -v -O --inserts --column-inserts --disable-dollar-quoting --no-tablespaces -a -t $table -f $dumpfile -U${user} -h $host --role=${user} $DB"
    echo "$cmd"
    eval "$cmd"
    if [ -e "$dumpfile" ];then
       massagedfile=/tmp/${dumpfile}.$$
       sed -i '/--/d' $dumpfile
       sed -i '/SET /d' $dumpfile 
       sed -i '/SELECT pg_/d' $dumpfile 
       sed -i '/^$/d' $dumpfile
       cat -s $dumpfile | ./tzfix.pl > /tmp/temp.$$
       mv /tmp/temp.$$ $dumpfile
       if [ "$table" == 'pid_domain' ];then
          cat $dumpfile | sort -t "(" -k3.1,3 -n > /tmp/temp.$$
          mv /tmp/temp.$$ $dumpfile
       fi
       [ ! -s "$dumpfile" ] && rm -f $dumpfile
       if [ "$table" == 'pid_target' ];then
          if [ -e "$dumpfile" ];then
             [ -e "$orphans" ] && rm -f "$orphans"
             cat $dumpfile | awk '{print $13}' | sed 's/,//'| sort -n |\
             while read p;do 
                 echo "DELETE FROM pid_target WHERE pid_id = $p AND NOT EXISTS (SELECT * from pid_pid WHERE id = $p);" >> ${dir}/$orphans
             done
          fi
       fi
    fi
done
rm -r $tablelist
