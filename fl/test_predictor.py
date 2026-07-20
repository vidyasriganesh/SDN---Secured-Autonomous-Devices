from fl.predictor import Predictor
import torch
from fl.data_prep import X_test_tensor

print("\n===== Testing Predictor =====")

predictor = Predictor()

sample = X_test_tensor[0].tolist()

result = predictor.predict(sample)

print("\nPrediction:", result)
