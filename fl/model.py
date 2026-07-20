import torch
import torch.nn as nn


class LSTM_IDS(nn.Module):

    def __init__(self, input_dim):

        super(LSTM_IDS, self).__init__()

        self.lstm = nn.LSTM(
            input_size=input_dim,
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

        output = self.fc(lstm_out[:, -1, :])

        output = self.sigmoid(output)

        return output
