
import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT, FEW_SHOT_EXAMPLES, GUARDRAIL_RESPONSE

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["GEMINI_API_KEY"],
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
                )

st.set_page_config(page_title="Chef Alex - Culinary Assistant", page_icon="🍳")
st.title("🍳 Chef Alex: Your AI cuisine assistant")
st.write("Welcome to my kitchen! Ask me for quick recipe tweaks, smart ingredient swaps, or cooking tips.")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Quick Guardrail Check
def is_out_of_scope(user_input):
    food_keywords = ["cook", "bake", "recipe", "food", "ingredient", "taste", "salt", "chicken", "boil", "fry", "substitute", "dish", "sauce"]
    if not any(word in user_input.lower() for word in food_keywords):
        if any(tech_word in user_input.lower() for tech_word in ["code", "python", "javascript", "bug", "software"]):
            return True
    return False

# React to user input
# React to user input
if user_query := st.chat_input("How do I make a perfect soufflé?"):
    # 1. Immediately display the user message and save it to history
    st.chat_message("user").markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})

    if is_out_of_scope(user_query):
        response_text = GUARDRAIL_RESPONSE
    else:
        try:
            messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}]
            for example in FEW_SHOT_EXAMPLES:
                messages_payload.append(example)
            for msg in st.session_state.messages:
                messages_payload.append({"role": msg["role"], "content": msg["content"]})

            response = client.chat.completions.create(
                model="gemini-2.5-flash",  # Using a highly stable model version
                messages=messages_payload,
                temperature=0.7
            )
            response_text = response.choices[0].message.content
        except Exception as e:
            if "503" in str(e):
                response_text = "Chef Remy's kitchen is packed with guests right now! 🍳 Please wait a moment and ask me again—the oven is warming back up!"
            else:
                response_text = f"An error occurred: {str(e)}"

    # 2. Display the assistant response and save it to history immediately
    with st.chat_message("assistant"):
        st.markdown(response_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})

# Sidebar Feedback System
# Sidebar Layout: Chat History Log & Feedback
st.sidebar.title("📜 Conversation Log")

# Display a scannable list of user questions sent so far
if st.session_state.messages:
    user_queries = [msg["content"] for msg in st.session_state.messages if msg["role"] == "user"]
    if user_queries:
        for i, query in enumerate(user_queries, 1):
            # Truncate long questions so they look neat in the sidebar
            short_query = query if len(query) < 30 else query[:27] + "..."
            st.sidebar.text(f"{i}. {short_query}")
    
    st.sidebar.markdown("---") # Visual separator line
    
    # Feedback Panel
    st.sidebar.title("👍 Feedback")
    st.sidebar.write("Rate the last response:")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Good"):
            st.sidebar.success("Logged! Thanks!")
    with col2:
        if st.button("Bad"):
            st.sidebar.error("Logged. We will optimize!")
else:
    st.sidebar.info("Your chat session history will appear here once you start messaging Chef Remy.")