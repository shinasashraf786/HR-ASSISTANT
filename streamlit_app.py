# Copyright 2025
# HR Shortlister Streamlit Chat Application

import os
import time
#from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

# -------------------------------------------------
# Environment Setup
# -------------------------------------------------

# Load environment variables from .env
#load_dotenv()

# Configure OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Your Assistant ID
ASSISTANT_ID = "asst_bBLvW1TIJ2lBYTjCYlfftrhu"

# Streamlit Page Config
st.set_page_config(page_title="HR Shortlister", page_icon="🤖")

# -------------------------------------------------
# App Header
# -------------------------------------------------

st.title("ELEVARE HR 👨‍💻")
st.caption("Hire smart, not hard — your AI mate for shortlisting")

st.markdown("""
With ELEVARE HR, you can:
- Cut through the pile and find top candidates fast.
- Build sharp shortlists that hit the mark.
- Get hiring insights that actually help.
""")

# -------------------------------------------------
# Chat Interface Setup
# -------------------------------------------------

if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------------------------------
# User Input
# -------------------------------------------------

if prompt := st.chat_input("Ask HR Shortlister anything..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to thread
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=prompt
    )

    # Run the assistant
    with st.chat_message("assistant"):
        with st.spinner("HR Shortlister is thinking..."):
            try:
                run = client.beta.threads.runs.create(
                    thread_id=st.session_state.thread_id,
                    assistant_id=ASSISTANT_ID
                )

                # Poll until run completes
                while True:
                    status = client.beta.threads.runs.retrieve(
                        thread_id=st.session_state.thread_id,
                        run_id=run.id
                    )
                    if status.status == "completed":
                        break
                    time.sleep(1)

                # Get assistant reply
                messages = client.beta.threads.messages.list(
                    thread_id=st.session_state.thread_id
                )
                reply = messages.data[0].content[0].text.value

                st.markdown(reply)

                # Store assistant response
                st.session_state.messages.append({"role": "assistant", "content": reply})

            except Exception as e:
                st.error(f"An error occurred: {e}")


