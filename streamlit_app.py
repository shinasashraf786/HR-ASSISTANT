import os
import time
from openai import OpenAI
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

# -------------------------------------------------
# Environment Setup
# -------------------------------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ASSISTANT_ID = "asst_bBLvW1TIJ2lBYTjCYlfftrhu"

# -------------------------------------------------
# Streamlit Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="INNOVA DATA INTEGRATION AND EMAIL CATEGORISATION",
    page_icon="♾",
    layout="wide"
)

# -------------------------------------------------
# CSS Styling for Light Text and Sidebar
# -------------------------------------------------
st.markdown("""
    <style>
        .block-container {
            padding: 0 2rem;
        }
        .css-1d391kg {  
            background-color: #111;
        }
        .stTextInput>div>div>input {
            color: white;
        }
        .stTextInput>div>div {
            background-color: #222;
        }
        .stButton>button {
            background-color: #444;
            color: white;
        }
        .stButton>button:hover {
            background-color: #666;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Sidebar Functionality
# -------------------------------------------------
st.sidebar.title("Folders")
folder_search = st.sidebar.text_input("Search folders")
st.sidebar.selectbox("Select folder", options=["+ New Folder"])
create_folder = st.sidebar.text_input("Create new folder")

st.sidebar.markdown("---")
st.sidebar.title("Chats")
chat_search = st.sidebar.text_input("Search chats")
new_chat_btn = st.sidebar.button("New Chat")
delete_folder_btn = st.sidebar.button("Delete Folder")

# -------------------------------------------------
# App Header
# -------------------------------------------------
st.markdown("""
    <h1 style='color:white;'>INNOVA DATA INTEGRATION AND EMAIL CATEGORISATION ♾</h1>
    <p style='color:grey;'>Handle INNOVA data and email categories in one place, without the clutter</p>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Chat Setup
# -------------------------------------------------
if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display message history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask anything about INNOVA data..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=prompt
    )

    with st.chat_message("assistant"):
        with st.spinner("Working on it..."):
            try:
                run = client.beta.threads.runs.create(
                    thread_id=st.session_state.thread_id,
                    assistant_id=ASSISTANT_ID
                )

                while True:
                    status = client.beta.threads.runs.retrieve(
                        thread_id=st.session_state.thread_id,
                        run_id=run.id
                    )
                    if status.status == "completed":
                        break
                    time.sleep(1)

                messages = client.beta.threads.messages.list(
                    thread_id=st.session_state.thread_id
                )
                reply = messages.data[0].content[0].text.value

                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

            except Exception as e:
                st.error(f"An error occurred: {e}")
