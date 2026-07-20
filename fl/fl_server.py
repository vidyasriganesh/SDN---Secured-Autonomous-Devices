import flwr as fl
import numpy as np
import torch

from collections import OrderedDict
from typing import List, Tuple, Dict, Optional

from flwr.common import (
    FitRes,
    Parameters,
    parameters_to_ndarrays,
    ndarrays_to_parameters,
)

from fl.local_ids import model

print("\n--- Starting the Secure Cloud Server (with Anti-Poisoning) ---")


class SecureStrategy(fl.server.strategy.FedAvg):

    def aggregate_fit(
        self,
        server_round: int,
        results: List[Tuple[fl.server.client_proxy.ClientProxy, FitRes]],
        failures: List[BaseException],
    ) -> Tuple[Optional[Parameters], Dict[str, fl.common.Scalar]]:

        print("\n=======================================================")
        print(f"[Server] Round {server_round}: Running Anti-Poisoning Check...")

        # Receive weights from clients
        client_weights = [
            parameters_to_ndarrays(res.parameters)
            for _, res in results
        ]

        print(
            f"[Server] Received AI weights from {len(client_weights)} connected IoT Node(s)."
        )

        # Anti-poisoning: compare each client to the CURRENT global model (trusted reference)
        def flatten(ndarrays):
            return np.concatenate([w.flatten() for w in ndarrays])

        current_global = flatten([val.cpu().numpy() for val in model.state_dict().values()])

        similarities = []
        for w in client_weights:
            flat_w = flatten(w)
            sim = np.dot(flat_w, current_global) / (
                np.linalg.norm(flat_w) * np.linalg.norm(current_global) + 1e-10
            )
            similarities.append(sim)

        print(f"[Server] Cosine similarities to current global model: {[round(s, 4) for s in similarities]}")

        threshold = 0.3
        clean_results = []
        for (client, res), sim in zip(results, similarities):
            if sim >= threshold:
                clean_results.append((client, res))
            else:
                print(f"[Server] REJECTED client (similarity {sim:.4f} below threshold {threshold}) — likely poisoned")

        if len(clean_results) == 0:
            print("[Server] WARNING: all clients rejected this round, skipping aggregation (keeping previous global model)")
            print("=======================================================\n")
            return None, {}

        print(f"[Server] Accepted {len(clean_results)}/{len(results)} client update(s) for aggregation")
        print("=======================================================\n")

        aggregated_parameters, metrics = super().aggregate_fit(
            server_round,
            clean_results,
            failures,
        )
        # Save the new global model
        if aggregated_parameters is not None:

            aggregated_ndarrays = parameters_to_ndarrays(
                aggregated_parameters
            )

            params_dict = zip(
                model.state_dict().keys(),
                aggregated_ndarrays,
            )

            state_dict = OrderedDict(
                {
                    k: torch.tensor(v)
                    for k, v in params_dict
                }
            )

            model.load_state_dict(state_dict)

            torch.save(
                model.state_dict(),
                "models/global_model.pth",
            )

            print("===================================")
            print("Global Model Saved Successfully")
            print("Saved to models/global_model.pth")
            print("===================================")

        return aggregated_parameters, metrics


initial_ndarrays = [val.cpu().numpy() for val in model.state_dict().values()]
initial_parameters = ndarrays_to_parameters(initial_ndarrays)

strategy = SecureStrategy(
    fraction_fit=1.0,
    fraction_evaluate=1.0,
    min_fit_clients=2,
    min_evaluate_clients=2,
    min_available_clients=2,
    initial_parameters=initial_parameters,
)

fl.server.start_server(
    server_address="0.0.0.0:8080",
    config=fl.server.ServerConfig(num_rounds=20),
    strategy=strategy,
)
