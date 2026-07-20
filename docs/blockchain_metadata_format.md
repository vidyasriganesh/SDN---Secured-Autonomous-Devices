# Metadata sent from SDN to Blockchain

Fields:

controller_id
packet_id
timestamp
src_mac
dst_mac
src_ip
dst_ip
protocol
transport
decision

Example

{
    "controller_id":"SDN_CONTROLLER_1",
    "packet_id":124,
    "timestamp":"2026-07-01 08:37:29",

    "src_mac":"00:00:00:00:00:01",
    "dst_mac":"ff:ff:ff:ff:ff:ff",

    "src_ip":null,
    "dst_ip":null,

    "protocol":null,

    "transport":"OTHER",

    "decision":"BUFFER"
}
