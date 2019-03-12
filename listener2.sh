
name=$1
warmup='--++'
mainloop='++--'
begintime=`date +%s`
# database=`cut -d ';' -f 2 machinename`
database=rapls2
# machinename=`cut -d ';' -f 1 machinename`
machinename="test" #need to be changed 
serveraddres="127.0.0.1" # need to be changed 
serverport="27019" # need to match the port given to the docker container  chakibmed/bitwatts-g5k-energy

while read line
do
    prefix=${line:0:4} 
    if [  "$prefix" == "$warmup" ] ; then 
    warmuptime=`date +%s` ; 
    elif [  "$prefix" == "$mainloop" ] ; then 
    executiontime=`date +%s` ; 
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

warmuptime=warmuptime&executiontime=$executiontime&endtime=$endtime

curl -X POST  "$serveraddres:$serverport/$database/$machinename?name=$name&begin=$begintime&beginwarmup=$warmuptime&beginexecution=$executiontime&end=$endtime&id=$id"
# `python logger.sh.py $name $begintime $warmuptime $executiontime $endtime $collectionname`