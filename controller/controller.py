import sys
import os

PROJECT_ROOT = os.path.expanduser("~/Blockchain_FL_IDS")

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from pox.core import core
import pox.openflow.libopenflow_01 as of

from parser.packet_parser import PacketParser
from fl.feature_generator import FeatureGenerator
from fl.predictor import Predictor
from security.decision_engine import DecisionEngine
from security.quarantine import QuarantineManager
from metadata.metadata_generator import MetadataGenerator
from blockchain_client.client import BlockchainClient
from flow.flow_statistics import FlowStatistics

log = core.getLogger()


class SDNController(object):

    def __init__(self):

        core.openflow.addListeners(self)

        self.parser = PacketParser()
        self.feature_generator = FeatureGenerator()
        self.predictor = Predictor()
        self.decision_engine = DecisionEngine()
        self.quarantine = QuarantineManager()
        self.metadata_generator = MetadataGenerator()
        self.blockchain = BlockchainClient()
        self.flow_statistics = FlowStatistics()

        # Network Statistics
        self.total_packets = 0
        self.packet_id = 0
        self.normal_packets = 0
        self.attack_packets = 0
        self.allowed_packets = 0
        self.blocked_packets = 0

        print("\n" + "=" * 60)
        print(" SDN CONTROLLER STARTED ")
        print("=" * 60 + "\n")

    def _handle_ConnectionUp(self, event):
        print("\n" + "=" * 60)
        print(f" SWITCH CONNECTED  |  DPID: {event.dpid}")
        print("=" * 60 + "\n")

        msg = of.ofp_flow_mod()
        msg.priority = 0
        msg.actions.append(
            of.ofp_action_output(port=of.OFPP_CONTROLLER)
        )
        event.connection.send(msg)

        print("Default flow installed. Waiting for traffic...\n")

    def _handle_PacketIn(self, event):

        packet = event.parsed
        self.packet_id += 1

        if not packet.parsed:
            return

        parsed_packet = self.parser.parse(packet)

        # Ignore LLDP packets silently
        if packet.find('lldp'):
            return

        # Forward ARP packets quietly (one-line note, no block)
        if "src_ip" not in parsed_packet:
            print(f"[ARP #{self.packet_id}] {parsed_packet.get('src_mac')} -> {parsed_packet.get('dst_mac')} (flooded)")

            msg = of.ofp_packet_out()
            msg.data = event.ofp
            msg.actions.append(
                of.ofp_action_output(port=of.OFPP_FLOOD)
            )
            event.connection.send(msg)
            return

        # Check Quarantine
        if self.quarantine.is_blocked(parsed_packet["src_ip"]):
            print(f"[BLOCKED #{self.packet_id}] Dropped — {parsed_packet['src_ip']} is quarantined")
            return

        # Flow Statistics
        flow_stats = self.flow_statistics.update(parsed_packet)

        # Feature Generation + Prediction
        features = self.feature_generator.generate(parsed_packet, flow_stats)
        result = self.predictor.predict(features)

        prediction = result["prediction"]
        probability = result["probability"]
        confidence = result["confidence"]

        self.total_packets += 1

        if prediction == "NORMAL":
            self.normal_packets += 1
        else:
            self.attack_packets += 1

        decision = self.decision_engine.inspect(prediction)

        # ================== SINGLE CLEAN SUMMARY BLOCK ==================
        status_icon = "ATTACK" if decision == "BLOCK" else "NORMAL"

        print("\n" + "-" * 60)
        print(f"PACKET #{self.packet_id}  |  {status_icon}")
        print("-" * 60)
        print(f"  Src IP / Port     : {parsed_packet.get('src_ip')}:{parsed_packet.get('src_port')}")
        print(f"  Dst IP / Port     : {parsed_packet.get('dst_ip')}:{parsed_packet.get('dst_port')}")
        print(f"  Transport         : {parsed_packet.get('transport')}   "
              f"(SYN={parsed_packet.get('syn')} ACK={parsed_packet.get('ack')} "
              f"FIN={parsed_packet.get('fin')} RST={parsed_packet.get('rst')})")
        print(f"  Flow packet count : {flow_stats.get('packet_count')}   "
              f"| Duration(us): {flow_stats.get('flow_duration'):.0f}   "
              f"| Pkts/sec: {flow_stats.get('packets_per_second'):.2f}")
        print(f"  Prediction        : {prediction}   "
              f"| Probability: {probability:.6f}   | Confidence: {confidence:.2f}%")
        print(f"  Decision          : {decision}")

        # Quarantine
        if decision == "BLOCK":
            self.quarantine.quarantine(parsed_packet["src_ip"])
            print(f"  >>> Device {parsed_packet['src_ip']} added to quarantine")

        # Metadata
        metadata = self.metadata_generator.generate(
            parsed_packet, decision, prediction, probability, confidence
        )

        # Blockchain Logging (only on BLOCK, to avoid stalling under flood load)
        receipt = None
        if decision == "BLOCK":
            receipt = self.blockchain.send(metadata)

        if receipt:
            tx_hash = receipt.transactionHash.hex()
            block_number = receipt.blockNumber
            metadata["transaction_hash"] = tx_hash
            metadata["block_number"] = block_number
            self.metadata_generator.update_blockchain_info(tx_hash, block_number)
            print(f"  >>> Blockchain TX  : {tx_hash}")
            print(f"  >>> Block Number   : {block_number}")

        # Controller Action
        if decision == "ALLOW":
            self.allowed_packets += 1
            msg = of.ofp_packet_out()
            msg.data = event.ofp
            msg.actions.append(
                of.ofp_action_output(port=of.OFPP_FLOOD)
            )
            event.connection.send(msg)
            print(f"  Action            : Packet forwarded")

        elif decision == "BLOCK":
            self.blocked_packets += 1
            print(f"  Action            : Packet BLOCKED")

        else:
            print(f"  Action            : Packet buffered")

        print("-" * 60)

        # Periodic summary every 100 packets (instead of every single packet)
        if self.total_packets % 100 == 0:
            print("\n" + "=" * 60)
            print(" NETWORK SUMMARY (running totals)")
            print("=" * 60)
            print(f"  Packets Processed : {self.total_packets}")
            print(f"  Normal / Attack   : {self.normal_packets} / {self.attack_packets}")
            print(f"  Allowed / Blocked : {self.allowed_packets} / {self.blocked_packets}")
            print("=" * 60 + "\n")


def launch():
    core.registerNew(SDNController)
