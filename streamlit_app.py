# Copyright 2025
# ELEVARE HR – Stable White UI (Sidebar + Layout Fixed)

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
# GLOBAL CSS – CLEAN WHITE, NO BREAKAGE
# -------------------------------------------------

st.markdown("""
<style>

/* Prevent horizontal scroll everywhere */
html, body {
    overflow-x: hidden;
}

/* Force white theme */
html, body, [class*="css"] {
    background-color: #ffffff !important;
    color: #111827 !important;
}

/* Main container */
.block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}

/* App canvas */
[data-testid="stAppViewContainer"] {
    background-color: #ffffff !important;
}

/* IMPORTANT: Do NOT hide header (keeps sidebar toggle working) */
header {
    background: #ffffff;
    border-bottom: 1px solid #e5e7eb;
}

/* Footer hidden safely */
footer {
    visibility: hidden;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e5e7eb;
}

/* Sidebar text */
[data-testid="stSidebar"] * {
    color: #111827 !important;
}

/* Inputs */
input, textarea, select {
    background-color: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #d1d5db !important;
}

/* Buttons */
button {
    background-color: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #d1d5db !important;
    border-radius: 6px !important;
}
button:hover {
    border-color: #2563eb !important;
    color: #2563eb !important;
}

/* Chat bubbles */
[data-testid="stChatMessage"] {
    background: transparent !important;
}

/* Chat input – NO fixed width, NO vertical bar */
[data-testid="stChatInput"] {
    position: sticky;
    bottom: 0;
    background-color: #ffffff !important;
    border-top: 1px solid #e5e7eb;
    padding-bottom: 8px;
}

/* Kill any rogue borders */
* {
    box-shadow: none !important;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------

with st.sidebar:
    st.markdown("### Folders")
    st.text_input("Search folders")

    st.selectbox("", ["+ New Folder"])

    st.divider()

    st.markdown("### Chats")
    st.text_input("Search chats")

    st.button("New Chat")
    st.button("Delete Folder")

# -------------------------------------------------
# MAIN HERO (UNCHANGED TEXT)
# -------------------------------------------------

st.markdown("""
<div style="padding:32px 48px 16px 48px;">
    <h1 style="font-size:28px; font-weight:600; margin-bottom:6px;">
        ELEVARE HR 👨‍💻
    </h1>
    <p style="color:#6b7280; font-size:14px; margin-bottom:4px;">
        Hire smart, not hard — your AI mate for shortlisting
    </p>
    <p style="color:#9ca3af; font-size:13px;">
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
