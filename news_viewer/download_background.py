"""
下载新闻播报默认背景图片
支持从 Unsplash 或 Pexels 等免费图片源下载
"""

import os
import requests
from pathlib import Path


def download_unsplash_image(
    query: str = "news broadcast studio",
    filename: str = "news_background.jpg",
    width: int = 1280,
    height: int = 720
):
    """
    从 Unsplash 下载背景图片
    
    Args:
        query: 搜索关键词
        filename: 保存的文件名
        width: 图片宽度
        height: 图片高度
    """
    # Unsplash Source API（无需API Key）
    url = f"https://source.unsplash.com/{width}x{height}/?{query.replace(' ', ',')}"
    
    output_path = Path(__file__).parent / filename
    
    print(f"📥 正在下载背景图片...")
    print(f"   来源: Unsplash")
    print(f"   关键词: {query}")
    print(f"   尺寸: {width}x{height}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        size_kb = output_path.stat().st_size / 1024
        print(f"✅ 下载成功: {output_path.name} ({size_kb:.1f} KB)")
        return True
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return False


def create_gradient_background(
    filename: str = "news_background.jpg",
    width: int = 1280,
    height: int = 720,
    color1: str = "#1a1a2e",  # 深蓝
    color2: str = "#0f3460"   # 稍浅的蓝
):
    """
    使用 PIL 创建渐变背景图片（如果没有网络）
    
    Args:
        filename: 保存的文件名
        width: 图片宽度
        height: 图片高度
        color1: 起始颜色（十六进制）
        color2: 结束颜色（十六进制）
    """
    try:
        from PIL import Image, ImageDraw
        
        output_path = Path(__file__).parent / filename
        
        print(f"🎨 创建渐变背景...")
        
        # 创建图片
        image = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(image)
        
        # 解析颜色
        r1 = int(color1[1:3], 16)
        g1 = int(color1[3:5], 16)
        b1 = int(color1[5:7], 16)
        
        r2 = int(color2[1:3], 16)
        g2 = int(color2[3:5], 16)
        b2 = int(color2[5:7], 16)
        
        # 绘制垂直渐变
        for y in range(height):
            ratio = y / height
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # 保存
        image.save(output_path, quality=95)
        
        size_kb = output_path.stat().st_size / 1024
        print(f"✅ 创建成功: {output_path.name} ({size_kb:.1f} KB)")
        return True
        
    except ImportError:
        print("❌ 需要安装 Pillow: pip install Pillow")
        return False
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 50)
    print("新闻播报背景图片下载器")
    print("=" * 50)
    print()
    
    # 预设的主题
    themes = {
        "1": ("news broadcast studio", "新闻演播室"),
        "2": ("modern office", "现代办公室"),
        "3": ("abstract technology", "科技抽象"),
        "4": ("gradient", "纯色渐变（本地生成）"),
    }
    
    print("可用主题:")
    for key, (query, name) in themes.items():
        print(f"  {key}. {name}")
    print()
    
    choice = input("请选择主题 (1-4，默认1): ").strip() or "1"
    
    if choice == "4":
        # 本地生成渐变
        create_gradient_background()
    elif choice in themes:
        query, _ = themes[choice]
        success = download_unsplash_image(query)
        
        if not success:
            print()
            print("⚠️ 网络下载失败，尝试本地生成...")
            create_gradient_background()
    else:
        print("❌ 无效选择")


if __name__ == "__main__":
    main()
