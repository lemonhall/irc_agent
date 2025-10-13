"""
AI 新闻播报员 - 将新闻转换为播报稿
读取 news.json，使用 AI 整合成适合语音播报的中文稿件
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
    
    def generate_broadcast_script(self, category_name: str, news_items: list) -> str:
        """
        为一个类别生成播报稿
        
        Args:
            category_name: 类别名称
            news_items: 该类别的新闻列表
            
        Returns:
            播报稿文本
        """
        # 构建新闻摘要
        news_summary = "\n".join([
            f"{i+1}. {item['title_cn']}"
            for i, item in enumerate(news_items)
        ])
        
        prompt = f"""你是一位专业的新闻播音员。请根据以下 {category_name} 的新闻标题，创作一段自然流畅的播报稿。

新闻标题：
{news_summary}

要求：
1. 将这些新闻整合成一段连贯的播报文稿，不要逐条罗列
2. 语言要口语化、自然，适合语音播报
3. 突出重点新闻，次要新闻可以简略带过
4. 使用新闻播报的专业语气，但不要过于正式刻板
5. 控制在 150-200 字以内
6. 不要使用"据纽约时报报道"等字眼，直接播报内容
7. 开头不要说"以下是XXX新闻"，直接进入内容

示例风格：
"乌克兰无人机继续对俄罗斯炼油设施展开打击，给俄罗斯能源供应带来压力。与此同时，中东局势出现缓和迹象，多名人质获释..."

请直接输出播报稿文本，不要任何前缀或解释。"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是专业的新闻播音员，擅长将新闻整合成流畅自然的播报稿。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            script = response.choices[0].message.content.strip()
            logger.info(f"✅ {category_name} 播报稿已生成 ({len(script)} 字)")
            return script
            
        except Exception as e:
            logger.error(f"生成播报稿失败 {category_name}: {e}")
            return None
    
    def run(self):
        """运行新闻播报员"""
        logger.info("=" * 60)
        logger.info("🎙️  AI 新闻播报员启动")
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
        
        for category in news_data["categories"]:
            category_name = category["name"]
            news_items = category["news"]
            
            logger.info(f"正在生成 {category_name} 播报稿...")
            
            script = self.generate_broadcast_script(category_name, news_items)
            
            if script:
                broadcasts["scripts"].append({
                    "category_id": category["id"],
                    "category_name": category_name,
                    "script": script,
                    "news_count": len(news_items)
                })
        
        # 保存为 JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = OUTPUT_DIR / f"broadcast_{timestamp}.json"
        
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(broadcasts, f, ensure_ascii=False, indent=2)
            logger.info(f"\n✅ 播报稿已保存到: {json_file}")
        except Exception as e:
            logger.error(f"保存播报稿失败: {e}")
        
        # 同时保存一份纯文本版本（方便查看和 TTS）
        txt_file = OUTPUT_DIR / f"broadcast_{timestamp}.txt"
        
        try:
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(f"新闻播报稿\n")
                f.write(f"生成时间: {broadcasts['generate_time']}\n")
                f.write(f"新闻时间: {broadcasts['news_time']}\n")
                f.write("=" * 60 + "\n\n")
                
                for i, script_data in enumerate(broadcasts["scripts"], 1):
                    f.write(f"【{script_data['category_name']}】\n")
                    f.write(f"{script_data['script']}\n\n")
                    f.write("-" * 60 + "\n\n")
            
            logger.info(f"✅ 纯文本版本已保存到: {txt_file}")
        except Exception as e:
            logger.error(f"保存纯文本版本失败: {e}")
        
        # 打印摘要
        logger.info("\n" + "=" * 60)
        logger.info("📻 播报稿生成完成")
        logger.info("=" * 60)
        
        total_chars = sum(len(s["script"]) for s in broadcasts["scripts"])
        logger.info(f"共生成 {len(broadcasts['scripts'])} 段播报稿")
        logger.info(f"总字数: {total_chars} 字")
        logger.info(f"预计播报时长: {total_chars / 4:.1f} 秒 (按每秒 4 字计算)")
        logger.info("=" * 60)
        
        # 打印预览
        logger.info("\n📄 播报稿预览：\n")
        for script_data in broadcasts["scripts"]:
            logger.info(f"【{script_data['category_name']}】")
            logger.info(f"{script_data['script']}\n")


def main():
    """主函数"""
    anchor = NewsAnchor()
    anchor.run()


if __name__ == "__main__":
    main()
