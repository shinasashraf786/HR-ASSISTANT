import os
import time
import json
from openai import OpenAI
import streamlit as st

# Configure OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ASSISTANT_ID = "asst_bBLvW1TIJ2lBYTjCYlfftrhu"
DATA_FILE = "conversations.json"

# ----------------------
# Utilities
# ----------------------

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"folders": {}, "current_folder": None}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def save_chat_to_folder(data, folder, chat):
    if folder not in data["folders"]:
        data["folders"][folder] = []
    data["folders"][folder].append(chat)
    save_data(data)

def delete_folder(data, folder):
    if folder in data["folders"] and not data["folders"][folder]:
        del data["folders"][folder]
        if data["current_folder"] == folder:
            data["current_folder"] = None
        save_data(data)
        return True
    return False

# ----------------------
# Streamlit Config
# ----------------------

st.set_page_config(page_title="HR Shortlister", page_icon="🤖")

# ----------------------
# Session Setup
# ----------------------

if "data" not in st.session_state:
    st.session_state.data = load_data()

if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

if "messages" not in st.session_state:
    st.session_state.messages = []

data = st.session_state.data
folders = list(data["folders"].keys())
selected_folder = data.get("current_folder")

# ----------------------
# Sidebar UI (Folder + Chat)
# ----------------------

with st.sidebar:
    st.subheader("Folders")

    folder_search = st.text_input("Search folders")
    filtered_folders = [f for f in folders if folder_search.lower() in f.lower()]
    folder_selection = st.selectbox("Select folder", ["+ New Folder"] + filtered_folders)

    if folder_selection and folder_selection != "+ New Folder":
        data["current_folder"] = folder_selection
        save_data(data)

    new_folder = st.text_input("Create new folder")
    if new_folder and st.button("Create Folder"):
        if new_folder not in data["folders"]:
            data["folders"][new_folder] = []
            data["current_folder"] = new_folder
            save_data(data)
            st.experimental_rerun()

    st.divider()
    st.subheader("Chats")

    chat_search = st.text_input("Search chats")

    if selected_folder := data.get("current_folder"):
        chats = data["folders"].get(selected_folder, [])
        filtered_chats = [c for c in chats if chat_search.lower() in c["user"].lower()]
    else:
        chats = []
        filtered_chats = []

    if st.button("New Chat"):
        st.session_state.messages = []
        st.session_state.thread_id = client.beta.threads.create().id

    if st.button("🗑 Delete Folder"):
        if selected_folder:
            success = delete_folder(data, selected_folder)
            if success:
                st.success("Folder deleted.")
                st.experimental_rerun()
            else:
                st.warning("Folder not empty.")

    if filtered_chats:
        for chat in filtered_chats:
            st.markdown(f"🔴 **{chat['user']}**\n\n🟠 {chat['assistant']}")

# ----------------------
# Main Page: Chat Assistant
# ----------------------

st.title("ELEVARE HR 👨‍💻")
st.caption("Hire smart, not hard — your AI mate for shortlisting")

st.markdown("""
With ELEVARE HR, you can:
- Cut through the pile and find top candidates fast.
- Build sharp shortlists that hit the mark.
- Get hiring insights that actually help.
""")

# Display prior messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input and response
if prompt := st.chat_input("Ask HR Shortlister anything..."):
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

                if selected_folder:
                    save_chat_to_folder(
                        data,
                        selected_folder,
                        {"user": prompt, "assistant": reply}
                    )

            except Exception as e:
                st.error(f"An error occurred: {e}")
