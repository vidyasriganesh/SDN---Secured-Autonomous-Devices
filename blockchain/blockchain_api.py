from web3 import Web3
import json
import os

_DIR = os.path.dirname(os.path.abspath(__file__))

# Load config
with open(os.path.join(_DIR, "config.json"), "r") as f:
    config = json.load(f)

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider(config["ganache_url"]))

if w3.is_connected():
    print("Connected to Ganache")
else:
    print("Connection failed")

# Load ABIs
with open(os.path.join(_DIR, "trust_manager_abi.json")) as f:
    trust_manager_abi = json.load(f)

with open(os.path.join(_DIR, "sdn_verifier_abi.json")) as f:
    sdn_verifier_abi = json.load(f)

# Addresses and accounts from config
TRUST_MANAGER_ADDRESS = config["trust_manager_address"]
SDN_VERIFIER_ADDRESS = config["sdn_verifier_address"]
ADMIN_ACCOUNT = config["admin_account"]
ADMIN_PRIVATE_KEY = config["admin_private_key"]
SDN_ACCOUNT = config["sdn_account"]

# Load contracts
trust_manager = w3.eth.contract(
    address=TRUST_MANAGER_ADDRESS,
    abi=trust_manager_abi
)

sdn_verifier = w3.eth.contract(
    address=SDN_VERIFIER_ADDRESS,
    abi=sdn_verifier_abi
)


# ── Contract A: IoT Device Verification ──────────────────────────

def add_device(mac_address):
    tx = trust_manager.functions.addDevice(mac_address).build_transaction({
        'from': ADMIN_ACCOUNT,
        'gas': 200000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': w3.eth.get_transaction_count(ADMIN_ACCOUNT),
    })
    signed_tx = w3.eth.account.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Device {mac_address} added. TX: {tx_hash.hex()}")
    return receipt

def remove_device(mac_address):
    tx = trust_manager.functions.removeDevice(mac_address).build_transaction({
        'from': ADMIN_ACCOUNT,
        'gas': 200000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': w3.eth.get_transaction_count(ADMIN_ACCOUNT),
    })
    signed_tx = w3.eth.account.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Device {mac_address} removed. TX: {tx_hash.hex()}")
    return receipt

def is_device_allowed(mac_address):
    result = trust_manager.functions.isDeviceAllowed(mac_address).call()
    return result

def verify_device(mac_address):
    tx = trust_manager.functions.verifyDevice(mac_address).build_transaction({
        'from': ADMIN_ACCOUNT,
        'gas': 200000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': w3.eth.get_transaction_count(ADMIN_ACCOUNT),
    })
    signed_tx = w3.eth.account.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Device {mac_address} verified. TX: {tx_hash.hex()}")
    return receipt

# ── Contract B: SDN Signature Verification ───────────────────────

def verify_signature(message_hash, signature):
    tx = sdn_verifier.functions.verifySignature(message_hash, signature).build_transaction({
        'from': ADMIN_ACCOUNT,
        'gas': 200000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': w3.eth.get_transaction_count(ADMIN_ACCOUNT),
    })
    signed_tx = w3.eth.account.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Signature verified. TX: {tx_hash.hex()}")
    return receipt


def setup_devices():
    macs = [
        "00:00:00:00:00:01",
        "00:00:00:00:00:02",
        "00:00:00:00:00:03",
        "00:00:00:00:00:04",
        "00:00:00:00:00:05",
    ]
    print("Adding IoT devices to blockchain...")
    for mac in macs:
        add_device(mac)
    print("All devices added.")
    print("Verifying...")
    for mac in macs:
        print(f"{mac}: {is_device_allowed(mac)}")

if __name__ == "__main__":
    setup_devices()
