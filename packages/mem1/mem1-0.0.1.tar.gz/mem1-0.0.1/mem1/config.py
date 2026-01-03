"""配置管理"""
import os
from typing import Optional
from pydantic import BaseModel


class LLMConfig(BaseModel):
    """LLM 配置"""
    provider: str = "openai"  # openai/deepseek/qwen
    model: str = "deepseek-chat"
    api_key: str
    base_url: Optional[str] = None


class MemoryConfig(BaseModel):
    """记忆系统配置"""
    memory_dir: str = "./memories"
    auto_update_profile: bool = True
    max_profile_chars: int = 3000
    # 画像更新触发条件（满足任一即触发）
    update_interval_rounds: int = 5      # 每 N 轮对话触发更新
    update_interval_minutes: int = 3     # 距上次更新超过 M 分钟触发


class ESConfig(BaseModel):
    """Elasticsearch 配置"""
    hosts: list[str] = ["http://localhost:9200"]
    index_name: str = "conversation_history"


class ImagesConfig(BaseModel):
    """图片存储配置"""
    images_dir: str = "./memories/images"


class Mem1Config(BaseModel):
    """Mem1 总配置"""
    llm: LLMConfig
    memory: MemoryConfig = MemoryConfig()
    es: ESConfig = ESConfig()
    images: ImagesConfig = ImagesConfig()
    
    @classmethod
    def from_env(cls) -> "Mem1Config":
        """从环境变量加载配置"""
        # ES hosts 支持逗号分隔的多个地址
        es_hosts_str = os.getenv("MEM1_ES_HOSTS", "http://localhost:9200")
        es_hosts = [h.strip() for h in es_hosts_str.split(",")]
        
        return cls(
            llm=LLMConfig(
                provider="openai",
                model="deepseek-chat",
                api_key=os.getenv("DEEPSEEK_API_KEY", ""),
                base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
            ),
            memory=MemoryConfig(
                memory_dir=os.getenv("MEM1_MEMORY_DIR", "./memories"),
                auto_update_profile=os.getenv("MEM1_AUTO_UPDATE_PROFILE", "true").lower() == "true",
                max_profile_chars=int(os.getenv("MEM1_MAX_PROFILE_CHARS", "3000")),
                update_interval_rounds=int(os.getenv("MEM1_UPDATE_INTERVAL_ROUNDS", "5")),
                update_interval_minutes=int(os.getenv("MEM1_UPDATE_INTERVAL_MINUTES", "3"))
            ),
            es=ESConfig(
                hosts=es_hosts,
                index_name=os.getenv("MEM1_ES_INDEX", "conversation_history")
            ),
            images=ImagesConfig(
                images_dir=os.getenv("MEM1_IMAGES_DIR", "./memories/images")
            )
        )
