"""
MedSafe AI – Symptom Guidance System
======================================
Provides educational health guidance based on user-reported symptoms.
Uses fuzzy matching to identify relevant conditions from a local
symptom database (JSON).

⚠ DISCLAIMER: This is for educational purposes only.
  Not a substitute for professional medical advice.

Usage:
    from symptom_engine.symptom_solver import get_symptom_guidance
    result = get_symptom_guidance(["headache", "fever", "fatigue"])
"""

import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

from rapidfuzz import process, fuzz

DISCLAIMER = (
    "⚕ Educational guidance only. This is NOT a medical diagnosis. "
    "Please consult a qualified healthcare professional for proper evaluation."
)


# ──────────── Symptom Database ────────────

def load_symptom_db():
    """Load symptom conditions from JSON database."""
    json_path = config.SYMPTOM_DB_PATH
    if not os.path.exists(json_path):
        print(f"[SYMPTOM] Warning: Symptom database not found at {json_path}")
        return []
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ──────────── Symptom Matching ────────────

def get_symptom_guidance(user_symptoms):
    """
    Analyse user symptoms and return educational guidance.

    Args:
        user_symptoms: List of symptom strings reported by the user.

    Returns:
        {
            "input_symptoms": [str],
            "matched_conditions": [
                {
                    "condition": str,
                    "match_score": float,
                    "possible_causes": [str],
                    "home_remedies": [str],
                    "lifestyle_advice": [str],
                    "warning_signs": [str],
                }
            ],
            "disclaimer": str,
        }
    """
    db = load_symptom_db()
    if not db:
        return {
            "input_symptoms": user_symptoms,
            "matched_conditions": [],
            "disclaimer": DISCLAIMER,
            "note": "Symptom database is empty or missing.",
        }

    matched_conditions = []

    for condition in db:
        known_symptoms = condition.get("symptoms", [])
        if not known_symptoms:
            continue

        # Score: how many of the user's symptoms match this condition
        total_score = 0
        matches = 0

        for user_sym in user_symptoms:
            best = process.extractOne(
                user_sym, known_symptoms, scorer=fuzz.token_sort_ratio
            )
            if best and best[1] >= 55:
                total_score += best[1]
                matches += 1

        if matches > 0:
            avg_score = total_score / len(user_symptoms)
            matched_conditions.append({
                "condition":        condition["condition"],
                "match_score":      round(avg_score, 1),
                "matched_symptoms": matches,
                "possible_causes":  condition.get("causes", []),
                "home_remedies":    condition.get("home_remedies", []),
                "lifestyle_advice": condition.get("lifestyle_advice", []),
                "warning_signs":    condition.get("warning_signs", []),
            })

    # Sort by match score (descending)
    matched_conditions.sort(key=lambda x: x["match_score"], reverse=True)

    # Return top 3 matches
    return {
        "input_symptoms":    user_symptoms,
        "matched_conditions": matched_conditions[:3],
        "disclaimer":        DISCLAIMER,
    }


# ──────── Side-Effect Monitor ────────

def analyze_side_effects(age, gender, medicine, dosage, symptoms):
    """
    Provide educational guidance about reported side effects.

    This simulates an AI response – in production, this could be
    connected to an LLM API for more nuanced responses.

    Args:
        age:      Patient age (int)
        gender:   Patient gender (str)
        medicine: Medicine name (str)
        dosage:   Dosage info (str)
        symptoms: Reported symptoms (list of str)

    Returns:
        dict with analysis and recommendations.
    """
    # Simulated AI analysis based on common knowledge
    symptom_text = ", ".join(symptoms)

    analysis = {
        "patient_profile": {
            "age": age,
            "gender": gender,
            "medicine": medicine,
            "dosage": dosage,
        },
        "reported_symptoms": symptoms,
        "analysis": (
            f"Patient ({age}y, {gender}) reports [{symptom_text}] "
            f"while taking {medicine} ({dosage}). "
            f"These symptoms may be related to the medication. "
            f"Common side effects of many medications include nausea, "
            f"dizziness, and fatigue."
        ),
        "recommendations": [
            "Monitor symptoms for 24-48 hours.",
            "Stay hydrated and rest adequately.",
            "Do not stop medication without consulting your doctor.",
            "If symptoms worsen or new symptoms appear, seek medical attention.",
            "Keep a symptom diary for your next doctor visit.",
        ],
        "urgency": _assess_urgency(symptoms),
        "disclaimer": DISCLAIMER,
    }

    return analysis


def _assess_urgency(symptoms):
    """Simple rule-based urgency assessment."""
    urgent_keywords = [
        "chest pain", "difficulty breathing", "severe pain",
        "swelling", "bleeding", "fainting", "seizure",
        "allergic reaction", "rash", "anaphylaxis",
    ]
    for sym in symptoms:
        for keyword in urgent_keywords:
            if keyword.lower() in sym.lower():
                return "HIGH – Seek immediate medical attention"
    return "LOW – Monitor and consult your doctor at next visit"


# ─────── Quick Test ───────

if __name__ == "__main__":
    print("=== Symptom Guidance ===")
    result = get_symptom_guidance(["headache", "fever", "body ache"])
    print(f"Input: {result['input_symptoms']}")
    for cond in result["matched_conditions"]:
        print(f"\n  Condition: {cond['condition']} (score: {cond['match_score']})")
        print(f"  Causes: {cond['possible_causes']}")
        print(f"  Remedies: {cond['home_remedies']}")
    print(f"\n{result['disclaimer']}")

    print("\n\n=== Side-Effect Analysis ===")
    se_result = analyze_side_effects(
        age=35, gender="Male", medicine="Metformin",
        dosage="500mg twice daily", symptoms=["nausea", "dizziness"]
    )
    print(se_result["analysis"])
    print(f"Urgency: {se_result['urgency']}")
