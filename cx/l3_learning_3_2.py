# -*- coding: UTF-8 -*-
from ryu.lib.packet import *
from ryu.lib.packet import in_proto
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import ether_types
from ryu.lib.packet import tcp
from ryu.lib.packet import udp

#  idle_timeout



class IcmpResponder(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    def __init__(self, *args, **kwargs):
        super(IcmpResponder, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.ip_to_port = {}
        self.idle_timeout = 10


    # switch IN
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def _switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        # install the table-miss flow entry
        match = ofp_parser.OFPMatch()
        actions = [ofp_parser.OFPActionOutput(
            ofproto.OFPP_CONTROLLER,
            ofproto.OFPCML_NO_BUFFER
        )]
        self.add_flow(datapath, 0, match, actions)

    # add flow
    def add_flow(self,datapath, priority, match, actions, idle_timeout = 0):
        #add a flow entry and install it into datapath
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        #construct a flow_mod msg and send it
        inst = [ofp_parser.OFPInstructionActions(
            ofproto.OFPIT_APPLY_ACTIONS,
            actions)]

        mod = ofp_parser.OFPFlowMod(
            datapath = datapath,
            priority = priority,
            match = match,
            instructions = inst,
            idle_timeout = self.idle_timeout
        )
        datapath.send_msg(mod)

    # packet_in handler
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        #mac_address_record
        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})
        self.ip_to_port.setdefault(dpid, {})
        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port
        #mac learning
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD
        actions = [parser.OFPActionOutput(out_port)]
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
        #mac learn end


        #如果是arp报文，记录源ip的进端口
        pkt_arp = pkt.get_protocol(arp.arp)
        if pkt_arp:
            arp_ip_src = pkt_arp.src_ip
            arp_ip_dst = pkt_arp.dst_ip

            self.ip_to_port[dpid][arp_ip_src] = in_port
            if arp_ip_dst in self.ip_to_port[dpid]:
                out_port = self.ip_to_port[dpid][arp_ip_dst]
            else:
                out_port = ofproto.OFPP_FLOOD

            actions = [parser.OFPActionOutput(out_port)]

            out = parser.OFPPacketOut(
                datapath=datapath,
                buffer_id=msg.buffer_id,
                in_port=in_port,
                actions=actions,
                data=msg.data
            )
            datapath.send_msg(out)
            return

        #如果是ipv4报文，则要对报文进行分类，分出icmp、tcp、udp报文，并执行相应的流表下发规则
        pkt_ipv4 = pkt.get_protocol(ipv4.ipv4)
        #if pkt_ipv4:
        if pkt_ipv4:

            ip4_src = pkt_ipv4.src
            ip4_dst = pkt_ipv4.dst
            ip4_pro = pkt_ipv4.proto

            self.ip_to_port[dpid][ip4_src] = in_port

            if ip4_dst in self.ip_to_port[dpid]:
                out_port = self.ip_to_port[dpid][ip4_dst]
            else:
                out_port = 5#ofproto.OFPP_FLOOD #

            actions = [parser.OFPActionOutput(out_port)]

            if out_port != ofproto.OFPP_FLOOD:
                # icmp
                if ip4_pro == in_proto.IPPROTO_ICMP:
                    #if dpid == 1:
                    #    print('icmp', self.ip_to_port[dpid])
                    match = parser.OFPMatch(
                        #in_port=in_port,
                        eth_type=ether_types.ETH_TYPE_IP,
                        ip_proto = ip4_pro,
                        ipv4_src=ip4_src, ipv4_dst=ip4_dst
                    )
                    self.add_flow(datapath, 1, match, actions, self.idle_timeout)
                    return

                # tcp
                if ip4_pro == in_proto.IPPROTO_TCP:
                    #print(pkt_ipv4)
                    #if dpid == 1:
                    #    print('tcp', self.ip_to_port[dpid])

                    pkt_tcp = pkt.get_protocol(tcp.tcp)
                    tcp_src_port = pkt_tcp.src_port
                    tcp_dst_port = pkt_tcp.dst_port

                    match = parser.OFPMatch(
                        #in_port=in_port,
                        eth_type=ether_types.ETH_TYPE_IP,
                        ip_proto=ip4_pro,
                        ipv4_src=ip4_src, ipv4_dst=ip4_dst,
                        tcp_src = tcp_src_port,
                        tcp_dst = tcp_dst_port
                    )
                    self.add_flow(datapath, 1, match, actions, self.idle_timeout)
                    return

                # udp
                if ip4_pro == in_proto.IPPROTO_UDP:
                    #if dpid == 1:
                    #    print('udp', self.ip_to_port[dpid])

                    pkt_udp = pkt.get_protocol(udp.udp)
                    udp_src_port = pkt_udp.src_port
                    udp_dst_port = pkt_udp.dst_port

                    match = parser.OFPMatch(
                        #in_port=in_port,
                        eth_type=ether_types.ETH_TYPE_IP,
                        ip_proto=ip4_pro,
                        ipv4_src=ip4_src, ipv4_dst=ip4_dst,
                        udp_src=udp_src_port,
                        udp_dst=udp_dst_port
                    )
                    self.add_flow(datapath, 1, match, actions, self.idle_timeout)
                    return

            out = parser.OFPPacketOut(
                datapath=datapath,
                buffer_id=msg.buffer_id,
                in_port=in_port,
                actions=actions,
                data=msg.data
            )
            datapath.send_msg(out)
            return


