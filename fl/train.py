import torch
import torch.nn as nn
import torch.optim as optim

from fl.model import LSTM_IDS

from fl.data_prep import (
    train_loader,
    test_loader,
    input_size
)
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
print("\n========== TRAINING ==========\n")

model = LSTM_IDS(input_size)

criterion = nn.BCELoss()

optimizer = optim.Adam(
    model.parameters(),
    lr=0.001
)

epochs = 15

for epoch in range(epochs):

    model.train()

    running_loss = 0

    for X_batch, y_batch in train_loader:

        predictions = model(X_batch)

        loss = criterion(predictions, y_batch)

        optimizer.zero_grad()

        loss.backward()

        optimizer.step()

        running_loss += loss.item()

    print(
        f"Epoch [{epoch+1}/{epochs}]  Loss : {running_loss/len(train_loader):.4f}"
    )

torch.save(
    model.state_dict(),
    "models/model.pth"
)

print("\nModel Saved Successfully")
print("\n========== MODEL EVALUATION ==========\n")

model.eval()

all_predictions = []
all_labels = []

with torch.no_grad():

    for X_batch, y_batch in test_loader:

        outputs = model(X_batch)

        predictions = (outputs >= 0.5).float()

        all_predictions.extend(predictions.cpu().numpy())

        all_labels.extend(y_batch.cpu().numpy())

import numpy as np

all_predictions = np.array(all_predictions).flatten()
all_labels = np.array(all_labels).flatten()

accuracy = accuracy_score(all_labels, all_predictions)
precision = precision_score(all_labels, all_predictions)
recall = recall_score(all_labels, all_predictions)
f1 = f1_score(all_labels, all_predictions)

cm = confusion_matrix(all_labels, all_predictions)

print("="*60)
print("MODEL PERFORMANCE")
print("="*60)
print(f"Accuracy  : {accuracy*100:.2f}%")
print(f"Precision : {precision*100:.2f}%")
print(f"Recall    : {recall*100:.2f}%")
print(f"F1 Score  : {f1*100:.2f}%")

print("\nConfusion Matrix")
print(cm)

print("\nClassification Report")
print(classification_report(all_labels, all_predictions))
