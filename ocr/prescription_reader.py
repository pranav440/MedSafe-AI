"""
MedSafe AI – OCR Prescription Reader
======================================
Extracts medicine names from prescription images using Tesseract OCR
and fuzzy-matches them against a local medicine database.

Dependencies:
    - pytesseract (Python wrapper)
    - Tesseract-OCR engine (must be installed on the system)
    - rapidfuzz   (fuzzy string matching)

Usage:
    from ocr.prescription_reader import extract_medicines
    results = extract_medicines("path/to/prescription.jpg")
"""

import os
import sys
import csv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

from rapidfuzz import process, fuzz


# ──────────── Medicine Database ────────────

def load_medicine_db():
    """Load sample medicine database from CSV."""
    medicines = []
    csv_path = config.MEDICINE_DB_PATH
    if not os.path.exists(csv_path):
        print(f"[OCR] Warning: Medicine database not found at {csv_path}")
        return medicines
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            medicines.append({
                "medicine_name": row["medicine_name"].strip(),
                "active_salt":   row["active_salt"].strip(),
                "category":      row.get("category", "").strip(),
            })
    return medicines


# ──────────── OCR Functions ────────────

def extract_text_from_image(image_path):
    """
    Extract raw text from a prescription image using Tesseract.
    Returns the extracted text as a string.
    """
    if not OCR_AVAILABLE:
        return "[OCR] pytesseract/Pillow not installed. Cannot process image."

    if not os.path.exists(image_path):
        return f"[OCR] Image file not found: {image_path}"

    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        return f"[OCR] Error processing image: {e}"


def extract_medicines(image_path, score_threshold=60):
    """
    Extract medicines from a prescription image.

    Steps:
        1. OCR → raw text
        2. Tokenize words
        3. Fuzzy-match each word against medicine database
        4. Return matched medicines with active salts

    Args:
        image_path:      Path to the prescription image.
        score_threshold: Minimum fuzzy match score (0-100) to accept.

    Returns:
        {
            "raw_text": str,
            "medicines_found": [
                {"medicine": str, "active_salt": str, "confidence": float},
                …
            ]
        }
    """
    raw_text = extract_text_from_image(image_path)
    db = load_medicine_db()

    if not db:
        return {"raw_text": raw_text, "medicines_found": [],
                "note": "Medicine database is empty or missing."}

    # Build a list of known medicine names for matching
    med_names = [m["medicine_name"] for m in db]
    med_lookup = {m["medicine_name"].lower(): m for m in db}

    # Tokenize the OCR text – split on whitespace and common delimiters
    words = raw_text.replace(",", " ").replace(".", " ").replace("\n", " ").split()
    # Also try bigrams (two-word medicine names)
    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words) - 1)]
    candidates = words + bigrams

    found = []
    seen = set()

    for candidate in candidates:
        if len(candidate) < 3:
            continue
        match = process.extractOne(candidate, med_names,
                                   scorer=fuzz.token_sort_ratio)
        if match and match[1] >= score_threshold:
            matched_name = match[0].lower()
            if matched_name not in seen:
                seen.add(matched_name)
                med = med_lookup[matched_name]
                found.append({
                    "medicine":    med["medicine_name"],
                    "active_salt": med["active_salt"],
                    "confidence":  round(match[1], 1),
                })

    return {
        "raw_text": raw_text,
        "medicines_found": found,
    }


# ──────── Extract from raw text (no image) ────────

def extract_medicines_from_text(text, score_threshold=60):
    """
    Same as extract_medicines but takes raw text instead of an image.
    Useful when OCR is not available and user pastes the text directly.
    """
    db = load_medicine_db()
    if not db:
        return {"raw_text": text, "medicines_found": [],
                "note": "Medicine database is empty or missing."}

    med_names = [m["medicine_name"] for m in db]
    med_lookup = {m["medicine_name"].lower(): m for m in db}

    words = text.replace(",", " ").replace(".", " ").replace("\n", " ").split()
    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words) - 1)]
    candidates = words + bigrams

    found = []
    seen = set()

    for candidate in candidates:
        if len(candidate) < 3:
            continue
        match = process.extractOne(candidate, med_names,
                                   scorer=fuzz.token_sort_ratio)
        if match and match[1] >= score_threshold:
            matched_name = match[0].lower()
            if matched_name not in seen:
                seen.add(matched_name)
                med = med_lookup[matched_name]
                found.append({
                    "medicine":    med["medicine_name"],
                    "active_salt": med["active_salt"],
                    "confidence":  round(match[1], 1),
                })

    return {
        "raw_text": text,
        "medicines_found": found,
    }


# ─────── Quick Test ───────

if __name__ == "__main__":
    # Test with text (no image needed)
    sample_text = "Take Paracetamol 500mg twice daily. Amoxicillin 250mg thrice."
    result = extract_medicines_from_text(sample_text)
    print("Medicines found:")
    for m in result["medicines_found"]:
        print(f"  • {m['medicine']} ({m['active_salt']}) – confidence: {m['confidence']}%")
