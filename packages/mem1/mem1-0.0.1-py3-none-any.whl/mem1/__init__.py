"""
Mem1 - 基于 Elasticsearch 的用户记忆系统
"""

__version__ = "0.1.0"

from mem1.memory_es import Mem1Memory
from mem1.config import Mem1Config, LLMConfig

__all__ = ["Mem1Memory", "Mem1Config", "LLMConfig"]
