import re
from urllib.parse import urlparse

import cv2
import numpy as np


class QRAnalyzer:

    # =========================================================
    # SUSPICIOUS KEYWORDS
    # =========================================================

    SUSPICIOUS_KEYWORDS = [
        "login",
        "signin",
        "verify",
        "verification",
        "account",
        "password",
        "secure",
        "security",
        "confirm",
        "confirmation",
        "update",
        "wallet",
        "bank",
        "payment",
        "invoice",
        "claim",
        "reward",
        "prize",
        "urgent",
        "suspended",
        "unlock",
    ]

    # =========================================================
    # INITIALIZE
    # =========================================================

    def __init__(self, url_analyzer=None):

        self.url_analyzer = url_analyzer

        self.detector = cv2.QRCodeDetector()

    # =========================================================
    # CONTENT TYPE
    # =========================================================

    def detect_content_type(self, content: str):

        if not content:
            return "UNKNOWN"

        content = content.strip()

        # URL
        try:

            parsed = urlparse(content)

            if (
                parsed.scheme.lower() in {
                    "http",
                    "https"
                }
                and parsed.netloc
            ):

                return "URL"

        except Exception:
            pass

        # Email
        if re.match(
            r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
            content
        ):

            return "EMAIL"

        # Phone
        if re.match(
            r"^\+?[0-9][0-9\s\-\(\)]{7,}$",
            content
        ):

            return "PHONE"

        # WiFi
        if content.upper().startswith("WIFI:"):

            return "WIFI"

        # Payment / UPI
        if (
            content.lower().startswith("upi://")
            or "pa=" in content.lower()
        ):

            return "PAYMENT"

        return "TEXT"

    # =========================================================
    # URL ANALYSIS
    # =========================================================

    def analyze_url_content(self, content: str):

        if not self.url_analyzer:
            return None

        try:

            parsed = urlparse(content)

            if parsed.scheme.lower() not in {
                "http",
                "https"
            }:

                return None

            if not parsed.netloc:

                return None

            return self.url_analyzer.analyze(
                content
            )

        except Exception:

            return None

    # =========================================================
    # TEXT RISK
    # =========================================================

    def analyze_text_risk(self, content: str):

        content_lower = content.lower()

        matches = [
            keyword
            for keyword in self.SUSPICIOUS_KEYWORDS
            if keyword in content_lower
        ]

        score = min(
            len(matches) * 5,
            30
        )

        reasons = []

        if matches:

            reasons.append(
                "Suspicious QR content keywords detected: "
                + ", ".join(matches)
            )

        return {
            "risk_score": score,
            "keyword_matches": matches,
            "reasons": reasons
        }

    # =========================================================
    # NORMALIZE DECODED TEXT
    # =========================================================

    def normalize_decoded_text(self, value):

        if value is None:
            return ""

        if isinstance(value, bytes):

            try:
                value = value.decode(
                    "utf-8",
                    errors="ignore"
                )

            except Exception:
                return ""

        return str(value).strip()

    # =========================================================
    # TRY SINGLE QR DECODER
    # =========================================================

    def try_single_decode(self, image):

        try:

            result = self.detector.detectAndDecode(
                image
            )

            if isinstance(result, tuple):

                data = result[0]

            else:

                data = result

            data = self.normalize_decoded_text(
                data
            )

            if data:

                return data

        except Exception:
            pass

        return ""

    # =========================================================
    # TRY MULTI QR DECODER
    # =========================================================

    def try_multi_decode(self, image):

        try:

            result = self.detector.detectAndDecodeMulti(
                image
            )

            if not isinstance(result, tuple):
                return []

            if len(result) < 2:
                return []

            decoded_info = result[1]

            if not decoded_info:
                return []

            decoded_values = []

            for value in decoded_info:

                value = self.normalize_decoded_text(
                    value
                )

                if value:
                    decoded_values.append(
                        value
                    )

            return decoded_values

        except Exception:

            return []

    # =========================================================
    # IMAGE PREPROCESSING
    # =========================================================

    def generate_variants(self, image):

        variants = []

        # -----------------------------------------------------
        # ORIGINAL
        # -----------------------------------------------------

        variants.append(
            image
        )

        # -----------------------------------------------------
        # GRAYSCALE
        # -----------------------------------------------------

        try:

            gray = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2GRAY
            )

            variants.append(gray)

        except Exception:
            gray = None

        # -----------------------------------------------------
        # UPSCALE
        # -----------------------------------------------------

        try:

            height, width = image.shape[:2]

            max_dimension = max(
                height,
                width
            )

            scales = []

            if max_dimension < 800:
                scales = [2.0, 3.0, 4.0]

            elif max_dimension < 1500:
                scales = [1.5, 2.0]

            elif max_dimension < 3000:
                scales = [1.25, 1.5]

            else:
                scales = [1.25]

            for scale in scales:

                resized = cv2.resize(
                    image,
                    None,
                    fx=scale,
                    fy=scale,
                    interpolation=cv2.INTER_CUBIC
                )

                variants.append(
                    resized
                )

        except Exception:
            pass

        # -----------------------------------------------------
        # GRAYSCALE PROCESSING
        # -----------------------------------------------------

        if gray is not None:

            # OTSU
            try:

                _, otsu = cv2.threshold(
                    gray,
                    0,
                    255,
                    cv2.THRESH_BINARY
                    + cv2.THRESH_OTSU
                )

                variants.append(
                    otsu
                )

            except Exception:
                pass

            # ADAPTIVE THRESHOLD
            try:

                adaptive = cv2.adaptiveThreshold(
                    gray,
                    255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY,
                    31,
                    5
                )

                variants.append(
                    adaptive
                )

            except Exception:
                pass

            # INVERTED OTSU
            try:

                _, inverted = cv2.threshold(
                    gray,
                    0,
                    255,
                    cv2.THRESH_BINARY_INV
                    + cv2.THRESH_OTSU
                )

                variants.append(
                    inverted
                )

            except Exception:
                pass

            # CLAHE
            try:

                clahe = cv2.createCLAHE(
                    clipLimit=2.0,
                    tileGridSize=(8, 8)
                )

                enhanced = clahe.apply(
                    gray
                )

                variants.append(
                    enhanced
                )

            except Exception:
                pass

            # BLUR + OTSU
            try:

                blurred = cv2.GaussianBlur(
                    gray,
                    (3, 3),
                    0
                )

                _, blur_threshold = cv2.threshold(
                    blurred,
                    0,
                    255,
                    cv2.THRESH_BINARY
                    + cv2.THRESH_OTSU
                )

                variants.append(
                    blur_threshold
                )

            except Exception:
                pass

        # -----------------------------------------------------
        # REMOVE DUPLICATES BY SHAPE
        # -----------------------------------------------------

        unique_variants = []

        seen_shapes = set()

        for variant in variants:

            try:

                shape = variant.shape

                key = (
                    shape[0],
                    shape[1],
                    len(shape)
                )

                if key not in seen_shapes:

                    seen_shapes.add(key)

                    unique_variants.append(
                        variant
                    )

            except Exception:
                continue

        return unique_variants

    # =========================================================
    # DECODE QR
    # =========================================================

    def decode_qr(self, image):

        variants = self.generate_variants(
            image
        )

        # -----------------------------------------------------
        # TRY ALL VARIANTS
        # -----------------------------------------------------

        for variant in variants:

            # Single QR
            data = self.try_single_decode(
                variant
            )

            if data:

                return data

            # Multiple QR
            multi_data = self.try_multi_decode(
                variant
            )

            if multi_data:

                return multi_data[0]

        # -----------------------------------------------------
        # QR DETECTOR WITH WECHAT / CURVED SUPPORT
        # -----------------------------------------------------

        try:

            detector = cv2.QRCodeDetector()

            for variant in variants:

                try:

                    ok, decoded_info, points, _ = (
                        detector.detectAndDecodeMulti(
                            variant
                        )
                    )

                    if ok and decoded_info:

                        for value in decoded_info:

                            value = (
                                self.normalize_decoded_text(
                                    value
                                )
                            )

                            if value:

                                return value

                except Exception:
                    continue

        except Exception:
            pass

        return ""

    # =========================================================
    # MAIN ANALYSIS
    # =========================================================

    def analyze(
        self,
        image_path: str,
        filename: str = ""
    ):

        # -----------------------------------------------------
        # VALIDATE
        # -----------------------------------------------------

        if not image_path:

            raise ValueError(
                "Image path cannot be empty."
            )

        # -----------------------------------------------------
        # READ IMAGE
        # -----------------------------------------------------

        image = cv2.imread(
            image_path
        )

        if image is None:

            raise ValueError(
                "Unable to read the image."
            )

        # -----------------------------------------------------
        # IMAGE INFORMATION
        # -----------------------------------------------------

        height, width = image.shape[:2]

        # -----------------------------------------------------
        # DECODE
        # -----------------------------------------------------

        decoded_content = self.decode_qr(
            image
        )

        # -----------------------------------------------------
        # QR NOT FOUND
        # -----------------------------------------------------

        if not decoded_content:

            return {

                "filename": filename,

                "qr_detected": False,

                "decoded_content": "",

                "content_type": "UNKNOWN",

                "url_analysis": None,

                "keyword_matches": [],

                "risk_score": 0,

                "verdict": "QR_NOT_DETECTED",

                "reasons": [
                    "No readable QR code was detected."
                ],

                "image_width": width,

                "image_height": height,

                "analysis_status": "COMPLETED",

                "method": (
                    "QR Code Forensic Analysis"
                )
            }

        # -----------------------------------------------------
        # CONTENT TYPE
        # -----------------------------------------------------

        content_type = (
            self.detect_content_type(
                decoded_content
            )
        )

        # -----------------------------------------------------
        # INITIAL RISK
        # -----------------------------------------------------

        risk_score = 0

        reasons = []

        keyword_matches = []

        url_analysis = None

        # -----------------------------------------------------
        # URL
        # -----------------------------------------------------

        if content_type == "URL":

            url_analysis = (
                self.analyze_url_content(
                    decoded_content
                )
            )

            if url_analysis:

                risk_score = int(
                    url_analysis.get(
                        "risk_score",
                        0
                    )
                )

                keyword_matches = (
                    url_analysis.get(
                        "keyword_matches",
                        []
                    )
                )

                reasons.extend(
                    url_analysis.get(
                        "reasons",
                        []
                    )
                )

        # -----------------------------------------------------
        # TEXT / OTHER
        # -----------------------------------------------------

        else:

            text_result = (
                self.analyze_text_risk(
                    decoded_content
                )
            )

            risk_score = int(
                text_result.get(
                    "risk_score",
                    0
                )
            )

            keyword_matches = (
                text_result.get(
                    "keyword_matches",
                    []
                )
            )

            reasons.extend(
                text_result.get(
                    "reasons",
                    []
                )
            )

        # -----------------------------------------------------
        # PAYMENT
        # -----------------------------------------------------

        if content_type == "PAYMENT":

            risk_score += 10

            reasons.append(
                "QR code contains payment-related content."
            )

        # -----------------------------------------------------
        # WIFI
        # -----------------------------------------------------

        if content_type == "WIFI":

            reasons.append(
                "QR code contains Wi-Fi configuration data."
            )

        # -----------------------------------------------------
        # LIMIT
        # -----------------------------------------------------

        risk_score = min(
            max(
                risk_score,
                0
            ),
            100
        )

        # -----------------------------------------------------
        # VERDICT
        # -----------------------------------------------------

        if risk_score >= 70:

            verdict = "HIGH_RISK"

        elif risk_score >= 35:

            verdict = "MEDIUM_RISK"

        else:

            verdict = "LOW_RISK"

        # -----------------------------------------------------
        # DEFAULT REASON
        # -----------------------------------------------------

        if not reasons:

            reasons.append(
                "QR code content was decoded successfully "
                "with no significant suspicious indicators."
            )

        # -----------------------------------------------------
        # FINAL RESULT
        # -----------------------------------------------------

        return {

            "filename": filename,

            "qr_detected": True,

            "decoded_content": decoded_content,

            "content_type": content_type,

            "url_analysis": url_analysis,

            "keyword_matches": keyword_matches,

            "risk_score": risk_score,

            "verdict": verdict,

            "reasons": reasons,

            "image_width": width,

            "image_height": height,

            "analysis_status": "COMPLETED",

            "method": (
                "QR Code Forensic Analysis"
            )
        }