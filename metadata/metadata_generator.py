import os
import json
from datetime import datetime


class MetadataGenerator:

    def __init__(self):

        self.output_dir = os.path.expanduser(
            "~/Blockchain_FL_IDS/metadata/generated_metadata"
        )

        os.makedirs(self.output_dir, exist_ok=True)

        self.history_file = os.path.expanduser(
            "~/Blockchain_FL_IDS/metadata/metadata_history.json"
        )

        if not os.path.exists(self.history_file):
            with open(self.history_file, "w") as file:
                json.dump([], file, indent=4)

        self.packet_id = 0

    def generate(
        self,
        packet,
        decision,
        prediction,
        probability,
        confidence
    ):

        self.packet_id += 1

        metadata = {
            "controller_id": "SDN_CONTROLLER_1",
            "packet_id": self.packet_id,
            "timestamp": str(datetime.now()),

            "src_mac": packet.get("src_mac"),
            "dst_mac": packet.get("dst_mac"),

            "src_ip": packet.get("src_ip"),
            "dst_ip": packet.get("dst_ip"),

            "protocol": packet.get("protocol"),
            "transport": packet.get("transport"),

            "packet_length": packet.get("packet_length"),
            "ttl": packet.get("ttl"),

            "prediction": prediction,
            "probability": probability,
            "confidence": confidence,

            "decision": decision,

            "transaction_hash": None,
            "block_number": None
        }

        try:
            with open(self.history_file, "r") as file:
                history = json.load(file)

        except Exception:
            history = []

        history.append(metadata)

        with open(self.history_file, "w") as file:
            json.dump(history, file, indent=4)

        print("\n========================================")
        print("Metadata Generated")
        print("Packet ID :", self.packet_id)
        print("Saved To  :", self.history_file)
        print("========================================")

        return metadata

    def update_blockchain_info(self, transaction_hash, block_number):
        """
        Update the latest metadata record with blockchain details.
        """

        try:

            with open(self.history_file, "r") as file:
                history = json.load(file)

            if not history:
                return

            history[-1]["transaction_hash"] = transaction_hash
            history[-1]["block_number"] = block_number
            print("History updated:")
            print(history[-1])

            with open(self.history_file, "w") as file:
                json.dump(history, file, indent=4)

            print("Blockchain information updated in metadata.")

        except Exception as e:
            print(f"Metadata update failed: {e}")
