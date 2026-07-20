import time


class FlowStatistics:

    def __init__(self):
        self.flows = {}

    def update(self, packet):

        flow_key = (
            packet.get("src_ip"),
            packet.get("dst_ip"),
            packet.get("transport")
        )

        current = time.time()

        if flow_key not in self.flows:

            self.flows[flow_key] = {
                "start_time": current,
                "last_seen": current,
                "packet_count": 1,
                "byte_count": packet.get("packet_length", 0),
                "packet_lengths": [
                     packet.get("packet_length", 0)
                 ]
             }
        else:

            flow = self.flows[flow_key]

            flow["packet_count"] += 1

            flow["byte_count"] += packet.get("packet_length", 0)

            flow["packet_lengths"].append(
                packet.get("packet_length", 0)
            )

            flow["last_seen"] = current
        flow = self.flows[flow_key]

        duration = flow["last_seen"] - flow["start_time"]

        if duration <= 0:
            duration = 1

        average_packet_size = 0

        if flow["packet_count"] > 0:
            average_packet_size = (
                flow["byte_count"] /
                flow["packet_count"]
            )
        packet_lengths = flow["packet_lengths"]

        max_packet_length = max(packet_lengths)

        min_packet_length = min(packet_lengths)

        packet_length_mean = (
            sum(packet_lengths) / len(packet_lengths)
        ) 
        
        return {
            "max_packet_length": max_packet_length,

            "min_packet_length": min_packet_length,

            "packet_length_mean": packet_length_mean,
           
            "flow_duration": duration * 1000000, 
            "packet_count": flow["packet_count"],

            "byte_count": flow["byte_count"],

            "packets_per_second":
                flow["packet_count"] / duration,

            "bytes_per_second":
                flow["byte_count"] / duration,

            "average_packet_size":
                average_packet_size,

            "flow_bytes":
                flow["byte_count"],

            "flow_packets":
                flow["packet_count"]

        }
