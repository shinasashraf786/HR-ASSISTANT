# Copyright 2025
# ELEVARE HR – Fully Dark INNOVA-Style UI

import os
import time
from openai import OpenAI
import streamlit as st

# -------------------------------------------------
# CONFIG
# -------------------------------------------------

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ASSISTANT_ID = "asst_bBLvW1TIJ2lBYTjCYlfftrhu"

st.set_page_config(
    page_title="ELEVARE HR",
    layout="wide",
)

# -------------------------------------------------
# GLOBAL CSS – FORCE FULL DARK MODE
# -------------------------------------------------

st.markdown("""
<style>

/* Force dark everywhere */
html, body, [class*="css"] {
    background-color: #020617 !important;
    color: #e5e7eb !important;
}

/* Remove Streamlit padding */
.block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}

/* App container */
[data-testid="stAppViewContainer"] {
    background-color: #020617 !important;
}

/* Hide Streamlit header/footer */
header, footer {
    visibility: hidden;
    height: 0px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #020617 !important;
    border-right: 1px solid #0f172a;
    width: 280px;
}

/* Sidebar text */
[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

/* Inputs */
input, textarea, select {
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
    border-color: #2563eb !important;
    color: #2563eb !important;
}

/* Main canvas */
.main {
    background-color: #020617 !important;
    min-height: 100vh;
}

/* Chat bubbles transparent */
[data-testid="stChatMessage"] {
    background: transparent !important;
}

/* Chat input fixed bottom */
[data-testid="stChatInput"] {
    position: fixed;
    bottom: 20px;
    left: 320px;
    right: 320px;
    background-color: #020617 !important;
    border-top: 1px solid #1e293b;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# SIDEBAR – SAME STRUCTURE AS INNOVA
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
# MAIN HERO – TEXT UNCHANGED
# -------------------------------------------------

st.markdown("""
<div style="padding:48px 64px 24px 64px;">
    <h1 style="font-size:28px; font-weight:600; margin-bottom:8px;">
        ELEVARE HR 👨‍💻
    </h1>
    <p style="color:#9ca3af; font-size:14px; margin-bottom:4px;">
        Hire smart, not hard — your AI mate for shortlisting
    </p>
    <p style="color:#6b7280; font-size:13px;">
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

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------------------------------
# CHAT INPUT
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
