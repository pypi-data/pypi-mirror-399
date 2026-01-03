# mem1 示例代码

## 运行前准备

1. 启动 Elasticsearch
2. 配置 `.env` 文件（参考项目根目录）
3. 安装依赖：`pip install -e .`

## 示例列表

| 文件 | 说明 |
|------|------|
| `basic_usage.py` | 基础用法：添加对话、更新画像、获取上下文 |
| `langchain_integration.py` | LangChain 集成示例 |
| `batch_import.py` | 批量导入对话数据 |
| `image_usage.py` | 图片功能：添加带图片对话、搜索图片 |

## 运行示例

```bash
cd examples
python basic_usage.py
python langchain_integration.py
python batch_import.py
```
