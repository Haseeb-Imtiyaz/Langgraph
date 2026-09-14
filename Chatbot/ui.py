import streamlit as st


def setup_page():

    st.set_page_config(
        page_title="My ChatBot",
        page_icon="🤖",
        layout="wide"
    )


def apply_styles():

    st.markdown("""
    <style>

    .stApp {
        background-color: #0f1117;
    }

    section[data-testid="stSidebar"] {
        background-color: #171a21;
    }

    .chat-title {
        text-align: center;
        font-size: 28px;
        font-weight: 700;
        color: white;
        margin-bottom: 30px;
    }

    </style>
    """, unsafe_allow_html=True)


def show_sidebar_title():

    st.sidebar.markdown(
        "## 🤖 My ChatBot"
    )


def show_chat_title():

    st.markdown(
        '<div class="chat-title">🤖 My ChatBot</div>',
        unsafe_allow_html=True
    )