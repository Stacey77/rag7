"""Shared tools accessible by all agents."""

from typing import Any

from langchain_core.tools import tool


@tool
def search_web(query: str) -> str:
    """Search the web for information about a topic.

    Args:
        query: The search query string.

    Returns:
        Search results as a formatted string.
    """
    # This is a mock implementation. In production, integrate with
    # a real search API like Tavily, SerpAPI, or Brave Search.
    return f"Search results for: {query}\n\n[Mock search results would appear here]"


@tool
def analyze_text(text: str, analysis_type: str = "sentiment") -> dict[str, Any]:
    """Analyze text for various properties.

    Args:
        text: The text to analyze.
        analysis_type: Type of analysis (sentiment, entities, keywords).

    Returns:
        Analysis results as a dictionary.
    """
    # Mock implementation
    return {
        "analysis_type": analysis_type,
        "input_length": len(text),
        "result": f"Analysis of type '{analysis_type}' completed",
    }


@tool
def summarize_content(content: str, max_length: int = 200) -> str:
    """Summarize content to a specified length.

    Args:
        content: The content to summarize.
        max_length: Maximum length of the summary.

    Returns:
        Summarized content.
    """
    # Mock implementation - in production, this could use an LLM
    if len(content) <= max_length:
        return content
    return content[:max_length] + "..."


@tool
def format_output(content: str, format_type: str = "markdown") -> str:
    """Format content according to specified format type.

    Args:
        content: The content to format.
        format_type: Output format (markdown, html, plain).

    Returns:
        Formatted content.
    """
    if format_type == "markdown":
        return f"## Output\n\n{content}"
    elif format_type == "html":
        return f"<div class='output'><p>{content}</p></div>"
    return content


def get_available_tools() -> list:
    """Get list of all available tools.

    Returns:
        List of tool functions available to agents.
    """
    return [search_web, analyze_text, summarize_content, format_output]
