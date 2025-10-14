"""
测试图片配置功能
演示如何为 broadcast.json 配置图片
"""

from pathlib import Path
import json

def show_broadcast_info(broadcast_dir: Path):
    """显示 broadcast 信息"""
    broadcast_json = broadcast_dir / "broadcast.json"
    
    if not broadcast_json.exists():
        print(f"❌ 文件不存在: {broadcast_json}")
        return
    
    with open(broadcast_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    scripts = data.get("scripts", [])
    total_duration = data.get("total_duration", 0)
    
    print(f"📊 播报信息")
    print(f"   生成时间: {data.get('generate_time', 'Unknown')}")
    print(f"   总片段数: {len(scripts)}")
    print(f"   总时长: {total_duration:.1f} 秒")
    print()
    
    print("📋 片段详情:")
    for i, script in enumerate(scripts):
        category_name = script.get("category_name", "Unknown")
        start_time = script.get("start_time", 0)
        end_time = script.get("end_time", 0)
        duration = end_time - start_time
        image_file = script.get("image_file", None)
        
        image_status = "✅" if image_file else "⏭️"
        image_info = image_file if image_file else "(无图片)"
        
        print(f"  [{i+1:2d}] {category_name}")
        print(f"       时间: {start_time:.1f}s - {end_time:.1f}s ({duration:.1f}s)")
        print(f"       图片: {image_status} {image_info}")
        print()


def show_image_files(broadcast_dir: Path):
    """显示目录中的图片文件"""
    image_files = list(broadcast_dir.glob("*.jpg")) + list(broadcast_dir.glob("*.png"))
    
    if not image_files:
        print("📂 目录中没有图片文件")
        return
    
    print(f"📂 图片文件 ({len(image_files)} 个):")
    for img in sorted(image_files):
        size_kb = img.stat().st_size / 1024
        print(f"   {img.name} ({size_kb:.1f} KB)")
    print()


def main():
    """主函数"""
    import sys
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        broadcast_dir = Path(sys.argv[1])
    else:
        # 使用最新的 broadcast 目录
        broadcasts_dir = Path(__file__).parent / "broadcasts"
        if not broadcasts_dir.exists():
            print("❌ broadcasts 目录不存在")
            return
        
        subdirs = [d for d in broadcasts_dir.iterdir() if d.is_dir()]
        if not subdirs:
            print("❌ 没有找到 broadcast 子目录")
            return
        
        broadcast_dir = max(subdirs, key=lambda d: d.stat().st_mtime)
    
    print("=" * 60)
    print(f"📁 目标目录: {broadcast_dir.name}")
    print("=" * 60)
    print()
    
    # 显示信息
    show_broadcast_info(broadcast_dir)
    show_image_files(broadcast_dir)
    
    # 检查视频文件
    video_files = list(broadcast_dir.glob("*.mp4"))
    if video_files:
        print(f"🎬 视频文件 ({len(video_files)} 个):")
        for video in sorted(video_files):
            size_mb = video.stat().st_size / 1024 / 1024
            print(f"   {video.name} ({size_mb:.1f} MB)")
        print()
    
    print("=" * 60)
    print("💡 提示:")
    print("   1. 运行 assign_images.py 配置图片")
    print("   2. 运行 generate_video_with_timeline.py 生成视频")
    print("   3. 或使用: .\\run_workflow.ps1 -UseTimeline")
    print("=" * 60)


if __name__ == "__main__":
    main()
