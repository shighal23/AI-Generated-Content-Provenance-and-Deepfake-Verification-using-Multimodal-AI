from pathlib import Path

from ml.forensics.manipulation_analyzer import ManipulationAnalyzer
from ml.forensics.risk_engine import RiskEngine


def main():
    image_path = Path("backend/uploads/Anshika.jpg")

    print("=" * 50)
    print("DeepVerify-X - Risk Engine Test")
    print("=" * 50)

    if not image_path.exists():
        print(f"ERROR: IMAGE not found: {image_path}")
        return

    print(f"Image: {image_path}")
    print("\nRunning forensic analysis...")

    try:
        analyzer = ManipulationAnalyzer()
        forensic_result = analyzer.analyze(str(image_path))

        print("\nForensic Result:")
        print(forensic_result)

        risk_engine = RiskEngine()
        risk_result = risk_engine.calculate_score(
            forensic_result
        )

        print("\n" + "=" * 50)
        print("RISK ASSESSMENT")
        print("=" * 50)

        print(f"Risk Score   : {risk_result['risk_score']}")
        print(f"Verdict      : {risk_result['verdict']}")

        print("\nReason:")

        for reason in risk_result["reasons"]:
            print(f"- {reason}")

        print("=" * 50)

    except Exception as e:
        print("\nERROR during risk analysis:")
        print(e)

if __name__ == "__main__":
    main()