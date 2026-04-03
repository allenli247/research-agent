import wikipedia
import os

def search_wikipedia(query: str, sentences: int = 15) -> str:
    """
    Searches Wikipedia for a query and returns a detailed summary.
    """
    try:
        results = wikipedia.search(query)
        if not results:
            return f"No results found on Wikipedia for: {query}"
            
        page = wikipedia.page(results[0], auto_suggest=False)
        return f"Title: {page.title}\nContent:\n{wikipedia.summary(results[0], sentences=sentences)}"
    except wikipedia.DisambiguationError as e:
        return f"Query is too broad. Options: {e.options[:5]}"
    except Exception as e:
        return f"Error searching Wikipedia: {str(e)}"

def read_local_text(filepath: str) -> str:
    """
    Reads a local text file and returns its content. Useful for reading existing notes or the research log.
    """
    if not os.path.exists(filepath):
        return f"File not found: {filepath}"
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {filepath}: {str(e)}"

def write_markdown(filepath: str, content: str, mode: str = 'w') -> str:
    """
    Writes or appends markdown content to a local file.
    Use mode 'w' to overwrite, and 'a' to append.
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, mode, encoding='utf-8') as f:
            f.write(content)
            if mode == 'a':
                f.write("\n")
        action = "Appended to" if mode == 'a' else "Wrote to"
        return f"{action} successful: {filepath}"
    except Exception as e:
        return f"Error writing to {filepath}: {str(e)}"

def send_email_mock(subject: str, summary: str) -> str:
    """
    Mocks sending an email by beautifully printing it to the terminal.
    """
    border = "=" * 50
    print(f"\n{border}")
    print(f"📧 MOCK EMAIL DEPLOYMENT")
    print(border)
    print(f"SUBJECT: {subject}")
    print("-" * 50)
    print(f"{summary}")
    print(f"{border}\n")
    return "Email successfully sent (Mocked)."
