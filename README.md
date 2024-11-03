# Gemini Chatbot App

Gemini Chatbot App is an interactive chat application that uses the Google Generative AI API to generate real-time responses. The project provides a simple and user-friendly interface, allowing users to interact with the language model and provide feedback on the responses received.

## Features

- **Real-Time Interaction:** Users can send messages and receive instant responses from the model.
- **Feedback System:** Users can evaluate the usefulness of responses, contributing to the continuous improvement of the model.
- **Chat Clearing:** Includes a button to clear the chat history, allowing for a fresh start.

## Prerequisites

- Python 3.7 or higher
- Libraries: `streamlit`, `google-generativeai`
- A Google API key to access the generative model. You can obtain your key [here](https://ai.google.dev/gemini-api?gad_source=1&gclid=Cj0KCQjwvpy5BhDTARIsAHSilyl3VIxT1c2EvU1dIoh0fmZLMVf6y_9Yacf0ds2OZQ6UYVoBr4jYiZUaAl4mEALw_wcB).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ntsation/gemini-chatbot-app.git
   cd gemini-chatbot-app
   ```

2. Install the dependencies:
   ```bash
   pip install streamlit google-generativeai
   ```

3. Obtain a Google API key and set it in the application.

## Usage

1. Start the application:
   ```bash
   streamlit run app.py
   ```

2. Access the application in your browser, usually at `http://localhost:8501`.

3. Enter your API key in the sidebar and start interacting with the chat model.