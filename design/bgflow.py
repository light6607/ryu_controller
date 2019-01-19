# -*- coding:utf-8 -*-

'''
This file is used to generate background flow
'''

from scapy.all import *
import random
import time
from ip_port_list import *
import threading

def get_port(switch = 'Sw1'):
    if switch == 'Sw1':
        return k1[random.randint(0,len(k1)-1)]
    elif switch == 'Sw2':
        return k2[random.randint(0,len(k2)-1)]
    elif switch == 'Sw3':
        return k3[random.randint(0,len(k3)-1)]
    elif switch == 'Sw4':
        return k4[random.randint(0,len(k4)-1)]
    elif switch == 'Sw5':
        return k5[random.randint(0,len(k5)-1)]
    else:
        return 80

class SwBGFlow():
    def __init__(self,args):
        self.switch = args

    def getDstAdd(self):
        if self.switch == 'Sw1':
            return s1_dst_list[random.randint(0,len(s1_dst_list)-1)]
        elif self.switch == 'Sw2':
            return s2_dst_list[random.randint(0,len(s2_dst_list)-1)]
        elif self.switch == 'Sw3':
            return s3_dst_list[random.randint(0,len(s3_dst_list)-1)]
        elif self.switch == 'Sw4':
            return s4_dst_list[random.randint(0,len(s4_dst_list)-1)]
        elif self.switch == 'Sw5':
            return s5_dst_list[random.randint(0,len(s5_dst_list)-1)]

    def getSrcAdd(self):
        if self.switch == 'Sw1':
            return s1_ip_list[random.randint(0,len(s1_ip_list)-1)]
        elif self.switch == 'Sw2':
            return s2_ip_list[random.randint(0,len(s2_ip_list)-1)]
        elif self.switch == 'Sw3':
            return s3_ip_list[random.randint(0,len(s3_ip_list)-1)]
        elif self.switch == 'Sw4':
            return s4_ip_list[random.randint(0,len(s4_ip_list)-1)]
        elif self.switch == 'Sw5':
            return s5_ip_list[random.randint(0,len(s5_ip_list)-1)]

    def getPort(self):
        return get_port(self.switch)

    def sendTcpPkt(self,data='SDN Background_Flow'):
        src_ip = self.getSrcAdd()
        dst_ip = self.getDstAdd()
        src_port = self.getPort()
        dst_port = self.getPort()

        pkt = IP(src=src_ip,dst=dst_ip) / fuzz(TCP(sport=src_port,dport=dst_port)) / data

        pktCount = random.randint(1,5)
        print(self.switch+' sending '+str(pktCount)+' Tcp Packets')
        send(pkt,count=pktCount)
        
    def sendUdpPkt(self,data='SDN Background_Flow'):
        src_ip = self.getSrcAdd()
        dst_ip = self.getDstAdd()
        src_port = self.getPort()
        dst_port = self.getPort()

        pkt = IP(src=src_ip,dst=dst_ip) / fuzz(TCP(sport=src_port,dport=dst_port)) / data

        pktCount = random.randint(1,5)
        print(self.switch+' sending '+str(pktCount)+' Udp Packets')
        send(pkt,count=pktCount)

    def sendIcmpPkt(self,data='SDN Background_Flow'):
        src_ip = self.getSrcAdd()
        dst_ip = self.getDstAdd()

        pkt = IP(src=src_ip,dst=dst_ip) / ICMP()

        pktCount = random.randint(1,5)
        print(self.switch+' sending '+str(pktCount)+' Icmp Packets')
        send(pkt,count=pktCount)

    def msg_Generator(self,msgLength=16):
        msg=''
        baseMsgStr = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789!@#$%^&*()_+=-,./<>?;[]{}~'
        length = len(baseMsgStr)
        for i in range(msgLength):
            msg += baseMsgStr[random.randint(0,length-1)]
        return msg


    def sendMsg(self):
        pktType = random.randint(0,99)
        length = random.randint(18,600)
        data = self.msg_Generator(length)

        if pktType < 84:
            self.sendTcpPkt(data)
        elif pktType < 94:
            self.sendUdpPkt(data)
        else:
            self.sendIcmpPkt(data)


class BGFlowThread(threading.Thread):
    def __init__(self,threadID,name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        if name == 'Sw1':
            self.BGFlow = SwBGFlow('Sw1')
        elif name == 'Sw2':
            self.BGFlow = SwBGFlow('Sw2')
        elif name == 'Sw3':
            self.BGFlow = SwBGFlow('Sw3')
        elif name == 'Sw4':
            self.BGFlow = SwBGFlow('Sw4')
        elif name == 'Sw5':
            self.BGFlow = SwBGFlow('Sw5')

    def run(self):
        while True:
            self.BGFlow.sendMsg()
            sleep_time = random.random()
            print(sleep_time)
            time.sleep(sleep_time)

 
    

if __name__ == '__main__':
    print(conf.iface)
    #创建线程
    Sw1 = BGFlowThread(1,'Sw1')
    Sw2 = BGFlowThread(1,'Sw2')
    Sw3 = BGFlowThread(1,'Sw3')
    Sw4 = BGFlowThread(1,'Sw4')
    Sw5 = BGFlowThread(1,'Sw5')

    #开启线程
    Sw1.start()
    Sw2.start()
    Sw3.start()
    Sw4.start()
    Sw5.start()
    Sw1.join()
    Sw2.join()
    Sw3.join()
    Sw4.join()
    Sw5.join()
    
