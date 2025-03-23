import streamlit as st
import requests
import google.generativeai as genai

GENAI_API_KEY = "AIzaSyDoBjoSbfv0moLFvKOkf0aa8Nm3mpR6-Sk"
genai.configure(api_key=GENAI_API_KEY)
STACK_OVERFLOW_API = "https://api.stackexchange.com/2.3/search"
ANSWER_API = "https://api.stackexchange.com/2.3/questions/{}/answers"

def search_stackoverflow(error_query):
    params = {"order": "desc", "sort": "relevance", "intitle": error_query, "site": "stackoverflow"}
    response = requests.get(STACK_OVERFLOW_API, params=params)
    return response.json().get("items", []) if response.status_code == 200 else []

def get_top_answer(question_id):
    params = {"order": "desc", "sort": "votes", "site": "stackoverflow", "filter": "withbody"}
    response = requests.get(ANSWER_API.format(question_id), params=params)
    answers = response.json().get("items", []) if response.status_code == 200 else []
    return answers[0].get("body", "No answer available.") if answers else "No answer available."

def get_gemini_summary(answer_text):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"Summarize this Stack Overflow solution: {answer_text}")
    return response.text if response else "No summary available."

def run():
    st.subheader("Error Debugger with Stack Overflow & Gemini AI")
    error_query = st.text_input("Enter the error message or issue:")
    if st.button("Search & Get Solution"):
        if error_query:
            questions = search_stackoverflow(error_query)
            if not questions:
                st.error("No relevant questions found.")
            else:
                for q in questions[:3]:
                    st.markdown(f"**[{q['title']}]({q['link']})**")
                    answer_text = get_top_answer(q["question_id"])
                    ai_summary = get_gemini_summary(answer_text)
                    st.markdown("**Solution Summary:**")
                    st.write(ai_summary)
        else:
            st.warning("Please enter an error message.")