# PowerAPI
A distributed software infrastructure to measure the energy consumption of Docker containers. 

# Requirements

## Hardware 

PowerAPI is based on a master/slave architecture where:
- **Slave** is the physical machine that hosts all the containers we want to measure. We need a power sensor for each slave machine, which will collect all the measurements and report them to the server backend.
- **Server** is responsible for the data storage and estimating the energy consumption.

![Smartwatts architecture](https://github.com/chakib-belgaid/powerapi-g5k/raw/master/images/SmartWatts.png "Smartwatts Architecture")

As we see in the above figure, several slaves can be started in parallel with a single server. 

##### limitations :
- The slave node must use a new CPU (Xeon e5 v3 or newer, and _Intel Sandy Bridge_ generation or newer)
- The slave node has to be dedicated to measurements and thus run a _single test at once_.

## Software

**Docker** 
You can find the installation guide in the following [link](https://docs.docker.com/install/linux/docker-ce/ubuntu/).


# Usage: 

- **Server**: 
1. Create a Docker network using the following command :
        
        docker network create aloha 

2. Start a [MongoDB server](https://www.mongodb.com) using the official [Docker image](https://hub.docker.com/_/mongo)
   example: 

        docker run --name mongobase -p 27017:27017 --net aloha -d mongo

Here, we run a Docker container, named `mongobase`, mapped to the port `27017` and associated to the docker network `aloha`.

3. Start the [SmartWatts listener](https://hub.docker.com/r/chakibmed/bitwatts-g5k-energy) 

        docker run -d --name listener -p 27019:4443 --net aloha chakibmed/bitwatts-g5k-energy:latest 

Here, we listen to the port `27019` and we interact with the MongoDD database using the network `aloha`.

PS: The name of the Docker container of mongodb must be `mongobase` in order to make the server find him and it has been connected in the same docker network. 


- **TestMachine** 
1. activate the MSR 
   
        modprobe msr

2. start the sensor container 
   
        docker run --privileged --name smartwatts-sensor -td \
        -v /sys:/sys -v /var/docker/containers:/var/lib/docker/containers:ro \
        gfieni/powerapi:sensor -n $name -U "mongodb:$serveraddress:$serverport" -D rapls2 -C "sensor$name" \
        -s "rapl" -o -e "RAPL_ENERGY_PKG" -e "RAPL_ENERGY_DRAM" \
        -s "pcu" -o -e "UNC_P_POWER_STATE_OCCUPANCY:CORES_C0" \
        -e "UNC_P_POWER_STATE_OCCUPANCY:CORES_C3" \
        -e "UNC_P_POWER_STATE_OCCUPANCY:CORES_C6" \
        -c "core" -e "CPU_CLK_THREAD_UNHALTED:REF_P" \
        -e "CPU_CLK_THREAD_UNHALTED:THREAD_P" -e "LLC_MISSES"

Ps:
- Do not forget to replace the variables `name`, `serveraddress`, `serverport`, `sensor$name`  with their values (name if the name of the test machine).
- If your machine does not support any of the other modules, just remove them. The minimal command should look like:
  
        docker run --privileged --name smartwatts-sensor -td \
        -v /sys:/sys -v /var/docker/containers:/var/lib/docker/containers:ro \
        gfieni/powerapi:sensor -n $name -U "mongodb:$serveraddress:$serverport" \
        -D rapls2 -C "sensor$name" \
        -s "rapl" -o -e "RAPL_ENERGY_PKG"

1. Launch the script [tester.sh](tester.sh)

with the name of the container that you right to measure  

        ./tester.sh containername args 
        
PS: Do not forget to change the `server address` `machinename` and `server port` in the script [listener2.sh](listener2.sh)

#### example 

The command 

        ./tester.sh chakibmed/sleep n

Will launch a container of the image *chakibmed/sleep* with **n** as a parameter  

the test is just an idle container that sleeps during **n** seconds 

#### Remark 
by default it will take the name of the image + the tag of the version as a test name. In our case it the container name will be **sleep** 

so if we launch another test 

        ./tester.sh chakibmed/contaier:tag 

the default name will be **container_tag** 

but you can specify it with the option `-n`

        .tester.sh -n mytest chakibmed/sleep 5 

will give the name **mytest** to the container 

To check the name of the container, you can run 

        docker ps 

## Get the power consumptions 

You will find the measure in a collection named **recap"machinename"** a mongodb database situated in the address "mongodb://serveraddres:serverport" 

For more details check the following [file](computeConso.ipynb) 

#### Remarks

1. You can find more details, such as the power consumption during the time, etc., in the second part [file](computeConso.ipynb)

2. You find here a jupyter client that uses *pymongo* to consult the database 

you can download the Docker container 
        
        docker pull chakibmed/jupyter:notebook 

and start it by running this command 

        docker run -d -v "$(pwd)":/home/jovyan/work --name noptebook -p 8888:8888 chakibmed/jupyter:powerapi 

to connect, use the authentication link that you will get from 

        docker logs notebook 

