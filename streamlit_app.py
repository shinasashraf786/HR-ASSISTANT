# Copyright 2025
# Elevare HR – Streamlit Application

import os
import time
from openai import OpenAI
import streamlit as st

# -------------------------------------------------
# Environment Setup
# -------------------------------------------------

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ASSISTANT_ID = "asst_bBLvW1TIJ2lBYTjCYlfftrhu"

st.set_page_config(
    page_title="Elevare HR",
    layout="wide",
)

# -------------------------------------------------
# Global Styling (Dark Enterprise UI)
# -------------------------------------------------

st.markdown(
    """
    <style>
    body {
        background-color: #0e1117;
    }
    .block-container {
        padding-top: 2rem;
    }
    h1, h2, h3, p {
        color: #ffffff;
    }
    .stTextInput input {
        background-color: #1c1f26;
        color: #ffffff;
    }
    .stButton button {
        background-color: #1c1f26;
        color: white;
        border-radius: 6px;
        border: 1px solid #2e3440;
    }
    .stButton button:hover {
        border-color: #4c8bf5;
        color: #4c8bf5;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# Sidebar – Folders & Chats
# -------------------------------------------------

with st.sidebar:
    st.markdown("### Folders")

    folder_search = st.text_input("Search folders")

    selected_folder = st.selectbox(
        "Select folder",
        options=["+ New Folder"],
    )

    new_folder_name = st.text_input("Create new folder")

    st.divider()

    st.markdown("### Chats")

    chat_search = st.text_input("Search chats")

    if st.button("New Chat"):
        if "thread_id" in st.session_state:
            del st.session_state.thread_id
        st.session_state.messages = []

    if st.button("Delete Folder"):
        st.warning("Folder deleted")

# -------------------------------------------------
# Main Header (Hero Section)
# -------------------------------------------------

st.markdown(
    """
    <h1> ELEVARE HR </h1>
    <p style="color:#9aa4b2; font-size:16px;">
    Hire smart, not hard. Your AI mate for shortlisting.
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <p style="color:#cfd6e4;">
    Handle candidate shortlisting in one place, without the clutter.
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

# -------------------------------------------------
# Chat Setup
# -------------------------------------------------

if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------------------------------
# Chat Input
# -------------------------------------------------

if prompt := st.chat_input("Ask Elevare HR anything..."):
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=prompt
    )

    with st.chat_message("assistant"):
        with st.spinner("Shortlisting in progress..."):
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

                st.session_state.messages.append(
                    {"role": "assistant", "content": reply}
                )

            except Exception as e:
                st.error(f"Error: {e}")
