import sys
sys.path.insert(0, 'src/analysis')
from Rudolp import get_rudolph_score

# Test cases
print("Testing Rudolph Score Calculator")
print("=" * 60)

# Test 1: Female, 10, 50m Freestyle, 30.4 seconds (should get 11 points)
score = get_rudolph_score('Female', 10, '50m Freestyle', 30.4)
print(f"Test 1: Female, Age 10, 50m Freestyle, 30.4s -> {score} points")

# Test 2: Male, 12, 100m Backstroke, 65.5 seconds
score = get_rudolph_score('Male', 12, '100m Backstroke', 65.5)
print(f"Test 2: Male, Age 12, 100m Backstroke, 65.5s -> {score} points")

# Test 3: Female, 14, 200m Freestyle, 125.0 seconds
score = get_rudolph_score('Female', 14, '200m Freestyle', 125.0)
print(f"Test 3: Female, Age 14, 200m Freestyle, 125.0s -> {score} points")

# Test 4: Male, 10, 50m Freestyle, 29.27 seconds (should get 20 points - fastest)
score = get_rudolph_score('Male', 10, '50m Freestyle', 29.27)
print(f"Test 4: Male, Age 10, 50m Freestyle, 29.27s -> {score} points")

# Test 5: Male, 10, 50m Freestyle, 29.00 seconds (faster than 20 points - still 20)
score = get_rudolph_score('Male', 10, '50m Freestyle', 29.00)
print(f"Test 5: Male, Age 10, 50m Freestyle, 29.00s -> {score} points")

# Test 6: Male, 10, 50m Freestyle, 50.00 seconds (too slow - should be None)
score = get_rudolph_score('Male', 10, '50m Freestyle', 50.00)
print(f"Test 6: Male, Age 10, 50m Freestyle, 50.00s -> {score} points")

print("\n" + "=" * 60)
print("Testing complete!")
