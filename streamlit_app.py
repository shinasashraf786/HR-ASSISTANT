# Copyright 2025
# HR Shortlister Streamlit Chat Application

import os
import time
from openai import OpenAI
import streamlit as st

# -------------------------------------------------
# Config
# -------------------------------------------------

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ASSISTANT_ID = "asst_bBLvW1TIJ2lBYTjCYlfftrhu"

st.set_page_config(
    page_title="ELEVARE HR",
    layout="wide",
)

# -------------------------------------------------
# GLOBAL CSS – MATCH INNOVA UI
# -------------------------------------------------

st.markdown("""
<style>

/* Remove Streamlit padding */
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* App background */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top, #0f172a 0%, #020617 70%);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #020617;
    border-right: 1px solid #0f172a;
}

/* Sidebar text */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: #e5e7eb;
}

/* Inputs */
input, textarea {
    background-color: #020617 !important;
    color: #e5e7eb !important;
    border: 1px solid #1e293b !important;
}

/* Buttons */
button {
    background-color: #020617 !important;
    color: #e5e7eb !important;
    border: 1px solid #1e293b !important;
    border-radius: 6px !important;
}
button:hover {
    border-color: #6366f1 !important;
    color: #6366f1 !important;
}

/* Chat bubbles */
[data-testid="stChatMessage"] {
    background: transparent !important;
}

/* Chat input bar */
[data-testid="stChatInput"] {
    position: fixed;
    bottom: 24px;
    left: 22%;
    width: 56%;
    background: transparent;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# SIDEBAR (same structure as INNOVA)
# -------------------------------------------------

with st.sidebar:
    st.markdown("### Folders")
    st.text_input("", placeholder="Search folders")
    st.selectbox("", ["+ New Folder"])

    st.divider()

    st.markdown("### Chats")
    st.text_input("", placeholder="Search chats")

    st.button("New Chat")
    st.button("Delete Folder")

# -------------------------------------------------
# MAIN HERO SECTION (UNCHANGED TEXT)
# -------------------------------------------------

st.markdown("""
<div style="padding:60px 80px 20px 80px;">
    <h1 style="margin-bottom:8px;">ELEVARE HR 👨‍💻</h1>
    <p style="color:#9ca3af; margin-bottom:4px;">
        Hire smart, not hard — your AI mate for shortlisting
    </p>
    <p style="color:#6b7280;">
        Handle candidate shortlisting in one place, without the clutter.
    </p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# CHAT LOGIC (UNCHANGED)
# -------------------------------------------------

if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------------------------------
# CHAT INPUT
# -------------------------------------------------

if prompt := st.chat_input("Ask Elevare HR anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=prompt
    )

    with st.chat_message("assistant"):
        with st.spinner("HR Shortlister is thinking..."):
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
