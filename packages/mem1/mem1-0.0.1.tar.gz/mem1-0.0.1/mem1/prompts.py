"""提示词模板 - 通用记忆系统

记忆框架与业务场景解耦设计：
- 记忆框架（MarkdownMemory）：通用的存储、检索、更新能力
- 业务场景（ProfileTemplate）：可插拔的画像模板和提示词

使用方式：
1. 使用默认模板：直接使用 MarkdownMemory
2. 自定义业务场景：创建 ProfileTemplate 实例，传入 MarkdownMemory
"""

from typing import Optional


class ProfileTemplate:
    """用户画像模板 - 可自定义以适配不同业务场景
    
    记忆框架与业务场景解耦的核心：
    - 记忆框架只负责存储和检索
    - 业务场景通过 ProfileTemplate 定义画像结构和提示词
    """
    
    # 默认通用模板
    DEFAULT_SECTIONS = """## 基本信息
- 姓名/称呼：
- 身份/角色：
- 所属组织：
- 背景信息：

## 偏好习惯
- 沟通风格：（详细/简洁、正式/随意等）
- 关注重点：
- 特殊要求：

## 重要事项
（用户提到的重要背景、关键需求、待办事项等）

## 用户反馈
- 正向反馈：（满意的地方）
- 负向反馈：（不满意的地方、需改进的问题）

## 注意事项
（需要规避的话题、曾经的误解、用户不喜欢的做法等）"""

    def __init__(
        self,
        sections: Optional[str] = None,
        description: str = "从对话中整理的用户信息",
        update_prompt: Optional[str] = None,
        compress_prompt: Optional[str] = None
    ):
        """
        Args:
            sections: 自定义画像章节结构（Markdown 格式）
            description: 画像描述
            update_prompt: 自定义画像更新提示词（可选）
            compress_prompt: 自定义画像压缩提示词（可选）
        """
        self.sections = sections or self.DEFAULT_SECTIONS
        self.description = description
        self._update_prompt = update_prompt
        self._compress_prompt = compress_prompt
    
    def render(self, user_id: str, timestamp: str) -> str:
        """渲染初始画像模板"""
        return f"""# {user_id} 用户画像

> {self.description}

{self.sections}

---
*最后更新: {timestamp}*
"""
    
    def get_update_prompt(self) -> str:
        """获取画像更新提示词"""
        return self._update_prompt or DEFAULT_PROFILE_UPDATE_PROMPT
    
    def get_compress_prompt(self) -> str:
        """获取画像压缩提示词"""
        return self._compress_prompt or DEFAULT_PROFILE_COMPRESS_PROMPT


# ============ 默认提示词模板（通用） ============

DEFAULT_PROFILE_UPDATE_PROMPT = """你是用户画像分析专家。从对话记录中提取用户信息，更新用户画像。

## 对话记录
{normal_content}

## 现有用户画像
{import_content}

## 任务
分析对话记录，提取关于用户的重要信息，更新用户画像。

## 输出格式
直接输出完整的 Markdown 格式用户画像，保持现有画像的章节结构。

## 整理原则
1. 不能丢失现有画像中的信息，除非对话中明确否定
2. 新信息是补充，不是替换
3. 用户反馈（表扬或批评）必须保留
4. 只记录用户明确表达的信息，不要推测
5. 如果某个章节没有信息，保留标题但内容留空

---
*最后更新: {timestamp}*
"""

DEFAULT_PROFILE_COMPRESS_PROMPT = """你是用户画像压缩专家。当前用户画像过长，需要精简。

## 当前用户画像
{profile_content}

## 任务
将用户画像压缩到 {max_chars} 字符以内，保留最重要的信息。

## 压缩原则
1. 保留核心身份信息
2. 保留关键偏好（最重要的 2-3 条）
3. 合并相似条目
4. 删除过时信息
5. 保留负向反馈

## 输出格式
直接输出压缩后的完整 Markdown 格式用户画像。

---
*最后更新: {timestamp}*
*（已压缩）*
"""


# ============ 回忆判断提示词（通用） ============

RECALL_DECISION_PROMPT = """判断用户的问题是否需要查阅历史对话记录。

**需要查阅的情况：**
- 用户询问之前聊过的内容（"上次说的..."、"之前提到的..."）
- 用户想回顾历史对话
- 用户引用过去的对话

**不需要查阅的情况：**
- 新的问题或请求
- 基于用户画像就能回答的问题
- 通用知识类问题

## 用户问题
{query}

## 输出
只输出：`true`（需要查阅历史）或 `false`（不需要）"""


# ============ 图片搜索提示词（通用） ============

IMAGE_SEARCH_PROMPT = """根据用户查询，从图片列表中找出匹配的图片。

## 图片列表
{images_desc}

## 用户查询
{query}

## 输出格式
只输出匹配图片的索引号，每行一个。如果没有匹配的图片，输出"无"。
"""


# ============ 业务场景模板示例 ============

# 舆情行业模板
YUQING_PROFILE_TEMPLATE = ProfileTemplate(
    description="舆情行业用户画像",
    sections="""## 基本信息
- 姓名/称呼：
- 职位/角色：
- 所属机构：
- 职责范围：

## 偏好习惯
- 报告风格：（详细/简洁、图表/文字等）
- 沟通方式：（直接/委婉、正式/随意等）
- 关注重点：（时效性/准确性/全面性等）
- 图表偏好：

## 重要事项
（重要背景、成功案例、关键需求、定期任务等）

## 用户反馈
- 正向反馈：
- 负向反馈：

## 注意事项
（敏感话题、规避要点、历史问题等）"""
)


# 电商客服模板
ECOMMERCE_PROFILE_TEMPLATE = ProfileTemplate(
    description="电商客户画像",
    sections="""## 基本信息
- 称呼：
- 会员等级：
- 常用收货地址：

## 购物偏好
- 常购品类：
- 价格敏感度：
- 品牌偏好：

## 服务记录
- 历史订单问题：
- 退换货记录：
- 投诉记录：

## 沟通偏好
- 响应速度要求：
- 沟通风格：

## 注意事项
（特殊需求、敏感话题等）"""
)


# 医疗助手模板
MEDICAL_PROFILE_TEMPLATE = ProfileTemplate(
    description="患者健康档案摘要",
    sections="""## 基本信息
- 称呼：
- 年龄段：
- 主要健康关注：

## 健康背景
- 已知病史：
- 过敏信息：
- 用药情况：

## 咨询偏好
- 信息详细程度：
- 关注重点：

## 重要提醒
（需要特别注意的健康事项）

## 注意事项
（沟通禁忌、敏感话题等）"""
)


# ============ 兼容旧接口 ============
# 保持向后兼容，旧代码仍可使用这些变量名

PROFILE_UPDATE_PROMPT = DEFAULT_PROFILE_UPDATE_PROMPT
PROFILE_COMPRESS_PROMPT = DEFAULT_PROFILE_COMPRESS_PROMPT
