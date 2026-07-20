from fl.feature_generator import FeatureGenerator
from fl.predictor import Predictor

print("\n====== COMPLETE AI PIPELINE TEST ======\n")

packet = {
    "transport": "TCP",
    "protocol": 6
}

generator = FeatureGenerator()

predictor = Predictor()

features = generator.generate(packet)

print("Generated Features:", len(features))

prediction = predictor.predict(features)

print("Prediction :", prediction)
