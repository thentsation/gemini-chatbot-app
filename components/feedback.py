import streamlit as st

def feedback_system(response):
    feedback = st.radio("How would you rate the response?", ("Helpful", "Somewhat Helpful", "Not Relevant"))
    if st.button("Submit Feedback"):
        st.success("Thank you for your feedback!")
