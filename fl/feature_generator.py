class FeatureGenerator:

    def generate(self, packet, flow_stats):

        return [

            float(packet.get("dst_port", 0)),                  # Destination Port
            float(flow_stats["flow_duration"]),                # Flow Duration
            float(flow_stats["packet_count"]),                 # Total Fwd Packets
            float(flow_stats["byte_count"]),                   # Total Length of Fwd Packets
            float(flow_stats["max_packet_length"]),            # Fwd Packet Length Max
            float(flow_stats["min_packet_length"]),            # Fwd Packet Length Min
            float(flow_stats["packet_length_mean"]),           # Fwd Packet Length Mean
            float(flow_stats["bytes_per_second"]),             # Flow Bytes/s
            float(flow_stats["packets_per_second"]),           # Flow Packets/s
            float(flow_stats["min_packet_length"]),            # Min Packet Length
            float(flow_stats["max_packet_length"]),            # Max Packet Length
            float(flow_stats["packet_length_mean"]),           # Packet Length Mean
            float(packet.get("fin", 0)),                       # FIN Flag Count
            float(packet.get("ack", 0)),                       # ACK Flag Count
            float(flow_stats["average_packet_size"]),          # Average Packet Size
            float(flow_stats["byte_count"])                    # Subflow Fwd Bytes

        ]
