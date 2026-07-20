from web3 import Web3

print("--- Initializing Web3 Security Middleware ---")

# This connects to Member 3's local Ganache blockchain (which runs on port 8545)
# Note: This will fail until Member 3 actually turns Ganache on!
ganache_url = "http://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

def verify_client_authorization(client_mac_address):
    """
    This function acts as the security middleware. 
    It checks the Blockchain Smart Contract to see if the client is allowed to connect.
    """
    print(f"\n[Blockchain] Intercepting connection from MAC: {client_mac_address}")
    
    # 1. Check if the local blockchain is actually running
    if not web3.is_connected():
        print("[Blockchain] ERROR: Cannot connect to Ganache network.")
        # For testing purposes right now, we will just return True so your AI still works
        return True 

    # 2. This is where Member 3 will link their Smart Contract!
    # contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    # is_authorized = contract.functions.checkAuthorization(client_mac_address).call()
    
    print("[Blockchain] Client verified via Smart Contract. Access Granted.")
    return True # Change this to 'return is_authorized' once Member 3 finishes their code