import streamlit as st
import google.generativeai as genai
import requests
import json

# 🔐 Configure Gemini API with your API Key
GENAI_API_KEY = "AIzaSyDoBjoSbxxxxxxxxxxxxxxxx"  # Your actual API Key
genai.configure(api_key=GENAI_API_KEY)

# 🔐 SonarQube Configuration
SONARQUBE_URL = "http://localhost:9000/api/issues/search"  # Ensure SonarQube is running
SONARQUBE_TOKEN = "ssqp_7ba2e48835581xxxxxxxxxxxxxxx"  # Your SonarQube Token

def get_gemini_fix(code):
    """Ask Gemini AI to analyze and fix the code."""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")  # Using Gemini 2.0 Flash
        response = model.generate_content(f"Fix errors in this Python code:\n{code}")
        return response.text
    except Exception as e:
        return f"Error in Gemini AI: {e}"

def analyze_code_with_sonarqube():
    """Fetch analysis results from SonarQube and handle errors."""
    try:
        response = requests.get(
            SONARQUBE_URL,
            headers={"Authorization": f"Bearer {SONARQUBE_TOKEN}"},  # Use API Token Authentication
            params={"languages": "py"}  # Filter results for Python
        )

        if response.status_code == 401:
            return {"error": "Unauthorized. Invalid SonarQube token."}
        elif response.status_code != 200:
            return {"error": f"SonarQube API Error: {response.status_code}", "message": response.text}

        try:
            return response.json()  # Return JSON response
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response from SonarQube", "message": response.text}

    except requests.exceptions.RequestException as e:
        return {"error": "SonarQube Connection Error", "message": str(e)}

# Streamlit UI
st.title("AI-Powered Code Debugger & Optimizer")

# Code Input
code = st.text_area("Paste your Python code here:", height=200)

if st.button("Analyze & Fix Errors"):
    if code:
        fixed_code = get_gemini_fix(code)
        st.subheader("AI-Suggested Fix:")
        st.code(fixed_code, language="python")
    else:
        st.warning("Please enter your code first.")

if st.button("Analyze with SonarQube"):
    analysis_result = analyze_code_with_sonarqube()
    st.subheader("SonarQube Analysis:")
    st.json(analysis_result)  # Display JSON in readable format

