# -*- coding: UTF-8 -*-
from ryu.base import app_manager
from ryu.controller.handler import set_ev_cls
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller import ofp_event
from ryu.lib import hub
from ryu.lib.packet import in_proto
import time
import numpy as np


filename = "collect.log"


class MyMonitor13(app_manager.RyuApp):
    '''string for disription'''

    def __init__(self, *args, **kwargs):
        super(MyMonitor13, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)
        self.sleep_time = 10# sleep time
        self.Sip = []
        self.ip_ports = {}
        '''
        records:
        | flow_num | port_num | src_ip | packet_num |

        '''
        self.records = [0, 0, 0]
        '''
        rcd:
        | time | avg_pkt_num | avg_pkt_byte | chg_ports | chg_flow | chg_sip |
        '''
        self.rcd = [0, 0, 0, 0, 0, 0]
        self.temp_pkt_num = 0
        self.temp_pkt_byte = 0
        self.temp_ports = 0
        self.temp_flows = 0
        self.sip_num = 0


    # send request msg periodically
    def _monitor(self):
        while 1:
            for dp in self.datapaths.values():
                # self._request_stats(dp)
                # only s1
                if dp.id == 1:
                    self._request_stats(dp)
            hub.sleep(self.sleep_time)  # sleep N second.
            self._records()
            self.reset()

    def reset(self):
        self.temp_pkt_num = 0
        self.temp_pkt_byte = 0
        self.temp_ports = 0
        self.temp_flows = 0
        self.sip_num = 0
        self.Sip = []
        self.ip_ports = {}

    def _records(self):
        if self.temp_flows:
            avg_pkt_num = float(self.temp_pkt_num) / float(self.temp_flows)
        else:
            avg_pkt_num = 0
        # 流包平均比特数
        if avg_pkt_num:
            avg_pkt_byte = self.temp_pkt_byte / float(self.temp_flows)
        else:
            avg_pkt_byte = 0

        # 端口
        for ip in self.ip_ports:
            self.temp_ports += len(self.ip_ports[ip])
        # chg_ports = self.temp_ports - self.records[1]
        chg_ports = self.records[1] / float(self.sleep_time)
        # print('chg_ports:', chg_ports)

        # 流增长率
        # delta_flow = self.temp_flows - self.records[0]
        delta_flow = self.records[0] / float(self.sleep_time)
        chg_flow = delta_flow  # / self.sleep_time
        # print('chg_flow', chg_flow)

        # 源ip增速
        self.sip_num = len(self.Sip)
        # delta_sip = self.sip_num - self.records[2]
        delta_sip = self.records[2] / float(self.sleep_time)
        chg_sip = delta_sip  # / self.sleep_time
        # print('chg_sip', chg_sip)

        self.rcd[0] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.rcd[1] = avg_pkt_num
        self.rcd[2] = avg_pkt_byte
        self.rcd[3] = chg_ports
        self.rcd[4] = chg_flow
        self.rcd[5] = chg_sip

        file = open(filename, 'ab')  # a is like >> , and b is byte
        strs = ''
        n = 0
        while n < len(self.rcd):
            #print(self.rcd[n])
            strs += str(self.rcd[n]) + " "
            n += 1
        # print(strs)
        file.write(strs + '\n')
        file.close()
        self.records[0] = self.temp_flows
        self.records[1] = self.temp_ports
        self.records[2] = self.sip_num

    # switch IN
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def _switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        self.reset()
        # install the table-miss flow entry

    # get datapath info
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



    # send stats request msg to datapath
    def _request_stats(self, datapath):
        self.logger.debug('send stats request to datapath: %16x', datapath.id)
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        # send flow stats request msg
        req = ofp_parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

    # handle the flow entries stats reply msg
    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body

        flow_num = 0
        pktsNum = 0
        byte_counts = 0
        for flow in body:
            if flow.priority == 1:
                #print (flow)
                #流
                self.temp_flows += 1
                #比特数
                self.temp_pkt_byte += flow.byte_count
                #包数
                self.temp_pkt_num += flow.packet_count
                #端口增长
                #tcp:  tcp_src, tcp_dst
                if flow.match['ip_proto'] == in_proto.IPPROTO_TCP:
                    ip = flow.match['ipv4_src']
                    if ip not in self.ip_ports:
                        self.ip_ports.setdefault(ip, [])
                    tcp_src = flow.match['tcp_src']
                    tcp_dst = flow.match['tcp_dst']
                    if tcp_src not in self.ip_ports[ip]:
                        self.ip_ports[ip].append(tcp_src)
                    ip = flow.match['ipv4_dst']
                    if ip not in self.ip_ports:
                        self.ip_ports.setdefault(ip, [])
                    if tcp_dst not in self.ip_ports[ip]:
                        self.ip_ports[ip].append(tcp_dst)
                #udp: udp_src, udp_dst  // udp lai hui
                if flow.match['ip_proto'] == in_proto.IPPROTO_UDP:
                    #print(flow)
                    ip = flow.match['ipv4_src']
                    if ip not in self.ip_ports:
                        self.ip_ports.setdefault(ip,[])
                    udp_src = flow.match['udp_src']
                    udp_dst = flow.match['udp_dst']
                    if udp_src not in self.ip_ports[ip]:
                        self.ip_ports[ip].append(udp_src)
                    ip = flow.match['ipv4_dst']
                    if ip not in self.ip_ports:
                        self.ip_ports.setdefault(ip,[])
                    if udp_dst not in self.ip_ports[ip]:
                        self.ip_ports[ip].append(udp_dst)
                #源ip
                Src_ip = flow.match['ipv4_src']
                if Src_ip not in self.Sip:
                    self.Sip.append(Src_ip)
