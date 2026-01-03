"""
When you install and import this library, it will automatically hook
ollama.chat, ollama.generate, and ollama.embed using wrapt, and log token usage after
each request. You can customize or extend this logging logic later
to add user or organization metadata for metering purposes.
"""
from .middleware import chat_wrapper, generate_wrapper, embed_wrapper