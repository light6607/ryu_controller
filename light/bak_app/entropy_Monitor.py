# -*- coding: UTF-8 -*-
'''
monitor entropy change
'''

from ryu.base import app_manager
from ryu.controller.handler import set_ev_cls
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller import ofp_event
from ryu.lib import hub
from ryu.lib.packet import in_proto
import time
import numpy as np
import math

threshhold = 0.5

class entropy_monitor(app_manager.RyuApp):

    def __init__(self,*args,**kwargs):
        super(entropy_monitor,self).__init__(*args,**kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self.entropy_alert)
        self.interval = 10
        self.SwIp = []
        self.ip_ports = {}
        
        #src_ip_pkt_count:{'src_ip':count}
        self.src_ip_pkt_total = {}
        #pri_src_ip_pkt_count:{'sip':count}
        self.src_ip_pkt_pri = {}
        self.src_ip_increase = {}
        self.increase_pkt_count = 0
        
        
        pass


    def entropy_alert(self):
        while 1:
            self.increase_pkt_count = 0
            for dp in self.datapaths.values():
                if dp.id == 1:
                    self._request_stats(dp)

            file = open('entropy_log.txt','ab')
            file.write('before calculate:\n')
            file.write(str(self.src_ip_pkt_total)+'\n')            
            file.write(str(self.src_ip_pkt_pri)+'\n')
            file.write('\n')
            file.close()
            #calculate src_increase
            for ip in self.src_ip_pkt_total:
                if ip not in self.src_ip_pkt_pri:
                    pkt_count = self.src_ip_pkt_total[ip]
                    self.src_ip_pkt_pri.setdefault(ip,pkt_count)
                    self.src_ip_increase.setdefault(ip,pkt_count)
                    self.increase_pkt_count += pkt_count
                else:
                    pkt_count = self.src_ip_pkt_total[ip]- self.src_ip_pkt_pri[ip]
                    self.src_ip_pkt_pri[ip] = self.src_ip_pkt_total[ip]
                    self.src_ip_increase.setdefault(ip,pkt_count)
                    self.increase_pkt_count += pkt_count

            #calculate entropy
            entropy = self.cal_entropy()

            #if entropy < threshhold, if 5 windows true:alert; else:pass
            file = open('entropy_log.txt','ab')
            file.write('after cal')
            file.write(str(entropy)+'\n')
            file.write(str(self.src_ip_pkt_total)+'\n')            
            file.write(str(self.src_ip_pkt_pri)+'\n')
            file.write(str(self.increase_pkt_count)+'\n')
            file.write('\n')
            file.close()

            hub.sleep(self.interval)
        

    def reset(self):
        pass
    
    #entropy calculator
    def cal_entropy(self):
        entropy = 0
        P_src = []
        for ip in self.src_ip_increase:
            p = float(self.src_ip_increase[ip])/float(self.increase_pkt_count)
            P_src.append(p)

        for i in P_src:
            entropy += (-math.log(2,i))

        return entropy

    #switch in handle  emm,this seems useless
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self,ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        self.reset()

    #get dp info
    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.datapaths[datapath.id] = datapath
                self.logger.debug('New datapath in: %16x', datapath.id)

        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                del self.datapaths[datapath.id]
                self.logger.debug('A datapath die: %16x', datapath.id)

    #request stats
    def _request_stats(self,datapath):
        self.logger.debug('sending stats request to datapath:%16x',datapath.id)
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser


        #send request msg
        req = ofp_parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

    #stats reply handler
    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def stats_reply_handler(self,ev):
        body = ev.msg.body

        for flow in body:
            if flow.priority == 1:
                ip = flow.match['ipv4_src']
                pkt_count = flow.packet_count
                if ip not in self.src_ip_pkt_total:
                    self.src_ip_pkt_total.setdefault(ip,pkt_count)
                else:
                    self.src_ip_pkt_total[ip] += pkt_count

            
