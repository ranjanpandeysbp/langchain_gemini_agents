# Import required libraries for Gemini AI agent
from langchain_google_genai import ChatGoogleGenerativeAI  # Gemini LLM integration
from langchain.agents import create_react_agent  # ReAct agent framework
from langchain.agents.agent import AgentExecutor  # Executes agent decisions
from langchain.tools import tool  # Decorator for defining custom tools
from langchain import hub  # Loads pre-built prompt templates

import os  # For environment variable access
from dotenv import load_dotenv  # Loads .env file variables

# Load environment variables from .env file
load_dotenv()
# Disable LangSmith tracing to suppress API key warning
os.environ["LANGCHAIN_TRACING_V2"] = "false"  # Disable LangChain tracing to avoid LangSmith API key warnings
api_key = os.getenv('GEMINI_API_KEY')  # Get Gemini API key
model = os.getenv('GEMINI_MODEL')  # Get model name (e.g., 'gemini-pro')

# Fix: ZERO_SHOT_REACT_DESCRIPTION only accepts single-input tools.
# Wrap both args into a single string input instead.
@tool  # Decorator marks this function as a tool available to the agent
def multiply_numbers(input: str) -> int:
    """Multiply two numbers. Input must be two numbers separated by a comma, e.g. '6,7'"""
    a, b = input.strip().split(",")  # Parse comma-separated input
    return int(a.strip()) * int(b.strip())  # Return multiplication result

# Initialize the Gemini LLM with specific configuration
llm = ChatGoogleGenerativeAI(
    model=model,  # Use the model from environment
    temperature=0,  # Set to 0 for deterministic/consistent responses
    google_api_key=api_key  # Authenticate with API key
)

# Register available tools for the agent
tools = [multiply_numbers]  # Agent can use multiply_numbers tool

# Pull pre-built ReAct prompt template from LangChain Hub
prompt = hub.pull("hwchase17/react")  # Standard ReAct prompt

# Create the agent with ReAct (Reasoning + Acting) framework
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

# Create executor that runs the agent with error handling
executor = AgentExecutor(
    agent=agent,  # The agent to execute
    tools=tools,  # Available tools
    verbose=True,  # Print agent's thinking process
    handle_parsing_errors=True  # Handle parsing errors gracefully
)

# Execute agent with a natural language request
result = executor.invoke({"input": "What is 6 multiplied by 7?"})  # Invoke the agent
print(result["output"])  # Print the final answer

'''ZERO_SHOT_REACT_DESCRIPTION is a type of agent that performs a reasoning step before taking action. 
It does not rely on any chat history, meaning it makes decisions based solely on the current input. '''

'''CHAT_ZERO_SHOT_REACT_DESCRIPTION also performs a reasoning step before acting, but unlike `ZERO_SHOT_REACT_DESCRIPTION`, 
it uses a chat history variable in the prompt. This means that the final prompt will include the chat history, 
allowing the agent to remember the context of the chat and the history of the conversation. 
This agent type is designed for multi-turn tasks that require maintaining the context of a conversation.'''