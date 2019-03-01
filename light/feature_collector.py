# -*- coding: UTF-8 -*-
'''
feature_collector
'''

from ryu.base import app_manager
from ryu.controller.handler import set_ev_cls
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller import ofp_event
from ryu.lib import hub
from ryu.lib.packet import in_proto
import time
import numpy as np

filename = 'feature_test.csv'

class Feature_Collector(app_manager.RyuApp):
    '''
    
    '''
    def __init__(self,*args,**kwargs):
        super(Feature_Collector,self).__init__(*args,**kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self.feature_monitor)
        self.interval = 10
        self.Sip = []
        self.ip_ports = []

        '''
        flow(ip) feature:
        | flow_num | port_num | src_ip | packet_num |
        '''
        self.flow_features = [0,0,0]

        '''
        pkt feature:
        | time | avg_pkt_num | avg_pkt_byte | port_rate | flow_rate | sip_rate |
        '''

        self.pkt_feature = [0,0,0,0,0,0]

        '''init period status recorder'''
        self.per_pkt_num = 0
        self.per_pkt_byte = 0
        self.per_ports = 0
        self.per_flows = 0
        self.sip_num = 0

        
    def feature_monitor(self):
        while 1:
            for sw in self.datapaths.values():
                if sw.id == 1:
                    self._request_stats(sw)
            hub.sleep(self.interval)
            self._record_feature()
            self.reset()


    def reset(self):
        self.per_pkt_num = 0
        self.per_pkt_byte = 0
        self.per_ports = 0
        self.per_flows = 0
        self.sip_num = 0
        self.Sip = []
        self.ip_ports = {}

    def _record_feature(self):
        #calculate avg_pkt_num
        if self.per_flows:
            avg_pkt_num = float(self.per_pkt_num)/float(self.per_flows)
        else:
            avg_pkt_num = 0
            
        #calculate avg_pkt_byte
        if avg_pkt_num:
            avg_pkt_byte = self.per_pkt_byte/float(self.per_pkt_num)
        else:
            avg_pkt_byte = 0

        #cal port_rate
        port_rate = self.flow_features[1] / float(self.interval)


        #cal flow_rate
        flow_rate = self.flow_features[0] / float(self.interval)

        #cal sip_rate
        sip_rate = self.flow_features[2]/float(self.interval)

        self.pkt_feature[0] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.pkt_feature[1] = avg_pkt_num
        self.pkt_feature[2] = avg_pkt_byte
        self.pkt_feature[3] = port_rate
        self.pkt_feature[4] = flow_rate
        self.pkt_feature[5] = sip_rate

        #record feature
        file = open(filename,'ab')
        featureStr = ''
        n = 0
        while n < len(self.pkt_feature):
            featureStr += str(self.pkt_feature[n])+ ','
            n += 1
        file.write(featureStr+'1\n')
        print(featureStr+'\n\n')
        file.close()

        #record this period flow feature
        self.flow_features[0] = self.per_flows
        self.flow_features[1] = self.per_ports
        self.flow_features[2] = self.sip_num

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

        flow_num = 0
        pkt_num = 0
        byte = 0

        for flow in body:
            if flow.priority == 1:
                self.per_flows += 1
                self.per_pkt_num += flow.packet_count
                self.per_pkt_byte += flow.byte_count

                #mark down src ip
                src_ip = flow.match['ipv4_src']
                if src_ip not in self.Sip:
                    self.Sip.append(src_ip)
                    self.sip_num += 1

                #tcp
                if flow.match['ip_proto'] == in_proto.IPPROTO_TCP:
                    if src_ip not in self.ip_ports:
                        self.ip_ports.setdefault(src_ip,[])
                    tcp_src = flow.match['tcp_src']
                    tcp_dst = flow.match['tcp_dst']
                    if tcp_src not in self.ip_ports[src_ip]:
                        self.ip_ports[src_ip].append(tcp_src)
                        self.per_ports += 1

                    ip = flow.match['ipv4_dst']
                    if ip not in self.ip_ports:
                        self.ip_ports.setdefault(ip,[])
                    if tcp_dst not in self.ip_ports[ip]:
                        self.ip_ports[ip].append(tcp_dst)
                        self.per_ports += 1

                #udp
                if flow.match['ip_proto'] == in_proto.IPPROTO_UDP:
                    if src_ip not in self.ip_ports:
                        self.ip_ports.setdefault(src_ip,[])                        
                    udp_src = flow.match['udp_src']
                    udp_dst = flow.match['udp_dst']
                    if udp_src not in self.ip_ports[src_ip]:
                        self.ip_ports[src_ip].append(udp_src)
                        self.per_ports += 1

                    ip = flow.match['ipv4_dst']
                    if ip not in self.ip_ports:
                        self.ip_ports.set_default(ip,[])
                    if udp_dst not in self.ip_ports[ip]:
                        self.ip_ports[ip].append(udp_dst)
                        self.per_ports += 1

                

    #switch_in_handler
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self,ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        opf_parser = datapath.ofproto_parser
        self.reset()

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.datapaths[datapath.id] = datapath
                self.logger.debug('Register datapath: %16x', datapath.id)

        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                del self.datapaths[datapath.id]
                self.logger.debug('Unregister datapath: %16x', datapath.id)
    

    
    
