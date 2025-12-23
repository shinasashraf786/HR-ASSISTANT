# ELEVARE HR - Final Light UI with Visible Chat Actions (no box styling)
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
st.session_state["conversations"][cid] = {"title": "New Conversation", "folder": selected_folder, "messages": []}
thread = client.beta.threads.create()
st.session_state["threads"][cid] = thread.id
st.session_state["active_convo"] = cid
save_conversations(st.session_state["conversations"])
st.rerun()


for cid, convo in st.session_state["conversations"].items():
if convo.get("folder") == selected_folder and chat_search.lower() in convo["title"].lower():
col1, col2, col3 = st.columns([6, 1, 1])
if col1.button(convo["title"], key=cid):
st.session_state["active_convo"] = cid
st.rerun()
if col2.button("\u274C", key=f"del_{cid}"):
st.session_state["conversations"].pop(cid)
st.session_state["threads"].pop(cid, None)
if st.session_state["active_convo"] == cid:
st.session_state["active_convo"] = None
save_conversations(st.session_state["conversations"])
st.rerun()
if col3.download_button("\u2B07\uFE0F", data=open(export_chat_to_pdf(cid, convo), "rb"), file_name=f"{convo['title']}.pdf", mime="application/pdf", key=f"pdf_{cid}"):
pass


if st.button("\U0001F5D1\uFE0F Delete Folder"):
ids_to_delete = [cid for cid, c in st.session_state["conversations"].items() if c.get("folder") == selected_folder]
for cid in ids_to_delete:
st.session_state["conversations"].pop(cid, None)
st.session_state["threads"].pop(cid, None)
st.session_state["active_convo"] = None
save_conversations(st.session_state["conversations"])
st.rerun()


# --------- MAIN ---------


if st.session_state["active_convo"] is None:
st.markdown("""
<div style="padding:48px 64px;">
<h1>ELEVARE HR \U0001F468‍\U0001F4BB</h1>
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
st.caption(f"Folder: {convo.get('folder', 'Uncategorised')}")


with st.expander("\u2699 Chat Settings"):
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
