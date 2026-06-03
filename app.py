
import streamlit as st
from huggingface_hub import InferenceClient

# ==========================================
# 1. Page Configuration & Setup
# ==========================================
st.set_page_config(page_title="Chef Alex - Culinary Assistant", page_icon="🍳")
st.title("🍳 Chef Alex")
st.write("Welcome! I am your personal culinary assistant. Ask me anything about recipes, cooking techniques, or food adjustments!")

# ==========================================
# 2. Initialize Hugging Face Client securely
# ==========================================
# Fetching the token from your Streamlit Secrets dashboard
hf_token = st.secrets["GEMINI_API_KEY"] 
client = InferenceClient(provider="hf-inference", token=hf_token)

# ==========================================
# 3. Guardrail Logic (In-Scope vs Out-of-Scope)
# ==========================================
def is_out_of_scope(query):
    # Convert query to lowercase to catch variations
    q = query.lower()
    
    # List of blocked keywords unrelated to cooking
    blocked_keywords = [
        "code", "python", "java", "javascript", "c++", "html", "css", 
        "programming", "software", "bug", "database", "git", "github",
        "terminal", "machine learning", "neural network", "framework"
    ]
    
    # Check if any blocked word is in the user's query
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

# Display existing chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# 5. React to User Input
# ==========================================
if user_query := st.chat_input("How do I make a perfect soufflé?", key="chef_chat_input"):
    # Display user message and save to history
    st.chat_message("user").markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Check Guardrails
    if is_out_of_scope(user_query):
        response_text = "I'm sorry, I am Chef Alex, your culinary assistant. I can only help you with recipes, food, and cooking questions!"
    else:
        try:
            # Call Hugging Face API natively using a fast Llama 3 model
            response = client.chat.completions.create(
                model="meta-llama/Meta-Llama-3-8B-Instruct",
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