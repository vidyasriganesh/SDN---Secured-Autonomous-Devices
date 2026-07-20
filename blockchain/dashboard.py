import streamlit as st
import time
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

METADATA_FILE = os.path.join(
    BASE_DIR,
    "metadata",
    "metadata_history.json"
)
from blockchain_api import (
    w3,
    trust_manager,
    is_device_allowed,
    ADMIN_ACCOUNT
)

st.set_page_config(
    page_title="Blockchain-Secured IDS Dashboard",
    page_icon="🔐",
    layout="wide"
)

st.title("🔐 Blockchain-Secured Federated Learning IDS")
st.caption("Real-time monitoring — IoT Network Security Dashboard")

# Connection status
if w3.is_connected():
    st.success("🟢 Connected to Ganache Blockchain")
else:
    st.error("🔴 Blockchain connection lost")

st.divider()

# Known IoT devices (update with Member 1's MACs later)
KNOWN_DEVICES = [
    "00:00:00:00:00:01",
    "00:00:00:00:00:02",
    "00:00:00:00:00:03",
    "00:00:00:00:00:04",
    "00:00:00:00:00:05",
]

st.subheader("📡 IoT Device Status")

cols = st.columns(len(KNOWN_DEVICES))
for i, mac in enumerate(KNOWN_DEVICES):
    allowed = is_device_allowed(mac)
    with cols[i]:
        if allowed:
            st.success(f"✅ {mac}")
            st.caption("Trusted")
        else:
            st.error(f"❌ {mac}")
            st.caption("Blocked")

st.divider()

st.subheader("🚨 Live Attack Alerts")

try:
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as f:
            records = json.load(f)

        blocked = [r for r in records if r["decision"] == "BLOCK"]

        if blocked:
            for r in reversed(blocked[-10:]):
                st.error(
                    f"""
                🚨 ATTACK DETECTED

                Prediction : {r.get('prediction','-')}

                Decision : {r.get('decision','-')}

                Confidence : {r.get('confidence',0):.2f}%

                Source IP : {r.get('src_ip','-')}

                Destination IP : {r.get('dst_ip','-')}

                Transport : {r.get('transport','-')}

                Time : {r.get('timestamp','-')}
                """
                )
        else:
            st.info("No attacks detected yet.")
    else:
        st.info("Waiting for SDN data...")
except Exception as e:
    st.warning(f"Could not fetch alerts: {e}")

st.divider()

st.subheader("🔗 Blockchain Transaction Logs")
st.divider()

st.subheader("📊 Live Network Statistics")

try:
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as f:
            records = json.load(f)

        total_packets = len(records)
        attack_packets = len([r for r in records if r.get("decision") == "BLOCK"])
        normal_packets = total_packets - attack_packets

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("Packets Processed", total_packets)

        with c2:
            st.metric("Normal Packets", normal_packets)

        with c3:
            st.metric("Detected Attacks", attack_packets)

    else:
        st.info("Waiting for metadata...")
except Exception as e:
    st.warning(f"Statistics unavailable: {e}")

try:
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as f:
            records = json.load(f)

        if records:
            log_data = []
            for r in reversed(records[-15:]):
                log_data.append({
                    "Packet ID": r.get("packet_id", "-"),
                    "Timestamp": r.get("timestamp", "-"),

                    "Prediction": r.get("prediction", "-"),
                    "Confidence (%)": f"{r.get('confidence', 0):.2f}",
                    "Probability": f"{r.get('probability', 0):.6f}",

                    "Decision": r.get("decision", "-"),

                    "Src MAC": r.get("src_mac", "-"),
                    "Dst MAC": r.get("dst_mac", "-"),

                    "Src IP": r.get("src_ip", "-"),
                    "Dst IP": r.get("dst_ip", "-"),

                    "Protocol": r.get("protocol", "-"),
                    "Transport": r.get("transport", "-"),

                    "Transaction Hash": r.get("transaction_hash", "Pending"),
                    "Block Number": r.get("block_number", "Pending")
            })
            st.table(log_data)
        else:
            st.info("No packets logged yet.")
    else:
        st.info("Waiting for metadata file from SDN...")
except Exception as e:
    st.warning(f"Could not read metadata: {e}")

st.divider()

st.subheader("🧠 FL Model Update Progress")

FL_STATUS_FILE = os.path.join(BASE_DIR, "fl_status.json")

if os.path.exists(FL_STATUS_FILE):
    with open(FL_STATUS_FILE) as f:
        fl_status = json.load(f)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Global Model Version", value=f"v1.{fl_status['round']}")
    with col2:
        st.metric(label="Round", value=fl_status["round"])
    with col3:
        st.metric(label="Participating Nodes", value=fl_status["accepted"])

    if fl_status["attack_detected"]:
        st.error(f"🚨 Anti-poisoning check FAILED: {fl_status['rejected']} malicious node(s) rejected this round!")
    else:
        st.success("🎉 Anti-poisoning check PASSED. All nodes clean.")
else:
    st.info("Waiting for FL server status...")
st.divider()

# Auto refresh every 3 seconds
time.sleep(3)
st.rerun()
