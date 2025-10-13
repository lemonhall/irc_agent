"""
为新闻播报音频添加背景音乐
使用 ffmpeg 将 BGM 混入完整播报音频
"""

import os
import sys
from pathlib import Path
import subprocess
from datetime import datetime


class AudioMixer:
    """音频混音器"""
    
    def __init__(self, bgm_volume: float = 0.15):
        """
        初始化混音器
        
        Args:
            bgm_volume: 背景音乐音量 (0.0-1.0)，默认 0.15 (15%)
        """
        self.bgm_volume = bgm_volume
        print(f"🎵 音频混音器初始化 (BGM音量: {int(bgm_volume*100)}%)")
    
    def find_bgm(self, bgm_dir: Path = None) -> Path:
        """
        查找背景音乐文件
        
        Args:
            bgm_dir: BGM目录路径，默认为 news_viewer/bgm/
            
        Returns:
            BGM文件路径
        """
        if bgm_dir is None:
            bgm_dir = Path(__file__).parent / "bgm"
        
        if not bgm_dir.exists():
            print(f"⚠️  BGM目录不存在: {bgm_dir}")
            print(f"   创建目录并放入背景音乐文件（支持 mp3, wav, m4a, flac）")
            bgm_dir.mkdir(parents=True, exist_ok=True)
            return None
        
        # 支持的音频格式
        audio_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg']
        
        # 查找音频文件
        bgm_files = []
        for ext in audio_extensions:
            bgm_files.extend(bgm_dir.glob(f"*{ext}"))
        
        if not bgm_files:
            print(f"⚠️  在 {bgm_dir} 中未找到音频文件")
            return None
        
        # 使用第一个找到的文件
        bgm_file = bgm_files[0]
        print(f"🎼 使用背景音乐: {bgm_file.name}")
        
        return bgm_file
    
    def get_audio_duration(self, audio_file: Path) -> float:
        """
        获取音频时长（秒）
        
        Args:
            audio_file: 音频文件路径
            
        Returns:
            时长（秒）
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(audio_file)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode == 0:
                return float(result.stdout.strip())
            else:
                return 0.0
                
        except Exception:
            return 0.0
    
    def mix_audio(self, voice_file: Path, bgm_file: Path, output_file: Path = None) -> bool:
        """
        混合人声和背景音乐
        
        Args:
            voice_file: 人声音频文件
            bgm_file: 背景音乐文件
            output_file: 输出文件路径，默认在同目录生成 *_with_bgm.mp3
            
        Returns:
            是否成功
        """
        if not voice_file.exists():
            print(f"❌ 人声文件不存在: {voice_file}")
            return False
        
        if not bgm_file.exists():
            print(f"❌ BGM文件不存在: {bgm_file}")
            return False
        
        # 默认输出文件名
        if output_file is None:
            output_file = voice_file.parent / f"{voice_file.stem}_with_bgm{voice_file.suffix}"
        
        # 获取音频时长
        voice_duration = self.get_audio_duration(voice_file)
        bgm_duration = self.get_audio_duration(bgm_file)
        
        print(f"\n🎚️  开始混音...")
        print(f"📥 人声: {voice_file.name} ({voice_duration:.1f}秒)")
        print(f"🎵 BGM: {bgm_file.name} ({bgm_duration:.1f}秒)")
        print(f"📤 输出: {output_file.name}")
        
        # 检查BGM长度
        if bgm_duration > 0 and bgm_duration < voice_duration:
            print(f"⚠️  BGM较短，将循环播放 ({int(voice_duration/bgm_duration)+1} 次)")
        elif bgm_duration > 0:
            print(f"✅ BGM长度足够，将裁剪至人声长度")
        
        try:
            # 使用 ffmpeg 混音
            # -stream_loop -1: 循环播放BGM（如果BGM较短）
            # -shortest: 以最短的音轨为准（即人声长度）
            # -filter_complex: 混音滤镜
            #   [1:a]volume={bgm_volume}: 调整BGM音量
            #   [0:a][1:a]amix=inputs=2:duration=first: 混合两个音轨
            cmd = [
                'ffmpeg',
                '-i', str(voice_file),           # 输入1: 人声
                '-stream_loop', '-1',             # 循环BGM
                '-i', str(bgm_file),             # 输入2: BGM
                '-filter_complex',
                f'[1:a]volume={self.bgm_volume}[bg];[0:a][bg]amix=inputs=2:duration=first:dropout_transition=2',
                '-codec:a', 'libmp3lame',        # 输出编码
                '-q:a', '2',                      # 音质 (VBR 2 = ~190 kbps)
                '-shortest',                      # 以最短的为准
                '-y',                             # 覆盖已存在文件
                str(output_file)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode == 0:
                file_size = output_file.stat().st_size / 1024 / 1024  # MB
                print(f"\n✅ 混音完成！")
                print(f"📦 文件大小: {file_size:.2f} MB")
                print(f"📁 保存位置: {output_file}")
                return True
            else:
                print(f"\n❌ ffmpeg错误:")
                print(result.stderr)
                return False
                
        except FileNotFoundError:
            print(f"\n❌ 未找到 ffmpeg，请确保已安装并添加到 PATH")
            print(f"   下载地址: https://ffmpeg.org/download.html")
            return False
        except Exception as e:
            print(f"\n❌ 混音失败: {e}")
            return False
    
    def batch_mix(self, broadcast_dir: Path, bgm_file: Path = None):
        """
        批量为播报目录中的音频添加背景音乐
        
        Args:
            broadcast_dir: 播报目录
            bgm_file: BGM文件，如果为None则自动查找
        """
        if not broadcast_dir.exists() or not broadcast_dir.is_dir():
            print(f"❌ 目录不存在: {broadcast_dir}")
            return
        
        # 查找BGM
        if bgm_file is None:
            bgm_file = self.find_bgm()
            if bgm_file is None:
                return
        
        # 查找所有MP3文件（排除已经带BGM的）
        mp3_files = [f for f in broadcast_dir.glob("*.mp3") 
                    if not f.stem.endswith("_with_bgm")]
        
        if not mp3_files:
            print(f"❌ 在 {broadcast_dir} 中未找到音频文件")
            return
        
        print(f"\n📊 找到 {len(mp3_files)} 个音频文件")
        success_count = 0
        
        for i, mp3_file in enumerate(mp3_files, 1):
            print(f"\n{'='*60}")
            print(f"处理 [{i}/{len(mp3_files)}]: {mp3_file.name}")
            
            if self.mix_audio(mp3_file, bgm_file):
                success_count += 1
        
        print(f"\n{'='*60}")
        print(f"🎉 批量混音完成！成功 {success_count}/{len(mp3_files)} 个文件")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="为新闻播报音频添加背景音乐")
    parser.add_argument("audio_file", nargs="?", help="音频文件或播报目录")
    parser.add_argument("--bgm", help="背景音乐文件路径")
    parser.add_argument("--volume", type=float, default=0.15, 
                       help="BGM音量 (0.0-1.0)，默认 0.15")
    parser.add_argument("--batch", action="store_true", 
                       help="批量处理目录中的所有音频")
    parser.add_argument("--today", action="store_true",
                       help="处理今天的播报")
    
    args = parser.parse_args()
    
    # 创建混音器
    mixer = AudioMixer(bgm_volume=args.volume)
    
    # 查找BGM
    if args.bgm:
        bgm_file = Path(args.bgm)
        if not bgm_file.exists():
            print(f"❌ BGM文件不存在: {bgm_file}")
            sys.exit(1)
    else:
        bgm_file = mixer.find_bgm()
        if bgm_file is None:
            print("\n💡 提示: 请在 news_viewer/bgm/ 目录中放入背景音乐文件")
            sys.exit(1)
    
    # 处理今天的播报
    if args.today:
        today = datetime.now().strftime("%Y%m%d")
        broadcast_dir = Path(__file__).parent / "broadcasts"
        
        # 查找今天的目录
        today_dirs = [d for d in broadcast_dir.iterdir() 
                     if d.is_dir() and d.name.startswith(today)]
        
        if not today_dirs:
            print(f"❌ 未找到今天的播报目录 (日期: {today})")
            sys.exit(1)
        
        # 使用最新的
        latest_dir = sorted(today_dirs, reverse=True)[0]
        print(f"📂 处理今天的播报: {latest_dir.name}")
        
        mixer.batch_mix(latest_dir, bgm_file)
        return
    
    # 处理指定文件或目录
    if args.audio_file:
        audio_path = Path(args.audio_file)
        
        # 如果是目录名（相对于broadcasts）
        if not audio_path.exists():
            broadcasts_dir = Path(__file__).parent / "broadcasts"
            audio_path = broadcasts_dir / args.audio_file
        
        if not audio_path.exists():
            print(f"❌ 文件或目录不存在: {audio_path}")
            sys.exit(1)
        
        # 批量处理目录
        if audio_path.is_dir() or args.batch:
            if audio_path.is_file():
                audio_path = audio_path.parent
            mixer.batch_mix(audio_path, bgm_file)
        else:
            # 处理单个文件
            mixer.mix_audio(audio_path, bgm_file)
    else:
        # 自动处理最新的播报完整音频
        broadcast_dir = Path(__file__).parent / "broadcasts"
        
        # 查找最新的子目录
        subdirs = sorted([d for d in broadcast_dir.iterdir() if d.is_dir()],
                        key=lambda p: p.stat().st_mtime,
                        reverse=True)
        
        if not subdirs:
            print("❌ broadcasts 目录下没有任何子目录")
            sys.exit(1)
        
        latest_dir = subdirs[0]
        print(f"📂 使用最新的播报目录: {latest_dir.name}")
        
        # 查找完整音频
        full_audio = latest_dir / "broadcast_full.mp3"
        
        if not full_audio.exists():
            print(f"❌ 未找到完整音频: {full_audio.name}")
            sys.exit(1)
        
        # 混音
        mixer.mix_audio(full_audio, bgm_file)


if __name__ == "__main__":
    main()
