"""CausalTransformerModel implementation for PyGPUkit.

This module re-exports from llm/models/ for backwards compatibility.
See llm/models/causal.py for the actual implementation.
"""

from __future__ import annotations

# Re-export everything from models/
from pygpukit.llm.models.causal import (
    CausalSelfAttention,
    CausalTransformerModel,
    GPT2Model,
    LayerNorm,
    LlamaAttention,
    LlamaBlock,
    LlamaMLP,
    LlamaModel,
    RMSNorm,
)

__all__ = [
    # Primary model class
    "CausalTransformerModel",
    # Architecture aliases
    "GPT2Model",
    "LlamaModel",
    # Legacy aliases
    "RMSNorm",
    "LayerNorm",
    "LlamaAttention",
    "LlamaMLP",
    "LlamaBlock",
    "CausalSelfAttention",
]
