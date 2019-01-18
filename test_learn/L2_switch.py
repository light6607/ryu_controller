import struct
import logging

from ryu.base import app_manager
from ryu.controller import mac_to_port
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet

class L2Switch(app_manager.RyuApp):

    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]#define the version of OpenFlow

    def __init__(self, *args, **kwargs):
        super(L2Switch, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

    def add_flow(self, datapath, in_port, dst, actions):
        ofproto = datapath.ofproto

        match = datapath.ofproto_parser.OFPMatch(
            in_port = in_port, dl_dst = haddr_to_bin(dst))

        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath = datapath, match = match, cookie = 0,
            command = ofproto.OFPFC_ADD, idle_timeout = 10,hard_timeout = 30,
            priority = ofproto.OFP_DEFAULT_PRIORITY,
            flags =ofproto.OFPFF_SEND_FLOW_REM, actions = actions)

        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        dst = eth.dst
        src = eth.src

        dpid = datapath.id    #get the dpid
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %s %s %s %s", dpid, src, dst , msg.in_port)
        #To learn a mac address to avoid FLOOD next time.

        self.mac_to_port[dpid][src] = msg.in_port


        out_port = ofproto.OFPP_FLOOD

        #Look up the out_port 
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]

        ofp_parser = datapath.ofproto_parser

        actions = [ofp_parser.OFPActionOutput(out_port)]

        if out_port != ofproto.OFPP_FLOOD:
            self.add_flow(datapath, msg.in_port, dst, actions)


        #We always send the packet_out to handle the first packet.
        packet_out = ofp_parser.OFPPacketOut(datapath = datapath, buffer_id = msg.buffer_id,
            in_port = msg.in_port, actions = actions)
        datapath.send_msg(packet_out)
    #To show the message of ports' status.
    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def _port_status_handler(self, ev):
        msg = ev.msg
        reason = msg.reason
        port_no = msg.desc.port_no

        ofproto = msg.datapath.ofproto

        if reason == ofproto.OFPPR_ADD:
            self.logger.info("port added %s", port_no)
        elif reason == ofproto.OFPPR_DELETE:
            self.logger.info("port deleted %s", port_no)
        elif reason == ofproto.OFPPR_MODIFY:
            self.logger.info("port modified %s", port_no)
        else:
            self.logger.info("Illeagal port state %s %s", port_no, reason)
