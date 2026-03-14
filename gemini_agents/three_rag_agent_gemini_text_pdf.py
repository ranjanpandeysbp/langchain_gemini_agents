"""
RAG (Retrieval-Augmented Generation) Agent using Gemini
Reads all .txt and .pdf files from /data folder and answers questions interactively
"""

# ── Imports ────────────────────────────────────────────────────────────────────
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings  # Gemini LLM and embedding model wrappers
from langchain.agents import create_react_agent          # Factory to build a ReAct-style reasoning agent
from langchain.agents.agent import AgentExecutor         # Runs the agent loop and manages tool calls
from langchain.tools import tool                         # Decorator that turns a plain function into an agent-usable tool
from langchain import hub                                # LangChain Hub – used to pull pre-built prompt templates
from langchain_community.vectorstores import FAISS       # FAISS vector store for fast similarity search
from langchain.text_splitter import CharacterTextSplitter  # Splits long text into overlapping chunks
from pypdf import PdfReader                              # Reads PDF files and extracts their text content
import os                                                # Standard library for environment variable access
from dotenv import load_dotenv                           # Loads key=value pairs from a .env file into os.environ
from pathlib import Path                                 # Object-oriented file system path handling


# ── Environment setup ──────────────────────────────────────────────────────────
load_dotenv()                                            # Read .env file and populate environment variables
os.environ["LANGCHAIN_TRACING_V2"] = "false"            # Disable LangSmith tracing to suppress API key warnings
api_key = os.getenv('GEMINI_API_KEY')                   # Pull Gemini API key from environment
model   = os.getenv('GEMINI_MODEL')                     # Pull model name (e.g. gemini-1.5-pro) from environment


# ── Helper: read a plain-text file ────────────────────────────────────────────
def load_txt_file(file_path: Path) -> str:
    """Read and return the full text content of a .txt file."""
    return file_path.read_text(encoding="utf-8").strip()  # Decode as UTF-8 and remove leading/trailing whitespace


# ── Helper: extract text from a PDF file ──────────────────────────────────────
def load_pdf_file(file_path: Path) -> str:
    """Extract and concatenate text from every page of a PDF file."""
    reader     = PdfReader(str(file_path))  # Open the PDF file with pypdf
    pages_text = []                         # List that will hold the text from each page

    for i, page in enumerate(reader.pages):        # Iterate over every page in the PDF
        text = page.extract_text()                 # Extract raw text from the current page
        if text:                                   # Only keep pages that contain actual text
            pages_text.append(text.strip())        # Strip whitespace and store the page text

    return "\n\n".join(pages_text)                 # Join all pages with a blank line separator


# ── Helper: load all .txt and .pdf files from a folder ────────────────────────
def load_documents_from_folder(folder_path: str) -> list[str]:
    """
    Scan a folder for .txt and .pdf files, extract their text,
    and return a list of raw document strings ready for chunking.
    """
    documents = []                  # Accumulator for successfully loaded document texts
    data_dir  = Path(folder_path)   # Convert the string path to a Path object for easy manipulation

    if not data_dir.exists():                                           # Check the folder actually exists on disk
        print(f"[ERROR] Folder '{folder_path}' does not exist.")        # Inform the user if it is missing
        return documents                                                # Return empty list so the caller can handle it

    # Gather all .txt and .pdf files in the folder (not recursive)
    all_files = list(data_dir.glob("*.txt")) + list(data_dir.glob("*.pdf"))  # Find every .txt and .pdf file

    if not all_files:                                                           # Check whether any supported files were found
        print(f"[WARNING] No .txt or .pdf files found in '{folder_path}'.")    # Warn the user if the folder is empty
        return documents                                                        # Return empty list early

    print(f"\n📂 Loading {len(all_files)} file(s) from '{folder_path}':")  # Report how many files were discovered

    for file_path in sorted(all_files):    # Process files in alphabetical order for reproducibility
        try:
            if file_path.suffix.lower() == ".txt":      # Detect plain-text files by their extension
                content   = load_txt_file(file_path)    # Read the full text of the .txt file
                file_type = "TXT"                        # Label for the status message

            elif file_path.suffix.lower() == ".pdf":    # Detect PDF files by their extension
                content   = load_pdf_file(file_path)    # Extract text from the PDF using pypdf
                file_type = "PDF"                        # Label for the status message

            else:
                continue                                # Skip any file type that is not .txt or .pdf

            if content:                                                                        # Only keep files that yielded non-empty text
                documents.append(content)                                                      # Add the extracted text to our document list
                print(f"   ✅ [{file_type}] {file_path.name} ({len(content)} chars)")         # Confirm successful load with character count
            else:
                print(f"   ⚠️  [{file_type}] Skipped (no extractable text): {file_path.name}")  # Warn when a file produced no text (e.g. scanned PDF)

        except Exception as e:
            print(f"   ❌ Failed to read {file_path.name}: {e}")  # Report any file-level error without crashing the whole run

    return documents   # Return the list of extracted document strings


# ── Load documents ─────────────────────────────────────────────────────────────
DATA_FOLDER = "../data"                              # Path to the folder containing your knowledge-base files
documents   = load_documents_from_folder(DATA_FOLDER)  # Load all .txt and .pdf files from that folder

if not documents:                                   # Abort early if no usable documents were found
    print("\n[ERROR] No documents loaded. Add .txt or .pdf files to the /data folder and retry.")
    exit(1)                                         # Exit with a non-zero code to signal failure


# ── Embeddings model ───────────────────────────────────────────────────────────
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",  # Google's current general-purpose embedding model
    google_api_key=api_key                # Authenticate the request with our API key
)


# ── Chunk documents ────────────────────────────────────────────────────────────
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)  # Split into 500-char chunks, 100-char overlap keeps context across boundaries
chunks = []                                          # List that will hold all text chunks from all documents

for doc in documents:                                # Iterate over every loaded document
    chunks.extend(text_splitter.split_text(doc))    # Split the document and add its chunks to the master list

print(f"\n🔪 Split into {len(chunks)} chunk(s) for indexing...")  # Show total number of chunks produced


# ── Build FAISS vector store ───────────────────────────────────────────────────
print("⚙️  Building vector store (this may take a moment)...")         # Notify the user that embedding calls are being made
vector_store = FAISS.from_texts(chunks, embeddings)                    # Embed every chunk and store vectors in an in-memory FAISS index
retriever    = vector_store.as_retriever(search_kwargs={"k": 3})       # Wrap the index as a LangChain retriever that returns the top-3 matches
print("✅ Vector store ready!\n")                                       # Confirm the index is built and ready for queries


# ── Search tool (exposed to the agent) ────────────────────────────────────────
@tool   # Register this function as a LangChain tool the agent can choose to call
def search_documents(query: str) -> str:
    """Search through the loaded documents to find relevant information. Input is a search query."""
    results = retriever.get_relevant_documents(query)              # Run semantic similarity search against the FAISS index
    if not results:                                                # Handle the case where nothing relevant was found
        return "No relevant information found in the documents."   # Return a clear message instead of an empty string
    return "\n\n".join([doc.page_content for doc in results])      # Concatenate the top-k chunk texts and return them to the agent


# ── LLM ───────────────────────────────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(
    model=model,            # Use the model name loaded from .env (e.g. gemini-1.5-pro)
    temperature=0.5,        # Mid-range temperature: balanced between factual and conversational
    google_api_key=api_key  # Authenticate with our Gemini API key
)


# ── Agent setup ────────────────────────────────────────────────────────────────
tools  = [search_documents]                                  # List of tools available to the agent (only document search here)
prompt = hub.pull("hwchase17/react")                         # Pull the standard ReAct prompt template from LangChain Hub
agent  = create_react_agent(llm=llm, tools=tools, prompt=prompt)  # Wire the LLM, tools, and prompt together into a ReAct agent

executor = AgentExecutor(
    agent=agent,                  # The ReAct agent that decides what to do each step
    tools=tools,                  # Same tool list passed again so the executor can invoke them
    verbose=False,                # Set to True to print the agent's internal Thought/Action/Observation loop
    handle_parsing_errors=True    # Gracefully recover if the LLM produces malformed output
)


# ── Interactive chat loop ──────────────────────────────────────────────────────
print("=" * 60)
print("  📚 RAG Agent with Gemini — Ask Anything!")   # Welcome banner
print("  Type your question and press Enter.")         # Usage instruction
print("  Type 'exit' or 'quit' to stop.")              # Exit instruction
print("=" * 60)

while True:                               # Keep the conversation going until the user explicitly quits
    try:
        user_input = input("\n🧑 You: ").strip()   # Prompt the user for input and remove surrounding whitespace
    except (KeyboardInterrupt, EOFError):           # Handle Ctrl+C or piped input reaching end-of-file
        print("\n\n👋 Session ended. Goodbye!")     # Friendly exit message
        break                                       # Exit the loop cleanly

    if not user_input:                             # Ignore empty submissions (user just pressed Enter)
        print("   ⚠️  Please enter a question.")   # Prompt them to type something
        continue                                   # Restart the loop without calling the agent

    if user_input.lower() in ("exit", "quit"):  # Check whether the user typed an exit command
        print("\n👋 Exiting. Goodbye!")           # Farewell message
        break                                    # Exit the while loop, ending the program

    try:
        result = executor.invoke({"input": user_input})   # Send the user's question to the RAG agent
        print(f"\n🤖 Agent: {result['output']}")           # Display the agent's final answer
    except Exception as e:
        print(f"\n❌ Error: {e}")   # Show any unexpected errors without crashing the program