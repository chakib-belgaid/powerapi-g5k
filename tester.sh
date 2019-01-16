

while getopts "n:" o; do
    case "${o}" in
        n)
            name=${OPTARG}
            ;;
    esac
done

shift $((OPTIND-1))
program="$@"

if [ -z $name ] ; then 
    name=$1
    name=${name#*\/} #exctracting the second part after / separator 
    name=${name/\:/_} # replacing : with _ to avoid conflicts 
    fi;

echo $name 
echo $program 
docker run -t   --cpuset-cpus 0  --name $name $program | ./listener2.sh $name 
#  | ./listener2.sh $name
docker rm  $name