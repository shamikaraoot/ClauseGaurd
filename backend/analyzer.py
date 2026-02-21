import os
import re
from typing import Dict, List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
client = None
if openai_api_key:
    try:
        client = OpenAI(api_key=openai_api_key)
    except Exception as e:
        print(f"Warning: Could not initialize OpenAI client: {e}")


def analyze_text(text: str) -> Dict[str, any]:
    """
    Analyze Terms and Conditions text and extract:
    - Summary
    - Risk score (Low/Medium/High)
    - Alert list
    """
    # Use OpenAI if available, otherwise use rule-based analysis
    if client:
        return analyze_with_openai(text)
    else:
        return analyze_with_rules(text)


def analyze_with_openai(text: str) -> Dict[str, any]:
    """Analyze text using OpenAI API."""
    try:
        # Truncate text if too long (OpenAI has token limits)
        max_chars = 12000
        text_to_analyze = text[:max_chars] if len(text) > max_chars else text

        prompt = f"""Analyze the following Terms and Conditions text and provide:
1. A simplified summary (2-3 sentences) IN ENGLISH
2. A risk score: Low, Medium, or High
3. A list of alerts (bullet points) for concerning clauses IN ENGLISH

IMPORTANT: Summarize in English regardless of the original language of the text.

Focus on detecting:
- Payment clauses and hidden fees
- Auto-renewal subscriptions
- Data collection practices
- Third-party data sharing
- Risky legal clauses (arbitration, liability waivers, etc.)

Text to analyze (may be in any language):
{text_to_analyze}

Respond in this exact JSON format (all text must be in English):
{{
  "summary": "Brief summary here in English",
  "risk_score": "Low|Medium|High",
  "alerts": ["Alert 1 in English", "Alert 2 in English", "Alert 3 in English"]
}}
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a legal analysis assistant. Always respond with valid JSON only. Always provide summaries and alerts in English, regardless of the input language."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )

        content = response.choices[0].message.content.strip()

        # Try to extract JSON from response
        import json
        # Remove markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        result = json.loads(content)

        # Validate and normalize risk score
        risk_score = result.get("risk_score", "Medium")
        if risk_score not in ["Low", "Medium", "High"]:
            risk_score = "Medium"

        return {
            "summary": result.get("summary", "Unable to generate summary."),
            "risk_score": risk_score,
            "alerts": result.get("alerts", [])
        }

    except Exception as e:
        print(f"OpenAI analysis failed: {e}, falling back to rule-based analysis")
        return analyze_with_rules(text)


def analyze_with_rules(text: str) -> Dict[str, any]:
    """
    Rule-based analysis as fallback when OpenAI is not available.
    Note: This method works best with English text. For non-English text,
    OpenAI API is recommended for accurate multilingual analysis.
    """
    text_lower = text.lower()
    
    # Detect if text appears to be non-English (simple heuristic)
    # Check for common non-English characters/patterns
    non_english_indicators = [
        r'[àáâãäåæçèéêëìíîïñòóôõöùúûüýÿ]',  # Common accented characters
        r'[ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝŸ]',
        r'[α-ωΑ-Ω]',  # Greek
        r'[一-龯]',  # Chinese/Japanese/Korean (CJK)
        r'[А-Яа-я]',  # Cyrillic
        r'[א-ת]',  # Hebrew
        r'[ا-ي]',  # Arabic
    ]
    
    is_likely_non_english = any(re.search(pattern, text) for pattern in non_english_indicators)
    
    if is_likely_non_english:
        # For non-English text, provide a note that OpenAI is recommended
        return {
            "summary": "This document appears to be in a non-English language. For accurate analysis of non-English Terms & Conditions, please configure an OpenAI API key. The system can analyze multilingual content when OpenAI is available.",
            "risk_score": "Medium",
            "alerts": [
                "Document appears to be in a non-English language",
                "For best results with multilingual content, use OpenAI API",
                "Please review the original document carefully"
            ]
        }

    alerts = []
    risk_score = "Low"
    risk_points = 0

    # Payment and subscription detection
    payment_patterns = [
        r"automatic.*renewal",
        r"auto.*renew",
        r"recurring.*charge",
        r"subscription.*fee",
        r"hidden.*fee",
        r"processing.*fee",
        r"cancellation.*fee",
    ]

    for pattern in payment_patterns:
        if re.search(pattern, text_lower):
            alerts.append("Contains automatic renewal or recurring payment clauses")
            risk_points += 2
            break

    # Data collection detection
    data_patterns = [
        r"collect.*personal.*data",
        r"share.*third.*party",
        r"sell.*data",
        r"data.*collection",
        r"tracking.*cookies",
        r"analytics.*data",
    ]

    for pattern in data_patterns:
        if re.search(pattern, text_lower):
            alerts.append("Collects and may share personal data with third parties")
            risk_points += 1
            break

    # Risky legal clauses
    legal_patterns = [
        r"arbitration.*only",
        r"waive.*liability",
        r"no.*refund",
        r"as.*is.*basis",
        r"disclaim.*warranty",
        r"limit.*liability",
    ]

    for pattern in legal_patterns:
        if re.search(pattern, text_lower):
            alerts.append("Contains restrictive legal clauses (arbitration, liability waivers)")
            risk_points += 2
            break

    # Cancellation restrictions
    if re.search(r"no.*cancel|cancel.*not.*allowed|cancel.*restriction", text_lower):
        alerts.append("Restrictive cancellation policy")
        risk_points += 1

    # Determine risk score
    if risk_points >= 4:
        risk_score = "High"
    elif risk_points >= 2:
        risk_score = "Medium"
    else:
        risk_score = "Low"

    # Generate summary
    summary_parts = []
    if risk_points >= 4:
        summary_parts.append("This document contains multiple high-risk clauses.")
    elif risk_points >= 2:
        summary_parts.append("This document contains some concerning clauses.")
    else:
        summary_parts.append("This document appears relatively standard.")

    if alerts:
        summary_parts.append(f"Key concerns include: {', '.join(alerts[:2])}.")
    else:
        summary_parts.append("No major red flags detected, but review carefully.")

    summary = " ".join(summary_parts)

    # Ensure at least one alert
    if not alerts:
        alerts.append("No major concerns detected, but always review Terms and Conditions carefully.")

    return {
        "summary": summary,
        "risk_score": risk_score,
        "alerts": alerts
    }

