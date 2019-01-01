# powerapi-g5k
A sample project that demonstrate how to use Powerapi inside grid5000 

#Requires 

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

4. **docker-machine-driver-g5k** 
   You can get it from this [repository](https://github.com/Spirals-Team/docker-machine-driver-g5k)

#Usage

1. After getting all the requirements and configuring your environment variables 
       
        export G5K_USERNAME="user"
        export G5K_PASSWORD="********"

launch the starter script startmachine with the given name of the machine and the time when it ends.
#####example 
        ./startmachine.sh test1 15:00:00 

this command will reserve a machine from now until 15:00 of the same day and it will give herthe name *test1* 

ps: if the value of the date is less than the actual time than it will reserve until the given time from the next day (add 24h)


##### Remark : 
The default values of these parameters are 

* name: test

* time : *17:30*  if the actual time is between is before 17:30 else it will be *8:0* for the next day 

* it will reserve an node in *paravance* from *rennes* site unless you change it in the script

* the database name : rapls  

2. You can connect to the machine via *docker-machine* it will offer you this [set of options](https://docs.docker.com/machine/reference/)

#####example  
        docker-machine ls 
    
It will list all actual reserved machines 
       
        docker-machine ssh machinename 

To connect the remote machine through ssh  (the usage of [screen](https://linux.die.net/man/1/screen) is recommended to preserve the session even after a loss of connection )

        docker-machine scp localfile machinename:/file 

To copy files from local to the remote machine 

        docker-machine rm machinename 

To delete the remote machine 

3. you will find all the recorded data in a mongodb database situated in the address "mongodb://172.16.45.8:27017" 

you find here a jupyter client that uses pymongo to consult the database 

you can download the docker container 
        
        docker pull chakibmed/jupyter:notebook 

and to start it run this command 

        docker run -d -v "$pwd":/home/jovyan/work --name noptebook -p 8888:8888 chakibmed/jupyter:notebook 

to connect use the authentication link that you'll get from 

        docker logs notebook 
