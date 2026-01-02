"""Example vulnerable code for testing Bastion.

This file contains intentional security vulnerabilities for demonstration purposes.
DO NOT use these patterns in production code!
"""

import openai


# PS001: User input directly concatenated into prompt
def vulnerable_concat(user_input: str) -> str:
    prompt = "You are a helpful assistant. User says: " + user_input
    return prompt


# PS002: User input in f-string prompt template
def vulnerable_fstring(user_message: str) -> str:
    prompt = f"You are a helpful assistant. Respond to: {user_message}"
    return prompt


# PS003: Hardcoded API key
def vulnerable_hardcoded_key():
    # This is a fake key for demonstration
    api_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz1234567890ab"
    client = openai.OpenAI(api_key=api_key)
    return client


# PS004: User input in system prompt
def vulnerable_system_prompt(user_input: str):
    messages = [
        {"role": "system", "content": f"You are an assistant. Context: {user_input}"},
        {"role": "user", "content": "Hello"},
    ]
    return messages


# PS008: Unsafe .format() on prompt string
def vulnerable_format(query: str) -> str:
    prompt_template = "You are a helpful assistant. Answer this: {}"
    prompt = prompt_template.format(query)
    return prompt


# PS015: Sensitive data in LLM context
def vulnerable_sensitive_data(password: str, user_query: str):
    # Bad: Including password in LLM context
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": f"User password is {password}. Query: {user_query}"}
        ]
    )
    return response


# SAFE PATTERNS - These should NOT trigger alerts

def safe_static_prompt() -> str:
    """Safe: Static prompt with no user input."""
    prompt = "You are a helpful assistant. How can I help you today?"
    return prompt


def safe_parameterized(user_input: str):
    """Safe: User input properly separated in user role."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_input},  # User input in user role is OK
    ]
    return messages


def safe_validated_input(user_input: str):
    """Safe: Input is validated before use."""
    # bastion: ignore[PS001]
    # Validated input - this suppression is intentional
    sanitized = user_input[:100].strip()
    prompt = "Respond to: " + sanitized
    return prompt
