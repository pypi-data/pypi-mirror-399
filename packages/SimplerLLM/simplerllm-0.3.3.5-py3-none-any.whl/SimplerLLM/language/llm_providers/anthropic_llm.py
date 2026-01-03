from typing import Dict, Optional
import os
from dotenv import load_dotenv
import time
from anthropic import Anthropic, AsyncAnthropic
from .llm_response_models import LLMFullResponse

# Load environment variables
load_dotenv(override=True)

# Constants
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", 2))


def generate_response(
    model_name: str,
    system_prompt: str = "You are a helpful AI Assistant",
    messages=None,
    temperature: float = 0.7,
    max_tokens: int = 300,
    top_p: float = 1.0,
    full_response: bool = False,
    prompt_caching: bool = False,
    cached_input: str = "",
    cache_control_type: str = "ephemeral",
    api_key=None,
    json_mode=False,
) -> Optional[Dict]:
    """
    Generate a response using the Anthropic API via the official SDK.

    Args:
        model_name: The model to use (e.g., 'claude-sonnet-4-5-20250514')
        system_prompt: The system prompt
        messages: List of message dictionaries
        temperature: Sampling temperature (0-1)
        max_tokens: Maximum tokens for the response
        top_p: Nucleus sampling parameter
        full_response: If True, returns LLMFullResponse
        prompt_caching: Enable prompt caching
        cached_input: Cached input text
        cache_control_type: Cache control type (ephemeral or persistent)
        api_key: Anthropic API key
        json_mode: Flag for JSON mode (handled via prompt engineering)

    Returns:
        str or LLMFullResponse: Generated text or full response
    """
    start_time = time.time()

    client = Anthropic(api_key=api_key)

    # Build system parameter
    if prompt_caching:
        system = [
            {"type": "text", "text": system_prompt},
            {"type": "text", "text": cached_input, "cache_control": {"type": cache_control_type}}
        ]
    else:
        system = system_prompt

    # Build extra headers for caching
    extra_headers = {}
    if prompt_caching:
        extra_headers["anthropic-beta"] = "prompt-caching-2024-07-31"

    # Note: Anthropic doesn't allow both temperature and top_p together
    # We use temperature only (more common parameter)
    response = client.messages.create(
        model=model_name,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
        temperature=temperature,
        extra_headers=extra_headers if extra_headers else None,
    )

    if full_response:
        return LLMFullResponse(
            generated_text=response.content[0].text,
            model=model_name,
            process_time=time.time() - start_time,
            input_token_count=response.usage.input_tokens,
            output_token_count=response.usage.output_tokens,
            llm_provider_response=response,
        )
    return response.content[0].text


async def generate_response_async(
    model_name: str,
    system_prompt: str = "You are a helpful AI Assistant",
    messages=None,
    temperature: float = 0.7,
    max_tokens: int = 300,
    top_p: float = 1.0,
    full_response: bool = False,
    prompt_caching: bool = False,
    cached_input: str = "",
    cache_control_type: str = "ephemeral",
    api_key=None,
    json_mode=False,
) -> Optional[Dict]:
    """
    Asynchronously generate a response using the Anthropic API via the official SDK.

    Args:
        model_name: The model to use (e.g., 'claude-sonnet-4-5-20250514')
        system_prompt: The system prompt
        messages: List of message dictionaries
        temperature: Sampling temperature (0-1)
        max_tokens: Maximum tokens for the response
        top_p: Nucleus sampling parameter
        full_response: If True, returns LLMFullResponse
        prompt_caching: Enable prompt caching
        cached_input: Cached input text
        cache_control_type: Cache control type (ephemeral or persistent)
        api_key: Anthropic API key
        json_mode: Flag for JSON mode (handled via prompt engineering)

    Returns:
        str or LLMFullResponse: Generated text or full response
    """
    start_time = time.time()

    client = AsyncAnthropic(api_key=api_key)

    # Build system parameter
    if prompt_caching:
        system = [
            {"type": "text", "text": system_prompt},
            {"type": "text", "text": cached_input, "cache_control": {"type": cache_control_type}}
        ]
    else:
        system = system_prompt

    # Build extra headers for caching
    extra_headers = {}
    if prompt_caching:
        extra_headers["anthropic-beta"] = "prompt-caching-2024-07-31"

    # Note: Anthropic doesn't allow both temperature and top_p together
    # We use temperature only (more common parameter)
    response = await client.messages.create(
        model=model_name,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
        temperature=temperature,
        extra_headers=extra_headers if extra_headers else None,
    )

    if full_response:
        return LLMFullResponse(
            generated_text=response.content[0].text,
            model=model_name,
            process_time=time.time() - start_time,
            input_token_count=response.usage.input_tokens,
            output_token_count=response.usage.output_tokens,
            llm_provider_response=response,
        )
    return response.content[0].text


def generate_response_with_web_search(
    model_name: str,
    system_prompt: str = "You are a helpful AI Assistant",
    messages=None,
    max_tokens: int = 300,
    full_response: bool = False,
    api_key=None,
) -> Optional[Dict]:
    """
    Generate a response using Anthropic's Messages API with web search enabled.

    Args:
        model_name: The model to use (e.g., 'claude-sonnet-4-5-20250514')
        system_prompt: The system prompt
        messages: List of message dictionaries
        max_tokens: Maximum tokens for the response
        full_response: If True, returns LLMFullResponse with web_sources
        api_key: Anthropic API key

    Returns:
        str or LLMFullResponse: Generated text or full response with web sources
    """
    start_time = time.time() if full_response else None

    client = Anthropic(api_key=api_key)

    response = client.messages.create(
        model=model_name,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=messages,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 5
        }]
    )

    # Extract text and citations from response content
    generated_text = ""
    web_sources = []

    for content_block in response.content:
        if content_block.type == "text":
            generated_text += content_block.text
            # Extract citations if present
            if hasattr(content_block, 'citations') and content_block.citations:
                for citation in content_block.citations:
                    if hasattr(citation, 'type') and citation.type == "web_search_result_location":
                        web_sources.append({
                            "title": getattr(citation, 'title', ''),
                            "url": getattr(citation, 'url', ''),
                            "cited_text": getattr(citation, 'cited_text', ''),
                        })

    if full_response:
        return LLMFullResponse(
            generated_text=generated_text,
            model=model_name,
            process_time=time.time() - start_time,
            input_token_count=response.usage.input_tokens,
            output_token_count=response.usage.output_tokens,
            llm_provider_response=response,
            web_sources=web_sources if web_sources else None,
        )
    return generated_text


async def generate_response_with_web_search_async(
    model_name: str,
    system_prompt: str = "You are a helpful AI Assistant",
    messages=None,
    max_tokens: int = 300,
    full_response: bool = False,
    api_key=None,
) -> Optional[Dict]:
    """
    Asynchronously generate a response using Anthropic's Messages API with web search enabled.

    Args:
        model_name: The model to use (e.g., 'claude-sonnet-4-5-20250514')
        system_prompt: The system prompt
        messages: List of message dictionaries
        max_tokens: Maximum tokens for the response
        full_response: If True, returns LLMFullResponse with web_sources
        api_key: Anthropic API key

    Returns:
        str or LLMFullResponse: Generated text or full response with web sources
    """
    start_time = time.time() if full_response else None

    client = AsyncAnthropic(api_key=api_key)

    response = await client.messages.create(
        model=model_name,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=messages,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 5
        }]
    )

    # Extract text and citations from response content
    generated_text = ""
    web_sources = []

    for content_block in response.content:
        if content_block.type == "text":
            generated_text += content_block.text
            # Extract citations if present
            if hasattr(content_block, 'citations') and content_block.citations:
                for citation in content_block.citations:
                    if hasattr(citation, 'type') and citation.type == "web_search_result_location":
                        web_sources.append({
                            "title": getattr(citation, 'title', ''),
                            "url": getattr(citation, 'url', ''),
                            "cited_text": getattr(citation, 'cited_text', ''),
                        })

    if full_response:
        return LLMFullResponse(
            generated_text=generated_text,
            model=model_name,
            process_time=time.time() - start_time,
            input_token_count=response.usage.input_tokens,
            output_token_count=response.usage.output_tokens,
            llm_provider_response=response,
            web_sources=web_sources if web_sources else None,
        )
    return generated_text
