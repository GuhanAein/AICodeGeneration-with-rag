import streamlit as st
import google.generativeai as genai
import ast
import requests

# Configure Gemini API
genai.configure(api_key="AIzaSyDoBjoSbfv0xxxxxxxxxxxx")

# SonarQube API Configuration
SONARQUBE_URL = "http://localhost:9000/api/issues/search"  # Ensure SonarQube is running
SONARQUBE_TOKEN = "sqp_2c6d26ce9e656978dxxxxxxxxxxxxxxx"

def get_gemini_fix(code):
    """Ask Gemini to analyze and fix the code."""
    model = genai.GenerativeModel("gemini-2.0-flash")  # Ensure the correct model name
    response = model.generate_content(f"Fix errors in this Python code:\n{code}")
    return response.text

def analyze_code_with_sonarqube(code):
    """Send code to SonarQube for static analysis."""
    response = requests.get(
        SONARQUBE_URL,
        headers={"Authorization": f"Bearer {SONARQUBE_TOKEN}"},
        params={"languages": "py"}  # Adjust for different languages if needed
    )
    return response.json()

# Streamlit UI
st.title("AI-Powered Code Debugger & Optimizer")

# Code Input
code = st.text_area("Paste your Python code here:", height=200)

if st.button("Analyze & Fix Errors"):
    if code:
        fixed_code = get_gemini_fix(code)
        st.subheader("AI-Suggested Fix:")
        st.code(fixed_code, language="python")

if st.button("Analyze with SonarQube"):
    if code:
        analysis_result = analyze_code_with_sonarqube(code)
        st.subheader("SonarQube Analysis:")
        st.write(analysis_result)
    else:
        st.warning("Please enter your code first.")

