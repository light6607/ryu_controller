'''
random send packet
'''
from scapy.all import *
import random
import time
from port_and_ip import *

def port_loader(switch = "s2"):
    if switch == "s2":
        return k2[random.randint(0, len(k2)-1)]
    elif switch == "s3":
        return k3[random.randint(0, len(k3)-1)]
    elif switch == "s4":
        return k4[random.randint(0, len(k4)-1)]
    elif switch == "s1":
        return k1[random.randint(0, len(k1)-1)] 
    else:
        return 80

class RandomSend():
    def __init__(self, args):
        self.switch = args

    def getDstAddress(self):
        if self.switch == 's1':
            return s1_dst_ip[random.randint(0, len(s1_dst_ip)-1)]
        elif self.switch == 's2':
            return s2_dst_ip[random.randint(0, len(s2_dst_ip)-1)]
        elif self.switch == 's3':
            return s3_dst_ip[random.randint(0, len(s3_dst_ip)-1)]
        elif self.switch == 's4':
            return s4_dst_ip[random.randint(0, len(s4_dst_ip)-1)]
        else :
            return all[random.randint(0, len(all)-1)]

    def getSrcAddress(self):
        if self.switch == 's1':
            return s1_all_ip[random.randint(0, len(s1_all_ip)-1)]
        elif self.switch == 's2':
            return s2_all_ip[random.randint(0, len(s2_all_ip)-1)]
        elif self.switch == 's3':
            return s3_all_ip[random.randint(0, len(s3_all_ip)-1)]
        elif self.switch == 's4':
            return s4_all_ip[random.randint(0, len(s4_all_ip)-1)]
        else:
            return all[random.randint(0, len(all)-1)]

    def getPort(self):
        return port_loader(self.switch)

    def sendicmp(self, data='hello_world'):
        src_ip = self.getSrcAddress()
        #src_ip = '10.0.0.13'
        dst_ip = self.getDstAddress()
        #dst_ip = '123.0.0.2'
        while dst_ip == src_ip:
            dst_ip = self.getAddress()
        pkt=IP(src=src_ip,dst=dst_ip)/ICMP()
        #pkt.show()
        send(pkt,count=random.randint(1,5))

    def sendtcp(self, data='hello_world'):
        src_ip = self.getSrcAddress()
        #src_ip = '10.0.0.13'
        dst_ip = self.getDstAddress()
        #dst_ip = '123.0.0.2'
        src_port = self.getPort()
        dst_port = self.getPort()
        while dst_ip == src_ip:
            dst_ip = self.getAddress()
        pkt = IP(src=src_ip, dst=dst_ip) / fuzz(TCP(sport=src_port, dport=dst_port)) /data
        #pkt.show()
        send(pkt,count=random.randint(1,5))

    def sendudp(self, data='hello_world'):
        src_ip = self.getSrcAddress()
        #src_ip = '10.0.0.13'
        dst_ip = self.getDstAddress()
        #dst_ip = '123.0.0.2'
        src_port = self.getPort()
        dst_port = self.getPort()
        while dst_ip == src_ip:
            dst_ip = self.getAddress()
        pkt = IP(src=src_ip, dst=dst_ip) / fuzz(UDP(sport=src_port, dport=dst_port)) / data
        #pkt.show()
        send(pkt,count=random.randint(1,5))

    def generate_random_str(self, randomlength=16):
        random_str = ''
        base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
        length = len(base_str) - 1
        for i in range(randomlength):
            random_str += base_str[random.randint(0, length)]
        return random_str

    def _send(self):
        n = random.randint(0,99)
        length = random.randint(18,600)
        data = self.generate_random_str(length)

        #tcp
        if n < 84:
            self.sendtcp(data)
        elif n < 94:
            self.sendudp(data)
        else :
            self.sendicmp(data)

if __name__ == '__main__':
    print(conf.iface)
    conf.iface = 's3'
    print(conf.iface)
    rs = RandomSend("s3")
    while True:
        rs._send()
        time.sleep(0.5)
