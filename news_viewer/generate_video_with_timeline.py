"""
新闻播报视频生成工具（时间轴版本）
根据 broadcast.json 的时间轴，为每个片段使用不同的背景图片
"""

import json
import subprocess
from pathlib import Path
from typing import Optional, Literal

VisualEffect = Literal["none", "wave", "spectrum", "vectorscope"]


class TimelineVideoGenerator:
    """基于时间轴的视频生成器"""
    
    DEFAULT_WIDTH = 1280
    DEFAULT_HEIGHT = 720
    DEFAULT_BG_COLOR = "0x1a1a2e"  # 深蓝色背景
    
    # 可视化效果颜色方案
    COLOR_SCHEMES = {
        "default": "white",
        "gradient": "0xff0000|0x00ff00|0x0000ff",
        "blue": "0x1e90ff",
        "gold": "0xffd700",
        "tech": "0x00ffff|0x00ff00"
    }
    
    def __init__(self):
        """初始化"""
        self.check_dependencies()
        print("🎬 时间轴视频生成器初始化完成")
    
    def check_dependencies(self):
        """检查 ffmpeg"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                check=True
            )
            version_line = result.stdout.split("\n")[0]
            print(f"✅ ffmpeg 已安装: {version_line}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ 错误: ffmpeg 未安装")
            raise RuntimeError("ffmpeg 不可用")
    
    def generate_video_from_broadcast(
        self,
        broadcast_dir: Path,
        effect: VisualEffect = "wave",
        color_scheme: str = "default",
        video_quality: int = 23
    ) -> bool:
        """
        根据 broadcast.json 生成带时间轴图片切换的视频
        
        Args:
            broadcast_dir: broadcast 目录
            effect: 视觉效果
            color_scheme: 颜色方案
            video_quality: 视频质量
            
        Returns:
            是否成功
        """
        # 读取 broadcast.json
        broadcast_json = broadcast_dir / "broadcast.json"
        if not broadcast_json.exists():
            print(f"❌ 文件不存在: {broadcast_json}")
            return False
        
        with open(broadcast_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        scripts = data.get("scripts", [])
        if not scripts:
            print("❌ 没有找到播报脚本")
            return False
        
        # 查找音频文件
        audio_file = None
        for filename in [
            "broadcast_full_with_bgm.mp3",
            "audio_full_with_bgm.mp3",
            "broadcast_full.mp3",
            "audio_full.mp3"
        ]:
            audio_path = broadcast_dir / filename
            if audio_path.exists():
                audio_file = audio_path
                print(f"📢 音频文件: {filename}")
                break
        
        if not audio_file:
            print(f"❌ 未找到音频文件")
            return False
        
        # 输出文件
        output_path = broadcast_dir / "video_full_timeline.mp4"
        
        print(f"🎬 开始生成时间轴视频...")
        print(f"   片段数: {len(scripts)}")
        print(f"   总时长: {data.get('total_duration', 0):.1f}秒")
        print(f"   效果: {effect}\n")
        
        # 生成视频
        return self._generate_timeline_video(
            audio_path=audio_file,
            broadcast_dir=broadcast_dir,
            scripts=scripts,
            output_path=output_path,
            effect=effect,
            color_scheme=color_scheme,
            video_quality=video_quality
        )
    
    def _generate_timeline_video(
        self,
        audio_path: Path,
        broadcast_dir: Path,
        scripts: list,
        output_path: Path,
        effect: VisualEffect,
        color_scheme: str,
        video_quality: int
    ) -> bool:
        """生成时间轴视频"""
        
        # 为每个片段生成临时视频
        temp_videos = []
        
        for i, script in enumerate(scripts):
            print(f"[{i+1}/{len(scripts)}] {script.get('category_name', 'Unknown')}")
            
            # 获取图片路径
            image_file = script.get("image_file")
            if image_file:
                image_path = broadcast_dir / image_file
                if not image_path.exists():
                    print(f"   ⚠️ 图片不存在: {image_file}，使用纯色背景")
                    image_path = None
            else:
                image_path = None
            
            # 获取时间信息
            start_time = script.get("start_time", 0)
            end_time = script.get("end_time", 0)
            duration = end_time - start_time
            
            if duration <= 0:
                print(f"   ⚠️ 时长无效，跳过")
                continue
            
            # 生成临时视频片段
            temp_video = broadcast_dir / f"temp_video_{i:02d}.mp4"
            success = self._generate_video_segment(
                audio_path=audio_path,
                image_path=image_path,
                output_path=temp_video,
                start_time=start_time,
                duration=duration,
                effect=effect,
                color_scheme=color_scheme,
                video_quality=video_quality
            )
            
            if success:
                temp_videos.append(temp_video)
                print(f"   ✅ 片段生成成功")
            else:
                print(f"   ❌ 片段生成失败")
                return False
        
        if not temp_videos:
            print("❌ 没有生成任何视频片段")
            return False
        
        # 合并所有视频片段
        print(f"\n🔗 合并 {len(temp_videos)} 个视频片段...")
        success = self._concat_videos(temp_videos, output_path)
        
        # 清理临时文件
        print("🧹 清理临时文件...")
        for temp_video in temp_videos:
            try:
                temp_video.unlink()
            except Exception as e:
                print(f"   ⚠️ 无法删除: {temp_video.name}")
        
        if success:
            print(f"\n✅ 视频生成完成: {output_path.name}")
        else:
            print(f"\n❌ 视频合并失败")
        
        return success
    
    def _generate_video_segment(
        self,
        audio_path: Path,
        image_path: Optional[Path],
        output_path: Path,
        start_time: float,
        duration: float,
        effect: VisualEffect,
        color_scheme: str,
        video_quality: int
    ) -> bool:
        """生成单个视频片段"""
        
        colors = self.COLOR_SCHEMES.get(color_scheme, self.COLOR_SCHEMES["default"])
        
        # 裁剪音频
        if image_path:
            # 使用图片背景
            if effect == "none":
                filter_complex = f"[1:v]scale={self.DEFAULT_WIDTH}:{self.DEFAULT_HEIGHT}:force_original_aspect_ratio=increase,crop={self.DEFAULT_WIDTH}:{self.DEFAULT_HEIGHT}[out]"
            else:
                filter_complex = self._build_filter_with_image(effect, colors)
            
            cmd = [
                "ffmpeg", "-y",
                "-ss", str(start_time),
                "-t", str(duration),
                "-i", str(audio_path),
                "-loop", "1",
                "-i", str(image_path),
                "-filter_complex", filter_complex,
                "-map", "[out]",
                "-map", "0:a",
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", str(video_quality),
                "-c:a", "aac",
                "-b:a", "192k",
                "-pix_fmt", "yuv420p",
                "-shortest",
                str(output_path)
            ]
        else:
            # 使用纯色背景
            if effect == "none":
                filter_complex = f"color=c={self.DEFAULT_BG_COLOR}:s={self.DEFAULT_WIDTH}x{self.DEFAULT_HEIGHT}[out]"
            else:
                filter_complex = self._build_filter_with_color(effect, colors)
            
            cmd = [
                "ffmpeg", "-y",
                "-ss", str(start_time),
                "-t", str(duration),
                "-i", str(audio_path),
                "-filter_complex", filter_complex,
                "-map", "[out]",
                "-map", "0:a",
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", str(video_quality),
                "-c:a", "aac",
                "-b:a", "192k",
                "-pix_fmt", "yuv420p",
                str(output_path)
            ]
        
        return self._run_ffmpeg(cmd)
    
    def _build_filter_with_image(self, effect: VisualEffect, colors: str) -> str:
        """构建带图片的滤镜"""
        # 缩放并裁剪图片
        bg = f"[1:v]scale={self.DEFAULT_WIDTH}:{self.DEFAULT_HEIGHT}:force_original_aspect_ratio=increase,crop={self.DEFAULT_WIDTH}:{self.DEFAULT_HEIGHT}[bg]"
        
        # 音频可视化
        if effect == "wave":
            viz = f"[0:a]showwaves=s={self.DEFAULT_WIDTH}x200:mode=line:rate=25:colors={colors}:scale=lin[viz]"
            overlay = "[bg][viz]overlay=0:H-h[out]"
        elif effect == "spectrum":
            viz = f"[0:a]showfreqs=s={self.DEFAULT_WIDTH}x200:mode=line:colors={colors}[viz]"
            overlay = "[bg][viz]overlay=0:H-h[out]"
        elif effect == "vectorscope":
            viz = f"[0:a]avectorscope=s={self.DEFAULT_WIDTH//3}x{self.DEFAULT_HEIGHT//3}:draw=line:scale=lin:rc=40:gc=40:bc=40[viz]"
            overlay = "[bg][viz]overlay=(W-w)/2:(H-h)/2[out]"
        else:
            return bg.replace("[bg]", "[out]")
        
        return f"{bg};{viz};{overlay}"
    
    def _build_filter_with_color(self, effect: VisualEffect, colors: str) -> str:
        """构建带纯色背景的滤镜"""
        bg = f"color=c={self.DEFAULT_BG_COLOR}:s={self.DEFAULT_WIDTH}x{self.DEFAULT_HEIGHT}[bg]"
        
        if effect == "wave":
            viz = f"[0:a]showwaves=s={self.DEFAULT_WIDTH}x200:mode=line:rate=25:colors={colors}:scale=lin[viz]"
            overlay = "[bg][viz]overlay=0:H-h[out]"
        elif effect == "spectrum":
            viz = f"[0:a]showfreqs=s={self.DEFAULT_WIDTH}x200:mode=line:colors={colors}[viz]"
            overlay = "[bg][viz]overlay=0:H-h[out]"
        elif effect == "vectorscope":
            viz = f"[0:a]avectorscope=s={self.DEFAULT_WIDTH//3}x{self.DEFAULT_HEIGHT//3}:draw=line:scale=lin:rc=40:gc=40:bc=40[viz]"
            overlay = "[bg][viz]overlay=(W-w)/2:(H-h)/2[out]"
        else:
            return bg.replace("[bg]", "[out]")
        
        return f"{bg};{viz};{overlay}"
    
    def _concat_videos(self, video_files: list[Path], output_path: Path) -> bool:
        """合并视频文件"""
        # 创建文件列表
        concat_file = output_path.parent / "concat_list.txt"
        with open(concat_file, 'w', encoding='utf-8') as f:
            for video in video_files:
                # 使用相对路径或转义路径
                f.write(f"file '{video.name}'\n")
        
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(output_path)
        ]
        
        success = self._run_ffmpeg(cmd)
        
        # 清理
        try:
            concat_file.unlink()
        except:
            pass
        
        return success
    
    def _run_ffmpeg(self, cmd: list) -> bool:
        """运行 ffmpeg 命令"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ ffmpeg 错误:")
            if e.stderr:
                # 只显示最后几行错误
                error_lines = e.stderr.split('\n')[-10:]
                for line in error_lines:
                    if line.strip():
                        print(f"   {line}")
            return False


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
        
        subdirs = [d for d in broadcasts_dir.iterdir() if d.is_dir()]
        if not subdirs:
            print("❌ 没有找到 broadcast 子目录")
            return
        
        broadcast_dir = max(subdirs, key=lambda d: d.stat().st_mtime)
    
    print(f"📁 目标目录: {broadcast_dir}\n")
    
    # 生成视频
    generator = TimelineVideoGenerator()
    success = generator.generate_video_from_broadcast(
        broadcast_dir,
        effect="wave",  # 或 "vectorscope"
        color_scheme="default"
    )
    
    if success:
        print("\n🎉 时间轴视频生成完成！")
    else:
        print("\n❌ 视频生成失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
