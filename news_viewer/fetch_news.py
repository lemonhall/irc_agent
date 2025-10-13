"""
新闻阅读器 - 带翻译和 JSON 输出
从纽约时报 RSS 获取新闻，使用 AI 翻译标题，输出 JSON 供前端渲染
"""
import json
import logging
import xml.etree.ElementTree as ET
from typing import List, Dict
from datetime import datetime
from pathlib import Path
import os

import httpx
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# RSS 源配置
RSS_FEEDS = {
    "world": {
        "name": "🌍 世界新闻",
        "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
    },
    "asia": {
        "name": "� 亚太新闻",
        "url": "https://rss.nytimes.com/services/xml/rss/nyt/AsiaPacific.xml"
    },
    "americas": {
        "name": "🗺️ 美洲新闻",
        "url": "https://rss.nytimes.com/services/xml/rss/nyt/Americas.xml"
    },
    "us": {
        "name": "🗽 美国新闻",
        "url": "https://rss.nytimes.com/services/xml/rss/nyt/US.xml"
    },
    "middleeast": {
        "name": "🕌 中东新闻",
        "url": "https://rss.nytimes.com/services/xml/rss/nyt/MiddleEast.xml"
    },
    "economy": {
        "name": "💰 经济新闻",
        "url": "https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml"
    },
    "technology": {
        "name": "💻 科技新闻",
        "url": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"
    },
    "science": {
        "name": "🔬 科学新闻",
        "url": "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml"
    }
}

# 输出路径
OUTPUT_DIR = Path(__file__).parent
OUTPUT_FILE = OUTPUT_DIR / "news.json"


class NewsReaderWithTranslation:
    """带翻译的新闻阅读器"""
    
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
            新闻列表
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
                link_elem = item.find('link')
                pubdate_elem = item.find('pubDate')
                
                if title_elem is not None and title_elem.text:
                    news_items.append({
                        'title': title_elem.text,
                        'link': link_elem.text if link_elem is not None else '',
                        'pubdate': pubdate_elem.text if pubdate_elem is not None else ''
                    })
            
            logger.info(f"从 {url} 获取到 {len(news_items)} 条新闻")
            return news_items
            
        except Exception as e:
            logger.error(f"获取 RSS 失败 {url}: {e}")
            return []
    
    def translate_titles(self, news_items: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        批量翻译新闻标题
        
        Args:
            news_items: 新闻列表
            
        Returns:
            添加了中文标题的新闻列表
        """
        if not news_items:
            return []
        
        # 构建批量翻译请求
        titles_text = "\n".join([
            f"{i+1}. {item['title']}"
            for i, item in enumerate(news_items)
        ])
        
        prompt = f"""请将以下英文新闻标题翻译成中文，要求：
1. 准确简洁，保留关键信息
2. 每条翻译不超过40字
3. 保持专业新闻语气
4. 按原序号输出，格式：序号. 中文标题

{titles_text}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是专业的新闻翻译，擅长将英文新闻标题翻译成简洁准确的中文。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            translation_text = response.choices[0].message.content.strip()
            
            # 解析翻译结果
            translated_lines = translation_text.split('\n')
            translations = {}
            
            for line in translated_lines:
                line = line.strip()
                if not line:
                    continue
                
                # 尝试匹配 "序号. 标题" 格式
                parts = line.split('.', 1)
                if len(parts) == 2:
                    try:
                        idx = int(parts[0].strip()) - 1
                        title_cn = parts[1].strip()
                        translations[idx] = title_cn
                    except ValueError:
                        continue
            
            # 将翻译添加到新闻列表
            for i, item in enumerate(news_items):
                item['title_cn'] = translations.get(i, item['title'])
            
            logger.info(f"成功翻译 {len(translations)} 条标题")
            return news_items
            
        except Exception as e:
            logger.error(f"翻译失败: {e}")
            # 翻译失败时，使用原标题
            for item in news_items:
                item['title_cn'] = item['title']
            return news_items
    
    def run(self, top_n: int = 5):
        """
        运行新闻阅读器
        
        Args:
            top_n: 每个类别获取前 N 条新闻
        """
        logger.info("=" * 60)
        logger.info("开始获取新闻")
        logger.info("=" * 60)
        
        result = {
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "categories": []
        }
        
        for category_id, config in RSS_FEEDS.items():
            logger.info(f"\n正在处理 {config['name']}...")
            
            # 获取新闻
            news_items = self.fetch_rss(config['url'])
            
            if not news_items:
                continue
            
            # 只取前 N 条
            news_items = news_items[:top_n]
            
            # 翻译标题
            news_items = self.translate_titles(news_items)
            
            # 添加到结果
            result["categories"].append({
                "id": category_id,
                "name": config["name"],
                "news": news_items
            })
        
        # 保存为 JSON
        try:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info(f"\n✅ 新闻已保存到: {OUTPUT_FILE}")
        except Exception as e:
            logger.error(f"保存 JSON 失败: {e}")
        
        # 打印摘要
        logger.info("\n" + "=" * 60)
        logger.info("新闻获取完成")
        logger.info("=" * 60)
        for category in result["categories"]:
            logger.info(f"{category['name']}: {len(category['news'])} 条")
        logger.info("=" * 60)


def main():
    """主函数"""
    import sys
    
    top_n = 5  # 默认每类显示 5 条
    
    if len(sys.argv) > 1:
        try:
            top_n = int(sys.argv[1])
        except ValueError:
            print(f"⚠️  无效的数字参数: {sys.argv[1]}，使用默认值 5")
    
    reader = NewsReaderWithTranslation()
    reader.run(top_n)


if __name__ == "__main__":
    main()
