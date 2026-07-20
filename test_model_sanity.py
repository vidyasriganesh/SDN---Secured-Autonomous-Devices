import sys
sys.path.append('.')
from fl.predictor import Predictor

predictor = Predictor()

print("\n--- TEST 1: All zeros ---")
result = predictor.predict([0]*16)
print(result)

print("\n--- TEST 2: All ones ---")
result = predictor.predict([1]*16)
print(result)

print("\n--- TEST 3: Large extreme values (simulating heavy attack traffic) ---")
result = predictor.predict([65000, 120000000, 2000, 200000, 13000, 1400, 3400,
                             2000000000, 3000000, 280, 13000, 1400, 1, 1, 3400, 200000])
print(result)

print("\n--- TEST 4: Random small values ---")
import random
result = predictor.predict([random.uniform(0, 10) for _ in range(16)])
print(result)
