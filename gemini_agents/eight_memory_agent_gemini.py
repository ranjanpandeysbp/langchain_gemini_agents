"""
Memory-Based Conversational Agent using Gemini
This agent maintains conversation history and context across multiple turns.
It uses LangChain's memory system to remember previous interactions.
"""

# Import Gemini and LangChain agent libraries
from langchain_google_genai import ChatGoogleGenerativeAI  # Gemini LLM
from langchain.agents import AgentExecutor, create_react_agent  # Agent framework
from langchain.tools import tool  # Tool decorator
from langchain import hub  # Prompt templates
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory  # Memory classes
import os  # Environment variables
from dotenv import load_dotenv  # Load .env file

# Load environment configuration
load_dotenv()
# Disable LangSmith tracing to suppress API key warning
os.environ["LANGCHAIN_TRACING_V2"] = "false"  # Disable LangChain tracing to avoid LangSmith API key warnings
api_key = os.getenv('GEMINI_API_KEY')  # Gemini API key
model = os.getenv('GEMINI_MODEL')  # Model identifier

# ============================================================================
# CUSTOM TOOLS FOR CONVERSATIONAL AGENT
# ============================================================================

@tool  # Mark as tool available to agent
def store_information(key: str, value: str) -> str:
    """Store information about the user. Input format: 'key:value' like 'name:John' or 'hobby:reading'"""
    try:
        # This tool simulates storing user information
        stored_info = f"Stored information - {key}: {value}"  # Create storage message
        return stored_info  # Return confirmation
    except Exception as e:
        return f"Error storing information: {str(e)}"  # Return error message

@tool  # Mark as tool available to agent
def retrieve_information(key: str) -> str:
    """Retrieve previously stored information about the user. Input is the key to look up."""
    try:
        # This tool simulates retrieving user information
        # In a real system, this would query a database
        retrieved = f"Retrieved: {key} value from memory"  # Simulate retrieval
        return retrieved  # Return retrieved value
    except Exception as e:
        return f"Error retrieving information: {str(e)}"  # Return error message

@tool  # Mark as tool available to agent
def summarize_conversation(topic: str) -> str:
    """Summarize what has been discussed about a topic in the conversation. Input is a topic."""
    try:
        # This tool would summarize previous conversation turns about a topic
        summary = f"Summary of discussion about {topic}: The conversation covered various aspects of {topic}."  # Create summary
        return summary  # Return summary
    except Exception as e:
        return f"Error summarizing conversation: {str(e)}"  # Return error message

# ============================================================================
# AGENT INITIALIZATION WITH MEMORY
# ============================================================================

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model=model,  # Use specified model
    temperature=0.7,  # Balanced creativity for conversational responses
    google_api_key=api_key  # API authentication
)

# Initialize ConversationBufferMemory to store all messages
memory = ConversationBufferMemory(
    memory_key="chat_history",  # Key for accessing memory in prompts
    return_messages=True  # Return messages as a list
)

# Note: Alternative memory types:
# ConversationSummaryMemory: Summarizes older messages to save tokens
# ConversationEntityMemory: Tracks entities mentioned in conversation
# ConversationTokenBufferMemory: Keeps messages up to a token limit

# Register tools available to agent
tools = [store_information, retrieve_information, summarize_conversation]  # Available conversational tools

# Load ReAct prompt template
prompt = hub.pull("hwchase17/react")  # Standard ReAct reasoning template

# Create the agent with tools and no memory (we'll add memory in executor)
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)  # Create agent

# Create agent executor with memory integration
agent_executor = AgentExecutor(
    agent=agent,  # The agent to execute
    tools=tools,  # Available tools
    memory=memory,  # Attach conversation memory
    verbose=True,  # Show agent's reasoning steps
    handle_parsing_errors=True  # Handle parsing errors gracefully
)

# ============================================================================
# CONVERSATION SIMULATION
# ============================================================================

def conduct_multi_turn_conversation():
    """
    Simulate a multi-turn conversation where the agent remembers context.
    Each turn builds upon previous conversations due to memory system.
    """
    
    print("\n" + "=" * 80)
    print("MEMORY-BASED CONVERSATIONAL AGENT WITH GEMINI")
    print("=" * 80)
    print("\nThis agent remembers previous interactions and maintains conversation context.")
    print("=" * 80)
    
    # Define a series of conversation turns
    conversation_turns = [
        {
            "turn": 1,  # First turn
            "user_message": "Hi! My name is Alice and I enjoy programming and coffee. Can you remember this about me?"  # User introduces themselves
        },
        {
            "turn": 2,  # Second turn
            "user_message": "I also work as a data scientist. What have you learned about me so far in our conversation?"  # User adds information and asks for summary
        },
        {
            "turn": 3,  # Third turn
            "user_message": "Can you tell me what you remember about my hobbies and profession?"  # User tests memory
        },
        {
            "turn": 4,  # Fourth turn
            "user_message": "I just started learning Python for machine learning. Does this align with what you know about me?"  # User provides update
        },
        {
            "turn": 5,  # Fifth turn
            "user_message": "Summarize everything you've learned about me in this conversation."  # User asks for comprehensive summary
        }
    ]
    
    # Execute each conversation turn
    for turn_info in conversation_turns:
        turn_number = turn_info["turn"]  # Get turn number
        user_message = turn_info["user_message"]  # Get user message
        
        # Display conversation turn header
        print(f"\n{'=' * 80}")
        print(f"TURN {turn_number}")  # Turn identifier
        print(f"{'=' * 80}")
        print(f"\nUser: {user_message}\n")  # Display user message
        print("-" * 80)
        
        try:
            # Invoke agent with user message
            result = agent_executor.invoke({"input": user_message})  # Execute conversation turn
            
            # Display agent response
            print(f"\nAgent Response: {result['output']}\n")  # Print agent's response
            
            # Display current memory state
            print("-" * 80)
            print("CONVERSATION MEMORY AT THIS POINT:")  # Memory state header
            print("-" * 80)
            # Get memory buffer contents
            memory_contents = memory.buffer  # Access stored memory
            print(f"{memory_contents}\n")  # Display memory contents
        
        except Exception as e:
            print(f"Error in conversation turn: {str(e)}")  # Handle execution errors
    
    # Final memory analysis
    print("\n" + "=" * 80)
    print("FINAL CONVERSATION MEMORY")
    print("=" * 80)
    final_memory = memory.buffer  # Get final memory state
    print(f"\n{final_memory}\n")  # Display final memory contents
    
    # Display memory statistics
    print("=" * 80)
    print("MEMORY STATISTICS")
    print("=" * 80)
    # Count conversation turns in memory
    memory_lines = final_memory.count("\n") if final_memory else 0  # Count memory entries
    print(f"Total memory entries: {memory_lines}")  # Display entry count
    print(f"Memory type: ConversationBufferMemory (stores all messages)")  # Memory type info
    print("=" * 80 + "\n")

# ============================================================================
# ALTERNATIVE MEMORY DEMONSTRATION
# ============================================================================

def demonstrate_summary_memory():
    """
    Demonstrate ConversationSummaryMemory which summarizes older messages.
    This is useful for long conversations where token limit matters.
    """
    
    print("\n" + "=" * 80)
    print("ALTERNATIVE: CONVERSATION SUMMARY MEMORY")
    print("=" * 80)
    print("\nNote: ConversationSummaryMemory would summarize older messages to save tokens.")
    print("This is useful for long, extended conversations.\n")
    
    # Initialize summary memory
    summary_memory = ConversationSummaryMemory(
        llm=llm,  # Use LLM to summarize previous messages
        memory_key="chat_history",  # Key for accessing memory
        return_messages=True  # Return as messages
    )
    
    # This would work the same way as ConversationBufferMemory
    # but would automatically summarize older messages when too many accumulate
    print("Benefits of ConversationSummaryMemory:")
    print("  - Saves tokens by summarizing old messages")
    print("  - Maintains conversation context")
    print("  - Better for long conversations")
    print("  - Reduces memory usage over time\n")

# ============================================================================
# SIMPLE MEMORY USAGE EXAMPLE
# ============================================================================

def simple_memory_example():
    """
    A simpler example showing basic memory functionality.
    Good for understanding memory without complex agent logic.
    """
    
    print("\n" + "=" * 80)
    print("SIMPLE MEMORY USAGE EXAMPLE")
    print("=" * 80 + "\n")
    
    # Create a simple buffer memory
    simple_memory = ConversationBufferMemory(
        memory_key="history",  # Key for memory
        return_messages=False  # Return as string instead of messages
    )
    
    # Simulate adding messages to memory
    messages = [
        ("User", "Hello, my name is Bob"),  # First user message
        ("Assistant", "Nice to meet you Bob!"),  # First assistant response
        ("User", "I like machine learning"),  # Second user message
        ("Assistant", "Machine learning is fascinating!"),  # Second assistant response
        ("User", "Can you remember my name?"),  # Third user message
        ("Assistant", "Yes, your name is Bob and you like machine learning."),  # Third assistant response
    ]
    
    # Add each message to memory
    for role, message in messages:
        if role == "User":  # Handle user messages
            simple_memory.save_context(
                {"input": message},  # User input
                {"output": "Acknowledged"}  # Dummy output for memory
            )
        else:  # Handle assistant messages
            simple_memory.save_context(
                {"input": "Previous user message"},  # Previous input
                {"output": message}  # Assistant output
            )
    
    # Display accumulated memory
    print("Accumulated Conversation Memory:")
    print("-" * 80)
    print(simple_memory.buffer)  # Display memory buffer
    print("-" * 80 + "\n")
    
    # Query memory with load_memory_variables
    memory_vars = simple_memory.load_memory_variables({})  # Load memory variables
    print("Memory Variables:")
    print("-" * 80)
    print(f"History: {memory_vars['history']}")  # Display history
    print("-" * 80 + "\n")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Run the main multi-turn conversation example
    conduct_multi_turn_conversation()  # Execute multi-turn conversation
    
    # Run the summary memory demonstration
    demonstrate_summary_memory()  # Show alternative memory type
    
    # Run the simple memory example
    simple_memory_example()  # Show basic memory usage
    
    print("\n" + "=" * 80)
    print("Memory-Based Agent Demonstration Complete")
    print("=" * 80 + "\n")
    
    # Display additional information
    print("Key Concepts:")
    print("1. ConversationBufferMemory: Stores all conversation messages")
    print("2. ConversationSummaryMemory: Summarizes old messages to save tokens")
    print("3. ConversationEntityMemory: Tracks entities discussed")
    print("4. ConversationTokenBufferMemory: Keeps messages up to token limit")
    print("\nMemory helps agents:")
    print("  - Maintain context across conversation turns")
    print("  - Remember user information and preferences")
    print("  - Reference previous discussions")
    print("  - Provide personalized responses\n")
