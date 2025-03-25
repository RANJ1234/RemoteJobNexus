import trafilatura
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_website_text_content(url: str) -> str:
    """
    This function takes a url and returns the main text content of the website.
    The text content is extracted using trafilatura and easier to understand.
    The results is not directly readable, better to be summarized by LLM before consume
    by the user.

    Some common website to crawl information from:
    MLB scores: https://www.mlb.com/scores/YYYY-MM-DD
    """
    try:
        # Send a request to the website
        logger.info(f"Fetching content from URL: {url}")
        downloaded = trafilatura.fetch_url(url)
        
        if not downloaded:
            logger.warning(f"Failed to download content from {url}")
            return f"Failed to download content from {url}. Please check the URL and try again."
        
        # Extract the main text content
        text = trafilatura.extract(downloaded)
        
        if not text:
            logger.warning(f"No text content extracted from {url}")
            return f"No text content could be extracted from {url}. The page might not contain enough text content or may be protected."
        
        logger.info(f"Successfully extracted {len(text)} characters from {url}")
        return text
    
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {str(e)}")
        return f"Error extracting content: {str(e)}"


def summarize_webpage(url: str) -> dict:
    """
    Extract and organize content from a webpage into a structured format.
    Returns a dictionary with title, main content, and metadata.
    """
    try:
        # Fetch the URL
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return {"error": f"Failed to download content from {url}"}
        
        # Extract text with metadata using trafilatura
        result = trafilatura.extract(downloaded, output_format="json", include_metadata=True)
        if not result:
            return {"error": f"Failed to extract content from {url}"}
        
        # Parse the JSON result
        import json
        data = json.loads(result)
        
        # Organize the extracted data
        summary = {
            "title": data.get("title", "Untitled Page"),
            "text": data.get("text", "No content extracted"),
            "author": data.get("author", "Unknown"),
            "date": data.get("date", "Unknown"),
            "hostname": data.get("hostname", url),
            "categories": data.get("categories", []),
            "tags": data.get("tags", [])
        }
        
        return summary
    
    except Exception as e:
        logger.error(f"Error summarizing content from {url}: {str(e)}")
        return {"error": f"Error summarizing content: {str(e)}"}


if __name__ == "__main__":
    # Example usage
    test_url = "https://www.example.com"
    content = get_website_text_content(test_url)
    print(f"Extracted {len(content)} characters of content")
    print(content[:300] + "..." if len(content) > 300 else content)