"""
AI 新闻播报员 - 将新闻转换为播报稿（分段式）
读取 news.json，为每条新闻生成独立的播报稿
"""
import json
import logging
from pathlib import Path
from datetime import datetime
import os

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

# 文件路径
NEWS_JSON = Path(__file__).parent / "news.json"
OUTPUT_DIR = Path(__file__).parent / "broadcasts"
OUTPUT_DIR.mkdir(exist_ok=True)


class NewsAnchor:
    """AI 新闻播报员"""
    
    def __init__(self):
        """初始化"""
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    def load_news(self) -> dict:
        """加载新闻数据"""
        try:
            with open(NEWS_JSON, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载新闻失败: {e}")
            return None
    
    def generate_single_news_script(self, news_title: str, category_name: str) -> str:
        """
        为单条新闻生成播报稿
        
        Args:
            news_title: 新闻标题
            category_name: 类别名称
            
        Returns:
            播报稿文本
        """
        prompt = f"""你是一位专业的新闻播音员。请根据以下新闻标题，创作一段简短的播报稿。

类别：{category_name}
新闻标题：{news_title}

要求：
1. 简洁明了，直接播报新闻要点
2. 语言口语化、自然，适合语音播报
3. 控制在 30-50 字以内
4. 不要使用"据报道"等字眼，直接陈述内容
5. 不要添加开场或结束语，只播报新闻本身
6. 使用新闻播报的专业语气

直接返回播报稿："""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是专业的新闻播音员，擅长将新闻标题转换为简洁的播报稿。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            script = response.choices[0].message.content.strip()
            return script
            
        except Exception as e:
            logger.error(f"生成播报稿失败: {e}")
            return None
    
    def run(self):
        """运行新闻播报员（分段式）"""
        logger.info("=" * 60)
        logger.info("🎙️  AI 新闻播报员启动（分段式）")
        logger.info("=" * 60)
        
        # 加载新闻
        news_data = self.load_news()
        if not news_data:
            logger.error("无法加载新闻数据")
            return
        
        logger.info(f"📰 新闻更新时间: {news_data['update_time']}")
        logger.info(f"📊 共 {len(news_data['categories'])} 个类别\n")
        
        # 生成播报稿
        broadcasts = {
            "generate_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "news_time": news_data["update_time"],
            "scripts": []
        }
        
        # 添加开场白
        broadcasts["scripts"].append({
            "category_id": "intro",
            "category_name": "🎙️ 开场白",
            "script": "欢迎收听新闻播报。以下是今日的新闻内容。",
            "news_index": None
        })
        
        # 为每个类别的每条新闻生成播报稿
        total_news = 0
        for category in news_data["categories"]:
            category_name = category["name"]
            category_id = category["id"]
            news_items = category["news"]
            
            logger.info(f"\n处理 {category_name}（共 {len(news_items)} 条）")
            
            for idx, news_item in enumerate(news_items):
                news_title = news_item["title_cn"]
                logger.info(f"  [{idx+1}/{len(news_items)}] {news_title[:30]}...")
                
                script = self.generate_single_news_script(news_title, category_name)
                
                if script:
                    broadcasts["scripts"].append({
                        "category_id": category_id,
                        "category_name": category_name,
                        "script": script,
                        "news_index": idx,
                        "news_title": news_title,
                        "news_link": news_item.get("link", "")
                    })
                    total_news += 1
                    logger.info(f"     ✅ 已生成 ({len(script)} 字)")
                else:
                    logger.warning(f"     ⚠️ 生成失败，跳过")
        
        # 创建以时间戳命名的子目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        broadcast_dir = OUTPUT_DIR / timestamp
        broadcast_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存为 JSON
        json_file = broadcast_dir / "broadcast.json"
        
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(broadcasts, f, ensure_ascii=False, indent=2)
            logger.info(f"\n✅ 播报稿已保存到: {json_file}")
        except Exception as e:
            logger.error(f"保存播报稿失败: {e}")
        
        # 同时保存一份纯文本版本（方便查看）
        txt_file = broadcast_dir / "broadcast.txt"
        
        try:
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(f"新闻播报稿（分段式）\n")
                f.write(f"生成时间: {broadcasts['generate_time']}\n")
                f.write(f"新闻时间: {broadcasts['news_time']}\n")
                f.write("=" * 60 + "\n\n")
                
                current_category = None
                for i, script_data in enumerate(broadcasts["scripts"], 1):
                    # 如果是新的类别，添加类别标题
                    if script_data["category_name"] != current_category:
                        current_category = script_data["category_name"]
                        f.write(f"\n【{current_category}】\n")
                        f.write("-" * 60 + "\n")
                    
                    # 写入播报稿
                    if script_data.get("news_title"):
                        f.write(f"  标题: {script_data['news_title']}\n")
                    f.write(f"  播报: {script_data['script']}\n\n")
            
            logger.info(f"✅ 纯文本版本已保存到: {txt_file}")
        except Exception as e:
            logger.error(f"保存纯文本版本失败: {e}")
        
        # 打印摘要
        logger.info("\n" + "=" * 60)
        logger.info("📻 播报稿生成完成")
        logger.info("=" * 60)
        
        logger.info(f"共生成 {len(broadcasts['scripts'])} 段播报稿")
        logger.info(f"涵盖 {total_news} 条新闻")
        total_chars = sum(len(s["script"]) for s in broadcasts["scripts"])
        logger.info(f"总字数: {total_chars} 字")
        logger.info(f"预计播报时长: {total_chars / 4:.1f} 秒 (按每秒 4 字计算)")
        logger.info("=" * 60)


def main():
    """主函数"""
    anchor = NewsAnchor()
    anchor.run()


if __name__ == "__main__":
    main()
