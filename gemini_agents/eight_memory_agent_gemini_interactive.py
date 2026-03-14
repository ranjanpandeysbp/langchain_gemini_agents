"""
Memory-Based Conversational Agent using Gemini
This agent maintains conversation history and context across multiple turns.
It uses LangChain's memory system to remember previous interactions.
Runs in an interactive Q&A loop until the user types 'exit'.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import tool
from langchain import hub
from langchain.memory import ConversationBufferMemory
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "false"
api_key = os.getenv('GEMINI_API_KEY')
model = os.getenv('GEMINI_MODEL')

# ============================================================================
# PERSISTENT KEY-VALUE STORE (shared across all tool calls in a session)
# ============================================================================

user_info_store: dict = {}  # Real in-memory store — persists for the whole session

# ============================================================================
# CUSTOM TOOLS FOR CONVERSATIONAL AGENT
# ============================================================================

@tool
def store_information(key_value: str) -> str:
    """Store a fact about the user. Input format: 'key:value', e.g. 'name:Alice' or 'profession:Engineer'."""
    try:
        if ":" not in key_value:
            return "Error: Input must be 'key:value' format, e.g. 'name:Alice'"
        key, value = key_value.split(":", 1)  # Split on first colon only
        key = key.strip().lower()
        value = value.strip()
        user_info_store[key] = value  # Write to real store
        return f"Stored: {key} = {value}"
    except Exception as e:
        return f"Error storing information: {str(e)}"

@tool
def retrieve_information(key: str) -> str:
    """Retrieve a stored fact about the user by key, e.g. 'name', 'profession', 'experience'."""
    try:
        key = key.strip().lower()
        if key in user_info_store:
            return f"{key} = {user_info_store[key]}"  # Return real stored value
        # Key not found — return everything so agent can search
        if user_info_store:
            all_info = "\n".join(f"  {k}: {v}" for k, v in user_info_store.items())
            return f"Key '{key}' not found. All stored facts:\n{all_info}"
        return "No information has been stored yet."
    except Exception as e:
        return f"Error retrieving information: {str(e)}"

@tool
def list_all_information(placeholder: str = "") -> str:
    """List every fact stored about the user. No input required — pass any string or leave blank."""
    try:
        if not user_info_store:
            return "No information has been stored yet."
        return "All stored facts:\n" + "\n".join(f"  {k}: {v}" for k, v in user_info_store.items())
    except Exception as e:
        return f"Error listing information: {str(e)}"

# ============================================================================
# AGENT INITIALIZATION WITH MEMORY
# ============================================================================

llm = ChatGoogleGenerativeAI(
    model=model,
    temperature=0.7,
    google_api_key=api_key
)

# ConversationBufferMemory keeps the full chat history in the prompt context
memory = ConversationBufferMemory(
    memory_key="chat_history",  # Must match the variable in the ReAct prompt
    return_messages=True         # Pass as message list (not plain string)
)

tools = [store_information, retrieve_information, list_all_information]

prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True
)

# ============================================================================
# INTERACTIVE Q&A LOOP
# ============================================================================

def interactive_session() -> None:
    """
    Run an interactive Q&A session with the memory-based conversational agent.
    The agent remembers everything said across the session until the user types 'exit'.
    """
    print("\n" + "=" * 70)
    print("  MEMORY-BASED CONVERSATIONAL AGENT — INTERACTIVE MODE")
    print("=" * 70)
    print("\nThe agent remembers your name, preferences, and anything you share.")
    print("Context is preserved across every turn of the conversation.")
    print("\nType your message and press Enter. Type 'exit' to quit.")
    print("Type 'memory' to inspect the conversation history.")
    print("Type 'store'  to inspect the key-value fact store directly.")
    print("Type 'reset'  to clear everything and start a fresh session.")
    print("=" * 70)

    turn_count = 0

    while True:
        print()
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nSession interrupted. Goodbye!")
            break

        if not user_input:
            print("(Please type a message, or type 'exit' to quit.)")
            continue

        if user_input.lower() == "exit":
            print("\n" + "=" * 70)
            print(f"Session ended after {turn_count} turn(s).")
            if user_info_store:
                print("\nFacts stored this session:")
                for k, v in user_info_store.items():
                    print(f"  {k}: {v}")
            print("\nThank you for chatting. Goodbye!")
            print("=" * 70 + "\n")
            break

        if user_input.lower() == "memory":
            print("\n" + "-" * 70)
            print("CONVERSATION HISTORY:")
            print("-" * 70)
            buf = memory.buffer
            if buf:
                for msg in buf:
                    role = "You  " if msg.type == "human" else "Agent"
                    print(f"  [{role}] {msg.content}")
            else:
                print("  (empty — start chatting!)")
            print("-" * 70)
            continue

        if user_input.lower() == "store":
            print("\n" + "-" * 70)
            print("KEY-VALUE FACT STORE:")
            print("-" * 70)
            if user_info_store:
                for k, v in user_info_store.items():
                    print(f"  {k}: {v}")
            else:
                print("  (empty)")
            print("-" * 70)
            continue

        if user_input.lower() == "reset":
            memory.clear()
            user_info_store.clear()
            turn_count = 0
            print("\n Memory and fact store cleared. Starting a fresh session.\n")
            continue

        if user_input.lower() in ("help", "?"):
            print("\nCommands:")
            print("  memory — show full conversation history")
            print("  store  — show all stored facts (name, profession, etc.)")
            print("  reset  — clear everything and start fresh")
            print("  exit   — end the session")
            print("\nTry saying things like:")
            print("  'My name is Alice and I love hiking.'")
            print("  'What is my name?'")
            print("  'What do you know about me?'")
            continue

        turn_count += 1
        print(f"\n[Turn #{turn_count}]")
        print("-" * 70)

        try:
            result = agent_executor.invoke({"input": user_input})
            print(f"\nAgent: {result['output']}\n")
        except Exception as e:
            print(f"Error during agent execution: {str(e)}")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    interactive_session()