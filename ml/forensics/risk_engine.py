class RiskEngine:

    def calculate_score(
        self,
        forensic_result: dict,
        detector_result: dict = None
    ):
        score = 0.0
        reasons = []

        metadata = forensic_result.get("metadata", {})
        ela = forensic_result.get("ela", {})
        noise = forensic_result.get("noise", {})

        if not metadata.get("has_exif", False):
            score += 10
            reasons.append(
                "No EXIF metadata was found."
            )

        mean_difference = float(
            ela.get("mean_difference", 0)
        )

        if mean_difference > 20:
            score += 30
            reasons.append(
                "Elevated ELA difference detected."
            )
        elif mean_difference > 10:
            score += 15
            reasons.append(
                "Moderate ELA difference detected."
            )

        noise_std = float(
            noise.get("noise_std", 0)
        )

        if noise_std > 25:
            score += 30
            reasons.append(
                "High image noise variation detected."
            )
        elif noise_std > 15:
            score += 15
            reasons.append(
                "Moderate image noise variation detected."
            )

        score = min(score, 100)

        if score < 25:
            verdict = "LOW_RISK"
        elif score < 60:
            verdict = "MEDIUM_RISK"
        else:
            verdict = "HIGH_RISK"

        return {
            "risk_score": round(score, 2),
            "verdict": verdict,
            "reasons": reasons
        }