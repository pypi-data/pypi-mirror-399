"""Example vulnerable LangChain code for testing Bastion.

This file contains intentional security vulnerabilities for demonstration purposes.
DO NOT use these patterns in production code!
"""

from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_openai import ChatOpenAI


# PS007: Unsafe string concatenation in LangChain prompt
def vulnerable_langchain_concat(user_input: str):
    template = "You are helpful. " + user_input + " Please respond."
    prompt = PromptTemplate.from_template(template)
    return prompt


# PS007: User input directly in template string
def vulnerable_langchain_template(user_query: str):
    # Bad: User input directly in template
    template = f"Answer this question: {user_query}"
    prompt = PromptTemplate.from_template(template)
    return prompt


# PS004: System message with user input (LangChain)
def vulnerable_system_message(user_context: str):
    from langchain.schema import SystemMessage, HumanMessage

    messages = [
        SystemMessage(content=f"You are an assistant. User context: {user_context}"),
        HumanMessage(content="Hello"),
    ]
    return messages


# SAFE PATTERNS

def safe_langchain_parameterized(user_input: str):
    """Safe: User input passed as parameter."""
    template = "Answer this question: {question}"
    prompt = PromptTemplate.from_template(template)
    formatted = prompt.format(question=user_input)
    return formatted


def safe_langchain_chat():
    """Safe: Static prompts with proper structure."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        ("human", "{input}"),  # Placeholder is safe
    ])
    return prompt
