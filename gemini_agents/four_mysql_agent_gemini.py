"""
MySQL Agent using Gemini
Connects to a MySQL database and answers natural-language questions interactively.
Type 'exit' or 'quit' to stop the session.
"""

# ── Imports ────────────────────────────────────────────────────────────────────
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent
from langchain.agents.agent import AgentExecutor
from langchain.tools import tool
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv

# FIX: import safety types to relax Gemini's content filters.
# FinishReason=19 ("RECITATION") fires when the model thinks it is reproducing
# copyrighted text – SQL results often trigger this.  Setting all thresholds to
# BLOCK_NONE prevents the proto enum crash: 'int' object has no attribute 'name'.
from google.generativeai.types import HarmCategory, HarmBlockThreshold


# ── Environment setup ──────────────────────────────────────────────────────────
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "false"
api_key = os.getenv("GEMINI_API_KEY")
model   = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")   # FIX: safe default in case .env is missing


# ── Database connection config ─────────────────────────────────────────────────
MYSQL_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "",
    "database": "ecommerce",
}


# ── Tool 1: execute a SQL SELECT query ────────────────────────────────────────
@tool
def execute_sql_query(query: str) -> str:
    """Execute a SQL SELECT query against the MySQL database and return the results."""
    try:
        import mysql.connector

        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor     = connection.cursor()

        cursor.execute(query)
        results      = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

        cursor.close()
        connection.close()

        if not results:
            return "No results found."

        formatted = f"Columns: {', '.join(column_names)}\n"
        for row in results[:10]:
            formatted += str(row) + "\n"

        return formatted

    except Exception as e:
        return (
            f"Error executing query: {str(e)}\n"
            "Make sure MySQL is running and MYSQL_CONFIG credentials are correct."
        )


# ── Tool 2: inspect the database schema ───────────────────────────────────────
# FIX: added `input: str = ""` — LangChain 0.2.x @tool requires a string
#      argument even for zero-parameter tools used inside a ReAct agent.
@tool
def get_database_schema(input: str = "") -> str:
    """Get the schema of the MySQL database: all table names and their columns.
    No input is required; pass an empty string."""
    try:
        import mysql.connector

        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor     = connection.cursor()

        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]

        schema_info = "Database Tables and Columns:\n"
        for table in tables:
            cursor.execute(f"DESCRIBE {table}")
            columns     = cursor.fetchall()
            schema_info += f"\nTable: {table}\n"
            for col in columns:
                schema_info += f"  - {col[0]} ({col[1]})\n"

        cursor.close()
        connection.close()

        return schema_info

    except Exception as e:
        return f"Error getting schema: {str(e)}"


# ── LLM ───────────────────────────────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(
    model=model,
    temperature=0,
    google_api_key=api_key,
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT:        HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH:       HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    },
)


# ── ReAct prompt (inline) ──────────────────────────────────────────────────────
REACT_TEMPLATE = """You are a helpful data analyst assistant. Answer questions about the MySQL database using the tools provided.

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

prompt = PromptTemplate.from_template(REACT_TEMPLATE)


# ── Agent setup ────────────────────────────────────────────────────────────────
tools    = [execute_sql_query, get_database_schema]
agent    = create_react_agent(llm=llm, tools=tools, prompt=prompt)

executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=False,
    handle_parsing_errors=True,
    max_iterations=10,          # FIX: prevent infinite loops on ambiguous queries
    max_execution_time=60,      # FIX: hard timeout (seconds) as a safety net
)


# ── Startup banner ─────────────────────────────────────────────────────────────
print("=" * 60)
print("  🗄️  MySQL Agent with Gemini — Ask Anything!")
print("  Ask questions about your database in plain English.")
print("  Type 'exit' or 'quit' to stop.")
print("=" * 60)
print("\n⚠️  Make sure MYSQL_CONFIG is updated with your credentials.\n")


# ── Interactive chat loop ──────────────────────────────────────────────────────
while True:
    try:
        user_input = input("\n🧑 You: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\n👋 Session ended. Goodbye!")
        break

    if not user_input:
        print("   ⚠️  Please enter a question.")
        continue

    if user_input.lower() in ("exit", "quit"):
        print("\n👋 Exiting. Goodbye!")
        break

    try:
        result = executor.invoke({"input": user_input})
        print(f"\n🤖 Agent: {result['output']}")
    except Exception as e:
        print(f"\n❌ Error: {e}")