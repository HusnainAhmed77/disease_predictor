# 🧠 Smart Disease Predictor

A Streamlit web application that predicts diseases based on user-provided symptoms using a trained machine learning model. It also suggests basic treatments using extracted medical knowledge and provides interactive visualizations of disease trends and symptom frequency.

---

## 🚀 Features

- ✅ **Disease prediction from selected symptoms**
- 💊 **Treatment suggestions** (Medicines, Steps, Duration)
- 📄 **Downloadable PDF diagnosis report**
- 📊 **Interactive charts**: top diseases and most frequent symptoms
- 📝 **Prediction log stored as CSV** for review or audit

---
## 🔍 How It Works

1. **Symptom Input:**  
   Users select symptoms from a predefined list.

2. **Model Prediction:**  
   A trained `RandomForestClassifier` predicts the most likely disease using encoded symptom input.

3. **Treatment Extraction:**  
   Based on the predicted disease, treatment details are shown from a curated file (`treatments.txt`).

4. **PDF Report (Optional):**  
   Users can download their diagnosis and treatment as a PDF.

5. **Data Visualization:**  
   Interactive charts display top 10 diseases and most common symptoms using `matplotlib` and `seaborn`.

---

## 🖥️ Getting Started Locally

### ✅ Install Requirements

```bash
pip install -r requirements.txt
