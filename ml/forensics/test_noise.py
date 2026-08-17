from noise_analyzer import NoiseAnalyzer

analyzer = NoiseAnalyzer()

result = analyzer.analyze(
    "../../backend/uploads/Anshika.jpg"
)

print("\nNoise Analysis Result:")
print(result)