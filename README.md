# Blockchain-Secured Federated Learning IDS for SDN-based IoT Networks

A real-time intrusion detection system that integrates **Software Defined Networking (SDN)**, **Blockchain**, **Federated Learning**, and **Deep Learning** to secure IoT networks. The system uses an LSTM model trained on the CICIDS2017 dataset to classify network traffic, immutably logs security decisions on an Ethereum blockchain, and supports collaborative model training across distributed IoT nodes via federated learning with anti-poisoning defenses.

## Architecture

```
                            ┌─────────────────────────────────┐
                            │      Streamlit Dashboard        │
                            │   (Real-time Monitoring UI)     │
                            └──────────────┬──────────────────┘
                                           │ reads
                            ┌──────────────▼──────────────────┐
                            │     metadata_history.json       │
                            └──────────────▲──────────────────┘
                                           │ writes
┌────────────┐    OpenFlow    ┌────────────┴──────────────────┐
│  Mininet   │───────────────▶│       POX SDN Controller      │
│  (5 IoT    │                │                               │
│   hosts)   │                │  ┌─────────┐  ┌────────────┐ │
└────────────┘                │  │ Parser  │─▶│  Feature   │ │
                              │  └─────────┘  │ Generator  │ │
                              │               └─────┬──────┘ │
                              │                     │        │
                              │               ┌─────▼──────┐ │
                              │               │ LSTM Model │ │
                              │               │ (PyTorch)  │ │
                              │               └─────┬──────┘ │
                              │                     │        │
                              │               ┌─────▼──────┐ │
                              │               │  Decision  │ │
                              │               │   Engine   │ │
                              │               └──┬────┬────┘ │
                              │                  │    │      │
                              │    ALLOW         │    │ BLOCK│
                              │    ┌─────────────┘    └──┬───┘
                              │    │                     │
                              │    ▼                     ▼
                              │  Flood              Quarantine
                              │                   + Blockchain TX
                              └───────────────────────────────┘
                                           │
                              ┌─────────────▼──────────────────┐
                              │     Ganache Blockchain         │
                              │  ┌─────────────┐ ┌──────────┐ │
                              │  │ TrustManager │ │SDNVerifier│ │
                              │  └─────────────┘ └──────────┘ │
                              └────────────────────────────────┘

                              ┌────────────────────────────────┐
                              │   Federated Learning (Flower)  │
                              │  ┌──────────┐  ┌───────────┐  │
                              │  │  Server   │  │  Clients   │  │
                              │  │ (Rounds)  │◀─│ (Honest /  │  │
                              │  │           │  │ Malicious) │  │
                              │  └──────────┘  └───────────┘  │
                              └────────────────────────────────┘
```

## Features

- **Real-time IDS**: LSTM-based binary classifier (NORMAL/ATTACK) running at the SDN controller level
- **Blockchain Audit Trail**: Every BLOCK decision is immutably logged on Ethereum with transaction hashes
- **Federated Learning**: Collaborative model training across IoT nodes using Flower framework
- **Anti-Poisoning Defense**: Cosine similarity filtering rejects malicious FL clients (threshold: 0.3)
- **Live Dashboard**: Streamlit web UI with device trust status, attack alerts, network stats, and FL progress
- **Quarantine System**: Automatic IP blocking for detected attacks
- **Multi-bank ATM Scenario**: 5 IoT devices across 3 banks with per-device trust verification

## Project Structure

```
Blockchain_FL_IDS/
├── blockchain/                 # Smart contracts + deployment + dashboard
│   ├── TrustManager.sol        #   Solidity: device trust management
│   ├── deploy.py               #   Contract deployment script
│   ├── blockchain_api.py       #   Python API for contract interaction
│   ├── dashboard.py            #   Streamlit real-time dashboard
│   ├── metadata_listener.py    #   Background metadata-to-blockchain sync
│   └── config.json             #   Ganache URL, accounts, contract addresses
├── blockchain_client/          # Blockchain transaction sender
│   └── client.py               #   Used by SDN controller for BLOCK events
├── controller/                 # SDN controller (POX)
│   └── controller.py           #   Core pipeline: parse → predict → decide → act
├── fl/                         # Federated Learning + ML
│   ├── model.py                #   LSTM_IDS model (PyTorch)
│   ├── data_prep.py            #   CICIDS2017 loading, cleaning, SMOTE, scaling
│   ├── train.py                #   Local training loop
│   ├── predictor.py            #   Real-time inference wrapper
│   ├── feature_generator.py    #   Packet → 16-feature vector
│   ├── fl_server.py            #   Flower server with anti-poisoning
│   ├── fl_client.py            #   Flower client (honest or malicious)
│   └── fl_client_malicious.py  #   Dedicated poisoning client
├── parser/                     # Packet parsing
│   └── packet_parser.py        #   Ethernet/IPv4/TCP/UDP extraction
├── flow/                       # Flow statistics
│   └── flow_statistics.py      #   Per-flow metrics (duration, bytes, rates)
├── security/                   # Security decisions
│   ├── decision_engine.py      #   ATTACK→BLOCK, NORMAL→ALLOW
│   └── quarantine.py           #   In-memory blocked IP set
├── metadata/                   # Metadata generation
│   └── metadata_generator.py   #   JSON metadata per packet
├── buffer/                     # Packet buffering
│   └── buffer_manager.py       #   Save uncertain packets
├── logger/                     # Traffic logging
│   └── traffic_logger.py       #   CSV traffic log
├── topology/                   # Network topology
│   └── topology.py             #   Mininet: 5 hosts + 1 switch
├── config/                     # Configuration
│   └── iot_registry.json       #   MAC → device name/owner mapping
├── datasets/                   # Training data
│   └── cicids2017_cleaned.csv  #   CICIDS2017 dataset (not in repo, see below)
├── models/                     # Trained model artifacts
│   ├── model.pth               #   Local LSTM weights
│   ├── global_model.pth        #   FL-aggregated weights (generated at runtime)
│   └── scaler.pkl              #   MinMaxScaler for feature normalization
├── docs/                       # Documentation
│   └── blockchain_metadata_format.md
├── test_attack_detection.py    # Test: DoS attack classification
├── test_normal_detection.py    # Test: normal traffic classification
└── test_model_sanity.py        # Test: synthetic input sanity checks
```

## Network Topology

| Host | Role | IP | MAC | Owner |
|------|------|----|-----|-------|
| h1 | ATM_1 | 10.0.0.1 | 00:00:00:00:00:01 | Bank_A |
| h2 | ATM_2 | 10.0.0.2 | 00:00:00:00:00:02 | Bank_A |
| h3 | ATM_3 | 10.0.0.3 | 00:00:00:00:00:03 | Bank_B |
| h4 | ATM_4 | 10.0.0.4 | 00:00:00:00:00:04 | Bank_B |
| h5 | ATM_5 | 10.0.0.5 | 00:00:00:00:00:05 | Bank_C |

Single OpenFlow switch (`s1`) in star topology. Subnet: `10.0.0.0/24`

## Model Architecture

```
Input (16 features)
    │
    ▼
LSTM(input_dim, hidden=64, layers=2, dropout=0.2)
    │
    ▼
Linear(64, 1)
    │
    ▼
Sigmoid → probability ≥ 0.5 → ATTACK / NORMAL
```

### 16 Input Features

| # | Feature | # | Feature |
|---|---------|---|---------|
| 1 | Destination Port | 9 | Flow Packets/s |
| 2 | Flow Duration | 10 | Min Packet Length |
| 3 | Total Fwd Packets | 11 | Max Packet Length |
| 4 | Total Length of Fwd Packets | 12 | Packet Length Mean |
| 5 | Fwd Packet Length Max | 13 | FIN Flag Count |
| 6 | Fwd Packet Length Min | 14 | ACK Flag Count |
| 7 | Fwd Packet Length Mean | 15 | Average Packet Size |
| 8 | Flow Bytes/s | 16 | Subflow Fwd Bytes |

## Prerequisites

- **Python 3.12+**
- **Ganache** (local Ethereum blockchain) — `npm install -g ganache`
- **POX** SDN controller — clone from [https://github.com/noxrepo/pox](https://github.com/noxrepo/pox)
- **Mininet** — `sudo apt install mininet`
- **hping3** — `sudo apt install hping3`

### Python Dependencies

```bash
pip install torch scikit-learn imbalanced-learn pandas numpy \
            flower web3 py-solc-x streamlit joblib
```

### Dataset

Download the CICIDS2017 dataset and place the cleaned CSV at:
```
datasets/cicids2017_cleaned.csv
```

> The dataset is excluded from the repository due to its size (685MB).

## Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/vidyasriganesh/SDN---Secured-Autonomous-Devices.git
cd SDN---Secured-Autonomous-Devices
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install torch scikit-learn imbalanced-learn pandas numpy \
            flower web3 py-solc-x streamlit joblib
```

### 3. Start Ganache

```bash
ganache \
  --wallet.mnemonic "model stock clarify solar rich armed crunch truly spread just moment early" \
  --chain.chainId 1337 \
  --server.host 127.0.0.1 \
  --server.port 8545
```

### 4. Deploy Smart Contracts

```bash
cd blockchain
python3 deploy.py
```

### 5. Register IoT Devices on Blockchain

```bash
python3 blockchain_api.py
```

### 6. Start the Streamlit Dashboard

```bash
cd ..
streamlit run blockchain/dashboard.py
```

Dashboard available at: `http://localhost:8501`

### 7. Start the POX SDN Controller

```bash
cd ~/pox  # path to your POX installation
source ~/Blockchain_FL_IDS/venv/bin/activate
./pox.py log.level --DEBUG openflow.of_01 blockchain_ids
```

### 8. Start Mininet

```bash
cd ~/Blockchain_FL_IDS
sudo mn -c
sudo mn --custom topology/topology.py --topo iottopo --controller remote
```

### 9. (Optional) Start Federated Learning

**Server** (Terminal A):
```bash
source venv/bin/activate
rm -f models/global_model.pth
python -m fl.fl_server
```

**Client — Honest** (Terminal B):
```bash
source venv/bin/activate
python -m fl.fl_client
```

**Client — Malicious** (Terminal C, for anti-poisoning testing):
```bash
source venv/bin/activate
python -m fl.fl_client_malicious
```

## Usage

### Test Connectivity

Inside Mininet:
```
mininet> pingall
mininet> h1 ping h2
```

### Simulate Attack

Inside Mininet:
```
mininet> h3 hping3 -S --flood -V h1
```

The IDS will detect the SYN flood, classify it as ATTACK, quarantine `10.0.0.3`, and log the BLOCK decision to the blockchain.

## Configuration

### Blockchain (`blockchain/config.json`)

| Key | Description |
|-----|-------------|
| `ganache_url` | Ganache RPC endpoint |
| `admin_account` | Ethereum account for deploying/registering |
| `sdn_account` | Account for SDN controller transactions |
| `trust_manager_address` | Deployed TrustManager contract address |
| `sdn_verifier_address` | Deployed SDNVerifier contract address |

### Federated Learning

| Parameter | Value | Location |
|-----------|-------|----------|
| Server address | `0.0.0.0:8080` | `fl/fl_server.py` |
| Training rounds | 20 | `fl/fl_server.py` |
| Min clients | 2 | `fl/fl_server.py` |
| Anti-poisoning threshold | 0.3 (cosine similarity) | `fl/fl_server.py` |
| Client epochs/round | 3 | `fl/fl_client.py` |
| Learning rate | 0.001 | `fl/local_ids.py` |
| Optimizer | Adam | `fl/local_ids.py` |
| Loss function | BCELoss | `fl/local_ids.py` |

### Model

| Parameter | Value |
|-----------|-------|
| Architecture | 2-layer LSTM |
| Hidden size | 64 |
| Dropout | 0.2 |
| Input features | 16 |
| Batch size | 256 |
| Prediction threshold | 0.5 |

## Testing

Run the standalone test scripts:

```bash
# Test attack detection (DoS samples from CICIDS2017)
python test_attack_detection.py

# Test normal traffic detection
python test_normal_detection.py

# Model sanity check (synthetic inputs)
python test_model_sanity.py
```

## Smart Contracts

### TrustManager

| Function | Description |
|----------|-------------|
| `addDevice(mac)` | Register an IoT device by MAC address |
| `removeDevice(mac)` | Remove a device from the allowed list |
| `verifyDevice(mac)` | Verify device and emit `DeviceVerified` event |
| `isDeviceAllowed(mac)` | Check if a device is trusted (view function) |

### SDNVerifier

| Function | Description |
|----------|-------------|
| `updateSDN(address)` | Update the authorized SDN controller address |
| `verifySignature(hash, sig)` | Verify ECDSA signature from the SDN controller |

## Dashboard

The Streamlit dashboard (`http://localhost:8501`) displays:

- **Connection Status** — Ganache blockchain connectivity
- **IoT Device Trust** — Per-device Trusted/Blocked status
- **Live Attack Alerts** — Last 10 BLOCK events with confidence scores
- **Network Statistics** — Total packets, normal count, attack count
- **Packet Log** — Last 15 classified packets with full metadata
- **FL Progress** — Global model version, round number, participating nodes

Auto-refreshes every 3 seconds.

## License

This project is for academic/research purposes.

## Acknowledgments

- [CICIDS2017](https://www.unb.ca/cic/datasets/ids-2017.html) — Network intrusion detection dataset
- [Flower](https://flower.ai/) — Federated learning framework
- [POX](https://github.com/noxrepo/pox) — OpenFlow SDN controller
- [Mininet](http://mininet.org/) — Network emulator
- [Ganache](https://trufflesuite.com/ganache/) — Ethereum development blockchain
- [Streamlit](https://streamlit.io/) — Web dashboard framework
