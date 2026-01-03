"""基于 Elasticsearch 的记忆管理系统"""
import json
import shutil
import base64
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
from elasticsearch import Elasticsearch
from mem1.config import Mem1Config
from mem1.llm import LLMClient
from mem1.prompts import ProfileTemplate, RECALL_DECISION_PROMPT, IMAGE_SEARCH_PROMPT

logger = logging.getLogger(__name__)

# 用户状态索引名
USER_STATE_INDEX = "mem1_user_state"
# 用户画像索引名
USER_PROFILE_INDEX = "mem1_user_profile"


class Mem1Memory:
    """基于 Elasticsearch 的用户记忆系统
    
    数据存储（全部在 ES）：
    - ES 索引 conversation_history: 历史对话记录
    - ES 索引 mem1_user_state: 用户更新状态（轮数、上次更新时间）
    - ES 索引 mem1_user_profile: 用户画像
    - 本地文件 _images.json: 图片索引（仅图片相关）
    """
    
    def __init__(
        self,
        config: Mem1Config,
        memory_dir: Optional[str] = None,
        profile_template: Optional[ProfileTemplate] = None
    ):
        """初始化 ES 记忆系统"""
        self.config = config
        self.memory_dir = Path(memory_dir or config.memory.memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # 图片存储目录（独立配置）
        self.images_dir = Path(config.images.images_dir)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # ES 连接（从配置读取）
        self.es = Elasticsearch(config.es.hosts)
        self.index_name = config.es.index_name
        
        # LLM 客户端
        self.llm = LLMClient(config.llm)
        
        # 业务场景模板
        self.profile_template = profile_template or ProfileTemplate()
        
        # 配置参数
        self.max_profile_chars = config.memory.max_profile_chars
        self.auto_update_profile = config.memory.auto_update_profile
        self.update_interval_rounds = config.memory.update_interval_rounds
        self.update_interval_minutes = config.memory.update_interval_minutes
        
        # 确保用户状态索引存在
        self._ensure_state_index()
    
    def _get_user_images_dir(self, user_id: str) -> Path:
        """获取用户图片目录"""
        images_dir = self.images_dir / user_id
        images_dir.mkdir(parents=True, exist_ok=True)
        return images_dir
    
    def _get_images_index_path(self, user_id: str) -> Path:
        """获取图片索引文件路径"""
        return self.images_dir / user_id / "_images.json"
    
    def _load_images_index(self, user_id: str) -> List[Dict[str, str]]:
        """加载图片索引"""
        path = self._get_images_index_path(user_id)
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return []
    
    def _save_images_index(self, user_id: str, index: List[Dict[str, str]]) -> None:
        """保存图片索引"""
        path = self._get_images_index_path(user_id)
        path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def _get_profile(self, user_id: str) -> Optional[str]:
        """从 ES 获取用户画像"""
        try:
            response = self.es.get(index=USER_PROFILE_INDEX, id=user_id)
            return response["_source"]["content"]
        except Exception:
            return None
    
    def _save_profile(self, user_id: str, content: str) -> None:
        """保存用户画像到 ES"""
        self.es.index(
            index=USER_PROFILE_INDEX,
            id=user_id,
            document={
                "user_id": user_id,
                "content": content,
                "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            refresh=True
        )
    
    def _init_profile(self, user_id: str) -> str:
        """初始化用户画像（从 ES 读取，不存在则创建）"""
        content = self._get_profile(user_id)
        if content is None:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            content = self.profile_template.render(user_id, timestamp)
            self._save_profile(user_id, content)
            logger.info(f"✓ 创建用户画像: {user_id}")
        return content
    
    def _ensure_state_index(self) -> None:
        """确保用户状态索引存在"""
        if not self.es.indices.exists(index=USER_STATE_INDEX):
            self.es.indices.create(
                index=USER_STATE_INDEX,
                body={
                    "mappings": {
                        "properties": {
                            "user_id": {"type": "keyword"},
                            "rounds": {"type": "integer"},
                            "last_update": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss||epoch_millis"}
                        }
                    }
                }
            )
            logger.info(f"✓ 创建用户状态索引: {USER_STATE_INDEX}")
        
        # 确保画像索引存在
        if not self.es.indices.exists(index=USER_PROFILE_INDEX):
            self.es.indices.create(
                index=USER_PROFILE_INDEX,
                body={
                    "mappings": {
                        "properties": {
                            "user_id": {"type": "keyword"},
                            "content": {"type": "text"},
                            "updated_at": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss||epoch_millis"}
                        }
                    }
                }
            )
            logger.info(f"✓ 创建用户画像索引: {USER_PROFILE_INDEX}")
    
    def _get_user_state(self, user_id: str) -> Dict[str, Any]:
        """从 ES 获取用户更新状态"""
        try:
            response = self.es.get(index=USER_STATE_INDEX, id=user_id)
            return response["_source"]
        except Exception:
            # 用户状态不存在，返回初始状态
            return {"user_id": user_id, "rounds": 0, "last_update": None}
    
    def _update_user_state(self, user_id: str, rounds: int, last_update: Optional[str] = None) -> None:
        """更新 ES 中的用户状态"""
        doc = {"user_id": user_id, "rounds": rounds}
        if last_update:
            doc["last_update"] = last_update
        
        self.es.index(
            index=USER_STATE_INDEX,
            id=user_id,
            document=doc,
            refresh=True
        )
    
    def _should_trigger_update(self, user_id: str) -> bool:
        """
        判断是否应该触发画像更新（基于 ES 存储的状态）
        
        触发条件（满足任一即触发）：
        1. 累积对话轮数 >= update_interval_rounds
        2. 距上次更新时间 >= update_interval_minutes
        3. 首次（无 last_update）
        """
        state = self._get_user_state(user_id)
        rounds = state.get("rounds", 0) + 1
        last_update_str = state.get("last_update")
        
        should_update = False
        reason = ""
        
        # 条件1：累积轮数达到阈值
        if rounds >= self.update_interval_rounds:
            should_update = True
            reason = f"轮数={rounds} >= {self.update_interval_rounds}"
        
        # 条件2：距上次更新超过时间阈值
        if not should_update and last_update_str:
            try:
                last_update = datetime.strptime(last_update_str, '%Y-%m-%d %H:%M:%S')
                elapsed = (datetime.now() - last_update).total_seconds() / 60
                if elapsed >= self.update_interval_minutes:
                    should_update = True
                    reason = f"时间={elapsed:.1f}分钟 >= {self.update_interval_minutes}"
            except ValueError:
                pass
        
        # 条件3：首次更新
        if not should_update and last_update_str is None:
            should_update = True
            reason = "首次创建画像"
        
        if should_update:
            logger.info(f"📊 触发画像更新（{reason}）: {user_id}")
            # 重置轮数
            self._update_user_state(user_id, 0, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        else:
            # 增加轮数
            self._update_user_state(user_id, rounds, last_update_str)
            logger.debug(f"📊 暂不更新（轮数={rounds}/{self.update_interval_rounds}）: {user_id}")
        
        return should_update
    
    def add_conversation(
        self,
        messages: List[Dict[str, str]],
        user_id: str,
        images: Optional[List[Dict[str, Any]]] = None,
        save_assistant_messages: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """添加对话到 ES"""
        ts = timestamp or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 处理图片
        image_refs = []
        if images:
            user_images_dir = self._get_user_images_dir(user_id)
            images_index = self._load_images_index(user_id)
            timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            for img in images:
                filename = f"{timestamp_str}_{img['filename']}"
                img_path = user_images_dir / filename
                
                if 'data' in img:
                    img_data = base64.b64decode(img['data'])
                    img_path.write_bytes(img_data)
                elif 'path' in img:
                    shutil.copy(img['path'], img_path)
                
                rel_path = f"./images/{filename}"
                image_refs.append(rel_path)
                
                description = img.get('description', '')
                if not description:
                    for msg in messages:
                        if msg["role"] == "user":
                            description = msg["content"][:100]
                            break
                
                images_index.append({
                    "filename": filename,
                    "path": rel_path,
                    "description": description,
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "original_name": img['filename']
                })
            
            self._save_images_index(user_id, images_index)
        
        # 构建对话记录
        conversation_entry = {
            "user_id": user_id,
            "timestamp": ts,
            "messages": [],
            "metadata": metadata or {}
        }
        
        first_user_msg = True
        for msg in messages:
            if msg["role"] == "user":
                msg_obj = {"role": "user", "content": msg["content"]}
                if first_user_msg and image_refs:
                    msg_obj["images"] = image_refs
                    first_user_msg = False
                conversation_entry["messages"].append(msg_obj)
            elif save_assistant_messages:
                conversation_entry["messages"].append({
                    "role": "assistant",
                    "content": msg["content"]
                })
        
        # 写入 ES（refresh=True 确保立即可搜索）
        response = self.es.index(
            index=self.index_name,
            document=conversation_entry,
            refresh=True
        )
        
        logger.info(f"✓ 对话已存入 ES: user={user_id}, timestamp={ts}, id={response['_id']}")
        
        # 自动更新画像（基于 ES 状态判断）
        if self.auto_update_profile and self._should_trigger_update(user_id):
            try:
                self.update_profile(user_id)
            except Exception as e:
                logger.error(f"❌ 画像更新失败: {user_id}, error={e}")
        
        return {"status": "success", "es_id": response['_id']}
    
    def get_conversations(
        self,
        user_id: str,
        days_limit: Optional[int] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        size: int = 1000
    ) -> List[Dict[str, Any]]:
        """从 ES 获取对话记录"""
        query = {
            "bool": {
                "must": [
                    {"term": {"user_id": user_id}}
                ]
            }
        }
        
        # 时间过滤
        if days_limit:
            cutoff_date = (datetime.now() - timedelta(days=days_limit)).strftime('%Y-%m-%d %H:%M:%S')
            query["bool"]["must"].append({
                "range": {
                    "timestamp": {"gte": cutoff_date}
                }
            })
        
        # 元数据过滤
        if metadata_filter:
            for k, v in metadata_filter.items():
                query["bool"]["must"].append({
                    "term": {f"metadata.{k}": v}
                })
        
        # 查询 ES
        response = self.es.search(
            index=self.index_name,
            query=query,
            size=size,
            sort=[{"timestamp": {"order": "asc"}}]
        )
        
        conversations = [hit["_source"] for hit in response["hits"]["hits"]]
        logger.info(f"📖 从 ES 读取对话: user={user_id}, count={len(conversations)}")
        
        return conversations
    
    def update_profile(self, user_id: str) -> Dict[str, Any]:
        """更新用户画像"""
        self._init_profile(user_id)
        
        # 从 ES 读取对话
        conversations = self.get_conversations(user_id)
        if not conversations:
            return {"status": "success", "updated": False, "reason": "no_conversation"}
        
        history_content = self._format_conversations_for_llm(conversations)
        
        # 从 ES 读取现有画像
        profile_content = self._get_profile(user_id)
        
        # LLM 更新画像
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        prompt = self.profile_template.get_update_prompt().format(
            user_id=user_id,
            normal_content=history_content,
            import_content=profile_content,
            timestamp=timestamp
        )
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": "请整理用户画像"}
        ]
        
        response = self.llm.generate(messages, response_format="text")
        
        # 检查是否需要压缩
        if len(response) > self.max_profile_chars:
            logger.info(f"📦 用户画像超长({len(response)}>{self.max_profile_chars})，触发压缩...")
            response = self._compress_profile(user_id, response)
            logger.info(f"📦 压缩后长度: {len(response)}")
        
        # 保存到 ES
        self._save_profile(user_id, response)
        logger.info(f"✓ 画像已更新到 ES: {user_id}")
        
        return {"status": "success", "updated": True, "length": len(response)}
    
    def get_context(
        self,
        user_id: str,
        query: str,
        include_normal: Optional[bool] = None,
        days_limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取记忆上下文"""
        profile_content = self._init_profile(user_id)
        
        now = datetime.now()
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        current_time = f"{now.strftime('%Y-%m-%d %H:%M')} {weekdays[now.weekday()]}"
        
        # 从 ES 获取画像更新时间
        profile_last_updated = "未更新"
        try:
            response = self.es.get(index=USER_PROFILE_INDEX, id=user_id)
            profile_last_updated = response["_source"].get("updated_at", "未更新")
        except Exception:
            pass
        
        result = {
            "current_time": current_time,
            "import_content": profile_content,
            "normal_content": "",
            "need_history": False,
            "recall_reason": "",
            "recall_triggered_by": "none",
            "profile_last_updated": profile_last_updated,
            "conversations_count": 0
        }
        
        # 判断是否需要历史记录
        if include_normal is None:
            need_history, reason = self._should_include_history(query)
            result["recall_reason"] = reason
            result["recall_triggered_by"] = "llm_decision"
        elif include_normal:
            need_history = True
            result["recall_triggered_by"] = "manual"
        else:
            need_history = False
            result["recall_triggered_by"] = "manual"
        
        if need_history:
            conversations = self.get_conversations(user_id, days_limit=days_limit)
            if conversations:
                result["normal_content"] = self._format_conversations_for_llm(conversations)
                result["need_history"] = True
                result["conversations_count"] = len(conversations)
        
        return result
    
    def _compress_profile(self, user_id: str, profile_content: str) -> str:
        """压缩用户画像"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        prompt = self.profile_template.get_compress_prompt().format(
            user_id=user_id,
            profile_content=profile_content,
            max_chars=self.max_profile_chars,
            timestamp=timestamp
        )
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": "请压缩用户画像"}
        ]
        
        response = self.llm.generate(messages, response_format="text")
        return response
    
    def _should_include_history(self, query: str) -> tuple[bool, str]:
        """LLM 判断是否需要加载历史记录"""
        prompt = RECALL_DECISION_PROMPT.format(query=query)
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": query}
        ]
        
        response = self.llm.generate(messages, response_format="text")
        response_lower = response.strip().lower()
        need_history = "true" in response_lower or "是" in response_lower or "需要" in response_lower
        
        logger.info(f"🔍 回忆判断: query='{query[:50]}...', need_history={need_history}")
        
        return need_history, response.strip()
    
    def search_images(self, user_id: str, query: str) -> List[Dict[str, str]]:
        """搜索用户图片"""
        images_index = self._load_images_index(user_id)
        if not images_index:
            return []
        
        images_desc = "\n".join([
            f"[{i}] 文件名: {img['original_name']}, 时间: {img['timestamp']}, 描述: {img['description'][:100]}"
            for i, img in enumerate(images_index)
        ])
        
        prompt = IMAGE_SEARCH_PROMPT.format(query=query, images_desc=images_desc)
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": query}
        ]
        
        response = self.llm.generate(messages, response_format="text")
        
        results = []
        for line in response.strip().split('\n'):
            line = line.strip()
            if line.isdigit():
                idx = int(line)
                if 0 <= idx < len(images_index):
                    results.append(images_index[idx])
        
        logger.info(f"🖼️ 图片搜索: query='{query}', 找到 {len(results)} 张")
        return results
    
    def _format_conversations_for_llm(self, conversations: List[Dict[str, Any]]) -> str:
        """格式化对话记录为文本"""
        output = []
        for conv in conversations:
            timestamp = conv.get("timestamp", "未知时间")
            metadata = conv.get("metadata", {})
            
            title = f"### {timestamp}"
            if metadata:
                tags = " ".join([f"[{k}:{v}]" for k, v in metadata.items()])
                title += f" {tags}"
            
            output.append(title)
            output.append("")
            
            for msg in conv.get("messages", []):
                role_icon = "👤" if msg["role"] == "user" else "🤖"
                role_name = "用户" if msg["role"] == "user" else "助手"
                output.append(f"**{role_icon} {role_name}**: {msg['content']}")
                if msg.get("images"):
                    for img_path in msg["images"]:
                        output.append(f"![Image]({img_path})")
                output.append("")
            
            output.append("---")
            output.append("")
        
        return "\n".join(output)
    
    def get_user_list(self) -> List[str]:
        """获取所有用户ID列表（从 ES）"""
        response = self.es.search(
            index=self.index_name,
            body={
                "size": 0,
                "aggs": {
                    "users": {
                        "terms": {"field": "user_id", "size": 10000}
                    }
                }
            }
        )
        
        users = [bucket["key"] for bucket in response["aggregations"]["users"]["buckets"]]
        return users
    
    def delete_user(self, user_id: str) -> Dict[str, Any]:
        """删除用户所有记忆"""
        # 删除 ES 中的对话记录
        self.es.delete_by_query(
            index=self.index_name,
            query={"term": {"user_id": user_id}},
            refresh=True
        )
        
        # 删除 ES 中的用户状态
        try:
            self.es.delete(index=USER_STATE_INDEX, id=user_id, refresh=True)
        except Exception:
            pass  # 状态可能不存在
        
        # 删除 ES 中的用户画像
        try:
            self.es.delete(index=USER_PROFILE_INDEX, id=user_id, refresh=True)
        except Exception:
            pass  # 画像可能不存在
        
        # 删除本地图片文件
        user_images_dir = self.images_dir / user_id
        if user_images_dir.exists():
            shutil.rmtree(user_images_dir)
        
        logger.info(f"✓ 已删除用户所有数据: {user_id}")
        return {"status": "success", "deleted": user_id}
