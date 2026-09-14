import re
from pathlib import Path

class MessageAnalyzer:
    """
    Performs basic forensic analysis of text messages.
    
    This analyzer indentifies structural and potentially suspicious
    characteristics. It is not a trained AI-generated text detector.
    """

    SUSPICIOUS_KEYWORDS = [
        "urgent",
        "verify your account",
        "click here",
        "click the link",
        "password",
        "otp",
        "bank account",
        "credit card",
        "limited time",
        "act now",
        "congratulations",
        "you have won",
        "claim now",
        "send money",
        "payment required",
        "login",
        "confirm your identity",
    ]

    URL_PATTERN = r"https?://[^\s]+|www\.[^\s]+"
    EMAIL_PATTERN = r"\b[A-Za-z0-9._]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    PHONE_PATTERN = r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)"

    def analyze(self, text: str):
        if not isinstance(text, str):
            raise TypeError("Text input must be a string.")

        text = text.strip()

        if not text:
            raise ValueError("Text cannot be empty.")

        words = re.findall(r"\b[\w'-]+\b", text)
        urls = re.findall(self.URL_PATTERN, text, flags=re.IGNORECASE)
        emails = re.findall(self.EMAIL_PATTERN, text)
        phones = re.findall(self.PHONE_PATTERN, text)

        lowercase_text =  text.lower()

        detected_keywords = []

        for keyword in self.SUSPICIOUS_KEYWORDS:
            if keyword in lowercase_text:
                detected_keywords.append(keyword)

        exclamation_count = text.count("!")
        question_count = text.count("?")
        uppercase_letters = sum(1 for char in text if char.isupper())
        alphabetic_letters = sum(1 for char in text if char.isalpha())

        uppercase_ratio =(
            uppercase_letters / alphabetic_letters
            if alphabetic_letters > 0
            else 0
        )        

        repeated_punctuation = bool(
            re.search(r"[!?.,]{3,}",text)
        )

        score = 0
        reasons = []

        if detected_keywords:
            keyword_score = min(len(detected_keywords) * 5, 25)
            score += keyword_score
            reasons.append(
                f"Detected {len(detected_keywords)} suspicious keyword pattern(s)."
            )

        if urls:
            score += min(len(urls) * 10, 20)
            reasons.append(
                f"Detected {len(urls)} URL/link(s)."
            ) 

        if emails:
            score += 5
            reasons.append(
                f"Detected {len(emails)} email address(es)."
            )  

        if phones:
            score += 5
            reasons.append(
                f"Detected {len(phones)} phone number(s)."
            )   

        if exclamation_count >= 3:
            score += 10
            reasons.append(
                "Excessive exclamation marks detected."
            ) 

        if repeated_punctuation:
            score += 5
            reasons.append(
                "Repeated punctaution patterns detected."
            )  

        if uppercase_ratio >= 0.40 and alphabetic_letters >= 10:
            score += 10
            reasons.append(
                "High uppercase-letter ratio detected."
            )               

        score = min(score, 100)

        if score < 25:
            verdict = "LOW_RISK"
        elif score < 60:
            verdict = "MEDIUM_Risk"
        else:
            verdict = "HIGH_RISK"

        return {
            "method": "Message Forensic Analysis",
            "analysis_status": "COMPLETED",
            "text_length": len(text),
            "word_count": len(words),
            "character_count": len(text),
            "url_count": len(urls),
            "email_count": len(emails),
            "phone_ count": len(phones),
            "suspicious_keywords": detected_keywords,
            "exclamation_count": exclamation_count,
            "question_count": question_count,
            "uppercase_ratio": round(uppercase_ratio, 3),
            "repeated_punctuation": repeated_punctuation,
            "risk_score": round(score, 2),
            "verdict": verdict,
            "reasons": reasons,
        }                