class RiskEngine:

    def calculate_score(
        self,
        forensic_result: dict,
        ml_result: dict | None = None
    ):
        metadata = forensic_result.get("metadata", {})
        ela = forensic_result.get("ela", {})
        noise = forensic_result.get("noise", {})

        metadata_score = 0
        ela_score = 0
        noise_score = 0

        reasons = []


        if not metadata.get("has_exif", False):
            metadata_score = 5
            reasons.append("No EXIF metadata was found.")

    
        mean_difference = float(
            ela.get("mean_difference", 0)
        )

        if mean_difference > 50:
            ela_score = 40
            reasons.append("Very high ELA difference detected.")

        elif mean_difference > 30:
            ela_score = 30
            reasons.append("High ELA difference detected.")

        elif mean_difference > 15:
            ela_score = 15
            reasons.append("Moderate ELA difference detected.")


        noise_std = float(
            noise.get("noise_std", 0)
        )

        if noise_std > 30:
            noise_score = 30
            reasons.append("High image noise variation detected.")

        elif noise_std > 15:
            noise_score = 15
            reasons.append("Moderate image noise variation detected.")

        score = min(
            metadata_score + ela_score + noise_score,
            100
        )

        if score < 25:
            verdict = "LOW_RISK"

        elif score < 60:
            verdict = "MEDIUM_RISK"

        else:
            verdict = "HIGH_RISK"


        return {
            "risk_score": round(score, 2),
            "verdict": verdict,
            "component_scores": {
                "metadata": metadata_score,
                "ela": ela_score,
                "noise": noise_score
            },
            "reasons": reasons
        }