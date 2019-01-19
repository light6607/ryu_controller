#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call


def myNetwork():

    net = Mininet(topo=None,
                  build=False,
                  ipBase = '10.0.0.0/8')

    info('*** Adding controller \n')
    c0 = net.addController(name='c0',
                           controller = RemoteController,
                           protocol='tcp',
                           port=6653)

    info('*** Adding Switches \n')
    #creat s1 - s5 as access switch and s6 as aggregation switch
    swList=[]
    for i in range(0,6):
        sid = 's'+str(i+1)
        sw = net.addSwitch(sid,cls = OVSKernelSwitch)
        swList.append(sw)



    info('*** Adding hosts \n')
    #creat 15 hosts
    hostList=[]
    hNum = 1
    for j in range(0,5):
        for k in range(1,4):
            hid = 'h'+str(hNum)
            hip = '192.168.'+str(j+1)+'.'+str(k)
            host = net.addHost(hid,cls=Host,ip=hip,defaultRoute=None)
            hostList.append(host)
            hNum += 1


    info('*** Adding links \n')
    #for s1 - s5, each switch link to 3 hosts
    #and s1 - s5 both link to s6
    for i in range(1,6):
       for j in range(1,4):
           hid = (i-1)*3 + j
           net.addLink(swList[i-1],hostList[hid-1])

    s1s6 = {'bw':100}
    s2s6 = {'bw':100}
    s3s6 = {'bw':100}
    s4s6 = {'bw':100}
    s5s6 = {'bw':100}
    for i in range(1,6):
        net.addLink(swList[i-1],swList[5])


    info('*** Starting Network \n')
    net.build()
    info('*** Starting Controller \n')
    for controller in net.controllers:
        controller.start()

    info('*** Starting Switches \n')
    for i in range(1,7):
        sid = 's'+str(i)
        net.get(sid).start([c0])


    info('*** Post configure switches and hosts \n')
    for i in range(0,6):
        sid = 's'+str(i+1)
        sip = '192.168.'+str(i+1)+'.250'
        cmd = 'ifconfig '+ sid + ' ' + sip

        swList[i].cmd(cmd)

    for i in range(1,16):
        hostConf = 'ip route add 0.0.0.0/0 dev h'+str(i)+'-eth0 scope link'
        hostList[i-1].cmd(hostConf)

    CLI(net)
    net.stop()

if __name__ ==  '__main__':
    setLogLevel('info')
    myNetwork()
