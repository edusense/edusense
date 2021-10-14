# Instruction to setup Edusense Development Workbench from scratch

Hi, my name is EduRise. I will help you to setup a workbench for EduSense and start developing on your own from scratch.
I am a non-intelligent script written by a developer trying to be creative. Thus, don't mind my errors or 
incompleteness. They are not my core nature, just inherited from my creator. 


##Step 1: Installing Linux and Dependencies

First, we need a linux based system, and an nvidia-GPU(even if it's external), preferably 1080-Ti. I know it's hard, But EduSense ain't going to 
run for us without these. Now, external GPUs can create too much mess collaborating with your linux. To make this part easier, 
Let's try some adventure, and not install Ubuntu this time.


### 1.1: Installing PopOS

Welcome, PopOS([https://pop.system76.com/]()), A brainchild of some really creative but sincere minds. You can start by installing their latest distribution
from their website. Make sure to choose a distribution pre-installed with nvidia-drivers.

### 1.2: Attaching external GPU(If there is any)

Thanks to this kind person Micheal Hertig([https://github.com/hertg]()), who automated whole process of adding external GPU for us.
Here are list of commands to connect your external GPU and make it a default

```bash
    1  nvidia-smi # Making sure nvidia drivers are working fine
    2  sudo boltctl 
    3  sudo add apt-repository ppa:hertg/egpu-switcher
    4  sudo apt add apt-repository ppa:hertg/egpu-switcher
    5  sudo add-apt-repository ppa:hertg/egpu-switcher
    6  sudo apt update
    7  sudo apt install egpu-switcher
    8  sudo egpu-switcher setup
    9  sudo reboot
    ## For easy and live GPU status, download nvtop
    10 sudo apt install nvtop
```

Once you have external GPU connected, nvidia-smi should give some output like this:

```bash
$nvidia-smi
Mon Oct xx xx:xx:xx 2021       
+-----------------------------------------------------------------------------+
| NVIDIA-SMI xxx.xx.xx    Driver Version: xxx.xx.xx    CUDA Version: x.x     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                               |                      |               MIG M. |
|===============================+======================+======================|
|   0  NVIDIA GeForce ...  Off  | 00000000:09:00.0 Off |                  N/A |
| 49%   49C    P0    85W / 250W |    634MiB / 11178MiB |      0%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+
                                                                               
+-----------------------------------------------------------------------------+
| Processes:                                                                  |
|  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
|        ID   ID                                                   Usage      |
|=============================================================================|
|    0   N/A  N/A      1060      G   /usr/lib/xorg/Xorg                 40MiB |
|    0   N/A  N/A      1203      G   /usr/bin/gnome-shell                7MiB |
|    0   N/A  N/A      1648      G   /usr/lib/xorg/Xorg                328MiB |
|    0   N/A  N/A      2225      G   /usr/bin/gnome-shell               57MiB |
+-----------------------------------------------------------------------------+

```


### 1.3: Only works in pycharm (Just kidding, download an editor of your choice :p)

For this tutorial, We are using pycharm editor, which can be downloaded from JetBrains site here([https://www.jetbrains.com/pycharm/]()).

### 1.4: Install Mongodb(for EduSense Data Storage)

Install latest distribution of mongo database to support storage service for EduSense.

Follow instructions here to setup the latest version of mongoDB for your OS.

[https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/]()

You can use the same instructions as used by ubuntu. Here is dump of what I did to successfully install mongodb

```bash
edusense@pop-os:~$ wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -
OK
edusense@pop-os:~$ echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list
deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse
edusense@pop-os:~$ sudo apt-get update
... # Skipping logs
edusense@pop-os:~$ sudo apt-get install -y mongodb-org
... # Skipping logs
edusense@pop-os:~$ sudo systemctl start mongod
edusense@pop-os:~$ sudo systemctl status mongod
● mongod.service - MongoDB Database Server
     Loaded: loaded (/lib/systemd/system/mongod.service; disabled; vendor preset: enabled)
     Active: active (running) since Mon 2021-10-11 18:14:24 EDT; 9s ago
       Docs: https://docs.mongodb.org/manual
   Main PID: 16636 (mongod)
     Memory: 60.2M
     CGroup: /system.slice/mongod.service
             └─16636 /usr/bin/mongod --config /etc/mongod.conf

Oct 11 18:14:24 pop-os systemd[1]: Started MongoDB Database Server.
edusense@pop-os:~$ sudo systemctl enable mongod
Created symlink /etc/systemd/system/multi-user.target.wants/mongod.service → /lib/systemd/system/mongod.service.
edusense@pop-os:~$ mongo
MongoDB shell version v5.0.3
connecting to: mongodb://127.0.0.1:27017/?compressors=disabled&gssapiServiceName=mongodb
... # Skipping logs
```

### 1.5: Get SSL certificates for Storage Server(optional)

If you need to protect your storage with SSL to add security for sensitive data. You can use certbot with a public ip for 
your system. This can help with remote access to storage by other applications. If you do not have/need public ip, you can skip this part

Get your public ip by following these instructions:

```bash
$ ip a

... #Skipping some output
3: <NET-NAME>: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether ... #Some private output
    inet 128.a.b.c/d ... #Some private output
       valid_lft ... #Some private output
    inet6 ... #Some private output
       valid_lft ... #Some private output

$ host 128.a.b.c/d
c.b.a.128.in-addr.arpa domain name pointer some.public.hostname.
```

Now install certificates following instructions on letsEncrypt([https://letsencrypt.org/]()). Here are instructions I used.

Before installing certbot, install snap for pop-os. Instructions are provided here([https://snapcraft.io/docs/installing-snap-on-pop]())
```bash


```



### 1.6: Install Docker and relevant dependencies

#### 1.6.1: Install docker core

Instructions to install core docker can be found here ([https://docs.docker.com/engine/install/ubuntu/]())

Once, downloaded and run hello-world program for docker, run post installation for non-root access from here
[https://docs.docker.com/engine/install/linux-postinstall/]()

Instructions I ran from their doc for reference.
```bash
edusense@pop-os:~$ sudo apt-get remove docker docker-engine docker.io containerd runc
Reading package lists... Done
Building dependency tree       
Reading state information... Done

E: Unable to locate package docker-engine
edusense@pop-os:~$ sudo apt-get update
... #Skipping some output 
edusense@pop-os:~$ sudo apt-get install \
>     apt-transport-https \
>     ca-certificates \
>     curl \
>     gnupg \
>     lsb-release
... #Skipping some output
edusense@pop-os:~$ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
edusense@pop-os:~$ echo \
>   "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
>   $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
edusense@pop-os:~$ sudo apt-get update
... #Skipping some output
edusense@pop-os:~$ sudo apt-get install docker-ce docker-ce-cli containerd.io
... #Skipping some output
edusense@pop-os:~$ sudo groupadd docker
groupadd: group 'docker' already exists
edusense@pop-os:~$ sudo usermod -aG docker $USER
edusense@pop-os:~$ newgrp docker
edusense@pop-os:~$ docker run hello-world
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
2db29710123e: Pull complete 
Digest: sha256:9ade9cc2e26189a19c2e8854b9c8f1e14829b51c55a630ee675a5a9540ef6ccf
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message shows that your installation appears to be working correctly.
... #Skipping some output
edusense@pop-os:~$ sudo systemctl enable docker.service
Synchronizing state of docker.service with SysV service script with /lib/systemd/systemd-sysv-install.
Executing: /lib/systemd/systemd-sysv-install enable docker
edusense@pop-os:~$ sudo systemctl enable containerd.service
```

#### 1.6.2: Install nvidia-docker(to support openpose pipeline)

Instructions for nvidia docker can be found here
[https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html]()

For general installation, this can be used first.

Instructions I ran from their doc for reference.

```bash
edusense@pop-os:~$ distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
>    && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - \
>    && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
OK
# Unsupported distribution!
# Check https://nvidia.github.io/nvidia-docker
edusense@pop-os:~$ sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
... #Skipping some output
Processing triggers for man-db (2.9.1-1) ...
edusense@pop-os:~$ sudo systemctl restart docker
edusense@pop-os:~$ sudo docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
Unable to find image 'nvidia/cuda:11.0-base' locally
11.0-base: Pulling from nvidia/cuda
54ee1f796a1e: Pull complete 
f7bfea53ad12: Pull complete 
46d371e02073: Pull complete 
b66c17bbf772: Pull complete 
3642f1a6dfb3: Pull complete 
e5ce55b8b4b9: Pull complete 
155bc0332b0a: Pull complete 
Digest: sha256:774ca3d612de15213102c2dbbba55df44dc5cf9870ca2be6c6e9c627fa63d67a
Mon Oct xx x:xx:xx xxxx       
+-----------------------------------------------------------------------------+
| NVIDIA-SMI xxx.xx.xx   Driver Version: xxx.xx.xx    CUDA Version: xx.x     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                               |                      |               MIG M. |
|===============================+======================+======================|
|   0  NVIDIA GeForce ...  Off  | 00000000:09:00.0 Off |                  N/A |
| 49%   46C    P0    85W / 250W |    581MiB / 11178MiB |      0%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+
                                                                               
+-----------------------------------------------------------------------------+
| Processes:                                                                  |
|  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
|        ID   ID                                                   Usage      |
|=============================================================================|
+-----------------------------------------------------------------------------+

```


Now, life's not easy, there will be some lemons waiting for you. like here, Pop-OS uses an outdated version of nvidia-runtime-toolkit, and
nvidia-docker needs the more updated version.

I found this workaround([https://github.com/pop-os/pop/issues/1708](), which should be okay for our case, hope pop OS peeps get time to figure this out without needing a work around.

## Step 2: Get Edusense and setup storage server, and compute dockers images

### 2.1: Clone Edusense Repo

Install github and clone Edusense Repo recursively with submodules.

```bash
$ cd ~/
$ git clone --recursive https://github.com/edusense/edusense.git edusense-dev
$ mkdir logs-dev && chmod 777 logs-dev # to supporting logging for running Edusense pipeline
```

### 2.2: Setup Storage Server

Create a new start-api-server.sh script and copy following code there:

```bash
$ vim start-api-server.sh

# COPY following code and save the file
export SSL_CERT=$(cat </path/to/ssl/fullchain.pem>) # Only required with public IP
export SSL_CERT_PRIVATE_KEY=$(cat <path/to/ssl/privkey.pem>) # Only required with public IP
export APP_USERNAME="<SOME-USERNAME>"
export APP_PASSWORD="<SOME_PASSWORD>"
~/edusense-dev/storage/apiserver/apiserver   -port <SOME-PORT>   -dbhost localhost:27017  -db <DB-NAME>
# Close the file
$ chmod 755 start-api-server.sh
$ ./start-api-server.sh
2021/10/11 19:12:58 Starting api server without TLS # output for no public IP

```

Here, /path/to/ssl/ are absolute path to certificate, and private key developed from letsencrypt. The provided SOME-USERNAME
and SOME-PASSWORD are necessary to set as environment variable before running compute dockers.

Once executed, the API-Server will start running at given port number. you can access it at localhost:<SOME-PORT>, or see new database in mongodb

### 2.3 Setup Compute Pipeline

Detailed instructions to setup compute pipeline are provided here
\
[https://github.com/edusense/edusense/tree/master/compute]()

Follow instructions here to create corresponding docker images and start running dockers.

### 2.4 End to end EduSense classroom processing with front and back video

Detailed instructions to run complete EduSense pipeline together for pre-recorded videos are provided here.
\
[https://github.com/edusense/edusense/tree/master/scripts]()

### 2.3 Development on Storage Server

TO explore more development options on storage server with Golang, Find detailed instructions here:
\
[https://github.com/edusense/edusense/tree/master/storage]()



