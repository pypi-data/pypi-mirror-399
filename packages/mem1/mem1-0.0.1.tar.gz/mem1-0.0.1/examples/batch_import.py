"""
批量导入对话数据示例

用于测试或迁移历史数据
"""
import os
import logging
from datetime import datetime, timedelta
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

USER_ID = "batch_demo_user"

# 示例数据
SAMPLE_CONVERSATIONS = [
    ("基本信息", [
        {"role": "user", "content": "你好，我是北京市网信办的张明，负责舆情监测。"},
        {"role": "assistant", "content": "张明您好！"}
    ], {"topic": "自我介绍"}),
    
    ("偏好设置", [
        {"role": "user", "content": "报告要简洁，图表多一些。"},
        {"role": "assistant", "content": "明白了。"}
    ], {"topic": "偏好设置"}),
    
    ("工作要求", [
        {"role": "user", "content": "每周五下午3点前要周报。"},
        {"role": "assistant", "content": "记下了。"}
    ], {"topic": "工作要求"}),
    
    ("反馈", [
        {"role": "user", "content": "上次报告太学术化了，领导看不懂。"},
        {"role": "assistant", "content": "以后会用通俗语言。"}
    ], {"topic": "用户反馈", "sentiment": "negative"}),
]


def main():
    memory = Mem1Memory(config)
    
    # 清空旧数据
    print("=== 清空旧数据 ===")
    memory.delete_user(USER_ID)
    
    # 批量导入
    print("\n=== 批量导入 ===")
    base_time = datetime.now()
    
    for i, (name, messages, metadata) in enumerate(SAMPLE_CONVERSATIONS):
        # 模拟不同时间
        fake_time = base_time - timedelta(days=len(SAMPLE_CONVERSATIONS) - i)
        ts = fake_time.strftime('%Y-%m-%d %H:%M:%S')
        
        memory.add_conversation(
            messages=messages,
            user_id=USER_ID,
            metadata=metadata,
            timestamp=ts
        )
        print(f"  [{i+1}] {name}")
    
    print(f"\n✓ 已导入 {len(SAMPLE_CONVERSATIONS)} 条对话")
    
    # 更新画像
    print("\n=== 更新画像 ===")
    memory.update_profile(USER_ID)
    
    # 验证
    print("\n=== 验证 ===")
    ctx = memory.get_context(user_id=USER_ID, query="")
    print(f"画像:\n{ctx['import_content']}")


if __name__ == "__main__":
    main()
