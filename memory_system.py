"""
向量记忆系统 - 为 IRC AI Agent 提供长期记忆能力

核心功能：
1. 自动判断消息的记忆价值
2. 语义检索相关记忆
3. 时间衰减和遗忘机制
4. 用户级记忆隔离
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from openai import AsyncOpenAI
import chromadb
from chromadb.utils import embedding_functions

# ============= 配置 =============
MEMORY_SCORE_THRESHOLD = 7  # 只有评分 >= 7 的消息才存入长期记忆
MEMORY_DECAY_DAYS = 30      # 30天后记忆权重开始衰减
MAX_RECALL_MEMORIES = 3     # 每次最多召回3条记忆


@dataclass
class Memory:
    """记忆条目"""
    id: str
    user: str           # 发言用户
    channel: str        # 频道
    content: str        # 消息内容
    timestamp: str      # ISO 格式时间戳
    score: int          # 记忆价值分数 (1-10)
    tags: List[str]     # 标签（用于过滤）
    context: str        # 上下文摘要（前3条消息）
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    def age_days(self) -> int:
        """计算记忆年龄（天数）"""
        created = datetime.fromisoformat(self.timestamp)
        return (datetime.now() - created).days


class MemorySystem:
    """向量记忆系统"""
    
    def __init__(
        self, 
        openai_api_key: str,
        openai_base_url: str = "https://api.openai.com/v1",
        db_path: str = "./chroma_db",
        collection_name: str = "irc_memories"
    ):
        self.client = AsyncOpenAI(api_key=openai_api_key, base_url=openai_base_url)
        
        # 初始化 ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        
        # 使用 OpenAI embedding（需要 API key）
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=openai_api_key,
            model_name="text-embedding-3-small"  # 便宜且快速
        )
        
        # 获取或创建集合
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
            metadata={"description": "IRC AI Agent 长期记忆存储"}
        )
    
    async def evaluate_memory_value(
        self, 
        message: str, 
        user: str,
        context: List[str]
    ) -> Optional[Dict]:
        """
        使用 LLM 判断消息是否值得记忆
        
        返回：
        {
            "score": 8,
            "reason": "用户表达了明确的技术偏好",
            "tags": ["技术选型", "数据库", "PostgreSQL"]
        }
        """
        context_text = "\n".join(context[-3:]) if context else "（无上下文）"
        
        prompt = f"""你是记忆价值评估专家。评估这条IRC消息是否值得长期记忆。

**消息内容**：
{user}: {message}

**上下文**（最近3条）：
{context_text}

**评分标准**：
- 9-10分：关键决策、重要偏好、核心观点、个人信息
  例："我们决定用PostgreSQL"，"我是Python开发者"
- 7-8分：有价值的事实信息、明确的态度、技术讨论
  例："我觉得微服务架构更适合"，"我们公司在用K8s"
- 4-6分：一般性讨论、技术探讨、观点交流
  例："这个方案有优缺点"，"可以考虑这样实现"
- 1-3分：闲聊、问候、重复信息、无意义内容
  例："你好"，"在吗"，"哈哈"

**返回JSON格式**：
```json
{{
    "score": 评分(1-10整数),
    "reason": "一句话解释为什么这样评分",
    "tags": ["标签1", "标签2", "标签3"]  // 2-5个关键词标签
}}
```

只返回JSON，不要其他内容。"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            result_text = response.choices[0].message.content.strip()
            # 提取JSON（可能被代码块包裹）
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            return result
            
        except Exception as e:
            print(f"❌ 记忆评估失败: {e}")
            return None
    
    async def store_memory(
        self,
        user: str,
        channel: str,
        message: str,
        context: List[str]
    ) -> bool:
        """
        存储一条消息到长期记忆（如果值得记忆）
        
        返回：True 表示已存储，False 表示不值得记忆
        """
        # 1. 评估记忆价值
        evaluation = await self.evaluate_memory_value(message, user, context)
        if not evaluation or evaluation["score"] < MEMORY_SCORE_THRESHOLD:
            return False
        
        # 2. 创建记忆对象
        memory = Memory(
            id=f"{user}_{channel}_{datetime.now().isoformat()}",
            user=user,
            channel=channel,
            content=message,
            timestamp=datetime.now().isoformat(),
            score=evaluation["score"],
            tags=evaluation["tags"],
            context="\n".join(context[-3:]) if context else ""
        )
        
        # 3. 存入向量数据库
        try:
            self.collection.add(
                ids=[memory.id],
                documents=[message],  # 用于向量化
                metadatas=[{
                    "user": user,
                    "channel": channel,
                    "timestamp": memory.timestamp,
                    "score": memory.score,
                    "tags": json.dumps(memory.tags, ensure_ascii=False),
                    "context": memory.context,
                    "reason": evaluation["reason"]
                }]
            )
            print(f"✅ 存储记忆 [{evaluation['score']}分]: {user}: {message[:50]}...")
            return True
            
        except Exception as e:
            print(f"❌ 存储记忆失败: {e}")
            return False
    
    def recall_memories(
        self,
        query: str,
        user: Optional[str] = None,
        channel: Optional[str] = None,
        top_k: int = MAX_RECALL_MEMORIES
    ) -> List[Dict]:
        """
        召回相关记忆
        
        参数：
        - query: 查询文本（当前对话内容）
        - user: 可选，只召回特定用户的记忆
        - channel: 可选，只召回特定频道的记忆
        - top_k: 最多返回多少条记忆
        
        返回：记忆列表，按相关性+时间衰减排序
        """
        try:
            # 构建过滤条件
            where = {}
            if user:
                where["user"] = user
            if channel:
                where["channel"] = channel
            
            # 向量语义搜索
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k * 2,  # 先多取一些，后面再应用时间衰减
                where=where if where else None
            )
            
            if not results["ids"][0]:
                return []
            
            # 3. 应用时间衰减，重新排序
            memories = []
            for i, doc_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i]
                
                # 计算时间衰减因子
                timestamp = datetime.fromisoformat(metadata["timestamp"])
                age_days = (datetime.now() - timestamp).days
                if age_days > MEMORY_DECAY_DAYS:
                    decay_factor = 0.5 ** ((age_days - MEMORY_DECAY_DAYS) / 30)  # 每30天衰减一半
                else:
                    decay_factor = 1.0
                
                # 综合分数 = 相似度 * 时间衰减 * 记忆价值
                final_score = (1 - distance) * decay_factor * (metadata["score"] / 10)
                
                memories.append({
                    "id": doc_id,
                    "user": metadata["user"],
                    "channel": metadata["channel"],
                    "content": results["documents"][0][i],
                    "timestamp": metadata["timestamp"],
                    "score": metadata["score"],
                    "tags": json.loads(metadata["tags"]),
                    "context": metadata.get("context", ""),
                    "reason": metadata.get("reason", ""),
                    "relevance": final_score,
                    "age_days": age_days
                })
            
            # 按综合分数排序，返回 top_k 条
            memories.sort(key=lambda x: x["relevance"], reverse=True)
            return memories[:top_k]
            
        except Exception as e:
            print(f"❌ 召回记忆失败: {e}")
            return []
    
    def format_memories_for_prompt(self, memories: List[Dict]) -> str:
        """
        将召回的记忆格式化为可以注入 prompt 的文本
        """
        if not memories:
            return ""
        
        formatted = ["[相关长期记忆]"]
        for mem in memories:
            age_desc = "最近" if mem["age_days"] < 7 else f"{mem['age_days']}天前"
            formatted.append(
                f"• {age_desc} {mem['user']} 说: {mem['content']} "
                f"[标签: {', '.join(mem['tags'])}]"
            )
        
        return "\n".join(formatted)
    
    def get_user_profile(self, user: str, channel: Optional[str] = None) -> str:
        """
        生成用户画像摘要（基于历史记忆）
        """
        # 获取该用户的所有高分记忆
        where = {"user": user, "score": {"$gte": 8}}
        if channel:
            where["channel"] = channel
        
        results = self.collection.get(
            where=where,
            limit=20
        )
        
        if not results["ids"]:
            return f"[用户 {user} 的记忆为空]"
        
        # 提取所有标签
        all_tags = []
        for metadata in results["metadatas"]:
            all_tags.extend(json.loads(metadata["tags"]))
        
        # 统计标签频率
        from collections import Counter
        tag_counts = Counter(all_tags)
        top_tags = [tag for tag, _ in tag_counts.most_common(5)]
        
        profile = f"[用户 {user} 的记忆画像]\n"
        profile += f"• 关键兴趣: {', '.join(top_tags)}\n"
        profile += f"• 重要记忆数: {len(results['ids'])} 条"
        
        return profile


# ============= 使用示例 =============
async def example_usage():
    """演示如何使用记忆系统"""
    
    # 初始化
    memory_system = MemorySystem(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    )
    
    # 1. 存储记忆（在 ai_agent.py 的消息处理函数中调用）
    context = [
        "我们在讨论技术选型",
        "有人提到了微服务",
    ]
    
    await memory_system.store_memory(
        user="lemonhall",
        channel="#ai-collab-test",
        message="我觉得对于我们这个规模，PostgreSQL + Redis 就够了",
        context=context
    )
    
    # 2. 召回记忆（在生成回复前调用）
    current_message = "我们要不要用数据库？"
    memories = memory_system.recall_memories(
        query=current_message,
        user="lemonhall",  # 可选：只召回特定用户的记忆
        top_k=3
    )
    
    # 3. 注入到 prompt
    memory_context = memory_system.format_memories_for_prompt(memories)
    print(memory_context)
    # 输出：
    # [相关长期记忆]
    # • 最近 lemonhall 说: 我觉得对于我们这个规模，PostgreSQL + Redis 就够了 [标签: 数据库, 技术选型, PostgreSQL]
    
    # 4. 查看用户画像
    profile = memory_system.get_user_profile("lemonhall")
    print(profile)


if __name__ == "__main__":
    asyncio.run(example_usage())
