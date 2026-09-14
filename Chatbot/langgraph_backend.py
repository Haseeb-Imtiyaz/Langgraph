from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun, ArxivQueryRun,PubmedQueryRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper, PubMedAPIWrapper
from langchain_core.tools import tool

load_dotenv(override= True)

conn = sqlite3.connect(database="ChatbotDb",check_same_thread = False)


web_search = DuckDuckGoSearchRun(
    name="web_search",
    description="""
Search the current web for websites, current events, news,
and information that is not specifically academic research.
"""
)

wiki_search = WikipediaQueryRun( 
    name="wikipedia_search", 
    description=""" Search Wikipedia for general factual information, concepts, people, places, history, science, technology, and background knowledge. Use this tool when the user wants a general explanation or factual background. Do not use it for the latest news or current events, and do not use it for academic research papers. """, 
    api_wrapper=WikipediaAPIWrapper( top_k_results=2, doc_content_chars_max=3000 ))

# ArXiv
arxiv = ArxivQueryRun(
    api_wrapper=ArxivAPIWrapper(
        top_k_results=3,
        doc_content_chars_max=4000
    ),
    name="arxiv_search",
    description="""
Search ArXiv for academic research papers, especially papers
about artificial intelligence, Agentic AI, LLMs, machine learning,
deep learning, and computer science.
"""
)

# PubMed
pubmed = PubmedQueryRun( 
    name="pubmed_search", 
    description=""" Search PubMed for medical, biomedical, healthcare, clinical, pharmaceutical, biology, and life-science research papers. Use this tool when the user's question involves medical or biomedical research, diseases, treatments, drugs, clinical studies, human health, or related scientific literature. Do not use this tool for general AI or computer-science research unless the question specifically involves healthcare or medicine. """, 
    api_wrapper=PubMedAPIWrapper( top_k_results=3 ) )

tools = [web_search,pubmed,arxiv,wiki_search]
tool_node = ToolNode(tools)


class Chat_State(TypedDict):
    messages: Annotated[list[BaseMessage],add_messages]


model = ChatGroq(model= "openai/gpt-oss-20b")
model_with_tools = model.bind_tools(tools)

def chatbot(state: Chat_State):

    system_message = SystemMessage(
        content="""
        You are a helpful AI assistant that answers user queries
        in simple English.

        Tool selection rules:

        - Use arxiv_search for academic research papers about AI,
          Agentic AI, LLMs, machine learning, deep learning,
          robotics, and computer science.

        - Use pubmed_search for medical, biomedical, healthcare,
          pharmaceutical, clinical, disease, treatment, and
          life-science research.

        - Use wikipedia_search for general factual information,
          concepts, history, people, places, science, and
          background knowledge.

        - Use web_search for current web information, news,
          websites, and current events.

        Prefer the single most relevant tool.

        Do not call multiple tools unless the question genuinely
        requires multiple sources.

        After using a tool, summarize the useful information
        instead of dumping the raw tool output.
        """
    )

    messages = [system_message] + state["messages"]

    response = model_with_tools.invoke(messages)

    return {
        "messages": [response]
    }

graph = StateGraph(Chat_State)

graph.add_node("chatbot", chatbot)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chatbot")

graph.add_conditional_edges(
    "chatbot",
    tools_condition,
    {
        "tools": "tools",
        "__end__": END
    }
)

graph.add_edge("tools", "chatbot")

memory = SqliteSaver(conn=conn)
workflow = graph.compile(checkpointer = memory)