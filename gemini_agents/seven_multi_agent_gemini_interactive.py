"""
Multi-Agent System using Gemini
This system demonstrates multiple specialized agents coordinating to solve complex tasks.
It includes a supervisor agent that routes requests to appropriate specialized agents.
Runs in an interactive Q&A loop until the user types 'exit'.
"""

# Import Gemini and LangChain agent libraries
from langchain_google_genai import ChatGoogleGenerativeAI  # Gemini LLM
from langchain.agents import create_react_agent, AgentExecutor  # Agent framework
from langchain.tools import tool  # Tool decorator for agent functions
from langchain import hub  # Prompt templates
import os  # Environment variables
from dotenv import load_dotenv  # Load .env file
from typing import List, Dict, Any  # Type hints for better code clarity

# Load environment configuration
load_dotenv()
# Disable LangSmith tracing to suppress API key warning
os.environ["LANGCHAIN_TRACING_V2"] = "false"  # Disable LangChain tracing to avoid LangSmith API key warnings
api_key = os.getenv('GEMINI_API_KEY')  # Gemini API key
model = os.getenv('GEMINI_MODEL')  # Model identifier

# ============================================================================
# SPECIALIZED AGENT TOOLS
# ============================================================================

# --- MATH AGENT TOOLS ---
@tool  # Mark as tool available to agents
def calculate_arithmetic(expression: str) -> str:
    """Perform arithmetic calculations. Input is a mathematical expression like '5+3*2'"""
    try:
        result = eval(expression)  # Evaluate mathematical expression
        return f"Result of '{expression}' = {result}"  # Return formatted result
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"  # Return error message

@tool  # Mark as tool available to agents
def solve_quadratic(coefficients: str) -> str:
    """Solve quadratic equation. Input format: 'a,b,c' for equation ax²+bx+c=0"""
    try:
        import math  # Math library for square root
        a, b, c = map(float, coefficients.split(","))  # Parse coefficients
        
        # Calculate discriminant
        discriminant = b**2 - 4*a*c  # b²-4ac
        
        if discriminant < 0:  # No real solutions
            return f"No real solutions for equation {a}x²+{b}x+{c}=0 (discriminant={discriminant})"
        
        # Calculate roots using quadratic formula
        sqrt_discriminant = math.sqrt(discriminant)  # √(b²-4ac)
        root1 = (-b + sqrt_discriminant) / (2*a)  # First root
        root2 = (-b - sqrt_discriminant) / (2*a)  # Second root
        
        return f"Solutions for {a}x²+{b}x+{c}=0:\nRoot 1: {root1}\nRoot 2: {root2}"  # Return both roots
    
    except Exception as e:
        return f"Error solving quadratic: {str(e)}"  # Return error message

# --- DATA ANALYSIS AGENT TOOLS ---
@tool  # Mark as tool available to agents
def analyze_numbers(numbers: str) -> str:
    """Analyze a list of numbers. Input is comma-separated numbers like '1,2,3,4,5'"""
    try:
        import statistics  # Statistics library for mean, median, etc.
        nums = list(map(float, numbers.split(",")))  # Parse numbers
        
        # Calculate statistics
        mean = statistics.mean(nums)  # Average
        median = statistics.median(nums)  # Middle value
        stdev = statistics.stdev(nums) if len(nums) > 1 else 0  # Standard deviation
        
        # Format analysis report
        analysis = f"Analysis of {numbers}:\n"
        analysis += f"- Count: {len(nums)}\n"  # Number of values
        analysis += f"- Sum: {sum(nums)}\n"  # Total
        analysis += f"- Mean: {mean:.2f}\n"  # Average
        analysis += f"- Median: {median:.2f}\n"  # Middle value
        analysis += f"- Std Dev: {stdev:.2f}\n"  # Spread/variation
        analysis += f"- Min: {min(nums)}\n"  # Lowest value
        analysis += f"- Max: {max(nums)}"  # Highest value
        
        return analysis  # Return analysis report
    
    except Exception as e:
        return f"Error analyzing numbers: {str(e)}"  # Return error message

@tool  # Mark as tool available to agents
def generate_insights(data_description: str) -> str:
    """Generate insights about data patterns. Input is a description of the data."""
    try:
        # Simulate insight generation based on data description
        insights = f"Insights about: {data_description}\n\n"  # Header
        
        # Generate sample insights
        insights += "1. Trend Analysis:\n"  # Insight category
        insights += "   - Check for increasing or decreasing patterns\n"  # Detail
        insights += "   - Identify seasonal variations if applicable\n\n"  # Detail
        
        insights += "2. Outlier Detection:\n"  # Insight category
        insights += "   - Look for unusual data points that deviate from patterns\n"  # Detail
        insights += "   - Investigate potential causes of anomalies\n\n"  # Detail
        
        insights += "3. Correlation Analysis:\n"  # Insight category
        insights += "   - Find relationships between different data variables\n"  # Detail
        insights += "   - Determine strength of correlations\n"  # Detail
        
        return insights  # Return insights report
    
    except Exception as e:
        return f"Error generating insights: {str(e)}"  # Return error message

# --- RESEARCH AGENT TOOLS ---
@tool  # Mark as tool available to agents
def summarize_information(topic: str) -> str:
    """Summarize information about a topic. Input is a topic string."""
    try:
        # Simulate information summary
        summary = f"Summary of {topic}:\n\n"  # Header
        
        summary += f"Overview:\n"  # Section
        summary += f"'{topic}' is a multifaceted subject that covers various aspects.\n\n"  # Content
        
        summary += f"Key Points:\n"  # Section
        summary += f"1. Definition and scope of {topic}\n"  # Point
        summary += f"2. Historical context and development\n"  # Point
        summary += f"3. Current applications and relevance\n"  # Point
        summary += f"4. Future trends and opportunities\n"  # Point
        
        return summary  # Return summary
    
    except Exception as e:
        return f"Error summarizing information: {str(e)}"  # Return error message

@tool  # Mark as tool available to agents
def compare_concepts(concepts: str) -> str:
    """Compare multiple concepts. Input is comma-separated concept names."""
    try:
        concept_list = [c.strip() for c in concepts.split(",")]  # Parse concepts
        
        # Generate comparison
        comparison = f"Comparison of: {', '.join(concept_list)}\n\n"  # Header
        
        comparison += f"Similarities:\n"  # Section
        for i, concept in enumerate(concept_list, 1):  # Iterate through concepts
            comparison += f"  - Aspect {i}: {concept} shares common characteristics\n"  # Content
        
        comparison += f"\nDifferences:\n"  # Section
        for i, concept in enumerate(concept_list, 1):  # Iterate through concepts
            comparison += f"  - {concept} has unique features\n"  # Content
        
        return comparison  # Return comparison
    
    except Exception as e:
        return f"Error comparing concepts: {str(e)}"  # Return error message

# ============================================================================
# AGENT INITIALIZATION
# ============================================================================

# Initialize Gemini LLM for all agents
llm = ChatGoogleGenerativeAI(
    model=model,  # Use specified model
    temperature=0.7,  # Balanced creativity for natural responses
    google_api_key=api_key  # API authentication
)

# Load ReAct prompt template
prompt = hub.pull("hwchase17/react")  # Standard ReAct reasoning template

# ============================================================================
# SPECIALIZED AGENTS
# ============================================================================

# --- MATH AGENT ---
math_tools = [calculate_arithmetic, solve_quadratic]
math_agent = create_react_agent(llm=llm, tools=math_tools, prompt=prompt)
math_executor = AgentExecutor(
    agent=math_agent,
    tools=math_tools,
    verbose=False,
    handle_parsing_errors=True
)

# --- DATA ANALYSIS AGENT ---
analysis_tools = [analyze_numbers, generate_insights]
analysis_agent = create_react_agent(llm=llm, tools=analysis_tools, prompt=prompt)
analysis_executor = AgentExecutor(
    agent=analysis_agent,
    tools=analysis_tools,
    verbose=False,
    handle_parsing_errors=True
)

# --- RESEARCH AGENT ---
research_tools = [summarize_information, compare_concepts]
research_agent = create_react_agent(llm=llm, tools=research_tools, prompt=prompt)
research_executor = AgentExecutor(
    agent=research_agent,
    tools=research_tools,
    verbose=False,
    handle_parsing_errors=True
)

# ============================================================================
# SUPERVISOR AGENT
# ============================================================================

@tool
def delegate_to_math_agent(task: str) -> str:
    """Delegate mathematical tasks to the Math Agent. Input is a math task description."""
    try:
        result = math_executor.invoke({"input": task})
        return f"Math Agent Result:\n{result['output']}"
    except Exception as e:
        return f"Math Agent Error: {str(e)}"

@tool
def delegate_to_analysis_agent(task: str) -> str:
    """Delegate data analysis tasks to the Analysis Agent. Input is an analysis task description."""
    try:
        result = analysis_executor.invoke({"input": task})
        return f"Analysis Agent Result:\n{result['output']}"
    except Exception as e:
        return f"Analysis Agent Error: {str(e)}"

@tool
def delegate_to_research_agent(task: str) -> str:
    """Delegate research tasks to the Research Agent. Input is a research task description."""
    try:
        result = research_executor.invoke({"input": task})
        return f"Research Agent Result:\n{result['output']}"
    except Exception as e:
        return f"Research Agent Error: {str(e)}"

supervisor_tools = [
    delegate_to_math_agent,
    delegate_to_analysis_agent,
    delegate_to_research_agent
]

supervisor_agent = create_react_agent(
    llm=llm,
    tools=supervisor_tools,
    prompt=prompt
)

supervisor_executor = AgentExecutor(
    agent=supervisor_agent,
    tools=supervisor_tools,
    verbose=True,
    handle_parsing_errors=True
)

# ============================================================================
# MULTI-AGENT ORCHESTRATION
# ============================================================================

def run_multi_agent_system(user_request: str) -> None:
    """
    Execute a user request through the multi-agent system.
    The supervisor agent automatically routes to appropriate specialists.

    Args:
        user_request: Natural language request from user
    """
    print("\n" + "=" * 70)
    print(f"User Request: {user_request}")
    print("-" * 70)
    
    try:
        result = supervisor_executor.invoke({"input": user_request})
        
        print("\n" + "=" * 70)
        print("FINAL RESULT")
        print("=" * 70)
        print(f"\n{result['output']}\n")
    
    except Exception as e:
        print(f"Error in multi-agent execution: {str(e)}")

# ============================================================================
# INTERACTIVE Q&A LOOP
# ============================================================================

def interactive_session() -> None:
    """
    Run an interactive Q&A session with the multi-agent system.
    Continuously prompts the user for input and processes requests
    until the user types 'exit'.
    """
    print("\n" + "=" * 70)
    print("  MULTI-AGENT SYSTEM WITH GEMINI — INTERACTIVE MODE")
    print("=" * 70)
    print("\nAvailable Agents:")
    print("  🧮  Math Agent     — arithmetic, quadratic equations")
    print("  📊  Analysis Agent — number analysis, pattern insights")
    print("  🔍  Research Agent — topic summaries, concept comparisons")
    print("\nType your request and press Enter. Type 'exit' to quit.")
    print("=" * 70)

    session_count = 0  # Track number of queries in this session

    while True:
        print()  # Blank line for readability
        try:
            user_input = input("You: ").strip()  # Prompt user for input
        except (EOFError, KeyboardInterrupt):
            # Handle Ctrl+D or Ctrl+C gracefully
            print("\n\nSession interrupted. Goodbye!")
            break

        if not user_input:
            # Skip empty inputs
            print("(Please enter a request or type 'exit' to quit.)")
            continue

        if user_input.lower() == "exit":
            # Exit condition
            print("\n" + "=" * 70)
            print(f"Session ended. Total queries processed: {session_count}")
            print("Thank you for using the Multi-Agent System. Goodbye!")
            print("=" * 70 + "\n")
            break

        if user_input.lower() in ("help", "?"):
            # Show quick help
            print("\nExample requests you can try:")
            print("  - Solve 2x² - 5x + 2 = 0")
            print("  - Analyze the numbers 4, 8, 15, 16, 23, 42")
            print("  - Summarize information about quantum computing")
            print("  - Compare Machine Learning, Deep Learning, and AI")
            print("  - Calculate 125 * 8 + 300 and explain the result")
            continue

        # Process the request through the multi-agent system
        session_count += 1
        print(f"\n[Query #{session_count}]")
        run_multi_agent_system(user_input)

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    interactive_session()