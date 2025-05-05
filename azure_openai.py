import openai
import os
import re
import logging
from typing import Tuple, Dict

# Setup logging for Azure Monitor integration (stub)
def log_query_to_azure_monitor(prompt, response, usage):
    # Stub: Integrate with Azure Monitor SDK if needed
    logging.info(f"Prompt: {prompt}\nUsage: {usage}")

# Mask PII in prompt (simple example)
def mask_pii(text: str) -> str:
    # Mask emails and phone numbers
    text = re.sub(r"[\w\.-]+@[\w\.-]+", "<EMAIL>", text)
    text = re.sub(r"\b\d{10,}\b", "<PHONE>", text)
    return text

def get_openai_client(api_key, api_base):
    from openai import AzureOpenAI
    return AzureOpenAI(
        api_key=api_key,
        azure_endpoint=api_base,
        api_version="2024-08-01-preview"
    )

def generate_pitch(profile, tone, channel, key, endpoint, deployment, temperature, max_tokens, top_p) -> Tuple[str, Dict]:
    prompt = f"You are a sales assistant. Craft a {tone.lower()} {channel.lower()} pitch for the following customer profile:\n{profile}"
    masked_prompt = mask_pii(prompt)
    client = get_openai_client(key, endpoint)
    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "system", "content": "You are a helpful sales assistant."},
                      {"role": "user", "content": masked_prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
        )
        pitch = response.choices[0].message.content
        usage = response.usage.model_dump() if hasattr(response, 'usage') else {}
        log_query_to_azure_monitor(masked_prompt, pitch, usage)
        return pitch, usage
    except Exception as e:
        err_msg = str(e)
        if "deployment" in err_msg or "model" in err_msg or "authentication" in err_msg or "key" in err_msg:
            raise RuntimeError("Azure OpenAI API error: Please check your deployment name, endpoint, or API key. If you need help, please provide the correct deployment/model or credentials.")
        raise RuntimeError(f"Azure OpenAI API error: {err_msg}")

def summarize_call(transcript, key, endpoint, deployment, temperature, max_tokens, top_p):
    prompt = f"Summarize the following sales call transcript. Highlight key takeaways and analyze sentiment.\nTranscript:\n{transcript}"
    masked_prompt = mask_pii(prompt)
    client = get_openai_client(key, endpoint)
    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "system", "content": "You are a helpful sales assistant."},
                      {"role": "user", "content": masked_prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
        )
        content = response.choices[0].message.content
        sentiment = "Positive" if "positive" in content.lower() else "Neutral"
        highlights = "\n".join([line for line in content.split("\n") if line.strip().startswith("-")])
        summary = content.split("Key Takeaways:")[0].strip() if "Key Takeaways:" in content else content
        usage = response.usage.model_dump() if hasattr(response, 'usage') else {}
        log_query_to_azure_monitor(masked_prompt, content, usage)
        return summary, sentiment, highlights, usage
    except Exception as e:
        err_msg = str(e)
        if "deployment" in err_msg or "model" in err_msg or "authentication" in err_msg or "key" in err_msg:
            raise RuntimeError("Azure OpenAI API error: Please check your deployment name, endpoint, or API key. If you need help, please provide the correct deployment/model or credentials.")
        raise RuntimeError(f"Azure OpenAI API error: {err_msg}")

def estimate_cost(usage):
    # Example: $0.03 per 1K tokens (adjust as needed)
    total_tokens = usage.get('total_tokens', 0)
    return 0.03 * total_tokens / 1000
