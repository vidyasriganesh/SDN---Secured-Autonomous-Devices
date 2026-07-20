import os
import torch
torch.set_num_threads(1)
import joblib

from fl.model import LSTM_IDS
INPUT_SIZE = 16

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLOBAL_MODEL_PATH = os.path.join(BASE_DIR, "models", "global_model.pth")
LOCAL_MODEL_PATH = os.path.join(BASE_DIR, "models", "model.pth")
SCALER_PATH = os.path.join(BASE_DIR, "models", "scaler.pkl")


class Predictor:

    def __init__(self):
        self.model = LSTM_IDS(INPUT_SIZE)
        # Prefer the latest Federated Global Model
        # Prefer the latest Federated Global Model
        if os.path.exists(GLOBAL_MODEL_PATH):
            model_path = GLOBAL_MODEL_PATH
            print("Using Federated Global Model")
        else:
            model_path = LOCAL_MODEL_PATH
            print("Using Local IDS Model")
        self.model.load_state_dict(
            torch.load(
                model_path,
                map_location=torch.device("cpu")
            )
         )
        self.model.eval()

        self.scaler = joblib.load(SCALER_PATH)

        print("========================================")
        print(" AI MODEL INITIALIZED")
        print("========================================")
        print("Model Loaded Successfully")
        print("Scaler Loaded Successfully")
        print("========================================")

    def predict(self, features):

        with torch.no_grad():

            # Scale features
            scaled_features = self.scaler.transform([features])

            # Convert to tensor
            x = torch.tensor(
                scaled_features,
                dtype=torch.float32
            )

            # Model output (Already Sigmoid Output)
            probability = self.model(x).item()

            # Prediction
            if probability >= 0.5:
                prediction = "ATTACK"
                confidence = probability * 100
            else:
                prediction = "NORMAL"
                confidence = (1 - probability) * 100

            print("\n========================================")
            print("          AI PREDICTION")
            print("========================================")
            print(f"Probability : {probability:.6f}")
            print(f"Confidence  : {confidence:.2f}%")
            print(f"Prediction  : {prediction}")
            print("========================================\n")

            return {
                "prediction": prediction,
                "probability": probability,
                "confidence": confidence
            }
