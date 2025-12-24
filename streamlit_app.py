import os
import time
import streamlit as st
from openai import OpenAI

# -------------------------------
# Config
# -------------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ASSISTANT_ID = "asst_bBLvW1TIJ2lBYTjCYlfftrhu"

st.set_page_config(
    page_title="INNOVA DATA INTEGRATION AND EMAIL CATEGORISATION",
    layout="wide"
)

# -------------------------------
# Styling (Dark Sidebar, Light Content)
# -------------------------------
st.markdown("""
<style>
    /* Sidebar background */
    .st-emotion-cache-1v0mbdj, .st-emotion-cache-6qob1r {
        background-color: #111;
        color: white;
    }

    /* Sidebar input + dropdown text */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div > input {
        background-color: #222 !important;
        color: white !important;
    }

    /* Buttons */
    .stButton>button {
        background-color: #444;
        color: white;
        border: none;
        padding: 0.4rem 1rem;
        border-radius: 6px;
    }
    .stButton>button:hover {
        background-color: #666;
    }

    /* Main header */
    .block-container {
        padding: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Sidebar (Folders & Chats)
# -------------------------------
st.sidebar.title("Folders")
st.sidebar.text_input("Search folders")
st.sidebar.selectbox("Select folder", options=["+ New Folder"])
st.sidebar.text_input("Create new folder")

st.sidebar.markdown("---")

st.sidebar.title("Chats")
st.sidebar.text_input("Search chats")
st.sidebar.button("New Chat")
st.sidebar.button("Delete Folder")

# -------------------------------
# Header
# -------------------------------
st.markdown("""
<h1 style='color:white;'>INNOVA DATA INTEGRATION AND EMAIL CATEGORISATION 🔁</h1>
<p style='color:grey;'>Handle INNOVA data and email categories in one place, without the clutter</p>
""", unsafe_allow_html=True)

# -------------------------------
# Initialise Session State
# -------------------------------
if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------
# Show Previous Messages
# -------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------------
# Chat Input
# -------------------------------
if prompt := st.chat_input("Ask anything about INNOVA data..."):
    # Show user input
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send message to thread
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=prompt
    )

    # Run assistant + stream reply
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                run = client.beta.threads.runs.create(
                    thread_id=st.session_state.thread_id,
                    assistant_id=ASSISTANT_ID
                )

                # Wait until complete
                while True:
                    status = client.beta.threads.runs.retrieve(
                        thread_id=st.session_state.thread_id,
                        run_id=run.id
                    )
                    if status.status == "completed":
                        break
                    time.sleep(1)

                # Get last assistant message
                messages = client.beta.threads.messages.list(
                    thread_id=st.session_state.thread_id
                )
                reply = messages.data[0].content[0].text.value

                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

            except Exception as e:
                st.error(f"An error occurred: {e}")
