"""
Native web search implementation for OpenAI and Anthropic.
Uses the default LLM from ara_config to determine which provider to use.
Includes source citations at the end of search results.

OpenAI API Compatibility:
- Responses API: Uses `web_search` tool with models like gpt-5, o4-mini
- Chat Completions: Uses specialized models gpt-5-search-api, gpt-4o-search-preview
"""
import os
from typing import Generator, Tuple, Optional, List, Dict

from ara_cli.prompt_handler import LLMSingleton
from ara_cli.error_handler import AraError


# OpenAI models that support web search via Responses API
OPENAI_RESPONSES_API_MODELS = [
    "gpt-5", "gpt-5.1", "gpt-5.2", "o3", "o4-mini",
    "openai/gpt-5", "openai/gpt-5.1", "openai/gpt-5.2", "openai/o3", "openai/o4-mini",
]

# OpenAI models that use Chat Completions API with built-in search
OPENAI_CHAT_COMPLETIONS_SEARCH_MODELS = [
    "gpt-5-search-api", "gpt-4o-search-preview", "gpt-4o-mini-search-preview",
    "openai/gpt-5-search-api", "openai/gpt-4o-search-preview", "openai/gpt-4o-mini-search-preview",
]

OPENAI_WEB_SEARCH_MODELS = OPENAI_RESPONSES_API_MODELS + \
    OPENAI_CHAT_COMPLETIONS_SEARCH_MODELS

ANTHROPIC_WEB_SEARCH_MODELS = [
    "claude-sonnet-4-5-20250929", "claude-sonnet-4-20250514",
    "claude-haiku-4-5-20251001", "claude-3-5-haiku-latest",
    "claude-opus-4-5-20251101", "claude-opus-4-1-20250805", "claude-opus-4-20250514",
    "anthropic/claude-sonnet-4-5-20250929", "anthropic/claude-sonnet-4-20250514",
    "anthropic/claude-haiku-4-5-20251001",
    "anthropic/claude-3-5-haiku-latest", "anthropic/claude-opus-4-5-20251101",
    "anthropic/claude-opus-4-1-20250805", "anthropic/claude-opus-4-20250514",
]


def is_web_search_supported(model: str) -> Tuple[bool, Optional[str]]:
    """Check if the model supports web search and return the provider."""
    if model in OPENAI_WEB_SEARCH_MODELS:
        return True, "openai"
    if model in ANTHROPIC_WEB_SEARCH_MODELS:
        return True, "anthropic"
    return False, None


def get_supported_models_message(model: str) -> str:
    """Return a message listing all supported web search models."""
    return (
        f"Web search is not supported by the current default model: {model}\n"
        "Please choose one of the following models:\n"
        "==OpenAI (Responses API)==\n"
        "\tgpt-5, gpt-5.1, gpt-5.2, o3, o4-mini\n"
        "==OpenAI (Chat Completions)==\n"
        "\tgpt-5-search-api, gpt-4o-search-preview, gpt-4o-mini-search-preview\n"
        "==Anthropic==\n"
        "\tclaude-sonnet-4-5-20250929, claude-sonnet-4-20250514\n"
        "\tclaude-haiku-4-5-20251001, claude-3-5-haiku-latest\n"
        "\tclaude-opus-4-5-20251101, claude-opus-4-1-20250805, claude-opus-4-20250514\n"
        "\nNote: Models can be prefixed with 'openai/' or 'anthropic/' for LiteLLM format.\n"
    )


def _get_raw_model_name(model: str) -> str:
    """Strip provider prefix from model name if present."""
    for prefix in ("openai/", "anthropic/"):
        if model.startswith(prefix):
            return model[len(prefix):]
    return model


def _deduplicate_citations(citations: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Remove duplicate citations by URL, preserving order."""
    seen_urls = set()
    unique = []
    for citation in citations:
        url = citation.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique.append(citation)
    return unique


def _format_citations(citations: List[Dict[str, str]]) -> str:
    """Format a list of citations into a markdown string."""
    unique_citations = _deduplicate_citations(citations)
    if not unique_citations:
        return ""

    lines = ["\n\n---\n**Sources:**"]
    for i, citation in enumerate(unique_citations, 1):
        title = citation.get("title", "Untitled")
        url = citation.get("url", "")
        line = f"{i}. [{title}]({url})" if url else f"{i}. {title}"
        lines.append(line)

    return "\n".join(lines) + "\n"


# Mock classes for litellm response format compatibility
class _MockDelta:
    def __init__(self, content: str):
        self.content = content


class _MockChoice:
    def __init__(self, content: str):
        self.delta = _MockDelta(content)


class _MockChunk:
    def __init__(self, content: str):
        self.choices = [_MockChoice(content)]


def _create_chunk(content: str) -> _MockChunk:
    """Create a mock chunk that matches litellm response format."""
    return _MockChunk(content)


def _extract_openai_citations(response) -> List[Dict[str, str]]:
    """Extract citations from OpenAI Responses API response."""
    citations = []
    output = getattr(response, 'output', None)
    if not output:
        return citations

    for output_item in output:
        if getattr(output_item, 'type', None) != 'message':
            continue
        content = getattr(output_item, 'content', [])
        for content_item in content:
            annotations = getattr(content_item, 'annotations', [])
            for annotation in annotations:
                if getattr(annotation, 'type', None) == 'url_citation':
                    citations.append({
                        "title": getattr(annotation, 'title', 'Source'),
                        "url": getattr(annotation, 'url', ''),
                    })
    return citations


def _perform_openai_chat_completions_search(client, raw_model: str, query: str) -> Generator:
    """Perform web search using Chat Completions API."""
    response = client.chat.completions.create(
        model=raw_model,
        messages=[{"role": "user", "content": query}],
        stream=True,
    )
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            yield _create_chunk(chunk.choices[0].delta.content)


def _perform_openai_responses_api_search(client, raw_model: str, query: str) -> Generator:
    """Perform web search using Responses API with web_search tool."""
    response = client.responses.create(
        model=raw_model,
        tools=[{"type": "web_search"}],
        input=query,
    )

    output_text = getattr(response, 'output_text', None)
    if output_text:
        yield _create_chunk(output_text)

    citations = _extract_openai_citations(response)
    citations_text = _format_citations(citations)
    if citations_text:
        yield _create_chunk(citations_text)


def perform_openai_web_search(query: str, model: str) -> Generator:
    """Perform web search using OpenAI's API."""
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    raw_model = _get_raw_model_name(model)

    if model in OPENAI_CHAT_COMPLETIONS_SEARCH_MODELS:
        yield from _perform_openai_chat_completions_search(client, raw_model, query)
    else:
        yield from _perform_openai_responses_api_search(client, raw_model, query)


def _extract_anthropic_text_citations(content_block) -> List[Dict[str, str]]:
    """Extract citations from Anthropic text block."""
    citations = []
    block_citations = getattr(content_block, 'citations', None)
    if not block_citations:
        return citations

    for citation in block_citations:
        if hasattr(citation, 'url'):
            citations.append({
                "title": getattr(citation, 'title', 'Source'),
                "url": citation.url,
            })
    return citations


def _extract_anthropic_search_results(content_block) -> List[Dict[str, str]]:
    """Extract citations from Anthropic web search tool result."""
    citations = []
    content = getattr(content_block, 'content', [])

    for result in content:
        if getattr(result, 'type', None) == "web_search_result":
            citations.append({
                "title": getattr(result, 'title', 'Source'),
                "url": getattr(result, 'url', ''),
            })
    return citations


def perform_anthropic_web_search(query: str, model: str) -> Generator:
    """Perform web search using Anthropic's Messages API."""
    import anthropic

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    raw_model = _get_raw_model_name(model)
    citations = []

    response = client.messages.create(
        model=raw_model,
        max_tokens=4096,
        tools=[{"type": "web_search_20250305",
                "name": "web_search", "max_uses": 5}],
        messages=[{"role": "user", "content": query}],
    )

    for content_block in response.content:
        if content_block.type == "text":
            yield _create_chunk(content_block.text)
            citations.extend(_extract_anthropic_text_citations(content_block))
        elif content_block.type == "web_search_tool_result":
            citations.extend(_extract_anthropic_search_results(content_block))

    citations_text = _format_citations(citations)
    if citations_text:
        yield _create_chunk(citations_text)


def perform_web_search_completion(query: str) -> Generator:
    """Performs a web search using the appropriate provider based on default LLM."""
    chat_instance = LLMSingleton.get_instance()
    config_parameters = chat_instance.get_config_by_purpose("default")
    model = config_parameters.get("model")

    is_supported, provider = is_web_search_supported(model)

    if not is_supported:
        raise AraError(get_supported_models_message(model))

    if provider == "openai":
        yield from perform_openai_web_search(query, model)
    elif provider == "anthropic":
        yield from perform_anthropic_web_search(query, model)
