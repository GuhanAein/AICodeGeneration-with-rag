import streamlit as st
import requests

# Stack Overflow API Endpoint
STACK_OVERFLOW_API = "https://api.stackexchange.com/2.3/search"
ANSWER_API = "https://api.stackexchange.com/2.3/questions/{}/answers"

def search_stackoverflow(error_query):
    """Search Stack Overflow for questions related to the given error."""
    params = {
        "order": "desc",
        "sort": "relevance",
        "intitle": error_query,
        "site": "stackoverflow"
    }
    
    response = requests.get(STACK_OVERFLOW_API, params=params)
    
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        return []

def get_top_answer(question_id):
    """Fetch the top-voted answer for a given Stack Overflow question ID."""
    params = {
        "order": "desc",
        "sort": "votes",
        "site": "stackoverflow",
        "filter": "withbody"  # Get the full answer body
    }
    
    response = requests.get(ANSWER_API.format(question_id), params=params)
    
    if response.status_code == 200:
        answers = response.json().get("items", [])
        if answers:
            return answers[0].get("body", "No answer available.")
    
    return "No answer available."

# Streamlit UI
st.title("Stack Overflow Error Debugger")

# User Input
error_query = st.text_input("Enter the error message or issue:")

if st.button("Search & Get Solution"):
    if error_query:
        st.subheader("Stack Overflow Search Results:")
        
        # Search Stack Overflow
        questions = search_stackoverflow(error_query)
        
        if not questions:
            st.error("No relevant Stack Overflow questions found. Try refining your query.")
        else:
            for q in questions[:3]:  # Show top 3 results
                question_title = q["title"]
                question_link = q["link"]
                question_id = q["question_id"]
                
                st.markdown(f"**[{question_title}]({question_link})**")
                
                # Fetching the top answer for the question
                answer_text = get_top_answer(question_id)

                st.markdown("**Top Answer:**")
                st.write(answer_text, unsafe_allow_html=True)  # Display answer in HTML format
    else:
        st.warning("Please enter an error message to search.")
