#! /bin/bash 

name=$1
warmup='--++'
mainloop='++--'
begintime=`date +%s`
database=`cut -d ';' -f 2 machinename`
# database="variation"
machinename=`cut -d ';' -f 1 machinename`
# machinename="lolo"
serveraddr="172.16.45.8:27019"
# serveraddr="127.0.0.1:27019"

if [ -z $machinename ];  then 
    machinename=`cat /proc/sys/kernel/hostname`
    # machinename="testmachine"
fi 
if [ -z $database ] ; then 
    database='rapl3'
fi 


re='.*[0-9]+.*'


while read line
do
    prefix=${line:0:4} 
    if [  "$prefix" == "$warmup" ] ; then 
        if [[ $line =~ $re ]] ;then  
            warmuptime=`echo $line | awk '{s=substr($0,6,length($0)-6); gsub("\\.","_",s);print s}'`
        else 
            warmuptime=`date +%s` ; 
        fi
    elif [  "$prefix" == "$mainloop" ]  ; then
        if [[ $line =~ $re ]] ;then  
            executiontime=`echo $line | awk '{s=substr($0,6,length($0)-6); gsub("\\.","_",s);print s}'`
            else 
            executiontime=`date +%s` ; 
            fi 
    fi
done < "/dev/stdin"
endtime=`date +%s`

id=`docker inspect --format "{{.Id}}" $name`

if [ -z $warmuptime ] ; then  
    warmuptime=$begintime;
fi

if [ -z $executiontime ] ;then 
    executiontime=$begintime;
fi  

echo "++++begin---"$begintime
echo '--++beginwarmup---'$warmuptime
echo '++--endwarmup---'$executiontime
echo "++++end---"$endtime ;


echo "$serveraddr/$database/$machinename?name=$name&begin=$begintime&beginwarmup=$warmuptime&beginexecution=$executiontime&end=$endtime&id=$id"
# curl -X POST  "$serveraddr/$database/$machinename?target=$name&begin=$begintime&beginwarmup=$warmuptime&beginexecution=$executiontime&end=$endtime&id=$id"
 