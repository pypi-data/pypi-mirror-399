"""
mem1 基础用法示例

演示：
- 初始化 Mem1Memory
- 添加对话
- 更新用户画像
- 获取记忆上下文
- 搜索图片
"""
import os
import logging
from dotenv import load_dotenv

from mem1 import Mem1Memory, Mem1Config, LLMConfig

load_dotenv()
logging.basicConfig(level=logging.INFO)

# 配置
config = Mem1Config(
    llm=LLMConfig(
        model="deepseek-chat",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com"
    )
)
config.memory.auto_update_profile = False  # 手动控制画像更新

USER_ID = "demo_user"


def main():
    memory = Mem1Memory(config)
    
    # 1. 添加对话
    print("\n=== 添加对话 ===")
    memory.add_conversation(
        user_id=USER_ID,
        messages=[
            {"role": "user", "content": "你好，我是张明，在北京工作。"},
            {"role": "assistant", "content": "你好张明！很高兴认识你。"}
        ],
        metadata={"topic": "自我介绍"}
    )
    
    memory.add_conversation(
        user_id=USER_ID,
        messages=[
            {"role": "user", "content": "我喜欢简洁的报告风格，不要太多废话。"},
            {"role": "assistant", "content": "明白，以后会保持简洁。"}
        ],
        metadata={"topic": "偏好设置"}
    )
    print("✓ 已添加 2 条对话")
    
    # 2. 更新画像
    print("\n=== 更新画像 ===")
    result = memory.update_profile(USER_ID)
    print(f"✓ 画像已更新，长度: {result.get('length', 0)} 字符")
    
    # 3. 获取上下文
    print("\n=== 获取上下文 ===")
    ctx = memory.get_context(user_id=USER_ID, query="帮我写个报告")
    print(f"当前时间: {ctx['current_time']}")
    print(f"需要历史: {ctx['need_history']}")
    print(f"画像内容:\n{ctx['import_content'][:500]}...")
    
    # 4. 查询对话
    print("\n=== 查询对话 ===")
    conversations = memory.get_conversations(USER_ID)
    print(f"✓ 共 {len(conversations)} 条对话")
    
    # 5. 清理（可选）
    # memory.delete_user(USER_ID)


if __name__ == "__main__":
    main()
