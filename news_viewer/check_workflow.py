"""
工作流测试脚本
快速检查每个步骤的输出文件是否存在
"""

from pathlib import Path
from datetime import datetime

def check_workflow_status(broadcast_dir: Path = None):
    """检查工作流各步骤的完成状态"""
    
    if broadcast_dir is None:
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
    
    print("=" * 70)
    print(f"📁 检查目录: {broadcast_dir.name}")
    print("=" * 70)
    print()
    
    # 定义检查项
    checks = [
        ("1️⃣ 播报脚本", [
            ("broadcast.json", "结构化播报稿"),
            ("broadcast.txt", "纯文本播报稿"),
        ]),
        ("2️⃣ 音频文件", [
            ("broadcast_full.mp3", "完整音频（纯人声）"),
            ("broadcast_full_with_bgm.mp3", "完整音频（带BGM）"),
        ]),
        ("3️⃣ 图片文件", [
            ("image_*.jpg", "新闻背景图片（多个）"),
        ]),
        ("4️⃣ 视频文件（时间轴模式）", [
            ("video_full_merged.mp4", "合并视频（无特效）"),
            ("video_full_with_effects.mp4", "特效视频（波形）"),
            ("video_full_with_effects_with_bgm.mp4", "最终视频（含BGM）"),
        ]),
        ("5️⃣ 视频文件（传统模式）", [
            ("video_full_with_bgm.mp4", "传统单图视频"),
        ]),
    ]
    
    # 检查每个步骤
    for step_name, files in checks:
        print(f"{step_name}")
        
        for pattern, description in files:
            if "*" in pattern:
                # 通配符匹配
                matches = list(broadcast_dir.glob(pattern))
                if matches:
                    print(f"   ✅ {description}: {len(matches)} 个文件")
                    for match in matches[:3]:  # 只显示前3个
                        size_kb = match.stat().st_size / 1024
                        if size_kb > 1024:
                            size_str = f"{size_kb/1024:.1f} MB"
                        else:
                            size_str = f"{size_kb:.1f} KB"
                        print(f"      - {match.name} ({size_str})")
                    if len(matches) > 3:
                        print(f"      ... 还有 {len(matches)-3} 个")
                else:
                    print(f"   ⏭️ {description}: 未找到")
            else:
                # 精确匹配
                file_path = broadcast_dir / pattern
                if file_path.exists():
                    size_kb = file_path.stat().st_size / 1024
                    if size_kb > 1024:
                        size_str = f"{size_kb/1024:.1f} MB"
                    else:
                        size_str = f"{size_kb:.1f} KB"
                    print(f"   ✅ {description}: {size_str}")
                else:
                    print(f"   ❌ {description}: 不存在")
        
        print()
    
    # 检查 broadcast.json 中的时间轴和图片配置
    broadcast_json = broadcast_dir / "broadcast.json"
    if broadcast_json.exists():
        import json
        with open(broadcast_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        scripts = data.get("scripts", [])
        has_timeline = any("start_time" in s for s in scripts)
        has_images = any("image_file" in s for s in scripts)
        
        print("📊 配置信息")
        print(f"   片段数: {len(scripts)}")
        print(f"   总时长: {data.get('total_duration', 0):.1f} 秒")
        print(f"   时间轴: {'✅ 已配置' if has_timeline else '❌ 未配置'}")
        print(f"   图片配置: {'✅ 已配置' if has_images else '❌ 未配置'}")
        
        if has_images:
            image_count = sum(1 for s in scripts if s.get("image_file"))
            print(f"   已配图片段: {image_count}/{len(scripts)}")
        
        print()
    
    # 推荐下一步操作
    print("=" * 70)
    print("💡 下一步操作")
    print("=" * 70)
    
    if not (broadcast_dir / "broadcast_full.mp3").exists():
        print("   → 运行: python generate_audio.py")
    elif not has_images:
        print("   → 运行: python assign_images.py")
    elif not (broadcast_dir / "video_full_with_effects.mp4").exists():
        print("   → 运行: python generate_video_optimized.py")
    elif not (broadcast_dir / "video_full_with_effects_with_bgm.mp4").exists():
        print("   → 运行: python add_bgm_to_video.py")
    else:
        print("   ✅ 所有步骤已完成！")
        print("   📹 最终视频: video_full_with_effects_with_bgm.mp4")
    
    print()


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1:
        broadcast_dir = Path(sys.argv[1])
        check_workflow_status(broadcast_dir)
    else:
        check_workflow_status()


if __name__ == "__main__":
    main()
