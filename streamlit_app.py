import os
import json
import time
from openai import OpenAI
import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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

# ---------- WHITE UI + CLEAN CSS ----------
st.markdown("""
<style>
/* Hide Streamlit header and footer */
header, footer {
    visibility: hidden;
    height: 0;
}

/* Body styling */
html, body, [class*="css"] {
    background-color: #ffffff !important;
    color: #1e293b !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #f8fafc !important;
    border-right: 1px solid #e2e8f0 !important;
}
[data-testid="stSidebar"] * {
    color: #1e293b !important;
}

/* Inputs */
input, textarea, select {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
}

/* Buttons */
button {
    background-color: #ffffff !important;
    color: #1e293b !important;
    border: 1px solid #cbd5e1 !important;
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

/* Chat input */
[data-testid="stChatInput"] {
    background-color: #ffffff !important;
    border-top: 1px solid #e2e8f0 !important;
    padding-bottom: 8px;
}

/* Remove box around ❌ ⬇️ */
[data-testid="stChatMessageAction"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- Data helpers ----------
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

# ---------- Init session ----------
if "conversations" not in st.session_state:
    st.session_state["conversations"] = load_conversations()
if "active_convo" not in st.session_state:
    st.session_state["active_convo"] = None
if "threads" not in st.session_state:
    st.session_state["threads"] = {}

# ---------- Sidebar ----------
def get_folders():
    return sorted(set(c.get("folder", "Uncategorised")
                      for c in st.session_state["conversations"].values()))

with st.sidebar:
    st.header("Folders")

    folder_search = st.text_input("Search folders")
    folders = [f for f in get_folders() if folder_search.lower() in f.lower()]
    selected_folder = st.selectbox("Select folder", folders + ["+ New Folder"])

    if selected_folder == "+ New Folder":
        new_folder_input = st.text_input("Create new folder")
        if new_folder_input:
            selected_folder = new_folder_input

    st.divider()
    st.header("Chats")
    chat_search = st.text_input("Search chats")

    if st.button("New Conversation"):
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
            col1, col2, col3 = st.columns([6, 1, 1])
            if col1.button(convo["title"], key=f"open_{cid}"):
                st.session_state["active_convo"] = cid
                st.rerun()
            if col2.button("❌", key=f"del_{cid}"):
                st.session_state["conversations"].pop(cid, None)
                st.session_state["threads"].pop(cid, None)
                if st.session_state["active_convo"] == cid:
                    st.session_state["active_convo"] = None
                save_conversations(st.session_state["conversations"])
                st.rerun()
            with open(export_chat_to_pdf(cid, convo), "rb") as f:
                col3.download_button("⬇️", data=f, file_name=f"{convo['title']}.pdf", mime="application/pdf", key=f"pdf_{cid}")

    if st.button("🗑️ Delete Folder"):
        to_delete = [cid for cid, c in st.session_state["conversations"].items()
                     if c.get("folder") == selected_folder]
        for cid in to_delete:
            st.session_state["conversations"].pop(cid, None)
            st.session_state["threads"].pop(cid, None)
        st.session_state["active_convo"] = None
        save_conversations(st.session_state["conversations"])
        st.rerun()

# ---------- Main Chat Area ----------
if st.session_state["active_convo"] is None:
    st.markdown("""
    <div style="padding:48px 64px;">
        <h1>ELEVARE HR 👨‍💻</h1>
        <p style="color:#334155;">Hire smart, not hard — your AI mate for shortlisting</p>
        <p style="color:#64748b;">Handle candidate shortlisting in one place, without the clutter.</p>
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

    client.beta.threads.messages.create(thread_id=thread_id, role="user", content=prompt)

    with st.chat_message("assistant"):
        with st.spinner("HR Shortlister is thinking..."):
            run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=ASSISTANT_ID)
            while True:
                status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
                if status.status == "completed":
                    break
                time.sleep(1)
            reply = client.beta.threads.messages.list(thread_id=thread_id).data[0].content[0].text.value
            st.markdown(reply)
            convo["messages"].append({"role": "assistant", "content": reply})
            save_conversations(st.session_state["conversations"])
