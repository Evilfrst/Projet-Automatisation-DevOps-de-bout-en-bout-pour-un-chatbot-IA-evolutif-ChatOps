def get_response(user_input: str) -> str:
    # Simple logique (remplaçable par OpenAI plus tard)
    if "hello" in user_input.lower():
        return "Hello! How can I help you?"
    elif "bye" in user_input.lower():
        return "Goodbye!"
    return "I am a simple chatbot for now."
