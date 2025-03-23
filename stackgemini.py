import streamlit as st
import requests
import google.generativeai as genai

# Configure Gemini API (Replace with your API key)
genai.configure(api_key="AIzaSyDoBjoSbfv0moLFvKOkf0aa8Nm3mpR6-Sk")

# Stack Overflow API Endpoint
STACK_OVERFLOW_API = "https://api.stackexchange.com/2.3/search"

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

def get_gemini_summary(answer_text):
    """Use Gemini AI to summarize the solution from Stack Overflow answers."""
    model = genai.GenerativeModel("gemini-1.5-flash")  # Adjust based on availability
    response = model.generate_content(f"Summarize this Stack Overflow solution: {answer_text}")
    return response.text if response else "No summary available."

# Streamlit UI
st.title("Error Debugger with Stack Overflow & Gemini AI")

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
                
                st.markdown(f"**[{question_title}]({question_link})**")
                
                # Fetching the top answer for the question
                answer_api = f"https://api.stackexchange.com/2.3/questions/{q['question_id']}/answers"
                answer_params = {"order": "desc", "sort": "votes", "site": "stackoverflow", "filter": "withbody"}
                answer_response = requests.get(answer_api, params=answer_params)

                if answer_response.status_code == 200:
                    answers = answer_response.json().get("items", [])
                    if answers:
                        answer_text = answers[0].get("body", "No answer available")
                        
                        # Get AI Summary of the solution
                        ai_summary = get_gemini_summary(answer_text)
                        
                        st.markdown("**Solution Summary:**")
                        st.write(ai_summary)
                    else:
                        st.warning("No answers found for this question.")
    else:
        st.warning("Please enter an error message to search.")
