from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class PacketMonitor(object):

    def __init__(self, connection):
        self.connection = connection
        connection.addListeners(self)
        log.info("Switch connected: %s", connection)

    def _handle_PacketIn(self, event):
        packet = event.parsed

        print("\n========== PACKET ==========")
        print("Source MAC      :", packet.src)
        print("Destination MAC :", packet.dst)
        print("Switch DPID     :", event.dpid)
        print("Ingress Port    :", event.port)
        print("============================")

        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        self.connection.send(msg)

def launch():
    def start_switch(event):
        PacketMonitor(event.connection)

    core.openflow.addListenerByName("ConnectionUp", start_switch)
