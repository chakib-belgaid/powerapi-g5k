# powerapi-g5k
A sample project that demonstrate how to use Powerapi inside grid5000 

# Requires 

1. **G5k** account 
   To open an account fill this  [form](https://www.grid5000.fr/mediawiki/index.php/Special:G5KRequestAccountUMS)  

2. Setup the **vpn** : 
   you'll find the configuration in this [page](https://www.grid5000.fr/mediawiki/index.php/VPN)


##### Remark : 

If you are using MacOS  add the following line in the file 
    *Grid5000_VPN.ovpn*
    
    dev tun

3. **Docker** installed 
    
    You'll find the installation guide in the following [link](https://docs.docker.com/install/)

4. **docker-machine-driver-g5k**  Installed 
To be enable the reservation of *g5k-machines* via docker machine plugin (In order to install docked and all it's infra in the g5k-machine once it is reserved )

   You can get it from this [repository](https://github.com/Spirals-Team/docker-machine-driver-g5k)
   
# How it works: 
SmartWatts, works a service. 
You launch the sensor (you find it as a docker container) in the machine that you want to monitor. Then this sensor will gather different metrics and upload them into the server (Mongodb base) after you can consult this base in order to get the information, 
you find in the project a client written in  

![Smartwatts architecture](https://github.com/chakib-belgaid/powerapi-g5k/raw/master/images/SmartWatts.png "Smartwatts Architecture")

# Usage

# Reservation of the machine 

1. After getting all the requirements and configuring your environment variables 
       
        export G5K_USERNAME="user"
        export G5K_PASSWORD="********"

2. launch the starter script startmachine with the given name of the machine and the time when it ends.
##### example 
        ./startmachine.sh test1 15:00:00 

this command will reserve a machine from now until 15:00 of the same day and it will give herthe name *test1* 

ps: if the value of the date is less than the actual time than it will reserve until the given time from the next day (add 24h)


##### Remark : 
The default values of these parameters are 

* name: test

* time : *17:30*  if the actual time is between is before 17:30 else it will be *8:0* for the next day 

* it will reserve an node in *paravance* from *rennes* site unless you change it in the script
        you can find the different clusters in this [link](https://www.grid5000.fr/mediawiki/index.php/Har dware)
Ps: this version of smartwats works only with machines that integrate Rapl sensors so in grid5000 case, the processor must be V3 or newer 

* the database name : rapls  

3. You can connect to the machine via *docker-machine* it will offer you this [set of options](https://docs.docker.com/machine/reference/)

        docker-machine ls 
    
It will list all actual reserved machines 
       
        docker-machine ssh machinename 

4. To connect the remote machine through ssh  (the usage of [screen](https://linux.die.net/man/1/screen) is recommended to preserve the session even after a loss of connection )

        docker-machine scp localfile machinename:/file 

5. To copy files from local to the remote machine 

        docker-machine rm machinename 

To delete the remote machine 

## Launch the tests 
after we connect to the reserved machine using the commande 

        docker-machine ssh machinename

just launch the script [tester.sh](tester.sh)

with the name of the container that you right to measure  

        ./tester.sh containername args 

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

you'll find the measure in a collection named **recap"machinename"** a mongodb database situated in the address "mongodb://172.16.45.8:27017" 

for more details check the following [file](computeConso.ipynb) 

#### remark 

1. you can find more details such as the power consumption during the time ..etc in the second part [file](computeConso.ipynb)

2. you find here a jupyter client that uses pymongo to consult the database 

you can download the docker container 
        
        docker pull chakibmed/jupyter:powerapi 

and to start it run this command 

        docker run -d -v "$(pwd)":/home/jovyan/work --name notebook2 -p 8888:8888 chakibmed/jupyter:powerapi 

to connect use the authentication link that you'll get from 

        docker logs notebook 

