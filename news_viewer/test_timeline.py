"""
测试音频时间轴生成功能
"""
import json
from pathlib import Path

def test_timeline():
    """测试时间轴信息"""
    # 查找最新的 broadcast.json
    broadcasts_dir = Path(__file__).parent / "broadcasts"
    
    # 获取所有子目录
    subdirs = [d for d in broadcasts_dir.iterdir() if d.is_dir()]
    if not subdirs:
        print("❌ 没有找到任何播报目录")
        return
    
    # 获取最新的目录
    latest_dir = sorted(subdirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]
    json_file = latest_dir / "broadcast.json"
    
    if not json_file.exists():
        print(f"❌ 文件不存在: {json_file}")
        return
    
    print(f"📂 读取文件: {json_file}")
    print(f"="*70)
    
    # 读取 JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 显示基本信息
    print(f"\n📊 播报信息:")
    print(f"  生成时间: {data.get('generate_time', 'N/A')}")
    print(f"  新闻时间: {data.get('news_time', 'N/A')}")
    print(f"  音频生成: {data.get('audio_generated_time', 'N/A')}")
    print(f"  总时长: {data.get('total_duration', 0):.1f} 秒 ({data.get('total_duration', 0)/60:.1f} 分钟)")
    
    # 显示时间轴
    scripts = data.get('scripts', [])
    print(f"\n🎵 音频时间轴 (共 {len(scripts)} 段):")
    print(f"="*70)
    
    for i, script in enumerate(scripts, 1):
        category = script.get('category_name', 'N/A')
        start = script.get('start_time', 0)
        end = script.get('end_time', 0)
        duration = script.get('duration', 0)
        audio_file = script.get('audio_file', 'N/A')
        
        # 格式化时间 (MM:SS)
        start_min = int(start // 60)
        start_sec = int(start % 60)
        end_min = int(end // 60)
        end_sec = int(end % 60)
        
        print(f"\n[{i}] {category}")
        print(f"    ⏱️  时间: {start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d} (时长 {duration:.1f}秒)")
        print(f"    🎵 文件: {audio_file}")
        
        # 显示文本（截断）
        script_text = script.get('script', '')
        if len(script_text) > 80:
            script_text = script_text[:80] + "..."
        print(f"    📝 内容: {script_text}")
    
    print(f"\n{'='*70}")
    print(f"✅ 时间轴测试完成！")

if __name__ == "__main__":
    test_timeline()
