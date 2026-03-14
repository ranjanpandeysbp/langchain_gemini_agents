# Import required libraries for Gemini AI agent
from langchain_google_genai import ChatGoogleGenerativeAI  # Gemini LLM integration
from langchain.agents import create_react_agent            # ReAct agent framework
from langchain.agents.agent import AgentExecutor           # Executes agent decisions
from langchain.tools import tool                           # Decorator for defining custom tools
from langchain import hub                                  # Loads pre-built prompt templates

import os                                                  # For environment variable access
from dotenv import load_dotenv                             # Loads .env file variables

# Load environment variables from .env file
load_dotenv()

# ── LangSmith tracing configuration ──────────────────────────────────────────
# Set these in your .env file:
#   LANGCHAIN_TRACING_V2=true
#   LANGCHAIN_API_KEY=<your-langsmith-api-key>
#   LANGCHAIN_PROJECT=<optional-project-name>      (defaults to "default")
#   LANGCHAIN_ENDPOINT=https://api.smith.langchain.com  (default, usually not needed)
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "true")
os.environ["LANGCHAIN_API_KEY"]    = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"]    = os.getenv("LANGCHAIN_PROJECT", "gemini-react-agent")
# ─────────────────────────────────────────────────────────────────────────────

api_key = os.getenv("GEMINI_API_KEY")   # Get Gemini API key
model   = os.getenv("GEMINI_MODEL")     # Get model name (e.g., 'gemini-pro')


# ── Tools ─────────────────────────────────────────────────────────────────────
@tool
def multiply_numbers(input: str) -> int:
    """Multiply two numbers. Input must be two numbers separated by a comma, e.g. '6,7'"""
    a, b = input.strip().split(",")
    return int(a.strip()) * int(b.strip())


# ── LLM ──────────────────────────────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(
    model=model,
    temperature=0,
    google_api_key=api_key,
)

tools  = [multiply_numbers]
prompt = hub.pull("hwchase17/react")

# ── Agent & Executor ──────────────────────────────────────────────────────────
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
)


# ── Interactive Q&A loop ──────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  Gemini ReAct Agent  |  LangSmith tracing enabled")
    print("  Type 'exit' or 'quit' to stop.")
    print("=" * 55)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit", "q"}:
            print("Goodbye!")
            break

        result = executor.invoke({"input": user_input})
        print(f"\nAgent: {result['output']}")


if __name__ == "__main__":
    main()