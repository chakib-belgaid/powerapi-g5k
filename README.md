# Powerapi
An infrastructure to measure energy consumption of docker containers. 

# Requirements 

## Hardware 

PowerApi is based on master/slave architecture when :

- **Slave** : is the test machine that contains all the containers we want to measure. We have a sensor for each slave machine which will collect all the data and send them to the server.
- **Server** : Responsible for Storage of the data and Calculating the energy measurement and then push them back in the database.

![Smartwatts architecture](https://github.com/chakib-belgaid/powerapi-g5k/raw/master/images/SmartWatts.png "Smartwatts Architecture")

As we see in the figure below, we can launch many slaves with a single server. 

##### limitations :
-The slave machine must use a new CPU (xenon e5 v3 or newer and sandy bridge generation or newer)
-the slave machine has to be dedicated only to tests and we have to run a _single test at once_.

## Software

**Docker** 
you can find the installation guide in the following [link](https://docs.docker.com/install/linux/docker-ce/ubuntu/).


# Usage: 

- **Server**: 
1. Start a [mangoBb server](https://www.mongodb.com) using the official [Docker image](https://hub.docker.com/_/mongo)
   example: 

        docker run --name mongobase -p docker ps  27017:27017 --net aloha -d mongo
here we run a docker container named *mongobase* mapped to the port 27017 and associated to the docker network *aloha*.

2. Start the [bitwatts listener](https://hub.docker.com/r/chakibmed/bitwatts-g5k-energy) 

        docker run -d --name listener -p 27019:4443 --net aloha chakibmed/bitwatts-g5k-energy:latest 

Here we will listen to the port 27019 and we will interact with the mongoDb database using the network *aloha*.
Ps: The name of the docker container of mongodb must be **mongobase** in order to make the server find him and it has been connected in the same docker network. 


- **TestMachine** 
1. activate the MSR 
   
        modprobe msr

2. start the sensor container 
   
        docker run --privileged --name smartwatts-sensor -td \
        -v /sys:/sys -v /var/docker/containers:/var/lib/docker/containers:ro \
        gfieni/powerapi:sensor -n $name -U "mongodb:$serveraddress:$serverport" -D $rapls2 -C "sensor$name" \
        -s "rapl" -o -e "RAPL_ENERGY_PKG" -e "RAPL_ENERGY_DRAM" \
        -s "pcu" -o -e "UNC_P_POWER_STATE_OCCUPANCY:CORES_C0" -e \
        "UNC_P_POWER_STATE_OCCUPANCY:CORES_C3" \
        -e "UNC_P_POWER_STATE_OCCUPANCY:CORES_C6" \
        -c "core" -e "CPU_CLK_THREAD_UNHALTED:REF_P" \
        -e "CPU_CLK_THREAD_UNHALTED:THREAD_P" -e "LLC_MISSES"

Ps: don't forget to replace the variables *serveraddress* *serverport* and *name* with their values (name if the name of the test machine).

3. launch the script [tester.sh](tester.sh)

with the name of the container that you right to measure  

        ./tester.sh containername args 
ps: don't forget to change the serveraddres in the script [listener2.sh](listener2.sh)

#### example 

The command 

        ./tester.sh chakibmed/sleep n

Will launch a container of the image 8*chakibmed/sleep*8 with **n** as a parameter  

the test is just an idle container that sleeps during **n** seconds 

#### Remark 
by default it will take the name of the image + the tag of the version as a test name. In our case it the container name will be **sleep** 

so if we launch another test 

        ./tester.sh chakibmed/contaier:tag 

the default name will be **container_tag** 

but you can specify it with the option -n 

        .tester.sh -n mytest chakibmed/sleep 5 

will give the name **mytest** to the container 

To check the name of the container you can run 

        docker ps 

## get the measures 

you'll find the measure in a collection named **recap"machinename"** a mongodb database situated in the address "mongodb://serveraddres:serverport" 

for more details check the following [file](computeConso.ipynb) 

#### remark 

1. you can find more details such as the power consumption during the time ..etc in the second part [file](computeConso.ipynb)

2. you find here a jupyter client that uses pymongo to consult the database 

you can download the docker container 
        
        docker pull chakibmed/jupyter:notebook 

and to start it run this command 

        docker run -d -v "$pwd":/home/jovyan/work --name noptebook -p 8888:8888 chakibmed/jupyter:notebook 

to connect use the authentication link that you'll get from 

        docker logs notebook 

