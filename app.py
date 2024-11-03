import streamlit as st
import google.generativeai as genai
import time

def get_answer(model, prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return "Sorry, I couldn't generate a response at this time."

def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

def setup_sidebar():
    with st.sidebar:
        st.write("### Settings")
        google_api_key = st.text_input("Google API Key:", type="password")
        st.sidebar.button('Clear Chat', on_click=reset_chat)
        return google_api_key

def setup_google_api(google_api_key):
    if google_api_key:
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model
    return None

def response_generator(response):
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

def reset_chat():
    st.session_state.messages = []
    st.success("Chat cleared successfully!")

def feedback_system(response):
    feedback = st.radio("How would you rate the response?", ("Helpful", "Somewhat Helpful", "Not Relevant"))
    if st.button("Submit Feedback"):
        st.success("Thank you for your feedback!")

def main(model):
    if prompt := st.chat_input("Type your message:", key="user_message"):
        with st.chat_message("user"):
            st.markdown(prompt)
        add_message("user", prompt)

        response = get_answer(model, prompt)

        with st.chat_message("assistant", avatar="🤖"):
            response_text = st.write_stream(response_generator(response))
        add_message("assistant", response_text)

        feedback_system(response)

st.title("Gemini Chatbot App")

if "messages" not in st.session_state:
    st.session_state.messages = []

google_api_key = setup_sidebar()
model = setup_google_api(google_api_key)

if model:
    main(model)
