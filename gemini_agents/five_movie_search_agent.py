"""
Movie Agent using Gemini + OMDB API (Free Tier)
This agent can search for movies and fetch detailed movie information.

Free tier endpoints used:
- Movie Search : https://www.omdbapi.com/?apikey=<key>&s=<title>
- Movie Detail : https://www.omdbapi.com/?apikey=<key>&i=<imdb_id>
1,000 requests/day free — no credit card required.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent
from langchain.agents.agent import AgentExecutor
from langchain.tools import tool
from langchain import hub
import os
from dotenv import load_dotenv

load_dotenv()
# Disable LangSmith tracing to suppress API key warning
os.environ["LANGCHAIN_TRACING_V2"] = "false"

api_key       = os.getenv('GEMINI_API_KEY')
model         = os.getenv('GEMINI_MODEL')
OMDB_API_KEY  = os.getenv('OMDB_API_KEY', '91565cbc57')


# ---------------------------------------------------------------------------
# Tool 1 — Search movies by title
# Endpoint: https://www.omdbapi.com/?apikey=<key>&s=<title>
# Returns a list of matching movies with basic info.
# ---------------------------------------------------------------------------
@tool
def search_movies(title: str) -> str:
    """Search for movies by title. Input is a movie title or keyword."""
    try:
        import requests

        url = (
            f"https://www.omdbapi.com/"
            f"?apikey={OMDB_API_KEY}&s={title}&type=movie"
        )
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            if data.get('Response') == 'False':
                return f"No movies found for '{title}'. Reason: {data.get('Error', 'Unknown error')}"

            results     = data.get('Search', [])
            total       = data.get('totalResults', '0')
            search_info = f"Found {total} result(s) for '{title}' (showing first {len(results)}):\n"

            for i, movie in enumerate(results, 1):
                search_info += f"""
#{i}
  Title  : {movie.get('Title', 'N/A')}
  Year   : {movie.get('Year', 'N/A')}
  Type   : {movie.get('Type', 'N/A')}
  IMDB ID: {movie.get('imdbID', 'N/A')}
  Poster : {movie.get('Poster', 'N/A')}
"""
            return search_info.strip()
        else:
            return f"Could not fetch search results. Status: {response.status_code} — {response.text}"

    except Exception as e:
        return f"Error searching movies: {str(e)}"


# ---------------------------------------------------------------------------
# Tool 2 — Get detailed movie info by IMDB ID
# Endpoint: https://www.omdbapi.com/?apikey=<key>&i=<imdb_id>
# Returns full details including plot, cast, ratings, etc.
# ---------------------------------------------------------------------------
@tool
def get_movie_details(imdb_id: str) -> str:
    """Get detailed information about a movie using its IMDB ID (e.g. tt1201607)."""
    try:
        import requests

        url = (
            f"https://www.omdbapi.com/"
            f"?apikey={OMDB_API_KEY}&i={imdb_id}&plot=full"
        )
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            if data.get('Response') == 'False':
                return f"No movie found for IMDB ID '{imdb_id}'. Reason: {data.get('Error', 'Unknown error')}"

            # Format ratings list
            ratings = data.get('Ratings', [])
            ratings_str = "\n".join(
                f"    {r.get('Source', 'N/A')}: {r.get('Value', 'N/A')}"
                for r in ratings
            ) or "    N/A"

            movie_info = f"""
Movie Details — {data.get('Title')} ({data.get('Year')}):
  IMDB ID    : {data.get('imdbID', 'N/A')}
  Type       : {data.get('Type', 'N/A')}
  Rated      : {data.get('Rated', 'N/A')}
  Released   : {data.get('Released', 'N/A')}
  Runtime    : {data.get('Runtime', 'N/A')}
  Genre      : {data.get('Genre', 'N/A')}
  Director   : {data.get('Director', 'N/A')}
  Writer(s)  : {data.get('Writer', 'N/A')}
  Actors     : {data.get('Actors', 'N/A')}
  Language   : {data.get('Language', 'N/A')}
  Country    : {data.get('Country', 'N/A')}
  Awards     : {data.get('Awards', 'N/A')}
  Box Office : {data.get('BoxOffice', 'N/A')}
  IMDB Rating: {data.get('imdbRating', 'N/A')} ({data.get('imdbVotes', 'N/A')} votes)
  Metascore  : {data.get('Metascore', 'N/A')}
  Ratings    :
{ratings_str}
  Plot       : {data.get('Plot', 'N/A')}
  Poster     : {data.get('Poster', 'N/A')}
            """
            return movie_info.strip()
        else:
            return f"Could not fetch movie details. Status: {response.status_code} — {response.text}"

    except Exception as e:
        return f"Error fetching movie details: {str(e)}"


# ---------------------------------------------------------------------------
# Tool 3 — Compare two movies side by side
# Calls the detail endpoint once per IMDB ID.
# ---------------------------------------------------------------------------
@tool
def compare_movies(imdb_ids: str) -> str:
    """Compare two movies side by side. Input is two IMDB IDs separated by a comma, e.g. 'tt1201607,tt0241527'."""
    try:
        import requests

        parts = [mid.strip() for mid in imdb_ids.split(",")]
        if len(parts) != 2:
            return "Please provide exactly two IMDB IDs separated by a comma, e.g. 'tt1201607,tt0241527'"

        movies      = []
        comparison  = "Movie Comparison:\n"

        for imdb_id in parts:
            url = (
                f"https://www.omdbapi.com/"
                f"?apikey={OMDB_API_KEY}&i={imdb_id}&plot=short"
            )
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                if data.get('Response') == 'False':
                    comparison += f"\n{imdb_id}: Not found — {data.get('Error', 'Unknown error')}\n"
                else:
                    movies.append(data)
            else:
                comparison += f"\n{imdb_id}: Failed to fetch (status {response.status_code})\n"

        for movie in movies:
            comparison += f"""
{movie.get('Title')} ({movie.get('Year')}):
  Genre      : {movie.get('Genre', 'N/A')}
  Director   : {movie.get('Director', 'N/A')}
  IMDB Rating: {movie.get('imdbRating', 'N/A')} / 10
  Metascore  : {movie.get('Metascore', 'N/A')}
  Runtime    : {movie.get('Runtime', 'N/A')}
  Box Office : {movie.get('BoxOffice', 'N/A')}
  Awards     : {movie.get('Awards', 'N/A')}
"""
        return comparison.strip()

    except Exception as e:
        return f"Error comparing movies: {str(e)}"


# ---------------------------------------------------------------------------
# LangChain / Gemini agent setup
# ---------------------------------------------------------------------------
llm = ChatGoogleGenerativeAI(
    model=model,
    temperature=0.7,
    google_api_key=api_key
)

tools  = [search_movies, get_movie_details, compare_movies]
prompt = hub.pull("hwchase17/react")

agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

# ---------------------------------------------------------------------------
# Interactive Q&A loop — type 'exit' or 'quit' to stop
# ---------------------------------------------------------------------------
BANNER = """
╔══════════════════════════════════════════════════════╗
║           🎬  Movie Agent — Powered by Gemini        ║
║  Ask anything about movies, or try:                  ║
║    • "Search for Inception"                          ║
║    • "Details for tt1201607"                         ║
║    • "Compare tt1201607 and tt0241527"               ║
║  Type 'exit' or 'quit' to stop.                      ║
╚══════════════════════════════════════════════════════╝
"""

def run_interactive():
    print(BANNER)
    chat_history = []  # keeps (human, ai) pairs for context if needed

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            # Graceful exit on Ctrl+C or piped input ending
            print("\n\n👋  Goodbye! Enjoy the movies.")
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit", "bye", "q"}:
            print("\n👋  Goodbye! Enjoy the movies.")
            break

        print()  # blank line for readability
        try:
            result = executor.invoke({"input": user_input})
            answer = result.get("output", "Sorry, I couldn't process that.")
            print(f"Agent: {answer}")
            chat_history.append((user_input, answer))
        except Exception as e:
            print(f"Agent: ⚠️  Something went wrong — {str(e)}")
        print()  # blank line after each answer


if __name__ == "__main__":
    run_interactive()