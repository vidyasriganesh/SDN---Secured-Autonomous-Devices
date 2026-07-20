from web3 import Web3
import json
import os


class BlockchainClient:

    def __init__(self):

        PROJECT_ROOT = os.path.expanduser("~/Blockchain_FL_IDS/blockchain")
        config_path = os.path.join(PROJECT_ROOT, "config.json")
        abi_path = os.path.join(PROJECT_ROOT, "trust_manager_abi.json")

        with open(config_path) as f:
            config = json.load(f)

        with open(abi_path) as f:
            trust_manager_abi = json.load(f)

        self.w3 = Web3(Web3.HTTPProvider(config["ganache_url"]))

        if not self.w3.is_connected():
            print("Blockchain Connection Failed")
            return

        print("Blockchain Connected")

        self.admin = config["admin_account"]
        self.private_key = config["admin_private_key"]

        self.contract = self.w3.eth.contract(
            address=config["trust_manager_address"],
            abi=trust_manager_abi
        )

    def send(self, metadata):

        mac = metadata.get("src_mac", "UNKNOWN")

        tx = self.contract.functions.verifyDevice(mac).build_transaction({

            "from": self.admin,

            "nonce": self.w3.eth.get_transaction_count(self.admin),

            "gas": 300000,

            "gasPrice": self.w3.to_wei("20", "gwei")

        })

        signed_tx = self.w3.eth.account.sign_transaction(
            tx,
            self.private_key
        )

        tx_hash = self.w3.eth.send_raw_transaction(
            signed_tx.raw_transaction
        )

        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        print("\n========================================")
        print("BLOCKCHAIN TRANSACTION")
        print("========================================")
        print("Transaction :", tx_hash.hex())
        print("Block :", receipt.blockNumber)
        print("Status :", receipt.status)
        print("========================================")

        return receipt
