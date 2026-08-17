from manipulation_analyzer import ManipulationAnalyzer


analyzer = ManipulationAnalyzer()

result = analyzer.analyze(
    "../../backend/uploads/Anshika.jpg"
)

print("\nManipulation Analysis Result:")
print(result)