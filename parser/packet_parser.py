from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.tcp import tcp
from pox.lib.packet.udp import udp


class PacketParser:

    def parse(self, packet):

        data = {}

        # ------------------------
        # Ethernet
        # ------------------------

        eth = packet.find('ethernet')

        if eth:
            data["src_mac"] = str(eth.src)
            data["dst_mac"] = str(eth.dst)

        # ------------------------
        # IPv4
        # ------------------------

        ip = packet.find('ipv4')

        if ip:

            data["src_ip"] = str(ip.srcip)
            data["dst_ip"] = str(ip.dstip)

            data["protocol"] = ip.protocol

            data["packet_length"] = ip.iplen

            data["ttl"] = ip.ttl

        # ------------------------
        # TCP
        # ------------------------

        tcp_packet = packet.find('tcp')

        if tcp_packet:

            data["transport"] = "TCP"

            data["src_port"] = tcp_packet.srcport

            data["dst_port"] = tcp_packet.dstport

            data["window"] = tcp_packet.win

            data["ack"] = tcp_packet.ACK

            data["syn"] = tcp_packet.SYN

            data["fin"] = tcp_packet.FIN

            data["rst"] = tcp_packet.RST

        # ------------------------
        # UDP
        # ------------------------

        udp_packet = packet.find('udp')

        if udp_packet:

            data["transport"] = "UDP"

            data["src_port"] = udp_packet.srcport

            data["dst_port"] = udp_packet.dstport

        # ------------------------

        if "transport" not in data:

            data["transport"] = "OTHER"

        return data
