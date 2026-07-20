import json
from web3 import Web3
from solcx import compile_source, install_solc

# Install solc compiler
install_solc('0.8.0')

# Connect to Ganache
GANACHE_URL = "http://127.0.0.1:8545"
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

ADMIN_ACCOUNT = w3.eth.accounts[0]

ADMIN_PRIVATE_KEY = "0x616922128b677d19882ca2e164d307ad07fe39a5ba3890666eac01d615290fc5"

SDN_ACCOUNT = w3.eth.accounts[1]

# Read your Solidity file
with open("TrustManager.sol", "r") as f:
    source = f.read()

# Compile both contracts
compiled = compile_source(source, output_values=["abi", "bin"], solc_version="0.8.0")

trust_manager_interface = compiled['<stdin>:TrustManager']
sdn_verifier_interface = compiled['<stdin>:SDNVerifier']

def deploy_contract(interface, constructor_args=None):
    contract = w3.eth.contract(
        abi=interface['abi'],
        bytecode=interface['bin']
    )
    tx = contract.constructor(*constructor_args or []).build_transaction({
        'from': ADMIN_ACCOUNT,
        'gas': 3000000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': w3.eth.get_transaction_count(ADMIN_ACCOUNT),
    })
    signed_tx = w3.eth.account.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt.contractAddress, interface['abi']

print("Deploying TrustManager...")
tm_address, tm_abi = deploy_contract(trust_manager_interface)
print(f"TrustManager deployed at: {tm_address}")

print("Deploying SDNVerifier...")
sdn_address, sdn_abi = deploy_contract(sdn_verifier_interface, [SDN_ACCOUNT])
print(f"SDNVerifier deployed at: {sdn_address}")

# Save everything to config.json
config = {
    "ganache_url": GANACHE_URL,
    "admin_account": ADMIN_ACCOUNT,
    "admin_private_key": ADMIN_PRIVATE_KEY,
    "sdn_account": SDN_ACCOUNT,
    "trust_manager_address": tm_address,
    "sdn_verifier_address": sdn_address,
}

with open("config.json", "w") as f:
    json.dump(config, f, indent=4)
    print("config.json saved")

# Save ABIs
with open("trust_manager_abi.json", "w") as f:
    json.dump(tm_abi, f, indent=4)

with open("sdn_verifier_abi.json", "w") as f:
    json.dump(sdn_abi, f, indent=4)
    print("ABI files updated")

print("Deployment complete. Run blockchain_api.py next.")
