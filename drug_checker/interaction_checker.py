"""
MedSafe AI – Drug Interaction Checker
=======================================
Checks for known drug–drug interactions using fuzzy matching
against a local CSV database of interaction pairs.

Usage:
    from drug_checker.interaction_checker import check_interactions
    warnings = check_interactions(["Aspirin", "Warfarin", "Ibuprofen"])
"""

import os
import sys
import csv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

from rapidfuzz import process, fuzz


# ──────────── Interaction Database ────────────

def load_interactions_db():
    """
    Load drug interactions from CSV.
    Expected columns: drug_1, drug_2, severity, description
    """
    interactions = []
    csv_path = config.DRUG_INTERACTIONS_PATH
    if not os.path.exists(csv_path):
        print(f"[DRUG] Warning: Interactions database not found at {csv_path}")
        return interactions
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            interactions.append({
                "drug_1":      row["drug_1"].strip(),
                "drug_2":      row["drug_2"].strip(),
                "severity":    row["severity"].strip(),
                "description": row["description"].strip(),
            })
    return interactions


def _fuzzy_match_drug(name, all_drugs, threshold=70):
    """Fuzzy-match a user-entered drug name against known drug names."""
    match = process.extractOne(name, all_drugs, scorer=fuzz.token_sort_ratio)
    if match and match[1] >= threshold:
        return match[0]
    return None


# ──────────── Interaction Checker ────────────

def check_interactions(medicine_list):
    """
    Check a list of medicine names for known interactions.

    Args:
        medicine_list: List of medicine name strings.

    Returns:
        {
            "medicines_checked": [str],
            "interactions_found": [
                {
                    "drug_1": str,
                    "drug_2": str,
                    "severity": str,
                    "description": str,
                    "warning": str,
                }
            ],
            "safe_message": str  (only if no interactions found)
        }
    """
    db = load_interactions_db()
    if not db:
        return {
            "medicines_checked": medicine_list,
            "interactions_found": [],
            "note": "Drug interactions database is empty or missing.",
        }

    # Collect all unique drug names from the database
    all_drugs = set()
    for entry in db:
        all_drugs.add(entry["drug_1"])
        all_drugs.add(entry["drug_2"])
    all_drugs = list(all_drugs)

    # Resolve user inputs to canonical names
    resolved = []
    for med in medicine_list:
        matched = _fuzzy_match_drug(med.strip(), all_drugs)
        resolved.append(matched if matched else med.strip())

    # Check all pairs
    interactions_found = []
    for i in range(len(resolved)):
        for j in range(i + 1, len(resolved)):
            drug_a = resolved[i].lower()
            drug_b = resolved[j].lower()

            for entry in db:
                d1 = entry["drug_1"].lower()
                d2 = entry["drug_2"].lower()

                if (drug_a == d1 and drug_b == d2) or \
                   (drug_a == d2 and drug_b == d1):
                    interactions_found.append({
                        "drug_1":      resolved[i],
                        "drug_2":      resolved[j],
                        "severity":    entry["severity"],
                        "description": entry["description"],
                        "warning":     f"⚠ {entry['severity']} interaction between "
                                       f"{resolved[i]} and {resolved[j]}: "
                                       f"{entry['description']}",
                    })

    result = {
        "medicines_checked": resolved,
        "interactions_found": interactions_found,
    }

    if not interactions_found:
        result["safe_message"] = (
            "✅ No known interactions found between the entered medicines. "
            "However, always consult a pharmacist or doctor."
        )

    return result


# ─────── Quick Test ───────

if __name__ == "__main__":
    test_meds = ["Aspirin", "Warfarin", "Metformin"]
    result = check_interactions(test_meds)
    print(f"Checked: {result['medicines_checked']}")
    if result["interactions_found"]:
        for interaction in result["interactions_found"]:
            print(f"  {interaction['warning']}")
    else:
        print(f"  {result.get('safe_message', 'No info')}")
