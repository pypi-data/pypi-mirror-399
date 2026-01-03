"""KV cache implementations.

Two backends:
- PagedKVCache: vLLM-style block allocation with hash-based prefix caching
- RadixKVCache: SGLang-style prefix tree (TODO)
"""

from wafer_core.rollouts.inference.cache.paged import Block, PagedKVCache
from wafer_core.rollouts.inference.cache.protocol import KVCacheManager
from wafer_core.rollouts.inference.cache.radix import RadixKVCache

__all__ = ["PagedKVCache", "RadixKVCache", "Block", "KVCacheManager"]
