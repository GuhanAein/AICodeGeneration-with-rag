import streamlit as st
import requests

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

def run():
    st.subheader("Stack Overflow Error Debugger")
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
                    st.markdown("**Top Answer:**")
                    st.write(answer_text, unsafe_allow_html=True)
        else:
            st.warning("Please enter an error message.")