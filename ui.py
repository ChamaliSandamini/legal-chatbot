import streamlit as st
from datetime import datetime
from chatbot_query import answer_question

st.set_page_config(page_title="Legal Chatbot", page_icon="⚖️")

# --- Company name at top center ---
st.markdown(
    """
    <h2 style='text-align: center; color: #2E86C1;'>
        Ontario Real Estate & Business Brokers
    </h2>
    """,
    unsafe_allow_html=True
)

# --- Title ---
st.title("⚖️ Legal Chatbot")
st.write("Ask me questions about the law text and I’ll try to answer with references.")

# --- Load external CSS ---
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Initialize chat history ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# --- Function to handle user query ---
def handle_submit():
    user_input = st.session_state.input_box.strip()
    if not user_input:
        st.warning("Please enter a question.")
        return

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    # Get bot response
    with st.spinner("Thinking..."):
        try:
            answer = answer_question(user_input)
            st.session_state.messages.append({
                "role": "bot",
                "content": answer,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        except Exception as e:
            st.session_state.messages.append({
                "role": "bot",
                "content": f"Error: {e}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

    # Clear the text box safely
    st.session_state.input_box = ""

# --- Display chat history inside scrollable container ---
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    timestamp = msg.get("timestamp", "")
    if msg["role"] == "user":
        st.markdown(
            f"<div class='user-bubble'>You: {msg['content']}<br><span class='timestamp'>{timestamp}</span></div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='bot-bubble'>Chatbot: {msg['content']}<br><span class='timestamp'>{timestamp}</span></div>",
            unsafe_allow_html=True
        )
st.markdown('</div>', unsafe_allow_html=True)

# --- Input box (clears automatically after submission) ---
st.text_input(
    "Your Question:",
    key="input_box",
    on_change=handle_submit
)
