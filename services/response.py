def get_answer(model, prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise RuntimeError(f"Error generating response: {str(e)}")
