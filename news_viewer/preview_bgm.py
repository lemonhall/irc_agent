"""
BGM 效果预览工具
快速生成 30 秒试听片段，测试不同 BGM 和音量
"""

import sys
from pathlib import Path
import subprocess


def create_preview(voice_file: Path, bgm_file: Path, volume: float = 0.15, 
                   duration: int = 30, output_file: Path = None):
    """
    创建 BGM 混音预览片段
    
    Args:
        voice_file: 人声文件
        bgm_file: BGM 文件
        volume: BGM 音量
        duration: 预览时长（秒）
        output_file: 输出文件
    """
    if output_file is None:
        output_file = Path("bgm_preview.mp3")
    
    print(f"🎧 创建预览片段...")
    print(f"📥 人声: {voice_file.name}")
    print(f"🎵 BGM: {bgm_file.name}")
    print(f"🔊 音量: {int(volume*100)}%")
    print(f"⏱️  时长: {duration}秒")
    
    try:
        cmd = [
            'ffmpeg',
            '-i', str(voice_file),
            '-stream_loop', '-1',
            '-i', str(bgm_file),
            '-filter_complex',
            f'[1:a]volume={volume}[bg];[0:a][bg]amix=inputs=2:duration=first:dropout_transition=2',
            '-t', str(duration),  # 限制时长
            '-codec:a', 'libmp3lame',
            '-q:a', '2',
            '-y',
            str(output_file)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        
        if result.returncode == 0:
            print(f"\n✅ 预览已生成: {output_file}")
            print(f"💡 试听后可调整 --volume 参数")
            return True
        else:
            print(f"\n❌ 生成失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="BGM效果预览工具")
    parser.add_argument("voice_file", nargs="?", help="人声音频文件")
    parser.add_argument("--bgm", help="BGM文件路径")
    parser.add_argument("--volume", type=float, default=0.15, help="BGM音量 (0.0-1.0)")
    parser.add_argument("--duration", type=int, default=30, help="预览时长（秒）")
    parser.add_argument("--output", help="输出文件名")
    
    args = parser.parse_args()
    
    # 查找人声文件
    if args.voice_file:
        voice_file = Path(args.voice_file)
    else:
        # 使用最新播报的完整音频
        broadcast_dir = Path(__file__).parent / "broadcasts"
        subdirs = sorted([d for d in broadcast_dir.iterdir() if d.is_dir()],
                        key=lambda p: p.stat().st_mtime, reverse=True)
        
        if not subdirs:
            print("❌ 未找到播报目录")
            sys.exit(1)
        
        voice_file = subdirs[0] / "broadcast_full.mp3"
        if not voice_file.exists():
            print(f"❌ 未找到音频文件")
            sys.exit(1)
        
        print(f"📂 使用: {subdirs[0].name}/broadcast_full.mp3")
    
    if not voice_file.exists():
        print(f"❌ 文件不存在: {voice_file}")
        sys.exit(1)
    
    # 查找 BGM
    if args.bgm:
        bgm_file = Path(args.bgm)
    else:
        bgm_dir = Path(__file__).parent / "bgm"
        audio_exts = ['.mp3', '.wav', '.m4a', '.flac', '.ogg']
        bgm_files = []
        for ext in audio_exts:
            bgm_files.extend(bgm_dir.glob(f"*{ext}"))
        
        if not bgm_files:
            print(f"❌ 在 bgm/ 目录中未找到音频文件")
            print(f"💡 请先放入 BGM 文件")
            sys.exit(1)
        
        bgm_file = bgm_files[0]
    
    if not bgm_file.exists():
        print(f"❌ BGM文件不存在: {bgm_file}")
        sys.exit(1)
    
    # 输出文件
    if args.output:
        output_file = Path(args.output)
    else:
        output_file = Path(f"preview_vol{int(args.volume*100)}.mp3")
    
    # 创建预览
    create_preview(voice_file, bgm_file, args.volume, args.duration, output_file)


if __name__ == "__main__":
    main()
