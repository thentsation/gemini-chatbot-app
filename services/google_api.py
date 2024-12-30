import google.generativeai as genai

def setup_google_api(api_key):
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model
    return None
