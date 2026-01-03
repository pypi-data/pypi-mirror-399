"""
mem1 图片功能示例

演示：
- 添加带图片的对话
- 搜索图片
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

from mem1 import Mem1Memory, Mem1Config, LLMConfig

load_dotenv()
logging.basicConfig(level=logging.INFO)

config = Mem1Config(
    llm=LLMConfig(
        model="deepseek-chat",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com"
    )
)
config.memory.auto_update_profile = False

USER_ID = "image_demo_user"
# 示例图片路径（替换为实际路径）
SAMPLE_IMAGE = Path(__file__).parent / "天价麻花.png"


def main():
    memory = Mem1Memory(config)
    
    # 1. 添加带图片的对话
    print("=== 添加带图片的对话 ===")
    
    if SAMPLE_IMAGE.exists():
        memory.add_conversation(
            user_id=USER_ID,
            messages=[
                {"role": "user", "content": "这是一个舆情截图，广东江门'天价麻花'事件，你看看需要关注吗？"},
                {"role": "assistant", "content": "收到截图。这是消费维权类舆情，建议关注是否持续发酵。"}
            ],
            images=[{"filename": "天价麻花.png", "path": str(SAMPLE_IMAGE)}],
            metadata={"topic": "舆情分析", "event_type": "消费维权"}
        )
        print("✓ 已添加带图片的对话")
    else:
        print(f"⚠️ 示例图片不存在: {SAMPLE_IMAGE}")
        print("  请将图片放到 examples/ 目录下")
        return
    
    # 2. 搜索图片
    print("\n=== 搜索图片 ===")
    
    keywords = ["麻花", "天价", "舆情"]
    for keyword in keywords:
        results = memory.search_images(user_id=USER_ID, query=keyword)
        print(f"  搜索 '{keyword}': 找到 {len(results)} 张")
        for img in results:
            print(f"    - {img['filename']}: {img['description'][:50]}...")


if __name__ == "__main__":
    main()
