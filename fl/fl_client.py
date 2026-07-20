import argparse
import numpy as np
import torch
import flwr as fl
from collections import OrderedDict

# Import the Brain and the Data from your previous files!
from fl.local_ids import LSTM_IDS, model, optimizer, criterion
from fl.data_prep import X_train_tensor, y_train_tensor, X_test_tensor, y_test_tensor, train_loader

# ---------------------------------------------------------------------------
# Command-line args: run this file normally for an honest client, or with
# --malicious to simulate a poisoning attacker for testing the server's
# anti-poisoning (cosine similarity) defense.
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument(
    "--malicious",
    action="store_true",
    help="Run this client as a malicious/poisoning attacker",
)
parser.add_argument(
    "--attack",
    type=str,
    default="sign_flip",
    choices=["sign_flip", "gaussian_noise", "scaling"],
    help="Which poisoning attack to simulate when --malicious is set",
)
parser.add_argument(
    "--server",
    type=str,
    default="20.244.23.91:8080",
    help="Server address (ip:port)",
)
args = parser.parse_args()

if args.malicious:
    print(f"\n--- Starting Federated Learning Client (MALICIOUS - {args.attack}) ---")
else:
    print("\n--- Starting Federated Learning Client (Honest Edge Node) ---")


def poison_parameters(parameters, attack_type):
    """Corrupt the trained parameters to simulate a model-poisoning attack."""
    poisoned = []
    for arr in parameters:
        if attack_type == "sign_flip":
            # Flip the sign of every weight -> pushes the update in the
            # opposite direction of real training, strongly disagreeing
            # with the honest global model direction.
            poisoned.append(-arr)
        elif attack_type == "gaussian_noise":
            # Replace weights with pure random noise of similar scale.
            noise = np.random.normal(
                loc=0.0, scale=np.std(arr) + 1e-6, size=arr.shape
            ).astype(arr.dtype)
            poisoned.append(noise)
        elif attack_type == "scaling":
            # Boost the update by a large factor (a classic "scaling attack"
            # used to dominate FedAvg averaging).
            poisoned.append(arr * 50.0)
        else:
            poisoned.append(arr)
    return poisoned


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

    # 3. Train the AI locally
    def fit(self, parameters, config):
        self.set_parameters(parameters)
        model.train()
        for epoch in range(3):
            for X_batch, y_batch in train_loader:
                predictions = model(X_batch)
                loss = criterion(predictions, y_batch)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

        updated_parameters = self.get_parameters(config={})

        if args.malicious:
            print(f"[MALICIOUS] Poisoning local update using '{args.attack}' attack before sending...")
            updated_parameters = poison_parameters(updated_parameters, args.attack)

        return updated_parameters, len(X_train_tensor), {}

    # 4. Test the AI locally
    def evaluate(self, parameters, config):
        self.set_parameters(parameters)
        model.eval()
        with torch.no_grad():
            test_predictions = model(X_test_tensor)
            correct_guesses = test_predictions.round().eq(y_test_tensor).sum().item()
            accuracy = float(correct_guesses) / len(y_test_tensor)
            loss = criterion(test_predictions, y_test_tensor).item()

        print(f"\n[Client] Evaluation Accuracy: {accuracy * 100:.2f}%\n")
        return float(loss), len(X_test_tensor), {"accuracy": float(accuracy)}


# Start the client and connect to the Server
fl.client.start_client(
    server_address=args.server,
    client=IDSClient().to_client()
)
