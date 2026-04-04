# Multi-Agent Research System

An autonomous, multi-agent research pipeline built from scratch to dynamically plan, research, draft, edit, and publish comprehensive white papers on any given topic.

## 🚀 Getting Started

If you've just cloned this repository, follow these steps to get your agents running:

### 1. Prerequisites
Ensure you have Python installed, along with **[uv](https://github.com/astral-sh/uv)** (an ultra-fast Python package installer and resolver).

To install uv 
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

### 2. Setup
Clone the repository and set up your environment variables.
```bash
git clone https://github.com/your-username/research_agent.git
cd research_agent

# Create your .env file
touch .env
```

Open the `.env` file and insert your API key:
```env
GEMINI_API_KEY=your_genai_api_key_here
```

### 3. Run the Agent
Run the main script and provide whatever topic you want it to research!
```bash
# Example 1: Scientific Topic
uv run python src/main.py "The Science of Baking Cookies"

# Example 2: Historical Topic
uv run python src/main.py "The Roman Empire"

# Other examples
uv run python src/main.py "The History of Jazz"
uv run python src/main.py "CRISPR Gene Editing"
```

---

## 📖 How It Works

### Purpose
The purpose of this repository is to demonstrate how to build an orchestration flow from scratch without relying on heavy agentic frameworks (like Langchain or Autogen). It relies strictly on the native **Google GenAI SDK**, an autonomous ReAct loop, and a rudimentary Model Context Protocol (MCP) server design. 

### The Orchestration Workflow
When you run the script, a purely dynamic pipeline kicks off to produce a verified, high-quality markdown white paper.

1. **Phase 0: Planner Agent** 
   - Dynamically analyzes the user's requested topic and writes a custom structured rubric (e.g. creating sections like *Ingredient Chemistry* and *Maillard Reaction* for Baking Cookies).
2. **Phase 1: Researcher Agent**
   - Ingests the Planner's rubric. Autonomously queries Wikipedia to gather raw facts strictly scoped to that rubric, avoiding irrelevant data. Dumps findings into `data/raw_research`.
3. **Phase 2: Technical Writer Agent**
   - Reads the raw research and drafts an eloquent markdown string with LaTeX math support. Saves to an intermediate draft.
4. **Phase 3: Critic Agent**
   - Validates the draft against best practices. Returns 3-4 specific areas of improvement (missing citations, poor sentence structure).
5. **Phase 4: Reviser (Writer)**
   - Re-reads the draft, incorporates the Critic's critiques, and finalizes the document.
6. **Phase 5: Publisher Agent**
   - Summarizes the finalized document into an abstract and executes a mock email notification tool to stakeholders.

At every stage, output file names are dynamically slugified based on the topic (e.g. `the_roman_empire_white_paper.md`) so that past runs are never overwritten.

### The LLM
The system is powered exclusively by the **Gemini 3.1 Pro** model via the `google-genai` SDK. The architecture leverages Gemini's function-calling capabilities within an intensive **ReAct (Reasoning and Acting)** loop (defined in `src/main.py`). The `run_agent_loop` continuously prompts Gemini to emit tool calls, intercepts those calls, executes them locally, and feeds the observations back to the LLM until the LLM resolves the task.

### MCP Inspired Servers (`src/server.py`)
To isolate tool logic from the LLM logic, we use a Model Context Protocol (MCP)-style server approach. The `ToolServer` object exposes a list of strict JSON schemas (schemas for what tools exist) via `server.get_all_tools()`. When the LLM chooses a tool, the engine simply passes the request via string interface to `server.execute()`. This architecture makes the agent infinitely extensible without muddying the LLM orchestration logic.

### Skills & Tools (`src/tools.py` & `AGENT.md`)
The system relies on concrete execution skills:
- **`search_wikipedia`**: Capable of querying pages across Wikipedia to ingest real-time factual text.
- **`read_local_text` / `write_markdown`**: Grants the agents read/write access to the local filesystem so they can physically maintain state between loops and pass files to downstream agents.
- **`send_email_mock`**: Simulates deployment integrations.

Overall rules and skill schemas are documented in `AGENT.md` (which serves as overarching context/principles for developer adjustments).