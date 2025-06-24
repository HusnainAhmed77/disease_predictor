import streamlit as st
import joblib
import ast
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from helper import generate_pdf, log_prediction

# Load model and encoders
model = joblib.load('models/disease_model.pkl')
symptom_encoder = joblib.load("models/symptom_encoder.pkl")
disease_encoder = joblib.load("models/disease_encoder.pkl")

# Load dataset
df = pd.read_csv("../data/data.csv")

# Load treatments
def parse_treatment_file(path):
    treatment_map = {}
    current_disease = None
    with open(path, "r") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            if line.endswith(":") and "Medicines" not in line:
                current_disease = line[:-1]
                treatment_map[current_disease] = {}
            elif current_disease:
                if line.startswith("Medicines:"):
                    treatment_map[current_disease]["medicines"] = line.replace("Medicines:", "").strip()
                elif line.startswith("Steps:"):
                    treatment_map[current_disease]["steps"] = line.replace("Steps:", "").strip()
                elif line.startswith("Duration:"):
                    treatment_map[current_disease]["duration"] = line.replace("Duration:", "").strip()
    return treatment_map

treatment_map = parse_treatment_file("../data/treatments.txt")

def normalize_disease_name(name):
    name = name.lower().strip()
    if "(" in name and ")" in name:
        name = name.split(")")[-1].strip()
    return name

normalized_treatment_map = {
    normalize_disease_name(d): v for d, v in treatment_map.items()
}

# Gather all unique symptoms
all_symptoms = set()
for val in df["Symptoms"].dropna():
    try:
        symptoms = ast.literal_eval(val)
        cleaned = [s.replace("_", " ").strip().lower() for s in symptoms]
        all_symptoms.update(cleaned)
    except:
        continue

st.title("🧠 Smart Disease Predictor")
st.write("Select symptoms below and click Predict to see likely diseases and treatment.")

selected = st.multiselect("Select your symptoms:", sorted(all_symptoms))

if selected:
    st.markdown(f"**Selected Symptoms:** {', '.join(selected)}")

    matches = {}
    for _, row in df.iterrows():
        try:
            row_symptoms = ast.literal_eval(row["Symptoms"])
            row_symptoms_set = set(s.strip().replace("_", " ").lower() for s in row_symptoms)
            if set(selected).issubset(row_symptoms_set):
                disease = row["Disease"]
                extras = row_symptoms_set - set(selected)
                if disease not in matches:
                    matches[disease] = set(extras)
                else:
                    matches[disease].update(extras)
        except:
            continue

    if matches:
        st.subheader("🧠 Diseases Matching All Symptoms:")
        for disease, extras in matches.items():
            st.markdown(f"### 🔸 {disease}")
            if extras:
                st.markdown(f"- Extra symptoms: {', '.join(list(extras)[:3])}")
            else:
                st.markdown("- All symptoms matched exactly ✅")

    # Model Prediction
    valid_symptoms = set(symptom_encoder.classes_)
    filtered = [s for s in selected if s in valid_symptoms]

    if filtered:
        X_input = symptom_encoder.transform([filtered])
        y_pred = model.predict(X_input)
        predicted = disease_encoder.inverse_transform(y_pred)[0]
        st.success(f"🎯 Predicted Disease: {predicted}")

        norm_pred = normalize_disease_name(predicted)
        if norm_pred in normalized_treatment_map:
            t = normalized_treatment_map[norm_pred]
            st.markdown("### 💊 Treatment Plan")
            st.markdown(f"**Medicines:** {t.get('medicines', 'Not specified')}")
            st.markdown(f"**Steps:** {t.get('steps', 'Not specified')}")
            st.markdown(f"**Duration:** {t.get('duration', 'Not specified')}")

            if st.button("📄 Download Report as PDF"):
                filename = "report.pdf"
                generate_pdf(selected, predicted, t, filename)
                with open(filename, "rb") as f:
                    st.download_button("⬇️ Click to Download PDF", f, file_name=filename)

            # 📝 Log the prediction
            log_prediction(selected, list(matches.keys()), predicted, t)
        else:
            st.warning("⚠️ No treatment info found.")
    else:
        st.error("❌ No valid symptoms matched model vocabulary.")
else:
    st.info("👆 Select symptoms to get started.")

# =====================
# 📊 Visualizations Section
# =====================
st.markdown("---")
st.markdown("## 📊 Data Visualizations")

viz_option = st.radio("Choose a chart to view:", ["Top 10 Diseases", "Top Symptoms"], horizontal=True)

if viz_option == "Top 10 Diseases":
    top_diseases = df['Disease'].value_counts().head(10)
    fig, ax = plt.subplots()
    sns.barplot(x=top_diseases.values, y=top_diseases.index, ax=ax, palette="viridis")
    ax.set_title("Top 10 Most Frequent Diseases")
    ax.set_xlabel("Cases")
    ax.set_ylabel("Disease")
    st.pyplot(fig)

elif viz_option == "Top Symptoms":
    symptom_counts = {}
    for val in df["Symptoms"].dropna():
        try:
            symptoms = ast.literal_eval(val)
            for s in symptoms:
                s_clean = s.strip().replace("_", " ").lower()
                symptom_counts[s_clean] = symptom_counts.get(s_clean, 0) + 1
        except:
            continue

    top_symptoms = dict(sorted(symptom_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    fig, ax = plt.subplots()
    sns.barplot(x=list(top_symptoms.values()), y=list(top_symptoms.keys()), ax=ax, palette="mako")
    ax.set_title("Top 10 Symptoms")
    ax.set_xlabel("Count")
    ax.set_ylabel("Symptom")
    st.pyplot(fig)
