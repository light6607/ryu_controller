#!/bin/bash
# author:light(jialiang) 2019.1.18
# used for the ryu and mininet install 
# just run this script 


sudo apt-get install git

# mininet install 
mininet_folder="/usr/local/src/mininet"
if [  ! -d "$mininet_folder" ];then
    cd /usr/local/src
	git clone git://github.com/mininet/mininet
	cd mininet
	./util/install.sh -n3V 2.5.0
fi



## sudo mn --test pingall (used for mininet install test)

# ryu install

sudo apt-get install python-eventlet
sudo apt-get install python-routes
sudo apt-get install python-webob
sudo apt-get install python-paramiko


ryu_folder="/usr/local/src/ryu"

if [  ! -d "$ryu_folder" ];then
    cd /usr/local/src
	git clone git://github.com/osrg/ryu.git
	cd ryu 
	sudo pip install -r tools/pip-requires
	sudo python setup.py install 
fi


sudo ryu-manager 


## ryu visual
#  #ryu-manager --verbose --observe-links ryu.topology.switches ryu.app.rest_topology ryu.app.ofctl_rest ryu.app.simple_switch
# attention : open another terminal and run 
# ./ryu/gui/controller.py
