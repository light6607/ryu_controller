# install the netsniff-ng
#!/bin/bash

git clone https://github.com/borkmann/netsniff-ng

sudo apt-get install flex
sudo apt-get install bison

cd netsniff-ng
./configure 
make 

cp ../syn.trafgen ./trafgen/syn.trafgen
cp ../attack_synflood.sh ./trafgen/attack_synflood.sh
