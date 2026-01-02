"""AI diagnostic agent using LiteLLM."""

from __future__ import annotations

import os
from typing import Optional

from netspecs.agent.prompts import ANALYST_SYSTEM_PROMPT, format_results_for_analysis
from netspecs.utils.config import DEFAULT_MODEL


def generate_diagnostic_report(
    results: dict,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
    custom_prompt: Optional[str] = None,
) -> str:
    """
    Generate a narrative diagnostic report from test results using an LLM.
    
    This function uses LiteLLM to support multiple LLM providers (OpenAI, Anthropic,
    Ollama, etc.) with a unified interface.
    
    Args:
        results: Dictionary of test results from netspecs diagnostics
        model: LLM model to use (default: gpt-5.2)
                Examples:
                - "gpt-5.2" (OpenAI)
                - "gpt-4o" (OpenAI)
                - "claude-3-sonnet-20240229" (Anthropic)
                - "ollama/llama2" (Ollama local)
        api_key: API key for the LLM provider (optional, will use env vars if not provided)
        custom_prompt: Optional custom system prompt to override the default
        
    Returns:
        Narrative diagnostic report as a string
        
    Raises:
        ValueError: If no API key is available
        Exception: If the LLM call fails
    """
    try:
        from litellm import completion
    except ImportError:
        raise ImportError(
            "LiteLLM is required for AI reports. "
            "Install it with: pip install litellm"
        )
    
    # Set API key if provided
    if api_key:
        # LiteLLM uses environment variables for API keys
        # Set the appropriate one based on the model
        if model.startswith("gpt") or model.startswith("o1"):
            os.environ["OPENAI_API_KEY"] = api_key
        elif model.startswith("claude"):
            os.environ["ANTHROPIC_API_KEY"] = api_key
        else:
            # Generic fallback
            os.environ["OPENAI_API_KEY"] = api_key
    
    # Format results for analysis
    user_message = format_results_for_analysis(results)
    
    # Use custom prompt if provided, otherwise use default
    system_prompt = custom_prompt if custom_prompt else ANALYST_SYSTEM_PROMPT
    
    # GPT-5 models only support temperature=1
    temperature = 1.0 if model.startswith("gpt-5") else 0.7
    
    # Call the LLM
    response = completion(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=temperature,
        max_tokens=2000,
    )
    
    return response.choices[0].message.content


async def generate_diagnostic_report_async(
    results: dict,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
) -> str:
    """
    Async version of generate_diagnostic_report.
    
    Args:
        results: Dictionary of test results from netspecs diagnostics
        model: LLM model to use
        api_key: API key for the LLM provider
        
    Returns:
        Narrative diagnostic report as a string
    """
    try:
        from litellm import acompletion
    except ImportError:
        raise ImportError(
            "LiteLLM is required for AI reports. "
            "Install it with: pip install litellm"
        )
    
    # Set API key if provided
    if api_key:
        if model.startswith("gpt") or model.startswith("o1"):
            os.environ["OPENAI_API_KEY"] = api_key
        elif model.startswith("claude"):
            os.environ["ANTHROPIC_API_KEY"] = api_key
        else:
            os.environ["OPENAI_API_KEY"] = api_key
    
    # Format results for analysis
    user_message = format_results_for_analysis(results)
    
    # GPT-5 models only support temperature=1
    temperature = 1.0 if model.startswith("gpt-5") else 0.7
    
    # Call the LLM asynchronously
    response = await acompletion(
        model=model,
        messages=[
            {"role": "system", "content": ANALYST_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=temperature,
        max_tokens=2000,
    )
    
    return response.choices[0].message.content

