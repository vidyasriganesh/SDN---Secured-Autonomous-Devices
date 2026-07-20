import csv
import os
from datetime import datetime


class TrafficLogger:

    def __init__(self):

        self.filename = os.path.expanduser(
            "~/Blockchain_FL_IDS/logs/traffic.csv"
        )

        if not os.path.exists(self.filename):

            with open(self.filename, "w", newline="") as file:

                writer = csv.writer(file)

                writer.writerow([
                    "Timestamp",
                    "Source MAC",
                    "Destination MAC",
                    "Source IP",
                    "Destination IP",
                    "Protocol",
                    "Transport"
                ])


    def log(self, packet):

        with open(self.filename, "a", newline="") as file:

            writer = csv.writer(file)

            writer.writerow([

                datetime.now(),

                packet.get("src_mac"),

                packet.get("dst_mac"),

                packet.get("src_ip"),

                packet.get("dst_ip"),

                packet.get("protocol"),

                packet.get("transport")

            ])
