import uuid
import streamlit as st
from langgraph_backend import workflow
from langgraph_backend import memory

def generate_thread():
    return str(uuid.uuid4())


def reset_chat():
    tid = generate_thread()

    st.session_state["thread_id"] = tid
    st.session_state["history"] = []

    add_thread(tid)


def add_thread(tid):
    if tid not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(tid)

def load_conversations(tid):
    state = workflow.get_state(
        config={"configurable": {"thread_id": tid}}
    )

    return state.values.get("messages", [])

def get_db_thread():
    db_threads = set()
    for i in memory.list(None):
        db_threads.add(i.config["configurable"]["thread_id"])
    return list(db_threads)
