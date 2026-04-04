import os
import sys
import time
import json

# Ensure the parent directory is in sys.path so 'from src.server' works
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai import errors
from src.server import ToolServer

# Load the .env file containing GEMINI_API_KEY
load_dotenv()

def safe_send_message(chat, message, attempt=1):
    """Helper method to catch rate limits (429) and retry automatically."""
    while True:
        try:
            return chat.send_message(message)
        except errors.ClientError as e:
            err_str = str(e)
            if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
                print(f"\n⚠️ Rate limit hit! (Attempt {attempt}). Sleeping for 65s to fully reset the 1-minute quota window...")
                # Extract the recommended wait time if any
                print(f"Details: {err_str[:200]}...")
                time.sleep(65)
                print("🔄 Retrying request...")
                attempt += 1
            else:
                raise e
        except Exception as e:
            raise e

def run_agent_loop(agent_name: str, system_instruction: str, user_prompt: str, server: ToolServer) -> str:
    """
    The Orchestration Loop (ReAct).
    This function gives the agent a persona and tools. It loops:
    Ask LLM -> LLM returns Function Call -> Execute Function -> Send Result Back -> Ask LLM again.
    It stops when the LLM returns plain text instead of a function call.
    """
    print(f"\n{'='*50}\n🚀 STARTING AGENT: {agent_name}\n{'='*50}")
    
    client = genai.Client()
    
    chat = client.chats.create(
        model="gemini-3.1-pro-preview",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=server.get_all_tools(),
            temperature=0.2
        )
    )
    
    print(f"[{agent_name}] Analyzing task...")
    response = safe_send_message(chat, user_prompt)
    
    loop_count = 0
    max_loops = 10  # Prevent infinite loops
    
    # The Action -> Observation Loop
    while loop_count < max_loops:
        loop_count += 1
        
        if response.function_calls:
            # Gather all parallel tool call responses
            responses_to_send = []
            
            for call in response.function_calls:
                print(f"[{agent_name}] 🛠️ Calls Tool: {call.name} with args {call.args}")
                args = {k: v for k, v in call.args.items()}
                
                # Execute the tool using our MCP-style server
                result = server.execute(call.name, args)
                print(f"[{agent_name}] 📄 Tool observation received (length: {len(result)})")
                
                # Add the result to our response parts
                responses_to_send.append(
                    types.Part.from_function_response(
                        name=call.name,
                        response={"result": result}
                    )
                )
                
            # Now send ALL the function responses back to the LLM in one message
            print(f"[{agent_name}] 🧠 Reasoning about observation(s)...")
            response = safe_send_message(chat, responses_to_send)
        else:
            # The agent decided to output text and stop
            print(f"[{agent_name}] ✅ Finished task.")
            return response.text
            
    print(f"[{agent_name}] ❌ Reached max loops ({max_loops}). Force stopping to save quota.")
    return getattr(response, 'text', "Max loops reached without final output.")

def main():
    if not os.getenv("GOOGLE_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        print("Error: GOOGLE_API_KEY or GEMINI_API_KEY not found in .env file.")
        sys.exit(1)

    # The topic to research
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Large Language Models"
    print(f"Target Topic: {topic}")

    server = ToolServer()
    
    # Create topic-specific filenames to prevent overwriting
    safe_topic = topic.replace(" ", "_").lower()
    
    research_log_path = f"data/raw_research/{safe_topic}_research_log.txt"
    draft_path = f"data/{safe_topic}_draft.md"
    final_path = f"research_summaries/{safe_topic}_white_paper.md"

    # ========================================================
    # PHASE 0: PLANNER AGENT
    # ========================================================
    planner_prompt = (
        "You are an expert Planning Agent. Your job is to determine the best structure for researching and writing about a specific topic. "
        "The user will provide a topic. You must output exactly 3 to 5 key section titles, separated by commas, that would make for the most comprehensive and engaging white paper on this topic. "
        "For example, if the topic is 'Baking Cookies', you might output: 'Ingredients and Chemistry, The Maillard Reaction, Temperature and Time, Variations and Techniques'. "
        "Do not use any tools or write extra text. Just output the comma-separated list of section titles."
    )
    dynamic_sections = run_agent_loop("Planner", planner_prompt, f"Topic: {topic}", server)
    print(f"\n[Planner] Generated Sections: {dynamic_sections}\n")

    # ========================================================
    # PHASE 1: INGEST / RESEARCHER AGENT
    # ========================================================
    researcher_prompt = (
        "You are an expert Researcher Agent. Your task is to perform comprehensive research on the given topic. "
        f"Use the `search_wikipedia` tool to find information covering these specific sections: {dynamic_sections}. "
        "Once you have enough information, use `write_markdown` to save all your findings into a file called "
        f"'{research_log_path}'. Do NOT write the final white paper. Just dump the raw facts, history, and notes. "
        "Return the string 'RESEARCH_COMPLETE' when done."
    )
    run_agent_loop("Researcher", researcher_prompt, f"Research the topic: {topic}", server)

    # ========================================================
    # PHASE 2: AUGMENT / DRAFTING AGENT
    # ========================================================
    writer_prompt = (
        "You are an expert Technical Writer Agent. Your task is to draft a comprehensive white paper with LaTeX math enabled. "
        f"First, use `read_local_text` to read the notes from '{research_log_path}'. "
        f"Then, write a structured and engaging markdown document clearly dividing the paper into these sections: {dynamic_sections}. "
        f"Use `write_markdown` to save the draft to '{draft_path}'. "
        "Return the string 'DRAFT_COMPLETE' when done."
    )
    run_agent_loop("Writer", writer_prompt, f"Draft the white paper for: {topic}", server)

    # ========================================================
    # PHASE 3: DRAFT & CRITIQUE / CRITIC AGENT
    # ========================================================
    critic_prompt = (
        "You are a strict Critic Agent. Your job is to review drafts. "
        f"Use `read_local_text` to read '{draft_path}'. "
        "Evaluate it based on: Is it comprehensive? Does it use LaTeX properly? Is the history and purpose clear? "
        "Do NOT rewrite the draft yourself. Just identify 3-4 specific areas for improvement, like missing details or formatting issues. "
        "Provide those points as your final text output."
    )
    critique = run_agent_loop("Critic", critic_prompt, "Review the draft and provide critique.", server)
    
    # Writer Revises
    reviser_prompt = (
        "You are the Technical Writer Agent. You previously wrote a draft. "
        "I will give you the Critic's feedback. "
        f"Use `read_local_text` to read the current draft from '{draft_path}'. "
        "Apply the feedback, improve the document, and use `write_markdown` to save the final version to "
        f"'{final_path}'. Return the string 'REVISION_COMPLETE' when done."
    )
    run_agent_loop("Writer (Reviser)", reviser_prompt, f"Here is the feedback. Please revise and deploy to {final_path}:\n{critique}", server)

    # ========================================================
    # PHASE 4: DEPLOY / PUBLISHER AGENT
    # ========================================================
    publisher_prompt = (
        "You are the Publisher Agent. Your job is to summarize documents and notify stakeholders. "
        f"Use `read_local_text` to read the final white paper from '{final_path}'. "
        "Generate a 3-sentence summary of the document. "
        "Then, use the `send_email_mock` tool to send an email with the subject 'New White Paper Published' and the summary as the body. "
        "Return the string 'DEPLOYED' when done."
    )
    run_agent_loop("Publisher", publisher_prompt, "Summarize and email the final paper.", server)

    print("\n🎉 Multi-Agent Workflow Completed Successfully!")

if __name__ == "__main__":
    main()
