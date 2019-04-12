
#! /bin/bash 

while getopts "s:c:" o; do
    case "${o}" in
        s) 
            site=${OPTARG}
            ;;
        c)  
            cluster=${OPTARG}
            ;;
    esac
done
shift $((OPTIND-1))

if [ -z $site ] ; then 
    site='rennes'; 
fi 

if [ -z $cluster ] ; then 
    cluster='paravance'; 
fi 


timediff()
{
    timeB=$1 # 09:59:35
    timeA=$2 # 17:32:55

    # feeding variables by using read and splitting with IFS
    IFS=: read ah am as <<< "$timeA"
    IFS=: read bh bm bs <<< "$timeB"

    # Convert hours to minutes.
    # The 10# is there to avoid errors with leading zeros
    # by telling bash that we use base 10
    secondsA=$((10#$ah*60*60 + 10#$am*60 + 10#$as))
    secondsB=$((10#$bh*60*60 + 10#$bm*60 + 10#$bs))
    DIFF_SEC=$((secondsB - secondsA))
    # echo "The difference is $DIFF_SEC seconds.";
    if [[ $DIFF_SEC -lt "0" ]] 
    then 
        DIFF_SEC=$((DIFF_SEC + 86400))
    fi 

    SEC=$(($DIFF_SEC%60))
    MIN=$((($DIFF_SEC-$SEC)%3600/60))
    HRS=$((($DIFF_SEC-$MIN*60)/3600))
    TIME_DIFF="$HRS:$MIN:$SEC";
    echo "$TIME_DIFF"
}

if [ $# -gt 0 ] 
then 
    name=$1
    shift
else 
    name="test"
fi

if [ $# -gt 0 ] 
then 
    endT=$1

else 
    if [ `date +%H` -lt 17 ] ; 
        then 
        endT="17:30:00"
    else 
        endT="8:00:00"
    fi 
fi
# echo $endT

# exit 



dbname='rapls2'
name=$name`date +"%d%m%y"`
wallTime=$(timediff $endT  `date +%H:%M:%S`)
echo $name  $wallTime

# to make faster deployement but cant reboot # --g5k-reuse-ref-environment \ 


docker-machine create -d g5k \
--engine-storage-driver "overlay2" \
--g5k-image "debian9-x64-min" \
--engine-opt "data-root=/tmp/docker" \
--g5k-site "$site" \
--g5k-resource-properties "cluster='$cluster'" \
--g5k-walltime "$wallTime" \
$name  && \
docker-machine ssh $name modprobe msr 
docker-machine ssh $name docker run --privileged --name smartwatts-sensor  -td -v /sys:/sys -v /tmp/docker/containers:/var/lib/docker/containers:ro gfieni/powerapi:sensor -n $name -r "mongodb" -U "mongodb://172.16.45.8:27017" -D $dbname -C "sensor$name" \
        -s "rapl" -o -e "RAPL_ENERGY_PKG"  -e "RAPL_ENERGY_DRAM"  \
        -s "pcu" -o -e "UNC_P_POWER_STATE_OCCUPANCY:CORES_C0" -e "UNC_P_POWER_STATE_OCCUPANCY:CORES_C3" -e "UNC_P_POWER_STATE_OCCUPANCY:CORES_C6" \
        -c "core" -e "CPU_CLK_THREAD_UNHALTED:REF_P" -e "CPU_CLK_THREAD_UNHALTED:THREAD_P" -e "LLC_MISSES"

# docker-machine ssh $name ln -s ''
echo  "$name;$dbname" > machinename 
docker-machine scp machinename $name:~/
docker-machine scp tester.sh $name:~/
docker-machine scp listener2.sh $name:~/

# docker-machine ssh $name "cp /home/$G5K_USERNAME/scripts/.bashrc ."
# docker-machine ssh $name "cp /home/$G5K_USERNAME/scripts/* ."
rm machinename
# docker-machine ssh $name echo  "$name2 > machinename"
# docker-machine ssh $name mkdir $name   
# docker-machine ssh $name chown -R mbelgaid $name 
# docker-machine ssh $name chmod o+x . 
# docker-machine ssh $name pip install pymongo

# ssh mbelgaid@frontend.lille.grid5000.fr mkdir  -p "tests"$day"/"$name 
# docker-machine ssh $name echo "tests$day/$name > dirname "
# docker-machine scp analyse.sh $name:
# docker-machine scp commands $name:

