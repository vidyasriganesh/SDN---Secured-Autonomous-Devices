import random
import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim

torch.manual_seed(42)
np.random.seed(42)
random.seed(42)

print("\n--- Starting the AI Training Process ---")

from fl.data_prep import (
    train_loader,
    test_loader,
    X_train_tensor,
    X_test_tensor
)

# Number of input features
input_size = X_train_tensor.shape[1]


# -------------------------------------------------
# LSTM MODEL
# -------------------------------------------------

class LSTM_IDS(nn.Module):

    def __init__(self, input_dim):
        super(LSTM_IDS, self).__init__()

        self.lstm = nn.LSTM(
            input_dim,
            hidden_size=64,
            num_layers=2,
            dropout=0.2,
            batch_first=True
        )

        self.fc = nn.Linear(64, 1)

        self.sigmoid = nn.Sigmoid()

    def forward(self, x):

        x = x.unsqueeze(1)

        lstm_out, _ = self.lstm(x)

        final_prediction = self.sigmoid(
            self.fc(lstm_out[:, -1, :])
        )

        return final_prediction


# -------------------------------------------------
# MODEL INITIALIZATION
# -------------------------------------------------

model = LSTM_IDS(input_dim=input_size)

criterion = nn.BCELoss()

optimizer = optim.Adam(
    model.parameters(),
    lr=0.001
)

epochs = 5


# -------------------------------------------------
# TRAIN ONLY WHEN THIS FILE IS EXECUTED DIRECTLY
# -------------------------------------------------

if __name__ == "__main__":

    print(f"\nTraining the LSTM Model on {len(X_train_tensor)} network packets...")

    for epoch in range(epochs):

        model.train()

        total_loss = 0.0

        for X_batch, y_batch in train_loader:

            predictions = model(X_batch)

            loss = criterion(predictions, y_batch)

            optimizer.zero_grad()

            loss.backward()

            optimizer.step()

            total_loss += loss.item()

        average_loss = total_loss / len(train_loader)

        print(
            f"Epoch [{epoch+1}/{epochs}] - Average Loss: {average_loss:.4f}"
        )

    print("\nTesting the AI on data it has never seen before...")

    model.eval()

    correct_guesses = 0

    total_tests = 0

    with torch.no_grad():

        for X_batch, y_batch in test_loader:

            predictions = model(X_batch)

            predicted = (predictions >= 0.5).float()

            correct_guesses += (
                predicted == y_batch
            ).sum().item()

            total_tests += y_batch.size(0)

    accuracy = (correct_guesses / total_tests) * 100

    print("\n--- FINAL RESULTS ---")

    print(
        f"The LSTM accurately classified {correct_guesses} out of {total_tests} network packets."
    )

    print(f"Overall Accuracy: {accuracy:.2f}%\n")
