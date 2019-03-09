#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 定义实验基本网络拓扑
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
                  ipBase='10.0.0.0/8')

    info('*** Adding controller\n')
    c0 = net.addController(name='c0',
                           controller=RemoteController,
                           protocol='tcp',
                           port=6653)

    info('*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)

    info('*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='121.0.0.1', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='121.0.0.2', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='121.0.0.3', defaultRoute=None)
    h4 = net.addHost('h4', cls=Host, ip='121.0.0.4', defaultRoute=None)
    h5 = net.addHost('h5', cls=Host, ip='121.0.0.5', defaultRoute=None)
    h6 = net.addHost('h6', cls=Host, ip='122.0.0.1', defaultRoute=None)
    h7 = net.addHost('h7', cls=Host, ip='122.0.0.2', defaultRoute=None)
    h8 = net.addHost('h8', cls=Host, ip='122.0.0.3', defaultRoute=None)
    h9 = net.addHost('h9', cls=Host, ip='122.0.0.4', defaultRoute=None)
    h10 = net.addHost('h10', cls=Host, ip='122.0.0.5', defaultRoute=None)
    h11 = net.addHost('h11', cls=Host, ip='123.0.0.1', defaultRoute=None)
    h12 = net.addHost('h12', cls=Host, ip='123.0.0.2', defaultRoute=None)
    h13 = net.addHost('h13', cls=Host, ip='123.0.0.3', defaultRoute=None)
    h14 = net.addHost('h14', cls=Host, ip='123.0.0.4', defaultRoute=None)
    h15 = net.addHost('h15', cls=Host, ip='123.0.0.5', defaultRoute=None)

    info('*** Add links\n')
    net.addLink(s1, h1)
    net.addLink(s1, h2)
    net.addLink(s1, h3)
    net.addLink(s1, h4)
    net.addLink(s1, h5)
    net.addLink(s2, h6)
    net.addLink(s2, h7)
    net.addLink(s2, h8)
    net.addLink(s2, h9)
    net.addLink(s2, h10)
    net.addLink(s3, h11)
    net.addLink(s3, h12)
    net.addLink(s3, h13)
    net.addLink(s3, h14)
    net.addLink(s3, h15)
    s1s2 = {'bw': 100}
    net.addLink(s1, s2, cls=TCLink, **s1s2)
    s1s3 = {'bw': 100}
    net.addLink(s1, s3, cls=TCLink, **s1s3)

    info('*** Starting network\n')
    net.build()
    info('*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info('*** Starting switches\n')
    net.get('s3').start([c0])
    net.get('s2').start([c0])
    net.get('s1').start([c0])

    info('*** Post configure switches and hosts\n')
    s3.cmd('ifconfig s3 123.0.0.11')
    s2.cmd('ifconfig s2 122.0.0.11')
    s1.cmd('ifconfig s1 121.0.0.11')

    h1.cmd('ip route add 0.0.0.0/0 dev h1-eth0 scope link')
    h2.cmd('ip route add 0.0.0.0/0 dev h2-eth0 scope link')
    h3.cmd('ip route add 0.0.0.0/0 dev h3-eth0 scope link')
    h4.cmd('ip route add 0.0.0.0/0 dev h4-eth0 scope link')
    h5.cmd('ip route add 0.0.0.0/0 dev h5-eth0 scope link')
    h6.cmd('ip route add 0.0.0.0/0 dev h6-eth0 scope link')
    h7.cmd('ip route add 0.0.0.0/0 dev h7-eth0 scope link')
    h8.cmd('ip route add 0.0.0.0/0 dev h8-eth0 scope link')
    h9.cmd('ip route add 0.0.0.0/0 dev h9-eth0 scope link')
    h10.cmd('ip route add 0.0.0.0/0 dev h10-eth0 scope link')
    h11.cmd('ip route add 0.0.0.0/0 dev h11-eth0 scope link')
    h12.cmd('ip route add 0.0.0.0/0 dev h12-eth0 scope link')
    h13.cmd('ip route add 0.0.0.0/0 dev h13-eth0 scope link')
    h14.cmd('ip route add 0.0.0.0/0 dev h14-eth0 scope link')
    h15.cmd('ip route add 0.0.0.0/0 dev h15-eth0 scope link')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    myNetwork()

