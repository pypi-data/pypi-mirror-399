"""LLM 客户端"""
from typing import List, Dict
from openai import OpenAI
from mem1.config import LLMConfig


class LLMClient:
    """LLM 客户端（基于 OpenAI 兼容 API）"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        response_format: str = "text"
    ) -> str:
        """
        生成响应
        
        Args:
            messages: [{"role": "system", "content": "..."}, ...]
            response_format: "text" 或 "json"
        
        Returns:
            响应文本
        """
        kwargs = {
            "model": self.config.model,
            "messages": messages,
            "temperature": 0.7,
        }
        
        if response_format == "json":
            kwargs["response_format"] = {"type": "json_object"}
        
        response = self.client.chat.completions.create(**kwargs)
        
        return response.choices[0].message.content
