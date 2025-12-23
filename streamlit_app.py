# Elevare HR – Final Clean Dark Version (No Boxes, No White Bars)

import os
import json
import time
from openai import OpenAI
import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- CONFIG ----------------

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ASSISTANT_ID = "asst_bBLvW1TIJ2lBYTjCYlfftrhu"

STORAGE_FILE = "conversations.json"
EXPORTS_DIR = "exports"
os.makedirs(EXPORTS_DIR, exist_ok=True)

st.set_page_config(
    page_title="ELEVARE HR",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- GLOBAL DARK CSS ----------------

st.markdown("""
<style>

/* Kill Streamlit header/footer */
header, footer {
    visibility: hidden;
    height: 0;
}

/* Full dark mode */
html, body, [class*="css"] {
    background-color: #0f172a !important;
    color: #e5e7eb !important;
}

/* Remove padding */
.block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}

/* App canvas */
[data-testid="stAppViewContainer"] {
    background-color: #0f172a !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #1e293b !important;
    border-right: 1px solid #334155;
}
[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

/* Inputs */
input, textarea, select {
    background-color: #1e293b !important;
    color: #f8fafc !important;
    border: 1px solid #334155 !important;
}

/* Buttons */
button {
    background-color: #1e293b !important;
    color: #f8fafc !important;
    border: 1px solid #334155 !important;
    border-radius: 6px !important;
}
button:hover {
    border-color: #3b82f6 !important;
    color: #3b82f6 !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: transparent !important;
}

/* REMOVE STREAMLIT CHAT ACTION BOXES (❌ ⬇️ etc) */
[data-testid="stChatMessageAction"] {
    display: none !important;
}
[data-testid="stChatMessageActions"] {
    display: none !important;
}

/* Chat input */
[data-testid="stChatInput"] {
    position: sticky;
    bottom: 0;
    background-color: #0f172a !important;
    border-top: 1px solid #334155;
    padding-bottom: 8px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- STORAGE HELPERS ----------------

def load_conversations():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_conversations(data):
    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def export_chat_to_pdf(cid, convo):
    filename = os.path.join(EXPORTS_DIR, f"Chat - {convo['title']}.pdf")
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    content = [
        Paragraph(f"<b>Conversation:</b> {convo['title']}", styles['Title']),
        Spacer(1, 12)
    ]
    for msg in convo["messages"]:
        role = "User" if msg["role"] == "user" else "Assistant"
        content.append(Paragraph(f"<b>{role}:</b> {msg['content']}", styles['BodyText']))
        content.append(Spacer(1, 8))
    doc.build(content)
    return filename

# ---------------- INIT STATE ----------------

if "conversations" not in st.session_state:
    st.session_state["conversations"] = load_conversations()

if "active_convo" not in st.session_state:
    st.session_state["active_convo"] = None

if "threads" not in st.session_state:
    st.session_state["threads"] = {}

# ---------------- SIDEBAR ----------------

def get_folders():
    return sorted(set(c.get("folder", "Uncategorised")
                      for c in st.session_state["conversations"].values()))

with st.sidebar:
    st.header("Folders")

    folder_search = st.text_input("Search folders")
    folders = [f for f in get_folders() if folder_search.lower() in f.lower()]
    selected_folder = st.selectbox("Select folder", folders + ["+ New Folder"])

    if selected_folder == "+ New Folder":
        new_folder = st.text_input("Create new folder")
        if new_folder:
            selected_folder = new_folder

    st.divider()
    st.header("Chats")
    chat_search = st.text_input("Search chats")

    if st.button("New Chat"):
        cid = str(time.time())
        st.session_state["conversations"][cid] = {
            "title": "New Conversation",
            "folder": selected_folder,
            "messages": []
        }
        thread = client.beta.threads.create()
        st.session_state["threads"][cid] = thread.id
        st.session_state["active_convo"] = cid
        save_conversations(st.session_state["conversations"])
        st.rerun()

    for cid, convo in st.session_state["conversations"].items():
        if convo.get("folder") == selected_folder and chat_search.lower() in convo["title"].lower():
            if st.button(convo["title"], key=f"open_{cid}"):
                st.session_state["active_convo"] = cid
                st.rerun()

    if st.button("🗑️ Delete Folder"):
        to_delete = [
            cid for cid, c in st.session_state["conversations"].items()
            if c.get("folder") == selected_folder
        ]
        for cid in to_delete:
            st.session_state["conversations"].pop(cid, None)
            st.session_state["threads"].pop(cid, None)
        st.session_state["active_convo"] = None
        save_conversations(st.session_state["conversations"])
        st.rerun()

# ---------------- MAIN VIEW ----------------

if st.session_state["active_convo"] is None:
    st.markdown("""
    <div style="padding:48px 64px;">
        <h1>ELEVARE HR 👨‍💻</h1>
        <p style="color:#cbd5e1;">Hire smart, not hard — your AI mate for shortlisting</p>
        <p style="color:#94a3b8;">Handle candidate shortlisting in one place, without the clutter.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

cid = st.session_state["active_convo"]
convo = st.session_state["conversations"][cid]

if cid not in st.session_state["threads"]:
    st.session_state["threads"][cid] = client.beta.threads.create().id

thread_id = st.session_state["threads"][cid]

st.title(convo["title"])
st.caption(f"Folder: {convo.get('folder')}")

with st.expander("⚙️ Chat Settings"):
    new_title = st.text_input("Rename chat", convo["title"])
    new_folder = st.text_input("Move to folder", convo.get("folder"))
    if st.button("Update"):
        convo["title"] = new_title or convo["title"]
        convo["folder"] = new_folder or convo["folder"]
        save_conversations(st.session_state["conversations"])
        st.rerun()

for msg in convo["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask Elevare HR anything..."):
    convo["messages"].append({"role": "user", "content": prompt})
    save_conversations(st.session_state["conversations"])

    with st.chat_message("user"):
        st.markdown(prompt)

    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt
    )

    with st.chat_message("assistant"):
        with st.spinner("HR Shortlister is thinking..."):
            run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=ASSISTANT_ID
            )
            while True:
                status = client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
                if status.status == "completed":
                    break
                time.sleep(1)

            reply = client.beta.threads.messages.list(
                thread_id=thread_id
            ).data[0].content[0].text.value

            st.markdown(reply)
            convo["messages"].append({"role": "assistant", "content": reply})
            save_conversations(st.session_state["conversations"])
