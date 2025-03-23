import streamlit as st
import google.generativeai as genai
import requests

GENAI_API_KEY = "AIzaSyDoBjoSbfv0moLFvKOkf0aa8Nm3mpR6-Sk"
genai.configure(api_key=GENAI_API_KEY)
SONARQUBE_URL = "http://localhost:9000/api/issues/search"
SONARQUBE_TOKEN = "sqp_2c6d26ce9e656978d73c78b1a96a19be5a8122cd"

def get_gemini_fix(code):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"Fix errors in this Python code:\n{code}")
    return response.text if response else "Error generating fix."

def analyze_code_with_sonarqube():
    try:
        response = requests.get(
            SONARQUBE_URL,
            headers={"Authorization": f"Bearer {SONARQUBE_TOKEN}"},
            params={"languages": "py"}
        )
        return response.json() if response.status_code == 200 else {"error": f"SonarQube Error: {response.status_code}"}
    except Exception as e:
        return {"error": "SonarQube Connection Error", "message": str(e)}

def run():
    st.subheader("AI-Powered Code Debugger & Optimizer")
    code = st.text_area("Paste your Python code here:", height=200)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Analyze & Fix Errors"):
            if code:
                fixed_code = get_gemini_fix(code)
                st.subheader("AI-Suggested Fix:")
                st.code(fixed_code, language="python")
            else:
                st.warning("Please enter your code.")
    with col2:
        if st.button("Analyze with SonarQube"):
            if code:
                analysis_result = analyze_code_with_sonarqube()
                st.subheader("SonarQube Analysis:")
                st.json(analysis_result)
            else:
                st.warning("Please enter your code.")

