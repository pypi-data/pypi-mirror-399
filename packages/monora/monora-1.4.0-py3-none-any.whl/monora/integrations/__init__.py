"""Framework integrations for Monora.

This package provides first-class integrations with popular AI frameworks:
- LangChain (Python)
- OpenAI SDK
- Anthropic SDK
- Vercel AI SDK (coming soon)
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .langchain import MonoraCallbackHandler
    from .openai_sdk import patch_openai
    from .anthropic_sdk import patch_anthropic

__all__ = ["MonoraCallbackHandler", "patch_openai", "patch_anthropic"]
