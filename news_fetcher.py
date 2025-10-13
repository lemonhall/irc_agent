"""
新闻抓取服务 - 从 RSS 源获取并筛选重要新闻
每天运行一次，提取最重要的世界和亚太新闻
"""
import json
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

import httpx
from openai import OpenAI
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# RSS 源配置
RSS_FEEDS = {
    "world": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "asia": "https://rss.nytimes.com/services/xml/rss/nyt/AsiaPacific.xml"
}

# 存储路径
NEWS_HISTORY_FILE = Path(__file__).parent / "news_history.json"
LATEST_NEWS_FILE = Path(__file__).parent / "latest_news.json"


class NewsFetcher:
    """新闻抓取器"""
    
    def __init__(self):
        """初始化"""
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
    def fetch_rss(self, url: str) -> List[Dict[str, str]]:
        """
        获取 RSS 内容并解析
        
        Args:
            url: RSS 源地址
            
        Returns:
            新闻列表，每条新闻包含 title 和 description
        """
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url)
                response.raise_for_status()
                
            # 解析 XML
            root = ET.fromstring(response.content)
            
            # 提取新闻条目
            news_items = []
            for item in root.findall('.//item'):
                title_elem = item.find('title')
                desc_elem = item.find('description')
                
                if title_elem is not None:
                    news_items.append({
                        'title': title_elem.text or '',
                        'description': desc_elem.text or '' if desc_elem is not None else ''
                    })
            
            logger.info(f"从 {url} 获取到 {len(news_items)} 条新闻")
            return news_items
            
        except Exception as e:
            logger.error(f"获取 RSS 失败 {url}: {e}")
            return []
    
    def extract_important_news(self, news_items: List[Dict[str, str]], category: str) -> Optional[str]:
        """
        使用 AI 从新闻列表中提取最重要的一条
        
        Args:
            news_items: 新闻列表
            category: 新闻类别（world/asia）
            
        Returns:
            最重要的新闻标题（中文）
        """
        if not news_items:
            return None
        
        # 构建新闻摘要（只取标题，避免 token 超限）
        news_summary = "\n".join([
            f"{i+1}. {item['title']}"
            for i, item in enumerate(news_items[:20])  # 只取前20条
        ])
        
        category_name = "世界" if category == "world" else "亚太地区"
        
        # 优化后的提示词
        prompt = f"""你是一位资深的国际新闻编辑。以下是今天来自纽约时报{category_name}版块的新闻标题：

{news_summary}

请从中选出 **1条** 最重要的新闻，要求：
1. 必须与经济、贸易、金融、科技发展相关
2. 对全球或区域经济有实质性影响
3. 排除纯政治、军事、意识形态类新闻
4. 排除娱乐、体育、文化类新闻

直接回复格式：
新闻标题的中文翻译（简洁版，不超过30字）

如果没有符合条件的新闻，回复：无"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是专业的国际新闻编辑，擅长从海量信息中筛选重要经济新闻。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            result = response.choices[0].message.content.strip()
            
            if result and result != "无":
                logger.info(f"{category_name}重要新闻: {result}")
                return result
            else:
                logger.warning(f"{category_name}未找到符合条件的新闻")
                return None
                
        except Exception as e:
            logger.error(f"AI 提取失败: {e}")
            return None
    
    def load_history(self) -> List[Dict]:
        """加载历史新闻"""
        if NEWS_HISTORY_FILE.exists():
            try:
                with open(NEWS_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载历史新闻失败: {e}")
                return []
        return []
    
    def save_history(self, history: List[Dict]):
        """保存历史新闻"""
        try:
            with open(NEWS_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            logger.info(f"历史新闻已保存到 {NEWS_HISTORY_FILE}")
        except Exception as e:
            logger.error(f"保存历史新闻失败: {e}")
    
    def save_latest(self, latest_news: Dict):
        """保存最新新闻（供 AI Agent 读取）"""
        try:
            with open(LATEST_NEWS_FILE, 'w', encoding='utf-8') as f:
                json.dump(latest_news, f, ensure_ascii=False, indent=2)
            logger.info(f"最新新闻已保存到 {LATEST_NEWS_FILE}")
        except Exception as e:
            logger.error(f"保存最新新闻失败: {e}")
    
    def run(self):
        """运行新闻抓取"""
        logger.info("=" * 60)
        logger.info("开始抓取新闻")
        logger.info("=" * 60)
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 加载历史记录
        history = self.load_history()
        
        # 检查今天是否已经抓取过
        if history and history[0].get('date') == today:
            logger.info(f"今天 ({today}) 的新闻已经抓取过，跳过")
            return
        
        # 抓取新闻
        results = {}
        
        for category, url in RSS_FEEDS.items():
            logger.info(f"\n正在处理 {category} 类别...")
            news_items = self.fetch_rss(url)
            
            if news_items:
                important_news = self.extract_important_news(news_items, category)
                if important_news:
                    results[category] = important_news
        
        # 如果有新闻，保存到历史和最新文件
        if results:
            # 构建记录
            record = {
                "date": today,
                "timestamp": datetime.now().isoformat(),
                "news": results
            }
            
            # 添加到历史记录（最新的在前面）
            history.insert(0, record)
            
            # 只保留最近 90 天的记录
            history = history[:90]
            
            # 保存
            self.save_history(history)
            self.save_latest(record)
            
            # 打印结果
            logger.info("\n" + "=" * 60)
            logger.info("今日重要新闻:")
            logger.info("=" * 60)
            if 'world' in results:
                logger.info(f"🌍 世界: {results['world']}")
            if 'asia' in results:
                logger.info(f"🌏 亚太: {results['asia']}")
            logger.info("=" * 60)
        else:
            logger.warning("今天没有抓取到符合条件的新闻")


def load_latest_news() -> Optional[Dict]:
    """
    便捷函数：加载最新新闻（供 AI Agent 调用）
    
    Returns:
        最新新闻字典，格式：
        {
            "date": "2025-10-13",
            "timestamp": "2025-10-13T10:30:00",
            "news": {
                "world": "世界新闻标题",
                "asia": "亚太新闻标题"
            }
        }
    """
    if not LATEST_NEWS_FILE.exists():
        return None
    
    try:
        with open(LATEST_NEWS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"读取最新新闻失败: {e}")
        return None


def format_news_for_injection() -> str:
    """
    格式化新闻用于注入到 AI 上下文
    
    Returns:
        格式化的新闻字符串，如："🌍世界: xxx  🌏亚太: xxx"
    """
    news_data = load_latest_news()
    
    if not news_data or 'news' not in news_data:
        return ""
    
    news = news_data['news']
    parts = []
    
    if 'world' in news:
        parts.append(f"🌍{news['world']}")
    if 'asia' in news:
        parts.append(f"🌏{news['asia']}")
    
    return "  ".join(parts) if parts else ""


if __name__ == "__main__":
    fetcher = NewsFetcher()
    fetcher.run()
