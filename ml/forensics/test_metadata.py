from metadata_analyzer import MetadataAnalyzer


analyzer = MetadataAnalyzer()

result = analyzer.analyze(
    "../../backend/uploads/Anshika.jpg"
)

print("\nMetadata Analysis Result:")
print(result)