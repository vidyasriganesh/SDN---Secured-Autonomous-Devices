import os
import pandas as pd
import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split

# UPGRADE: Import SMOTE to fix the 85.04% accuracy plateau
from imblearn.over_sampling import SMOTE

print("1. Loading Data...")

DATASET_PATH = os.path.join(
    os.path.expanduser("~/Blockchain_FL_IDS"),
    "datasets",
    "cicids2017_cleaned.csv"
)

df_full = pd.read_csv(DATASET_PATH)
df_full.columns = df_full.columns.str.strip()

# Stratified sample: up to 20,000 rows per class, keeps all attack types represented
df = pd.concat([
    grp.sample(n=min(len(grp), 20000), random_state=42)
    for _, grp in df_full.groupby("Attack Type")
], ignore_index=True)
# Strip invisible spaces from all column names just in case
df.columns = df.columns.str.strip()

# Set the target column to the one we found in your dataset
target_col = 'Attack Type'

print("2. Cleaning Data...")
df = df.replace([np.inf, -np.inf], np.nan).dropna()

y_raw = df[target_col]
X_raw = pd.DataFrame()

# Runtime feature mapping
X_raw["Destination Port"] = df["Destination Port"]
X_raw["Flow Duration"] = df["Flow Duration"]
X_raw["Total Fwd Packets"] = df["Total Fwd Packets"]
X_raw["Total Length of Fwd Packets"] = df["Total Length of Fwd Packets"]
X_raw["Fwd Packet Length Max"] = df["Fwd Packet Length Max"]
X_raw["Fwd Packet Length Min"] = df["Fwd Packet Length Min"]
X_raw["Fwd Packet Length Mean"] = df["Fwd Packet Length Mean"]
X_raw["Flow Bytes/s"] = df["Flow Bytes/s"]
X_raw["Flow Packets/s"] = df["Flow Packets/s"]
X_raw["Min Packet Length"] = df["Min Packet Length"]
X_raw["Max Packet Length"] = df["Max Packet Length"]
X_raw["Packet Length Mean"] = df["Packet Length Mean"]
X_raw["FIN Flag Count"] = df["FIN Flag Count"]
X_raw["ACK Flag Count"] = df["ACK Flag Count"]
X_raw["Average Packet Size"] = df["Average Packet Size"]
X_raw["Subflow Fwd Bytes"] = df["Subflow Fwd Bytes"]
print("3. Encoding Labels (Words to Numbers)...")
y_binary = np.where(y_raw == "Normal Traffic", 0, 1)

print("4. Splitting into Train and Test sets...")

X_train_raw, X_test_raw, y_train, y_test = train_test_split(
    X_raw,
    y_binary,
    test_size=0.2,
    random_state=42
)

print("5. Scaling Features...")

scaler = MinMaxScaler()

X_train = scaler.fit_transform(X_train_raw)

X_test = scaler.transform(X_test_raw)

import joblib

joblib.dump(
    scaler,
    os.path.join(
        os.path.expanduser("~/Blockchain_FL_IDS"),
        "models",
        "scaler.pkl"
    )
)

print("Scaler Saved Successfully")
# UPGRADE: Apply SMOTE to create a perfect 50/50 balance of Normal vs Attack data
print("5.5. Balancing the Dataset with SMOTE...")
smote = SMOTE(random_state=42)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

print("6. Converting to PyTorch Tensors...")
# UPGRADE: Feed the newly balanced data into the PyTorch Tensors
X_train_tensor = torch.tensor(X_train_balanced, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train_balanced, dtype=torch.float32).unsqueeze(1)
X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
y_test_tensor = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1)

print("\n--- Data Prep Complete! ---")
print(f"Training Data Shape: {X_train_tensor.shape}")
print(f"Testing Data Shape: {X_test_tensor.shape}")
# Create TensorDataset
train_dataset = TensorDataset(
    X_train_tensor,
    y_train_tensor
)

test_dataset = TensorDataset(
    X_test_tensor,
    y_test_tensor
)

# Create DataLoaders
train_loader = DataLoader(
    train_dataset,
    batch_size=256,
    shuffle=True
)

test_loader = DataLoader(
    test_dataset,
    batch_size=256,
    shuffle=False
)

print(f"Training Batches : {len(train_loader)}")
print(f"Testing Batches  : {len(test_loader)}")
# Number of input features
input_size = X_train_tensor.shape[1]
