"""
为视频添加背景音乐
保留原视频轨道，混合音频轨道（人声 + BGM）
"""

import sys
from pathlib import Path
import subprocess


class VideoAudioMixer:
    """视频音频混音器"""
    
    def __init__(self, bgm_volume: float = 0.15):
        """
        初始化混音器
        
        Args:
            bgm_volume: 背景音乐音量 (0.0-1.0)，默认 0.15 (15%)
        """
        self.bgm_volume = bgm_volume
        print(f"🎬 视频音频混音器初始化 (BGM音量: {int(bgm_volume*100)}%)")
    
    def find_bgm(self, bgm_dir: Path = None) -> Path:
        """查找背景音乐文件"""
        if bgm_dir is None:
            bgm_dir = Path(__file__).parent / "bgm"
        
        if not bgm_dir.exists():
            print(f"⚠️  BGM目录不存在: {bgm_dir}")
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
    
    def get_duration(self, file_path: Path) -> float:
        """获取媒体文件时长（秒）"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(file_path)
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
    
    def add_bgm_to_video(self, video_file: Path, bgm_file: Path, output_file: Path = None) -> bool:
        """
        为视频添加背景音乐
        
        Args:
            video_file: 输入视频文件（带人声）
            bgm_file: 背景音乐文件
            output_file: 输出视频文件，默认在同目录生成 *_with_bgm.mp4
            
        Returns:
            是否成功
        """
        if not video_file.exists():
            print(f"❌ 视频文件不存在: {video_file}")
            return False
        
        if not bgm_file.exists():
            print(f"❌ BGM文件不存在: {bgm_file}")
            return False
        
        # 默认输出文件名
        if output_file is None:
            output_file = video_file.parent / f"{video_file.stem}_with_bgm.mp4"
        
        # 获取时长
        video_duration = self.get_duration(video_file)
        bgm_duration = self.get_duration(bgm_file)
        
        print(f"\n🎚️  开始混音...")
        print(f"📥 视频: {video_file.name} ({video_duration:.1f}秒)")
        print(f"🎵 BGM: {bgm_file.name} ({bgm_duration:.1f}秒)")
        print(f"📤 输出: {output_file.name}")
        
        # 检查BGM长度
        if bgm_duration > 0 and bgm_duration < video_duration:
            print(f"⚠️  BGM较短，将循环播放 ({int(video_duration/bgm_duration)+1} 次)")
        elif bgm_duration > 0:
            print(f"✅ BGM长度足够，将裁剪至视频长度")
        
        try:
            # ffmpeg 命令：
            # -i video: 输入视频（带人声）
            # -stream_loop -1 -i bgm: 循环播放BGM
            # -filter_complex: 混音滤镜
            #   [0:a] 是视频的音频轨道（人声）
            #   [1:a]volume={volume} 是调整后的BGM
            #   amix 混合两个音轨
            # -map 0:v: 使用原视频的视频轨道
            # -c:v copy: 视频直接复制（不重新编码，速度快）
            # -c:a aac: 音频编码为AAC
            # -shortest: 以最短的为准
            
            cmd = [
                'ffmpeg', '-y',
                '-i', str(video_file),           # 输入视频（带人声）
                '-stream_loop', '-1',             # 循环BGM
                '-i', str(bgm_file),             # 输入BGM
                '-filter_complex',
                f'[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2:weights=1.0 {self.bgm_volume}[aout]',
                '-map', '0:v',                    # 使用原视频的视频轨道
                '-map', '[aout]',                 # 使用混合后的音频
                '-c:v', 'copy',                   # 视频直接复制（不重新编码）
                '-c:a', 'aac',                    # 音频编码
                '-b:a', '192k',                   # 音频比特率
                '-shortest',                      # 以最短的为准
                str(output_file)
            ]
            
            print(f"\n⏳ 处理中...", flush=True)
            
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
                # 显示最后几行错误信息
                error_lines = result.stderr.split('\n')[-15:]
                for line in error_lines:
                    if line.strip():
                        print(f"   {line}")
                return False
                
        except FileNotFoundError:
            print(f"\n❌ 未找到 ffmpeg，请确保已安装并添加到 PATH")
            print(f"   下载地址: https://ffmpeg.org/download.html")
            return False
        except Exception as e:
            print(f"\n❌ 混音失败: {e}")
            return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="为视频添加背景音乐")
    parser.add_argument("video_file", nargs="?", help="视频文件路径")
    parser.add_argument("--bgm", help="背景音乐文件路径")
    parser.add_argument("--volume", type=float, default=0.15, 
                       help="BGM音量 (0.0-1.0)，默认 0.15")
    
    args = parser.parse_args()
    
    # 创建混音器
    mixer = VideoAudioMixer(bgm_volume=args.volume)
    
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
    
    # 处理视频文件
    if args.video_file:
        video_path = Path(args.video_file)
        
        if not video_path.exists():
            print(f"❌ 视频文件不存在: {video_path}")
            sys.exit(1)
        
        mixer.add_bgm_to_video(video_path, bgm_file)
    else:
        # 自动处理最新的视频
        broadcast_dir = Path(__file__).parent / "broadcasts"
        
        # 查找最新的子目录
        subdirs = sorted([d for d in broadcast_dir.iterdir() if d.is_dir()],
                        key=lambda p: p.stat().st_mtime,
                        reverse=True)
        
        if not subdirs:
            print("❌ broadcasts 目录下没有任何子目录")
            sys.exit(1)
        
        latest_dir = subdirs[0]
        print(f"📂 使用最新的播报目录: {latest_dir.name}\n")
        
        # 查找视频文件（不包含已经带BGM的）
        video_files = [f for f in latest_dir.glob("*.mp4") 
                      if not f.stem.endswith("_with_bgm")]
        
        if not video_files:
            print(f"❌ 未找到视频文件")
            sys.exit(1)
        
        # 使用最新的视频
        video_file = sorted(video_files, key=lambda p: p.stat().st_mtime, reverse=True)[0]
        print(f"🎬 找到视频: {video_file.name}")
        
        # 混音
        mixer.add_bgm_to_video(video_file, bgm_file)


if __name__ == "__main__":
    main()
