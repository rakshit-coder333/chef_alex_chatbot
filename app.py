
import streamlit as st
from openai import OpenAI

# ==========================================
# 1. Page Configuration & Setup
# ==========================================
st.set_page_config(page_title="Chef Alex - Culinary Assistant", page_icon="🍳", layout="wide")
st.title("🍳 Chef Alex")
st.markdown("""
    <div class="chef-card">
        <h3 style='margin-top:0; color:#ff4b4b;'>Welcome to Chef Alex AI</h3>
        <p style='margin:0; color:#b0b3b8; font-size: 15px; line-height: 1.5;'>
            An intelligent, production-grade culinary engine. Ask me anything regarding recipes, 
            ingredient alternatives, or kitchen techniques. Built-in system guardrails will automatically 
            restrict non-culinary topics.
        </p>
    </div>
""", unsafe_allow_html=True)
# ==========================================
st.markdown("""
    <style>
    /* 1. Main Background and Base Typography */
    .stApp {
        background: linear-gradient(135deg, #1e1e24 0%, #121214 100%);
        color: #f5f6f8;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* 2. Sleek Custom Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1a1a22 !important;
        border-right: 1px solid #2d2d38;
    }
    
    /* 3. Style all Sidebar Action Buttons (Conversations & New Chat) */
    div[data-testid="stSidebar"] button {
        background-color: #242430 !important;
        color: #e2e8f0 !important;
        border: 1px solid #3f3f50 !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        transition: all 0.2s ease-in-out !important;
        font-weight: 500 !important;
        text-align: left !important;
    }
    
    /* Hover and Focus animations for Buttons */
    div[data-testid="stSidebar"] button:hover {
        background-color: #ff4b4b !important; /* Premium Red Accent */
        color: #ffffff !important;
        border-color: #ff4b4b !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.2);
    }
    
    /* 4. Chat Input Box Styling */
    div[data-testid="stChatInput"] textarea {
        background-color: #1e1e26 !important;
        color: #ffffff !important;
        border: 1px solid #3a3a4c !important;
        border-radius: 10px !important;
    }
    
    /* 5. Custom Card Callout Box */
    .chef-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 25px;
        backdrop-filter: blur(10px);
    }
    </style>
""", unsafe_allow_html=True)
# ==========================================
# 2. Initialize Secure Groq Client
# ==========================================
client = OpenAI(
    api_key=st.secrets["GEMINI_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

# ==========================================
# 3. Persistent Multi-Chat Storage
# ==========================================
# 'all_chats' stores multiple chat sessions. 
# 'current_chat_idx' tracks which chat we are currently viewing.
if "all_chats" not in st.session_state:
    st.session_state.all_chats = [
        {
            "title": "Chat 1 (Active)",
            "messages": [{"role": "assistant", "content": "Hello! I am Chef Alex. What are we cooking today?"}]
        }
    ]
if "current_chat_idx" not in st.session_state:
    st.session_state.current_chat_idx = 0

# Active session shortcut
active_chat = st.session_state.all_chats[st.session_state.current_chat_idx]

# ==========================================
# 4. Left Sidebar Layout (Chat History Tab)
# ==========================================
st.sidebar.title("💬 Chat History")

# Button to start a completely new conversation
if st.sidebar.button("➕ New Chat", use_container_width=True):
    new_chat_num = len(st.session_state.all_chats) + 1
    st.session_state.all_chats.append({
        "title": f"Chat {new_chat_num} (Active)",
        "messages": [{"role": "assistant", "content": "Hello! I am Chef Alex. What are we cooking today?"}]
    })
    # Switch automatically to the newest chat
    st.session_state.current_chat_idx = len(st.session_state.all_chats) - 1
    st.rerun()

st.sidebar.write("---")

# Render past chats as selectable buttons in the sidebar
st.sidebar.write("**Your Conversations:**")
for idx, chat in enumerate(st.session_state.all_chats):
    # Highlight the currently active chat tab
    button_label = chat["title"]
    
    if st.sidebar.button(button_label, key=f"sidebar_chat_{idx}", use_container_width=True):
        st.session_state.current_chat_idx = idx
        st.rerun()

# ==========================================
# 5. Guardrail Logic
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
# 6. Render Active Chat Messages
# ==========================================
for message in active_chat["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# 7. Handle User Input
# ==========================================
if user_query := st.chat_input("How do I make a perfect soufflé?", key="chef_input_v3"):
    # Render and save user message
    st.chat_message("user").markdown(user_query)
    active_chat["messages"].append({"role": "user", "content": user_query})
    
    # Generate a dynamic title based on their first question!
    if len(active_chat["messages"]) == 2:  # System/assistant is 1, user is 2
        # Clean up the query to make a short sidebar tab title
        short_title = user_query[:20] + "..." if len(user_query) > 20 else user_query
        active_chat["title"] = short_title

    # Check Guardrails
    if is_out_of_scope(user_query):
        response_text = "I'm sorry, I am Chef Alex, your culinary assistant. I can only help you with recipes, food, and cooking questions!"
    else:
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are Chef Alex, an expert, professional, and helpful culinary assistant."},
                    *active_chat["messages"] # Pass entire history for context!
                ],
                max_tokens=500
            )
            response_text = response.choices[0].message.content
        except Exception as e:
            response_text = f"An error occurred during connection: {e}"

    # Render and save assistant response
    with st.chat_message("assistant"):
        st.markdown(response_text)
    active_chat["messages"].append({"role": "assistant", "content": response_text})
    st.rerun()