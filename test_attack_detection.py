import sys
sys.path.append('.')
import pandas as pd
from fl.predictor import Predictor

df = pd.read_csv("datasets/cicids2017_cleaned.csv")

feature_cols = [
    "Destination Port", "Flow Duration", "Total Fwd Packets",
    "Total Length of Fwd Packets", "Fwd Packet Length Max",
    "Fwd Packet Length Min", "Fwd Packet Length Mean",
    "Flow Bytes/s", "Flow Packets/s", "Min Packet Length",
    "Max Packet Length", "Packet Length Mean", "FIN Flag Count",
    "ACK Flag Count", "Average Packet Size", "Subflow Fwd Bytes"
]

predictor = Predictor()

attack_rows = df[df["Attack Type"] == "DoS"].sample(5, random_state=1)

for idx, row in attack_rows.iterrows():
    features = row[feature_cols].tolist()
    result = predictor.predict(features)
    print(f"Row {idx}: Prediction={result['prediction']}, Probability={result['probability']:.6f}")
