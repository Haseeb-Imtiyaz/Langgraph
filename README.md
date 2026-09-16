# LangGraph Learning Projects

A collection of hands-on projects built while learning [LangGraph](https://langchain-ai.github.io/langgraph/) — from basic state graphs to LLM-powered workflows and a full chatbot with tools and memory.

## Prerequisites

- Python 3.10+
- A [Groq API key](https://console.groq.com/) (used by most notebooks and the chatbot)

## Setup

```bash
# Clone the repository
git clone https://github.com/<your-username>/Langraph.git
cd Langraph

# Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
copy .env.example .env         # Windows
# cp .env.example .env         # macOS / Linux
# Then edit .env and add your GROQ_API_KEY
```

## Project Overview

| # | File | Concept | Description |
|---|------|---------|-------------|
| 01 | `01_BMI_Calculator.ipynb` | Linear workflow | Two-node graph: calculate BMI → classify weight category |
| 02 | `02_simpleQ_A.ipynb` | LLM + graph | Single chatbot node that answers questions using Groq |
| 03 | `03_prompt_chaining.ipynb` | Sequential chaining | Outline generator → blog writer (two LLM nodes in series) |
| 04 | `04_Parallel_Workflow.ipynb` | Parallel execution | Cricket stats: strike rate, balls per boundary, and boundary % computed in parallel, then summarized |
| 05 | `05_Essay_Evaluation.ipynb` | Parallel + aggregation | Three LLM evaluators (language, thought, depth) run in parallel; a final node summarizes feedback and average score |
| 06 | `06_Conditional_Workflow.ipynb` | Conditional routing | Quadratic equation solver that routes to different nodes based on the discriminant |
| 07 | `07_Review_Response.ipynb` | Conditional + LLM | Sentiment analysis → positive reply or negative analysis → tailored negative reply |
| 08 | `08_Tweet_Generator.ipynb` | Loops + conditional edges | Generate → evaluate → optimize tweet loop until approved or max iterations reached |
| 09 | `09_RAG.ipynb` | How to use RAG in Langgraph as a tool |
| — | `Chatbot/` | Full application | Streamlit chatbot with tool calling, SQLite memory, and conversation history |

---

## Notebooks (Detailed)

### 01 — BMI Calculator

**Concepts:** `StateGraph`, `TypedDict`, linear edges, graph visualization

A non-LLM workflow that takes height and weight, calculates BMI, and assigns a category (Underweight, Normal, Overweight, Obese).

```
START → calculate_bmi → bmi_category → END
```

---

### 02 — Simple Q&A

**Concepts:** Integrating an LLM (`ChatGroq`) inside a LangGraph node

A minimal question-answering graph with one node that sends the user's question to Groq and stores the answer in state.

```
START → chatbot → END
```

---

### 03 — Prompt Chaining

**Concepts:** Multi-step LLM pipelines, passing state between nodes

Two nodes chained sequentially: first generates a blog outline for a topic, then writes the full blog post using that outline.

```
START → outline_generator → blog_writter → END
```

---

### 04 — Parallel Workflow

**Concepts:** Fan-out / fan-in pattern, partial state updates

Given cricket match stats (runs, balls, fours, sixes), three calculation nodes run **in parallel** from `START`. A summary node waits for all three before producing the final report.

```
                    ┌→ calculate_SR ────────┐
START ──────────────┼→ calculate_BPB ───────┼→ summary → END
                    └→ calculate_BPercent ──┘
```

---

### 05 — Essay Evaluation

**Concepts:** Parallel LLM evaluators, `Annotated` reducers (`operator.add`), structured output with Pydantic

Three evaluators assess an essay on language, thought, and depth simultaneously. Scores are aggregated with a list reducer. A final node produces a summary and average score.

```
                    ┌→ language_evaluation ──┐
START ──────────────┼→ thought_evaluation ─────┼→ final_evalution → END
                    └→ depth_evaluation ─────┘
```

---

### 06 — Conditional Workflow

**Concepts:** `add_conditional_edges`, routing functions, `Literal` return types

Solves quadratic equations `ax² + bx + c = 0`. After computing the discriminant, the graph routes to one of three nodes:

- `D > 0` → two distinct real roots
- `D = 0` → repeated real root
- `D < 0` → no real roots

```
START → create_eqn → calculate_D ──→ real_roots ──────────→ END
                               ├──→ repeated_real_roots ──→ END
                               └──→ no_real_roots ────────→ END
```

---

### 07 — Review Response

**Concepts:** Conditional routing with LLM, structured output for classification

Analyzes customer reviews and generates appropriate replies:

- **Positive** → polite thank-you reply
- **Negative** → deep analysis (issue type, tone, urgency) → empathetic tailored reply

```
START → sentiment_analysis ──→ postive_reply ──→ END
                          └──→ negative_analysis → negative_reply → END
```

---

### 08 — Tweet Generator

**Concepts:** Cyclic graphs, conditional loops, iteration limits, message history reducers

An agentic loop that generates a tweet, evaluates it, and optimizes until approved or the max iteration count is reached.

```
START → generate_tweet → evaluate_tweet ──→ END (approved)
                              ↑                  │
                              └── optimize_tweet ←┘ (need optimization)
```

---

## Chatbot Application

A full-featured Streamlit chatbot in the `Chatbot/` folder.

### Features

- **Tool calling** — DuckDuckGo (web), Wikipedia, ArXiv (AI/CS papers), PubMed (medical research)
- **Persistent memory** — SQLite checkpointer (`SqliteSaver`) for multi-turn conversations
- **Conversation history** — sidebar with thread switching and new chat
- **Streaming UI** — live token streaming with tool-use status indicators

### Architecture

```
START → chatbot ──→ tools ──→ chatbot (loop)
              └──→ END
```

### Run the Chatbot

```bash
cd Chatbot
streamlit run frontend.py
```

### File Structure

```
Chatbot/
├── frontend.py          # Main Streamlit app (chat UI, streaming)
├── langgraph_backend.py # LangGraph workflow, tools, SQLite memory
├── ui.py                # Page config and styling
└── utils.py             # Thread management and conversation loading
```

---

## Tech Stack

| Library | Purpose |
|---------|---------|
| [LangGraph](https://langchain-ai.github.io/langgraph/) | State graphs, conditional edges, checkpoints |
| [LangChain Groq](https://python.langchain.com/docs/integrations/chat/groq/) | LLM (`openai/gpt-oss-20b`) |
| [Streamlit](https://streamlit.io/) | Chatbot frontend |
| [Pydantic](https://docs.pydantic.dev/) | Structured LLM output schemas |
| SQLite | Conversation persistence |

---

## Learning Path

These projects follow a progressive learning order:

1. **Graph basics** — state, nodes, edges (01)
2. **LLM integration** — calling models inside nodes (02)
3. **Chaining** — sequential multi-step pipelines (03)
4. **Parallelism** — fan-out / fan-in (04)
5. **Parallel LLM + reducers** — aggregating results (05)
6. **Conditional routing** — branching logic (06)
7. **Conditional + LLM** — sentiment-based workflows (07)
8. **Loops** — iterative refinement (08)
9. **RAG** - RAG in Langgarpg (09)
10. **Production app** — tools, memory, UI (Chatbot)

---

## License

This project is for personal learning purposes.
