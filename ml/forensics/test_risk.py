from manipulation_analyzer import ManipulationAnalyzer
from risk_engine import RiskEngine


image_path = "../../backend/uploads/Anshika.jpg"


analyzer = ManipulationAnalyzer()

forensic_result = analyzer.analyze(
    image_path
)


risk_engine = RiskEngine()

risk_result = risk_engine.calculate_score(
    forensic_result
)


print("\nForensic Result:")
print(forensic_result)

print("\nRisk Result:")
print(risk_result)