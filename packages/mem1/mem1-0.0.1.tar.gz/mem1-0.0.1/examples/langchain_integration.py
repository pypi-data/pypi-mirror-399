"""
mem1 + LangChain 集成示例

三层记忆架构：
- Tier 1 (短期): LangChain 管理的当前会话
- Tier 2 (画像): mem1 用户画像，注入 system prompt
- Tier 3 (长期): ES 存储的历史对话
"""
import os
import logging
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory

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

USER_ID = "langchain_demo_user"


def demo_manual_integration():
    """方式1: 手动集成（更灵活）"""
    print("\n=== 手动集成 mem1 到 LangChain ===")
    
    memory = Mem1Memory(config)
    
    # 获取用户画像 (Tier 2)
    ctx = memory.get_context(user_id=USER_ID, query="帮我写报告")
    
    # 构建 system prompt
    system_prompt = f"""你是一个助手。

## 用户画像
{ctx['import_content']}

## 当前时间
{ctx['current_time']}
"""
    
    # LangChain LLM
    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com"
    )
    
    # Tier 1: 当前会话
    messages = [SystemMessage(content=system_prompt)]
    conversation_to_save = []
    
    # 多轮对话
    user_inputs = ["你好", "帮我写个简单的报告"]
    for user_input in user_inputs:
        print(f"\n👤 用户: {user_input}")
        messages.append(HumanMessage(content=user_input))
        
        response = llm.invoke(messages)
        print(f"🤖 助手: {response.content[:100]}...")
        
        messages.append(response)
        conversation_to_save.append({"role": "user", "content": user_input})
        conversation_to_save.append({"role": "assistant", "content": response.content})
    
    # 保存到 Tier 3
    memory.add_conversation(
        messages=conversation_to_save,
        user_id=USER_ID,
        metadata={"session": "manual_demo"}
    )
    print("\n✓ 会话已保存到 ES")


def demo_chain_integration():
    """方式2: 使用 LangChain Chain"""
    print("\n=== LangChain Chain + mem1 ===")
    
    memory = Mem1Memory(config)
    ctx = memory.get_context(user_id=USER_ID, query="")
    
    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com"
    )
    
    # Tier 1: LangChain 短期记忆
    chat_history = InMemoryChatMessageHistory()
    
    # 注入 Tier 2 画像
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"你是一个助手。\n\n## 用户画像\n{ctx['import_content']}"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
    
    chain = prompt | llm
    
    # 对话
    query = "你好，记得我的偏好吗？"
    print(f"\n👤 用户: {query}")
    
    result = chain.invoke({"input": query, "history": chat_history.messages})
    print(f"🤖 助手: {result.content[:100]}...")
    
    # 更新短期记忆
    chat_history.add_user_message(query)
    chat_history.add_ai_message(result.content)
    
    # 保存到 Tier 3
    memory.add_conversation(
        messages=[
            {"role": "user", "content": query},
            {"role": "assistant", "content": result.content}
        ],
        user_id=USER_ID,
        metadata={"session": "chain_demo"}
    )
    print("✓ 会话已保存到 ES")


if __name__ == "__main__":
    demo_manual_integration()
    demo_chain_integration()
