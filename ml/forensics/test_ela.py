from ela_analyzer import ELAAnalyzer


analyzer = ELAAnalyzer()

result = analyzer.analyze(
    "../../backend/uploads/Anshika.jpg"
)

print("\nELA Analysis Result:")
print(result)