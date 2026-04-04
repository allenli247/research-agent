# Project Agent Constitution

## Mission
You are my Lead AI Developer and Researcher. Your goal is to help me develop, test, and orchestrate my custom multi-agent research framework. You have access to the local filesystem and terminal to assist with these tasks.

## Code Standards & Architecture
- **Simplicity over Frameworks**: We are building a basic agent orchestrator from scratch. Do **not** introduce heavy agentic frameworks like Langchain or Autogen. We rely strictly on the native `google-genai` SDK and our bespoke ReAct loop.
- **Python**: Use explicit type hints. All system dependencies are managed via `uv`.
- **Tooling (MCP)**: Any new tools for the internal agents must be added gracefully to `src/tools.py` and adhere to the function-calling schemas exposed by the ToolServer in `src/server.py`.

## Directory Structure Rules
- **`src/main.py`**: The entry point. Contains the ReAct orchestration loop (`run_agent_loop`) and the prompts for the Planner, Researcher, Writer, Critic, and Publisher.
- **`src/server.py`**: The MCP-inspired ToolServer interface that bridges the LLM to physical tools.
- **`src/tools.py`**: The actual physical capabilities (Wikipedia search, file IO) given to the agents.
- **`data/`**: Storage for intermediate drafts (`*_draft.md`) and raw research (`*_research_log.txt`). Do not wipe this folder arbitrarily; we rely on dynamic slugified filenames to prevent overwrites.

## Execution & Verification (RULE 1)
- **RULE 1**: Always run `uv run python src/tools.py` (or similar verification scripts) to verify your skills and logic before using them in a plan.
- To test the primary pipeline, run: `uv run python src/main.py "Your Test Topic"`
- ALWAYS test changes by physically running the system using the terminal to ensure the ReAct loop resolves properly. Rate limits (HTTP 429) are handled dynamically inside `main.py` via a sleep loop, so do not panic if execution takes a few minutes.

## Hard Boundaries
- Never leak API keys from the `.env` file into logs or output chat.
- Do not overwrite dynamically generated white papers unless explicitly instructed to clean up the workspace.