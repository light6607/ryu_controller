# -*- coding:utf-8 -*-

from ryu.lib.packet import *
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import ether_types
from ryu.lib.packet import tcp
from ryu.lib.packet import udp

class SwitchModule(app_manager.RyuApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self,*args,**kwargs):
        super(SwitchModule,self).__init__(*args,**kwargs)
        self.mac_to_port = {}
        self.ip_to_port = {}
        self.idle_timeout = 10


    #add_flow
    def add_flow(self,datapath,priority,match,actions,idle_timeout=0):
        #add flow-entry and install it to datapath
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        #construct flow mod and send to datapath
        inst = [ofp_parser.OFPInstructionActions(
                ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = ofp_parser.OFPFlowMod(
                datapath = datapath,
                priority = priority,
                match = match,
                instructions = inst,
                idle_timeout = self.idle_timeout)

        datapath.send_msg(mod)

    #New Switch
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_feature_handler(self,ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        #install table-miss flow entry
        match = ofp_parser.OFPMatch()
        actions = [ofp_parser.OFPActionOutput(
                    ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]

        self.add_flow(datapath,0,match,actions)


    #packet_in handler
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self,ev):

        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            #ignore
            return

        dst = eth.dst
        src = eth.src

        #init dpid route
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid,{})
        self.ip_to_port.setdefault(dpid,{})

        #learn MAC
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [ofp_parser.OFPActionOutput(out_port)]

        data = None

        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = ofp_parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

        #distinguish protocol type
        pkt_arp = pkt.get_protocol(arp.arp)
        pkt_ipv4 = pkt.get_protocol(ipv4.ipv4)

        #arp msg
        if pkt_arp:
            
            arp_ip_src = pkt_arp.src_ip
            arp_ip_dst = pkt_arp.dst_ip

            self.ip_to_port[dpid][arp_ip_src] = in_port
            if arp_ip_dst in self.ip_to_port[dpid]:
                out_port = self.ip_to_port[dpid][arp_ip_dst]
            else:
                out_port = ofproto.OFPP_FLOOD

            actions = [ofp_parser.OFPActionOutput(out_port)]

            out = ofp_parser.OFPPacketOut(
                datapath = datapath,
                buffer_id = msg.buffer_id,
                in_port = in_port,
                actions = actions,
                data = msg.data)

            datapath.send_msg(out)
            return

        #if ipv4, distinguish icmp/tcp/udp
        if pkt_ipv4:        

            ipv4_src = pkt_ipv4.src
            ipv4_dst = pkt_ipv4.dst
            ipv4_proto = pkt_ipv4.proto

            self.ip_to_port[dpid][ipv4_src] = in_port

            if ipv4_dst in self.ip_to_port[dpid]:
                out_port = self.ip_to_port[dpid][ipv4_dst]
            else:
                out_port = ofproto.OFPP_FLOOD
            
            actions = [ofp_parser.OFPActionOutput(out_port)]

            #There's route in ip_to_port, add_flow
            if out_port != ofproto.OFPP_FLOOD:
                #icmp packet
                if ipv4_proto == in_proto.IPPROTO_ICMP:
                    match = ofp_parser.OFPMatch(
                        eth_type=ether_types.ETH_TYPE_IP,
                        ip_proto=ipv4_proto,
                        ipv4_src=ipv4_src, ipv4_dst=ipv4_dst)

                    self.add_flow(datapath,1,match,actions,self.idle_timeout)
                    return

                #tcp packet
                if ipv4_proto == in_proto.IPPROTO_TCP:
                    pkt_tcp = pkt.get_protocol(tcp.tcp)
                    tcp_src_port = pkt_tcp.src_port
                    tcp_dst_port = pkt_tcp.dst_port

                    match = ofp_parser.OFPMatch(
                        eth_type=eth_types.ETH_TYPE_IP,
                        ip_proto=ipv4_proto,
                        ipv4_src=ipv4_src,ipv4_dst=dst,
                        tcp_src=tcp_src_port,
                        tcp_dst=tcp_dst_port)

                    self.add_flow(datapath,1,match,actions,self.idle_timeout)
                    return

                #udp packet
                if ipv4_proto == in_proto.IPPROTO_UDP:

                    pkt_udp = pkt.get_protocol(udp.udp)
                    udp_src_port = pkt_udp.src_port
                    udp_dst_port = pkt_udp.dst_port

                    match = ofp_parser.OFPMatch(
                        eth_type=ether_type.ETH_TYPE_IP,
                        ip_proto=ipv4_proto,
                        ipv4_src=ipv4_src,ipv4_dst=ipv4_dst,
                        udp_src=udp_src_port,udp_dst=udp_dst_port)

                    self.add_flow(datapath,1,match,actions,self.idle_timeout)
                    return

            out = ofp_parser.OFPPacketOut(
                datapath=datapath,
                buffer_id=msg.buffer_id,
                in_port=in_port,
                actions=actions,
                data=msg.data)

            datapath.send_msg(out)

            return
