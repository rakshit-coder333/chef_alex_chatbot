
import streamlit as st
from openai import OpenAI

# ==========================================
# 1. Page Configuration & Setup
# ==========================================
st.set_page_config(page_title="Chef Alex - Culinary Assistant", page_icon="🍳")
st.title("🍳 Chef Alex")
st.write("Welcome! I am your personal culinary assistant. Ask me anything about recipes, cooking techniques, or food adjustments!")

# ==========================================
# 2. Initialize Secure Groq Client (Using OpenAI Library Format)
# ==========================================
client = OpenAI(
    api_key=st.secrets["GEMINI_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

# ==========================================
# 3. Guardrail Logic (In-Scope vs Out-of-Scope)
# ==========================================
def is_out_of_scope(query):
    q = query.lower()
    blocked_keywords = [
        "code", "python", "java", "javascript", "c++", "html", "css", 
        "programming", "software", "bug", "database", "git", "github",
        "terminal", "machine learning", "neural network", "framework"
    ]
    for word in blocked_keywords:
        if word in q:
            return True
    return False

# ==========================================
# 4. Initialize Chat History
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am Chef Alex. What are we cooking today?"}
    ]

# Display existing chat history (This will load perfectly now!)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# 5. React to User Input
# ==========================================
if user_query := st.chat_input("How do I make a perfect soufflé?", key="chef_input_v2"):
    # Display user message and save to history
    st.chat_message("user").markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Check Guardrails
    if is_out_of_scope(user_query):
        response_text = "I'm sorry, I am Chef Alex, your culinary assistant. I can only help you with recipes, food, and cooking questions!"
    else:
        try:
            # Call Groq's high-speed engine
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are Chef Alex, an expert, professional, and helpful culinary assistant."},
                    {"role": "user", "content": user_query}
                ],
                max_tokens=500
            )
            response_text = response.choices[0].message.content
        except Exception as e:
            response_text = f"An error occurred during connection: {e}"

    # Display Chef response and save to history
    with st.chat_message("assistant"):
        st.markdown(response_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})