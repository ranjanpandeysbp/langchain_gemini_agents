"""
Research Agent with DuckDuckGo using Gemini
This agent performs web searches using DuckDuckGo to gather information for research
"""

# Import Gemini and LangChain agent libraries
from langchain_google_genai import ChatGoogleGenerativeAI  # Gemini LLM
from langchain.agents import create_react_agent  # ReAct agent framework
from langchain.agents.agent import AgentExecutor  # Agent executor
from langchain.tools import tool  # Tool decorator
from langchain import hub  # Prompt templates
import os  # Environment variables
from dotenv import load_dotenv  # Load .env file

# Load environment configuration
load_dotenv()
# Disable LangSmith tracing to suppress API key warning
os.environ["LANGCHAIN_TRACING_V2"] = "false"  # Disable LangChain tracing to avoid LangSmith API key warnings
api_key = os.getenv('GEMINI_API_KEY')  # Gemini API key
model = os.getenv('GEMINI_MODEL')  # Model identifier

# Note: Install duckduckgo-search for web search functionality
# pip install duckduckgo-search

@tool  # Decorator marks this as an agent tool
def search_duckduckgo(query: str) -> str:
    """Search the web using DuckDuckGo. Input is a search query."""
    try:
        from duckduckgo_search import DDGS  # DuckDuckGo search library
        
        ddgs = DDGS()  # Initialize DuckDuckGo search
        results = ddgs.text(query, max_results=5)  # Perform text search, get top 5 results
        
        if not results:  # Check if results are empty
            return "No results found"  # Return no results message
        
        # Format search results for display
        search_results = f"Search results for '{query}':\n\n"  # Header
        for i, result in enumerate(results, 1):  # Iterate through results with numbering
            search_results += f"{i}. {result.get('title', 'N/A')}\n"  # Result title
            search_results += f"   URL: {result.get('href', 'N/A')}\n"  # Source URL
            search_results += f"   Summary: {result.get('body', 'N/A')}\n\n"  # Result snippet
        
        return search_results  # Return formatted results
    
    except Exception as e:
        return f"Error searching DuckDuckGo: {str(e)}\nNote: Install duckduckgo-search library: pip install duckduckgo-search"  # Return error

@tool  # Decorator marks this as an agent tool
def search_news(query: str) -> str:
    """Search for recent news about a topic using DuckDuckGo. Input is a news query."""
    try:
        from duckduckgo_search import DDGS  # DuckDuckGo search library
        
        ddgs = DDGS()  # Initialize DuckDuckGo search
        # Search with news filter by appending 'news' to query
        results = ddgs.text(f"{query} news", max_results=5)  # Search with news keyword, get top 5
        
        if not results:  # Check if results are empty
            return "No news found"  # Return no news message
        
        # Format news results for display
        news_results = f"News results for '{query}':\n\n"  # Header
        for i, result in enumerate(results, 1):  # Iterate through news with numbering
            news_results += f"{i}. {result.get('title', 'N/A')}\n"  # News title
            news_results += f"   Source: {result.get('href', 'N/A')}\n"  # Source URL
            news_results += f"   Details: {result.get('body', 'N/A')}\n\n"  # News snippet
        
        return news_results  # Return formatted news
    
    except Exception as e:
        return f"Error searching news: {str(e)}"  # Return error message

@tool  # Decorator marks this as an agent tool
def research_topic(topic: str) -> str:
    """Conduct comprehensive research on a topic with multiple searches. Input is a topic."""
    try:
        from duckduckgo_search import DDGS  # DuckDuckGo search library
        
        ddgs = DDGS()  # Initialize DuckDuckGo search
        
        # Initialize research report
        research = f"Research Report on: {topic}\n"  # Report title
        research += "=" * 50 + "\n\n"  # Separator
        
        # Search for general information about topic
        general_results = ddgs.text(topic, max_results=3)  # General search, top 3 results
        research += "General Information:\n"  # Section header
        for result in general_results:
            research += f"- {result.get('title', 'N/A')}: {result.get('body', 'N/A')}\n"  # Add result to report
        
        # Search for latest developments on topic
        development_results = ddgs.text(f"{topic} latest 2024 2025", max_results=3)  # Recent developments search
        research += f"\nLatest Developments:\n"  # Section header
        for result in development_results:
            research += f"- {result.get('title', 'N/A')}: {result.get('body', 'N/A')}\n"  # Add development to report
        
        return research  # Return comprehensive research report
    
    except Exception as e:
        return f"Error researching topic: {str(e)}"  # Return error message

# Initialize Gemini LLM with balanced creativity
llm = ChatGoogleGenerativeAI(
    model=model,  # Use specified model
    temperature=0.7,  # Balanced creativity for natural responses
    google_api_key=api_key  # API authentication
)

# Register research tools for agent
tools = [search_duckduckgo, search_news, research_topic]  # Available research operations

# Load ReAct prompt template
prompt = hub.pull("hwchase17/react")  # Standard ReAct reasoning prompt

# Create ReAct agent with research tools
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

# Initialize executor with verbose logging and error handling
executor = AgentExecutor(
    agent=agent,  # The agent to run
    tools=tools,  # Available tools
    verbose=True,  # Show agent's reasoning steps
    handle_parsing_errors=True  # Handle parsing errors gracefully
)

print("=" * 60)
print("Research Agent with DuckDuckGo and Gemini")
print("=" * 60)
print("\nNote: Install duckduckgo-search library:")
print("pip install duckduckgo-search\n")

# Example research queries
research_queries = [
    "What is the latest development in Artificial Intelligence?",  # Query about AI developments
    "Search for news about quantum computing",  # Query about quantum computing news
    "Research the impact of climate change on global economy",  # Query about climate impact
]

print("Agent ready. Example research queries:")
for query in research_queries:
    print(f"  - {query}\n")  # Display examples

# Test the agent (uncomment to run):
test_result = """
Example usage:
    result = executor.invoke({
        "input": "What is the latest development in Artificial Intelligence?"
    })
    print(result["output"])
"""
print(test_result)  
# Display usage example

# Uncomment to run a test:
print("\nRunning example query...\n")
result = executor.invoke({"input": "What are the latest developments in AI?"})
print(result["output"])
