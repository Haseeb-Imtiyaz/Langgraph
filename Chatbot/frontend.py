import streamlit as st
import time

from langgraph_backend import workflow
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from utils import (
    generate_thread,
    reset_chat,
    add_thread,
    load_conversations,
    get_db_thread
)

from ui import (
    setup_page,
    apply_styles,
    show_sidebar_title,
    show_chat_title
)


# -----------------------------
# UI SETUP
# -----------------------------

setup_page()
apply_styles()
show_sidebar_title()


# -----------------------------
# Sidebar
# -----------------------------

if st.sidebar.button("＋ New Chat"):
    reset_chat()

st.sidebar.header("Conversation History")


# -----------------------------
# Session State
# -----------------------------

if "history" not in st.session_state:
    st.session_state["history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = get_db_thread()

if "thread_names" not in st.session_state:
    st.session_state["thread_names"] = {}


add_thread(st.session_state["thread_id"])


# -----------------------------
# Conversation History
# -----------------------------

for tid in st.session_state["chat_threads"][::-1]:

    display_name = st.session_state["thread_names"].get(
        tid,
        "New Conversation"
    )

    display_name = display_name[:40]

    if st.sidebar.button(
        display_name,
        key=f"thread_{tid}"
    ):

        st.session_state["thread_id"] = tid

        msgs = load_conversations(tid)

        temp_msg = []

        for msg in msgs:

            if isinstance(msg, HumanMessage):
                role = "user"

            else:
                role = "assistant"

            temp_msg.append({
                "role": role,
                "content": msg.content
            })

        st.session_state["history"] = temp_msg

        st.rerun()


# -----------------------------
# Main Chat
# -----------------------------

show_chat_title()


for msg in st.session_state["history"]:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# -----------------------------
# Input
# -----------------------------

user_input = st.chat_input(
    "Enter your message here..."
)


if user_input:

    current_thread = st.session_state["thread_id"]


    # -----------------------------
    # Conversation Name
    # -----------------------------

    if current_thread not in st.session_state["thread_names"]:

        st.session_state["thread_names"][current_thread] = user_input


    # -----------------------------
    # Show User Message
    # -----------------------------

    with st.chat_message("user"):
        st.markdown(user_input)


    st.session_state["history"].append({
        "role": "user",
        "content": user_input
    })


    # -----------------------------
    # Assistant Response
    # -----------------------------

    with st.chat_message("assistant"):

        status_holder = {
            "box": None
        }


        def response_generator():

            for message_chunk, metadata in workflow.stream(

                {
                    "messages": [
                        HumanMessage(
                            content=user_input
                        )
                    ]
                },

                config={
                    "configurable": {
                        "thread_id": current_thread
                    }
                },

                stream_mode="messages",
            ):

                # =================================
                # TOOL MESSAGE
                # =================================

                if isinstance(
                    message_chunk,
                    ToolMessage
                ):

                    tool_name = getattr(
                        message_chunk,
                        "name",
                        "tool"
                    )


                    if status_holder["box"] is None:

                        status_holder["box"] = st.status(
                            f"🔧 Using `{tool_name}` …",
                            expanded=True
                        )

                    else:

                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}` …",
                            state="running",
                            expanded=True
                        )


                # =================================
                # AI MESSAGE
                # =================================

                if isinstance(
                    message_chunk,
                    AIMessage
                ):

                    if message_chunk.content:

                        yield message_chunk.content


        # -----------------------------
        # Stream Response
        # -----------------------------

        response = st.write_stream(
            response_generator()
        )


        # -----------------------------
        # Finalize Tool Status
        # -----------------------------

        if status_holder["box"] is not None:

            status_holder["box"].update(
                label="✅ Tool finished",
                state="complete",
                expanded=False
            )


    # -----------------------------
    # Save Assistant Response
    # -----------------------------

    st.session_state["history"].append({
        "role": "assistant",
        "content": response
    })

