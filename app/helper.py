from fpdf import FPDF
import unicodedata

def clean_text(text):
    """Remove unsupported unicode (emojis, fancy punctuation)."""
    text = unicodedata.normalize("NFKD", text)
    return text.encode("ascii", "ignore").decode("ascii")

def generate_pdf(symptoms, prediction, treatment, filename="report.pdf"):
    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Arial", size=14, style="B")
    pdf.cell(200, 10, "Disease Prediction Report", ln=True, align="C")
    pdf.ln(10)

    # Symptoms
    pdf.set_font("Arial", size=12)
    symptom_text = "Symptoms:\n- " + "\n- ".join(symptoms)
    pdf.multi_cell(0, 10, clean_text(symptom_text))
    pdf.ln(5)

    # Prediction
    pdf.set_font("Arial", size=12, style="B")
    pdf.cell(0, 10, clean_text(f"Predicted Disease: {prediction}"), ln=True)
    pdf.ln(5)

    # Treatment
    pdf.set_font("Arial", size=12, style="B")
    pdf.cell(0, 10, "Treatment Plan:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, clean_text(f"Medicines: {treatment.get('medicines', 'Not available')}"))
    pdf.multi_cell(0, 10, clean_text(f"Steps: {treatment.get('steps', 'Not available')}"))
    pdf.multi_cell(0, 10, clean_text(f"Duration: {treatment.get('duration', 'Not available')}"))

    pdf.output(filename)
    return filename

import csv
from datetime import datetime
import os

def log_prediction(symptoms, matched, predicted, treatment, log_file="logs/prediction_log.csv"):
    os.makedirs("logs", exist_ok=True)

    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_symptoms": ", ".join(symptoms),
        "matched_diseases": ", ".join(matched),
        "predicted_disease": predicted,
        "medicines": treatment.get("medicines", "N/A"),
        "steps": treatment.get("steps", "N/A"),
        "duration": treatment.get("duration", "N/A")
    }

    write_header = not os.path.exists(log_file)

    with open(log_file, mode="a", newline='', encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=row.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(row)
