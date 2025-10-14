"""
新闻播报图片配置工具
为每个新闻片段配置合适的背景图片
"""

import json
import os
import requests
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()


class NewsImageAssigner:
    """新闻图片配置器"""
    
    # 固定图片配置
    INTRO_IMAGE = "intro_background.jpg"  # 开场白固定图片
    OUTRO_IMAGE = None  # 结束语图片（None表示不使用）
    
    def __init__(self):
        """初始化"""
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        self.model = os.getenv("OPENAI_MODEL", "deepseek-chat")
        self.unsplash_access_key = os.getenv("UNSPLASH_ACCESS_KEY")
        
        if not self.unsplash_access_key:
            print("⚠️ 未设置 UNSPLASH_ACCESS_KEY，将使用备用图片源")
        
        print("🖼️ 新闻图片配置器初始化完成")
    
    def generate_search_keywords(self, news_title: str) -> str:
        """
        使用 AI 根据新闻标题生成图片搜索关键词
        
        Args:
            news_title: 新闻标题
            
        Returns:
            英文搜索关键词
        """
        prompt = f"""你是一位专业的图片编辑。根据以下新闻标题，生成合适的图片搜索关键词。

新闻标题：{news_title}

要求：
1. 生成 2-4 个英文关键词，用空格分隔
2. 关键词要能代表这条新闻的核心主题
3. 选择视觉效果好、适合做背景的主题
4. 避免过于具体的人物或事件，选择抽象概念
5. 优先选择：城市天际线、自然风景、科技元素、商务场景等
6. 只返回关键词，不要解释

示例：
- "乌克兰和平方案：少谈判多武器" → "military weapons conflict"
- "优衣库创始人将征服美国视为个人使命" → "business retail shopping"
- "轰炸虽停 巴勒斯坦人仍无欢庆理由" → "middle east cityscape"

请直接返回关键词："""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=50
            )
            keywords = response.choices[0].message.content.strip()
            print(f"   🔍 搜索关键词: {keywords}")
            return keywords
        except Exception as e:
            print(f"   ⚠️ AI 生成失败，使用默认关键词: {e}")
            # 降级方案：返回通用关键词
            return "news background professional"
    
    def _get_default_keywords(self, category_name: str) -> str:
        """获取默认关键词（降级方案）"""
        defaults = {
            "世界": "world news international",
            "亚太": "asia pacific cityscape",
            "美洲": "americas landscape",
            "美国": "united states capitol",
            "中东": "middle east architecture",
            "经济": "economy business finance",
            "科技": "technology digital innovation",
            "科学": "science laboratory research",
            "体育": "sports stadium",
            "文化": "culture art museum",
            "健康": "health medical wellness"
        }
        
        for key, value in defaults.items():
            if key in category_name:
                return value
        
        return "news background professional"
    
    def search_image(self, keywords: str) -> Optional[str]:
        """
        从 Unsplash 搜索图片
        
        Args:
            keywords: 搜索关键词
            
        Returns:
            图片 URL（高质量版本）
        """
        if not self.unsplash_access_key:
            return None
        
        try:
            url = "https://api.unsplash.com/search/photos"
            params = {
                "query": keywords,
                "per_page": 1,
                "orientation": "landscape",  # 横向图片
                "content_filter": "high",    # 高质量内容
            }
            headers = {
                "Authorization": f"Client-ID {self.unsplash_access_key}"
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data["results"]:
                # 获取常规质量图片（1080p）
                image_url = data["results"][0]["urls"]["regular"]
                photographer = data["results"][0]["user"]["name"]
                print(f"   ✅ 找到图片 (摄影师: {photographer})")
                return image_url
            else:
                print(f"   ⚠️ 未找到匹配的图片")
                return None
                
        except Exception as e:
            print(f"   ❌ 搜索图片失败: {e}")
            return None
    
    def download_image(self, image_url: str, output_path: Path) -> bool:
        """
        下载图片到本地
        
        Args:
            image_url: 图片 URL
            output_path: 输出路径
            
        Returns:
            是否成功
        """
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"   💾 已保存: {output_path.name}")
            return True
            
        except Exception as e:
            print(f"   ❌ 下载失败: {e}")
            return False
    
    def assign_images_to_broadcast(self, broadcast_dir: Path) -> bool:
        """
        为 broadcast.json 中的每个部分配置图片（支持分段式）
        
        Args:
            broadcast_dir: broadcast 目录路径
            
        Returns:
            是否成功
        """
        broadcast_json = broadcast_dir / "broadcast.json"
        
        if not broadcast_json.exists():
            print(f"❌ 文件不存在: {broadcast_json}")
            return False
        
        print(f"📖 读取播报配置: {broadcast_json}")
        
        # 读取 JSON
        with open(broadcast_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        scripts = data.get("scripts", [])
        if not scripts:
            print("❌ 没有找到播报脚本")
            return False
        
        print(f"🎯 找到 {len(scripts)} 个播报片段\n")
        
        # 为每个片段配置图片
        for i, script_item in enumerate(scripts):
            category_id = script_item.get("category_id", "")
            category_name = script_item.get("category_name", "")
            news_title = script_item.get("news_title", "")  # 新增：获取新闻标题
            
            print(f"[{i+1}/{len(scripts)}] {category_name}")
            if news_title:
                print(f"   📰 {news_title[:40]}...")
            
            # 特殊处理 intro 和 outro
            if category_id == "intro":
                if self.INTRO_IMAGE:
                    image_filename = self.INTRO_IMAGE
                    print(f"   📌 使用固定图片: {image_filename}")
                    script_item["image_file"] = image_filename
                else:
                    print(f"   ⏭️ 跳过（无固定图片）")
                    script_item["image_file"] = None
                continue
            
            if category_id == "outro":
                if self.OUTRO_IMAGE:
                    image_filename = self.OUTRO_IMAGE
                    print(f"   📌 使用固定图片: {image_filename}")
                    script_item["image_file"] = image_filename
                else:
                    print(f"   ⏭️ 跳过（无固定图片）")
                    script_item["image_file"] = None
                continue
            
            # 正常新闻片段：根据新闻标题生成关键词 + 搜索图片
            if news_title:
                keywords = self.generate_search_keywords(news_title)
            else:
                # 降级方案：如果没有标题，使用类别名
                keywords = self._get_default_keywords(category_name)
            
            image_url = self.search_image(keywords)
            
            if image_url:
                # 下载图片（文件名包含索引和类别）
                image_filename = f"image_{i:03d}_{category_id}.jpg"
                image_path = broadcast_dir / image_filename
                
                if self.download_image(image_url, image_path):
                    script_item["image_file"] = image_filename
                else:
                    script_item["image_file"] = None
            else:
                print(f"   ⚠️ 未配置图片（将使用默认背景）")
                script_item["image_file"] = None
            
            print()  # 空行分隔
        
        # 保存更新后的 JSON
        with open(broadcast_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已更新配置文件: {broadcast_json}")
        return True
    
    def copy_fixed_images(self, broadcast_dir: Path):
        """
        复制固定图片到 broadcast 目录
        
        Args:
            broadcast_dir: broadcast 目录路径
        """
        project_root = Path(__file__).parent
        
        # 复制 intro 图片
        if self.INTRO_IMAGE:
            src = project_root / self.INTRO_IMAGE
            dst = broadcast_dir / self.INTRO_IMAGE
            
            if src.exists():
                import shutil
                shutil.copy2(src, dst)
                print(f"📋 已复制固定图片: {self.INTRO_IMAGE}")
            else:
                print(f"⚠️ 固定图片不存在: {src}")
        
        # 复制 outro 图片
        if self.OUTRO_IMAGE:
            src = project_root / self.OUTRO_IMAGE
            dst = broadcast_dir / self.OUTRO_IMAGE
            
            if src.exists():
                import shutil
                shutil.copy2(src, dst)
                print(f"📋 已复制固定图片: {self.OUTRO_IMAGE}")
            else:
                print(f"⚠️ 固定图片不存在: {src}")


def main():
    """主函数"""
    import sys
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        broadcast_dir = Path(sys.argv[1])
    else:
        # 默认使用最新的 broadcast 目录
        broadcasts_dir = Path(__file__).parent / "broadcasts"
        if not broadcasts_dir.exists():
            print("❌ broadcasts 目录不存在")
            return
        
        # 找到最新的子目录
        subdirs = [d for d in broadcasts_dir.iterdir() if d.is_dir()]
        if not subdirs:
            print("❌ 没有找到 broadcast 子目录")
            return
        
        broadcast_dir = max(subdirs, key=lambda d: d.stat().st_mtime)
    
    print(f"📁 目标目录: {broadcast_dir}\n")
    
    # 创建配置器
    assigner = NewsImageAssigner()
    
    # 复制固定图片
    assigner.copy_fixed_images(broadcast_dir)
    
    # 配置图片
    success = assigner.assign_images_to_broadcast(broadcast_dir)
    
    if success:
        print("\n🎉 图片配置完成！")
    else:
        print("\n❌ 配置失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
