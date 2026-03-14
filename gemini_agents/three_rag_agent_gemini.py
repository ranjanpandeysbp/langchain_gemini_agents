"""
RAG (Retrieval-Augmented Generation) Agent using Gemini
Reads all .txt files from /data folder and answers questions interactively
"""

# ── Imports ────────────────────────────────────────────────────────────────────
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings  # Gemini LLM and embedding model wrappers
from langchain.agents import create_react_agent          # Factory function that builds a ReAct-style reasoning agent
from langchain.agents.agent import AgentExecutor         # Runs the agent loop and manages tool calls at each step
from langchain.tools import tool                         # Decorator that converts a plain Python function into an agent-usable tool
from langchain import hub                                # LangChain Hub client – used to pull pre-built prompt templates
from langchain_community.vectorstores import FAISS       # FAISS in-memory vector store for fast nearest-neighbour similarity search
from langchain.text_splitter import CharacterTextSplitter  # Splits long documents into smaller overlapping chunks
import os                                                # Standard library module for reading environment variables
from dotenv import load_dotenv                           # Reads key=value pairs from a .env file into os.environ
from pathlib import Path                                 # Object-oriented, cross-platform file system path handling


# ── Environment setup ──────────────────────────────────────────────────────────
load_dotenv()                                            # Parse the .env file and load all variables into the environment
os.environ["LANGCHAIN_TRACING_V2"] = "false"            # Disable LangSmith tracing so no API key warning is printed
api_key = os.getenv('GEMINI_API_KEY')                   # Retrieve the Gemini API key stored in the .env file
model   = os.getenv('GEMINI_MODEL')                     # Retrieve the model name (e.g. gemini-1.5-pro) from the .env file


# ── Helper: load all .txt files from a folder ─────────────────────────────────
def load_documents_from_folder(folder_path: str) -> list[str]:
    """Read all .txt files from the given folder and return their contents as a list of strings."""
    documents = []                  # Accumulator list that will hold the text content of every successfully read file
    data_dir  = Path(folder_path)   # Convert the raw string path into a Path object for safe, OS-agnostic operations

    if not data_dir.exists():                                           # Guard: verify the folder actually exists before scanning
        print(f"[ERROR] Folder '{folder_path}' does not exist.")        # Inform the user which path was not found
        return documents                                                # Return an empty list so the caller can handle the failure

    txt_files = list(data_dir.glob("*.txt"))   # Find every file that ends with .txt directly inside the folder (non-recursive)

    if not txt_files:                                                          # Guard: check whether any .txt files were discovered
        print(f"[WARNING] No .txt files found in '{folder_path}'.")            # Warn the user so they know the folder exists but is empty
        return documents                                                       # Return an empty list early; nothing to process

    print(f"\n📂 Loading {len(txt_files)} file(s) from '{folder_path}':")  # Report the number of files about to be loaded

    for file_path in txt_files:          # Iterate over each discovered .txt file path
        try:
            content = file_path.read_text(encoding="utf-8").strip()   # Read the file as UTF-8 text and remove leading/trailing whitespace
            if content:                                                # Only keep the file if it contains actual text
                documents.append(content)                             # Add the file's text to our document list
                print(f"   ✅ Loaded: {file_path.name} ({len(content)} chars)")   # Confirm success and show character count
            else:
                print(f"   ⚠️  Skipped (empty): {file_path.name}")    # Warn when the file exists but has no content
        except Exception as e:
            print(f"   ❌ Failed to read {file_path.name}: {e}")       # Report any read error without crashing the entire run

    return documents   # Return the list of non-empty document strings to the caller


# ── Load documents ─────────────────────────────────────────────────────────────
DATA_FOLDER = "../data"                                  # Path to the folder that holds your knowledge-base .txt files
documents   = load_documents_from_folder(DATA_FOLDER)  # Call the helper to read all .txt files from that folder

if not documents:                                       # Abort if the helper returned an empty list (no usable files found)
    print("\n[ERROR] No documents loaded. Please add .txt files to the /data folder and retry.")
    exit(1)                                             # Exit with code 1 to signal a failure to any calling process


# ── Embeddings model ───────────────────────────────────────────────────────────
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",  # Google's current general-purpose text embedding model
    google_api_key=api_key                # API key used to authenticate every embedding request
)


# ── Chunk documents ────────────────────────────────────────────────────────────
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)  # 500-char chunks; 100-char overlap preserves context at boundaries
chunks = []                              # Master list that will hold every chunk produced from all documents

for doc in documents:                                # Loop over each loaded document string
    chunks.extend(text_splitter.split_text(doc))    # Split the document into chunks and append them all to the master list

print(f"\n🔪 Split into {len(chunks)} chunk(s) for indexing...")  # Show the total number of chunks that will be embedded


# ── Build FAISS vector store ───────────────────────────────────────────────────
print("⚙️  Building vector store (this may take a moment)...")          # Notify the user that API calls are being made to embed each chunk
vector_store = FAISS.from_texts(chunks, embeddings)                     # Embed every chunk via Gemini and store the resulting vectors in FAISS
retriever    = vector_store.as_retriever(search_kwargs={"k": 3})        # Wrap FAISS as a LangChain retriever returning the top-3 nearest chunks
print("✅ Vector store ready!\n")                                        # Confirm the index is built and queries can now be served


# ── Search tool (exposed to the agent) ────────────────────────────────────────
@tool   # Register this function as a named LangChain tool the agent can choose to invoke
def search_documents(query: str) -> str:
    """Search through the loaded documents to find relevant information. Input is a search query."""
    results = retriever.get_relevant_documents(query)              # Perform semantic similarity search and get the top-k matching chunks
    if not results:                                                # Handle the edge case where no relevant chunks were found
        return "No relevant information found in the documents."   # Return a descriptive string so the agent can tell the user
    return "\n\n".join([doc.page_content for doc in results])      # Concatenate the chunk texts with blank-line separators and return them


# ── LLM ───────────────────────────────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(
    model=model,            # Model name loaded from .env (e.g. gemini-1.5-pro or gemini-2.0-flash)
    temperature=0.5,        # 0.5 balances factual accuracy with natural, conversational phrasing
    google_api_key=api_key  # API key used to authenticate every chat completion request
)


# ── Agent setup ────────────────────────────────────────────────────────────────
tools  = [search_documents]                                        # List of tools the agent is allowed to call (document search only)
prompt = hub.pull("hwchase17/react")                               # Download the standard ReAct prompt template from LangChain Hub
agent  = create_react_agent(llm=llm, tools=tools, prompt=prompt)  # Combine the LLM, tools, and prompt into a ReAct reasoning agent

executor = AgentExecutor(
    agent=agent,                  # The ReAct agent that decides the next Thought / Action at each step
    tools=tools,                  # Tool list passed again so the executor can actually invoke them
    verbose=False,                # Set to True to print the agent's internal Thought → Action → Observation trace
    handle_parsing_errors=True    # If the LLM returns malformed output, retry instead of raising an exception
)


# ── Interactive chat loop ──────────────────────────────────────────────────────
print("=" * 60)
print("  📚 RAG Agent with Gemini — Ask Anything!")   # Welcome banner shown once at startup
print("  Type your question and press Enter.")         # Instruction for normal usage
print("  Type 'exit' or 'quit' to stop.")              # Instruction for how to quit
print("=" * 60)

while True:                                   # Loop indefinitely until the user explicitly exits
    try:
        user_input = input("\n🧑 You: ").strip()   # Display the prompt, wait for the user to type, then strip whitespace
    except (KeyboardInterrupt, EOFError):           # Catch Ctrl+C (KeyboardInterrupt) or end-of-piped-input (EOFError)
        print("\n\n👋 Session ended. Goodbye!")     # Print a polite goodbye before the program terminates
        break                                       # Exit the while loop cleanly

    if not user_input:                             # If the user pressed Enter without typing anything
        print("   ⚠️  Please enter a question.")   # Nudge them to type a real question
        continue                                   # Skip the rest of the loop body and prompt again

    if user_input.lower() in ("exit", "quit"):  # Check whether the user typed one of the recognised exit commands
        print("\n👋 Exiting. Goodbye!")           # Print a farewell message
        break                                    # Break out of the while loop, ending the program

    try:
        result = executor.invoke({"input": user_input})   # Pass the user's question to the RAG agent and wait for a response
        print(f"\n🤖 Agent: {result['output']}")           # Print the agent's final answer extracted from the result dict
    except Exception as e:
        print(f"\n❌ Error: {e}")   # Catch and display any unexpected runtime errors without crashing the program