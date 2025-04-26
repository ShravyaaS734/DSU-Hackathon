import streamlit as st
import google.generativeai as genai

api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

model = genai.GenerativeModel(model_name="models/gemini-2.0-flash-thinking-exp")

def get_business_advice(user_input, conversation_history):
    conversation_history.append(f"You: {user_input}")
    full_conversation = "\n".join(conversation_history)
    response = model.generate_content(full_conversation)
    conversation_history.append(f"Chatbot: {response.text}")
    return response.text, conversation_history

def is_business_related(user_input):
    business_keywords = ["business", "marketing", "finance", "strategy", "startup", "management", "growth", "investment", "economy", "sales", "profit", "loss", "strategies", "company", "field"]
    return any(keyword.lower() in user_input.lower() for keyword in business_keywords)

st.title("Business Advisor Chatbot")
st.markdown("""
    I'm your business advisor chatbot! You can ask me about business strategies, marketing, finance, and more.
    Type 'exit' or 'quit' to end the chat, or 'clear' to reset the conversation.
""")

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

user_input = st.text_input("You: ", "")

if user_input:
    if user_input.lower() in ["exit", "quit", "bye"]:
        st.write("Goodbye! Feel free to reach out if you need more advice.")
        st.session_state.conversation_history = []  
    elif user_input.lower() == "clear":
        st.session_state.conversation_history = []  
        st.write("Conversation history cleared! Feel free to ask anything.")
    else:
        if is_business_related(user_input):
            response, updated_history = get_business_advice(user_input, st.session_state.conversation_history)
            st.session_state.conversation_history = updated_history  
            st.write(f"Chatbot: {response}")
        else:
            st.write("Please ask business-related questions (e.g., marketing, finance, strategy, etc.).")

st.write("### Conversation History")
for message in st.session_state.conversation_history:
    st.write(message)
