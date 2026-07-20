import flwr as fl
import torch
import numpy as np
from collections import OrderedDict
# Import the Brain and the Data from your previous files!
from fl.local_ids import LSTM_IDS, model, optimizer, criterion
from fl.data_prep import X_train_tensor, y_train_tensor, X_test_tensor, y_test_tensor, train_loader

print("\n--- Starting Federated Learning Client (MALICIOUS - Scaling Attack) ---")


# Define the Flower Client
class IDSClient(fl.client.NumPyClient):

    # 1. Package the math to send to the Server
    def get_parameters(self, config):
        return [val.cpu().numpy() for _, val in model.state_dict().items()]

    # 2. Receive the updated Master Brain from the Server
    def set_parameters(self, parameters):
        print(f"[DEBUG] Received {len(parameters)} parameter arrays, first shape: {parameters[0].shape}")
        params_dict = zip(model.state_dict().keys(), parameters)
        state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
        model.load_state_dict(state_dict, strict=True)

    # 3. "Train" the AI locally (POISONED - sends corrupted weights instead of real training)
    def fit(self, parameters, config):
        self.set_parameters(parameters)
        # THE FIX: Multiply actual weights by a massive negative number
        # to guarantee the Cosine Similarity goes entirely negative.
        poisoned_weights = [
            (-w).astype(w.dtype)
            for w in self.get_parameters(config={})
        ]
        print("[MALICIOUS] Sending poisoned (scaled+inverted) weights to server...")
        return poisoned_weights, len(X_train_tensor), {}

    # 4. Test the AI locally
    # NOTE: still required — the server's strategy has fraction_evaluate=1.0 /
    # min_evaluate_clients=2, so every client (including this malicious one)
    # gets asked to evaluate. Without this method, NumPyClient raises
    # NotImplementedError and the evaluate round shows as a client failure.
    def evaluate(self, parameters, config):
        self.set_parameters(parameters)
        model.eval()
        with torch.no_grad():
            test_predictions = model(X_test_tensor)
            correct_guesses = test_predictions.round().eq(y_test_tensor).sum().item()
            accuracy = float(correct_guesses) / len(y_test_tensor)
            loss = criterion(test_predictions, y_test_tensor).item()

        print(f"\n[Malicious Client] Evaluation Accuracy (on real global model): {accuracy * 100:.2f}%\n")
        return float(loss), len(X_test_tensor), {"accuracy": float(accuracy)}


# Start the client and connect to the Server
fl.client.start_client(
    server_address="20.244.23.91:8080",
    client=IDSClient().to_client()
)
