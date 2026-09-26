import re
from urllib.parse import urlparse, parse_qsl, unquote


class URLAnalyzer:

    # =========================================================
    # SUSPICIOUS KEYWORDS
    # =========================================================

    SUSPICIOUS_KEYWORDS = [
        "login",
        "signin",
        "sign-in",
        "verify",
        "verification",
        "account",
        "password",
        "passwd",
        "secure",
        "security",
        "confirm",
        "confirmation",
        "update",
        "wallet",
        "bank",
        "banking",
        "payment",
        "invoice",
        "claim",
        "reward",
        "prize",
        "urgent",
        "suspended",
        "suspend",
        "unlock",
        "limited",
        "security-check",
        "recover",
        "reset",
    ]

    # =========================================================
    # KNOWN URL SHORTENING SERVICES
    # =========================================================

    SHORTENED_DOMAINS = {
        "bit.ly",
        "tinyurl.com",
        "t.co",
        "goo.gl",
        "ow.ly",
        "is.gd",
        "buff.ly",
        "cutt.ly",
        "shorturl.at",
        "rb.gy",
        "rebrand.ly",
        "tiny.cc",
        "lnkd.in",
        "s.id",
        "soo.gd",
    }

    # =========================================================
    # SUSPICIOUS TLDs
    # =========================================================

    SUSPICIOUS_TLDS = {
        ".tk",
        ".ml",
        ".ga",
        ".cf",
        ".gq",
        ".top",
        ".xyz",
        ".click",
        ".link",
        ".work",
        ".zip",
        ".mov",
    }

    # =========================================================
    # SUSPICIOUS QUERY KEYWORDS
    # =========================================================

    SUSPICIOUS_QUERY_KEYWORDS = {
        "redirect",
        "url",
        "target",
        "dest",
        "destination",
        "next",
        "return",
        "redirect_url",
        "redirect_uri",
        "callback",
        "continue",
    }

    # =========================================================
    # URL ANALYSIS
    # =========================================================

    def analyze(self, url: str):

        # -----------------------------------------------------
        # VALIDATE INPUT
        # -----------------------------------------------------

        if not isinstance(url, str):
            raise ValueError("URL must be a string.")

        url = url.strip()

        if not url:
            raise ValueError("URL cannot be empty.")

        # -----------------------------------------------------
        # URL PARSING
        # -----------------------------------------------------

        try:
            parsed = urlparse(url)
        except Exception as exc:
            raise ValueError(
                f"Unable to parse URL: {str(exc)}"
            )

        scheme = parsed.scheme.lower()
        hostname = (parsed.hostname or "").lower()
        path = parsed.path or ""
        query = parsed.query or ""

        # -----------------------------------------------------
        # SCHEME VALIDATION
        # -----------------------------------------------------

        if not scheme:
            raise ValueError(
                "URL must contain a scheme such as http:// or https://."
            )

        if scheme not in {"http", "https"}:
            raise ValueError(
                "Only HTTP and HTTPS URLs are supported."
            )

        # -----------------------------------------------------
        # DOMAIN VALIDATION
        # -----------------------------------------------------

        if not hostname:
            raise ValueError(
                "URL must contain a valid domain or IP address."
            )

        # -----------------------------------------------------
        # NORMALIZED URL
        # -----------------------------------------------------

        decoded_url = unquote(url)
        url_lower = decoded_url.lower()

        # -----------------------------------------------------
        # IP ADDRESS CHECK
        # -----------------------------------------------------

        ipv4_pattern = re.compile(
            r"^(?:\d{1,3}\.){3}\d{1,3}$"
        )

        is_ip_address = bool(
            ipv4_pattern.match(hostname)
        )

        # -----------------------------------------------------
        # DOMAIN INFORMATION
        # -----------------------------------------------------

        hostname_without_www = hostname

        if hostname_without_www.startswith("www."):
            hostname_without_www = hostname_without_www[4:]

        # -----------------------------------------------------
        # SHORTENED URL CHECK
        # -----------------------------------------------------

        is_shortened_url = (
            hostname_without_www
            in self.SHORTENED_DOMAINS
        )

        # -----------------------------------------------------
        # HTTPS CHECK
        # -----------------------------------------------------

        is_https = scheme == "https"

        # -----------------------------------------------------
        # PORT CHECK
        # -----------------------------------------------------

        try:
            port = parsed.port
        except ValueError:
            raise ValueError(
                "URL contains an invalid port."
            )

        unusual_port = (
            port is not None
            and port not in {80, 443}
        )

        # -----------------------------------------------------
        # USER INFO / @ SYMBOL CHECK
        # -----------------------------------------------------

        has_username = parsed.username is not None
        has_password = parsed.password is not None

        has_at_symbol = (
            has_username
            or has_password
        )

        # -----------------------------------------------------
        # DOMAIN HYPHEN CHECK
        # -----------------------------------------------------

        has_multiple_hyphens = (
            hostname.count("-") >= 2
        )

        # -----------------------------------------------------
        # SUBDOMAIN CHECK
        # -----------------------------------------------------

        subdomain_count = 0

        if hostname and not is_ip_address:

            parts = hostname.split(".")

            if len(parts) > 2:

                subdomain_count = len(parts) - 2

        excessive_subdomains = (
            subdomain_count >= 3
        )

        # -----------------------------------------------------
        # PUNYCODE CHECK
        # -----------------------------------------------------

        has_punycode = (
            "xn--" in hostname
        )

        # -----------------------------------------------------
        # DOMAIN LENGTH CHECK
        # -----------------------------------------------------

        long_domain = (
            len(hostname) > 50
        )

        # -----------------------------------------------------
        # SUSPICIOUS TLD CHECK
        # -----------------------------------------------------

        suspicious_tld = False

        if not is_ip_address:

            for tld in self.SUSPICIOUS_TLDS:

                if hostname.endswith(tld):

                    suspicious_tld = True
                    break

        # -----------------------------------------------------
        # PATH KEYWORD MATCHING
        # -----------------------------------------------------

        suspicious_path_keywords = [
            keyword
            for keyword in self.SUSPICIOUS_KEYWORDS
            if keyword in path.lower()
        ]

        # -----------------------------------------------------
        # FULL URL KEYWORD MATCHING
        # -----------------------------------------------------

        keyword_matches = [
            keyword
            for keyword in self.SUSPICIOUS_KEYWORDS
            if keyword in url_lower
        ]

        # Remove duplicates while preserving order
        keyword_matches = list(
            dict.fromkeys(keyword_matches)
        )

        # -----------------------------------------------------
        # QUERY PARAMETERS
        # -----------------------------------------------------

        query_parameters = {}

        if query:

            try:

                query_items = parse_qsl(
                    query,
                    keep_blank_values=True
                )

                for key, value in query_items:

                    query_parameters[key] = value

            except Exception:

                query_parameters = {}

        # -----------------------------------------------------
        # SUSPICIOUS QUERY KEYWORDS
        # -----------------------------------------------------

        suspicious_query_keywords = []

        for keyword in self.SUSPICIOUS_QUERY_KEYWORDS:

            if keyword in query.lower():

                suspicious_query_keywords.append(
                    keyword
                )

        # -----------------------------------------------------
        # QUERY VALUES WITH SUSPICIOUS CONTENT
        # -----------------------------------------------------

        suspicious_query_values = []

        for key, value in query_parameters.items():

            combined = (
                f"{key}={value}"
            ).lower()

            for keyword in self.SUSPICIOUS_KEYWORDS:

                if keyword in combined:

                    suspicious_query_values.append(
                        keyword
                    )

        suspicious_query_values = list(
            dict.fromkeys(
                suspicious_query_values
            )
        )

        # -----------------------------------------------------
        # ENCODED URL CHECK
        # -----------------------------------------------------

        has_encoded_content = (
            "%" in url
        )

        # -----------------------------------------------------
        # DOUBLE SLASH PATH CHECK
        # -----------------------------------------------------

        has_double_slash_path = (
            "//" in path
        )

        # -----------------------------------------------------
        # URL LENGTH CHECK
        # -----------------------------------------------------

        very_long_url = (
            len(url) > 200
        )

        # =====================================================
        # RISK SCORE
        # =====================================================

        risk_score = 0

        reasons = []

        # -----------------------------------------------------
        # IP ADDRESS
        # -----------------------------------------------------

        if is_ip_address:

            risk_score += 25

            reasons.append(
                "URL uses an IP address instead of a normal domain."
            )

        # -----------------------------------------------------
        # SHORTENED URL
        # -----------------------------------------------------

        if is_shortened_url:

            risk_score += 15

            reasons.append(
                "URL uses a known URL shortening service."
            )

        # -----------------------------------------------------
        # HTTPS
        # -----------------------------------------------------

        if not is_https:

            risk_score += 10

            reasons.append(
                "URL does not use HTTPS."
            )

        # -----------------------------------------------------
        # SUSPICIOUS KEYWORDS
        # -----------------------------------------------------

        if keyword_matches:

            keyword_score = min(
                len(keyword_matches) * 5,
                25
            )

            risk_score += keyword_score

            reasons.append(
                "Suspicious URL keywords detected: "
                + ", ".join(keyword_matches)
            )

        # -----------------------------------------------------
        # SUSPICIOUS QUERY
        # -----------------------------------------------------

        if suspicious_query_keywords:

            risk_score += min(
                len(suspicious_query_keywords) * 5,
                15
            )

            reasons.append(
                "Suspicious query parameters detected: "
                + ", ".join(suspicious_query_keywords)
            )

        # -----------------------------------------------------
        # UNUSUAL PORT
        # -----------------------------------------------------

        if unusual_port:

            risk_score += 10

            reasons.append(
                f"URL uses an unusual port: {port}."
            )

        # -----------------------------------------------------
        # EXCESSIVE SUBDOMAINS
        # -----------------------------------------------------

        if excessive_subdomains:

            risk_score += 10

            reasons.append(
                "URL contains an unusually large number of subdomains."
            )

        # -----------------------------------------------------
        # @ SYMBOL / USERINFO
        # -----------------------------------------------------

        if has_at_symbol:

            risk_score += 15

            reasons.append(
                "URL contains user information before the destination "
                "domain, which can obscure the actual destination."
            )

        # -----------------------------------------------------
        # MULTIPLE HYPHENS
        # -----------------------------------------------------

        if has_multiple_hyphens:

            risk_score += 5

            reasons.append(
                "Domain contains multiple hyphens."
            )

        # -----------------------------------------------------
        # PUNYCODE
        # -----------------------------------------------------

        if has_punycode:

            risk_score += 10

            reasons.append(
                "Domain contains punycode, which may represent "
                "non-ASCII characters."
            )

        # -----------------------------------------------------
        # SUSPICIOUS TLD
        # -----------------------------------------------------

        if suspicious_tld:

            risk_score += 10

            reasons.append(
                "Domain uses a TLD commonly associated with "
                "higher-risk or disposable domains."
            )

        # -----------------------------------------------------
        # VERY LONG DOMAIN
        # -----------------------------------------------------

        if long_domain:

            risk_score += 5

            reasons.append(
                "Domain name is unusually long."
            )

        # -----------------------------------------------------
        # ENCODED CONTENT
        # -----------------------------------------------------

        if has_encoded_content:

            risk_score += 5

            reasons.append(
                "URL contains encoded characters."
            )

        # -----------------------------------------------------
        # DOUBLE SLASH PATH
        # -----------------------------------------------------

        if has_double_slash_path:

            risk_score += 5

            reasons.append(
                "URL path contains an unusual double slash."
            )

        # -----------------------------------------------------
        # VERY LONG URL
        # -----------------------------------------------------

        if very_long_url:

            risk_score += 5

            reasons.append(
                "URL is unusually long."
            )

        # -----------------------------------------------------
        # SUSPICIOUS QUERY VALUES
        # -----------------------------------------------------

        if suspicious_query_values:

            risk_score += min(
                len(suspicious_query_values) * 3,
                10
            )

            reasons.append(
                "Suspicious keywords were detected inside "
                "query parameter values."
            )

        # -----------------------------------------------------
        # LIMIT SCORE
        # -----------------------------------------------------

        risk_score = min(
            max(risk_score, 0),
            100
        )

        # =====================================================
        # VERDICT
        # =====================================================

        if risk_score >= 70:

            verdict = "HIGH_RISK"

        elif risk_score >= 35:

            verdict = "MEDIUM_RISK"

        else:

            verdict = "LOW_RISK"

        # -----------------------------------------------------
        # DEFAULT MESSAGE
        # -----------------------------------------------------

        if not reasons:

            reasons.append(
                "No significant suspicious URL indicators detected."
            )

        # =====================================================
        # FINAL RESULT
        # =====================================================

        return {

            "url": url,

            "scheme": scheme,

            "domain": hostname,

            "path": path,

            "query": query,

            "is_https": is_https,

            "is_ip_address": is_ip_address,

            "is_shortened_url": is_shortened_url,

            "port": port,

            "unusual_port": unusual_port,

            "subdomain_count": subdomain_count,

            "excessive_subdomains": excessive_subdomains,

            "has_at_symbol": has_at_symbol,

            "has_username": has_username,

            "has_password": has_password,

            "has_multiple_hyphens": has_multiple_hyphens,

            "has_punycode": has_punycode,

            "suspicious_tld": suspicious_tld,

            "long_domain": long_domain,

            "has_encoded_content": has_encoded_content,

            "has_double_slash_path": has_double_slash_path,

            "very_long_url": very_long_url,

            "keyword_matches": keyword_matches,

            "suspicious_path_keywords":
                suspicious_path_keywords,

            "suspicious_query_keywords":
                suspicious_query_keywords,

            "suspicious_query_values":
                suspicious_query_values,

            "query_parameters":
                query_parameters,

            "risk_score":
                risk_score,

            "verdict":
                verdict,

            "reasons":
                reasons,

            "analysis_status":
                "COMPLETED",

            "method":
                "URL Forensic Analysis"
        }