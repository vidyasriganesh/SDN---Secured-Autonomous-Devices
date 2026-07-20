import json
import time
import hashlib
from blockchain_api import w3, ADMIN_ACCOUNT, ADMIN_PRIVATE_KEY

METADATA_FILE = "../metadata/metadata_history.json"
previous_hash = "0" * 64  # genesis hash, no previous record
last_processed = 0  # tracks how many records we've already handled

def compute_hash(record):
    record_string = json.dumps(record, sort_keys=True)
    return hashlib.sha256(record_string.encode()).hexdigest()

def read_metadata():
    try:
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    
def store_on_blockchain(record, prev_hash, curr_hash):
    data = {
        "packet_id": record["packet_id"],
        "timestamp": record["timestamp"],
        "src_mac": record["src_mac"],
        "dst_mac": record["dst_mac"],
        "src_ip": record["src_ip"],
        "dst_ip": record["dst_ip"],
        "protocol": record["protocol"],
        "transport": record["transport"],
        "decision": record["decision"],
        "previous_hash": prev_hash,
        "current_hash": curr_hash
    }

    # Store as a transaction on Ganache
    tx = {
        'from': ADMIN_ACCOUNT,
        'to': ADMIN_ACCOUNT,  # sending to self, data is what matters
        'value': 0,
        'gas': 200000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': w3.eth.get_transaction_count(ADMIN_ACCOUNT),
        'data': json.dumps(data).encode().hex()
    }

    signed_tx = w3.eth.account.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Packet {record['packet_id']} stored. TX: {tx_hash.hex()}")
    return tx_hash.hex()

def watch():
    global previous_hash, last_processed
    print("Metadata listener started. Watching for new packets...")

    while True:
        records = read_metadata()
        new_records = records[last_processed:]

        for record in new_records:
            curr_hash = compute_hash(record)
            store_on_blockchain(record, previous_hash, curr_hash)
            previous_hash = curr_hash
            last_processed += 1

        time.sleep(2)  # check every 2 seconds

if __name__ == "__main__":
    watch()

