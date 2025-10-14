"""
新闻播报视频生成工具
将音频 + 静态图片合成为视频，并添加音频可视化效果
"""

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Literal

VisualEffect = Literal["none", "wave", "spectrum", "vectorscope"]
WavePosition = Literal["top", "bottom", "center"]


class NewsVideoGenerator:
    """新闻视频生成器"""
    
    # 默认配置
    DEFAULT_IMAGE = "news_background.jpg"  # 默认背景图
    DEFAULT_WIDTH = 1280
    DEFAULT_HEIGHT = 720
    
    # 可视化效果颜色方案
    COLOR_SCHEMES = {
        "default": "white",
        "gradient": "0xff0000|0x00ff00|0x0000ff",  # 红绿蓝渐变
        "blue": "0x1e90ff",
        "gold": "0xffd700",
        "tech": "0x00ffff|0x00ff00"  # 青绿科技风
    }
    
    def __init__(self, image_dir: Optional[Path] = None):
        """
        初始化视频生成器
        
        Args:
            image_dir: 背景图片目录（默认为当前目录）
        """
        self.image_dir = image_dir or Path(__file__).parent
        self.check_dependencies()
        print("🎬 新闻视频生成器初始化完成")
    
    def check_dependencies(self):
        """检查 ffmpeg 是否可用"""
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
            print("❌ 错误: ffmpeg 未安装或不在 PATH 中")
            print("   请访问 https://ffmpeg.org/download.html 下载安装")
            raise RuntimeError("ffmpeg 不可用")
    
    def generate_video(
        self,
        audio_path: Path,
        output_path: Path,
        image_path: Optional[Path] = None,
        effect: VisualEffect = "wave",
        wave_position: WavePosition = "bottom",
        color_scheme: str = "default",
        wave_height: int = 200,
        video_quality: int = 23  # CRF值，越小质量越高（18-28推荐）
    ) -> bool:
        """
        生成新闻视频
        
        Args:
            audio_path: 音频文件路径（MP3）
            output_path: 输出视频路径（MP4）
            image_path: 背景图片路径（可选，默认使用DEFAULT_IMAGE）
            effect: 视觉效果类型
                - "none": 仅静态图片
                - "wave": 波形图（推荐播客、新闻）
                - "spectrum": 频谱图（推荐音乐）
                - "vectorscope": 矢量示波器（炫酷）
            wave_position: 波形位置（仅effect != "none"时有效）
            color_scheme: 颜色方案（default/gradient/blue/gold/tech）
            wave_height: 波形高度（像素）
            video_quality: 视频质量（18=高质量大文件，28=低质量小文件）
        
        Returns:
            bool: 是否成功
        """
        # 验证音频文件
        if not audio_path.exists():
            print(f"❌ 音频文件不存在: {audio_path}")
            return False
        
        # 确定背景图片
        if image_path is None:
            image_path = self.image_dir / self.DEFAULT_IMAGE
        
        if not image_path.exists():
            print(f"⚠️ 背景图片不存在: {image_path}")
            print(f"   将使用纯色背景")
            return self._generate_video_with_color(
                audio_path, output_path, effect, wave_position, 
                color_scheme, wave_height, video_quality
            )
        
        print(f"🎬 开始生成视频...")
        print(f"   音频: {audio_path.name}")
        print(f"   图片: {image_path.name}")
        print(f"   效果: {effect}")
        
        if effect == "none":
            return self._generate_simple_video(
                audio_path, image_path, output_path, video_quality
            )
        else:
            return self._generate_video_with_visualization(
                audio_path, image_path, output_path, effect,
                wave_position, color_scheme, wave_height, video_quality
            )
    
    def _generate_simple_video(
        self,
        audio_path: Path,
        image_path: Path,
        output_path: Path,
        video_quality: int
    ) -> bool:
        """生成简单视频（无可视化效果）"""
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(image_path),
            "-i", str(audio_path),
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-crf", str(video_quality),
            "-shortest",
            str(output_path)
        ]
        
        return self._run_ffmpeg(cmd, output_path)
    
    def _generate_video_with_visualization(
        self,
        audio_path: Path,
        image_path: Path,
        output_path: Path,
        effect: VisualEffect,
        wave_position: WavePosition,
        color_scheme: str,
        wave_height: int,
        video_quality: int
    ) -> bool:
        """生成带音频可视化效果的视频"""
        # 获取颜色
        colors = self.COLOR_SCHEMES.get(color_scheme, self.COLOR_SCHEMES["default"])
        
        # 构建滤镜链
        filter_complex = self._build_filter_complex(
            effect, wave_position, colors, wave_height
        )
        
        cmd = [
            "ffmpeg", "-y",
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
        
        return self._run_ffmpeg(cmd, output_path)
    
    def _generate_video_with_color(
        self,
        audio_path: Path,
        output_path: Path,
        effect: VisualEffect,
        wave_position: WavePosition,
        color_scheme: str,
        wave_height: int,
        video_quality: int
    ) -> bool:
        """使用纯色背景生成视频"""
        colors = self.COLOR_SCHEMES.get(color_scheme, self.COLOR_SCHEMES["default"])
        
        # 使用深蓝色背景
        bg_color = "0x1a1a2e"
        
        if effect == "none":
            # 纯色背景 + 音频
            filter_complex = f"color=c={bg_color}:s={self.DEFAULT_WIDTH}x{self.DEFAULT_HEIGHT}[out]"
        else:
            # 纯色背景 + 音频可视化
            filter_complex = self._build_filter_complex_with_color(
                effect, wave_position, colors, wave_height, bg_color
            )
        
        cmd = [
            "ffmpeg", "-y",
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
            "-shortest",
            str(output_path)
        ]
        
        return self._run_ffmpeg(cmd, output_path)
    
    def _build_filter_complex(
        self,
        effect: VisualEffect,
        position: WavePosition,
        colors: str,
        height: int
    ) -> str:
        """构建 ffmpeg 滤镜链"""
        width = self.DEFAULT_WIDTH
        video_height = self.DEFAULT_HEIGHT
        
        # 位置计算
        position_map = {
            "bottom": f"0:H-{height}",
            "top": "0:0",
            "center": "(W-w)/2:(H-h)/2"
        }
        overlay_pos = position_map.get(position, position_map["bottom"])
        
        # 根据效果类型构建滤镜
        if effect == "wave":
            # 波形图
            vis_filter = (
                f"[0:a]showwaves=s={width}x{height}:mode=cline:"
                f"colors={colors}:scale=sqrt[vis]"
            )
        elif effect == "spectrum":
            # 频谱图（柱状图，宽度为画面的1/3，居中显示）
            spec_width = width // 3  # 1/3 宽度
            spec_height = video_height // 2  # 高度为画面的一半
            vis_filter = (
                f"[0:a]showfreqs=s={spec_width}x{spec_height}:mode=bar:"
                f"colors={colors}:ascale=log:fscale=log[vis]"
            )
            # 居中显示
            overlay_pos = "(W-w)/2:(H-h)/2"
        elif effect == "vectorscope":
            # 矢量示波器（居中显示，方形）
            size = min(width, video_height) // 2
            vis_filter = (
                f"[0:a]avectorscope=s={size}x{size}:"
                f"zoom=1.5:draw=line:scale=log[vis]"
            )
            overlay_pos = "(W-w)/2:(H-h)/2"
        else:
            vis_filter = f"[0:a]anullsink[vis]"
        
        # 组合滤镜链
        filter_complex = (
            f"{vis_filter};"
            f"[1:v]scale={width}:{video_height}[bg];"
            f"[bg][vis]overlay={overlay_pos}:shortest=1[out]"
        )
        
        return filter_complex
    
    def _build_filter_complex_with_color(
        self,
        effect: VisualEffect,
        position: WavePosition,
        colors: str,
        height: int,
        bg_color: str
    ) -> str:
        """构建纯色背景的滤镜链"""
        width = self.DEFAULT_WIDTH
        video_height = self.DEFAULT_HEIGHT
        
        position_map = {
            "bottom": f"0:H-{height}",
            "top": "0:0",
            "center": "(W-w)/2:(H-h)/2"
        }
        overlay_pos = position_map.get(position, position_map["bottom"])
        
        if effect == "wave":
            vis_filter = (
                f"[0:a]showwaves=s={width}x{height}:mode=cline:"
                f"colors={colors}:scale=sqrt[vis]"
            )
        elif effect == "spectrum":
            # 频谱图（柱状图，宽度为画面的1/3，居中显示）
            spec_width = width // 3  # 1/3 宽度
            spec_height = video_height // 2  # 高度为画面的一半
            vis_filter = (
                f"[0:a]showfreqs=s={spec_width}x{spec_height}:mode=bar:"
                f"colors={colors}:ascale=log:fscale=log[vis]"
            )
            # 居中显示
            overlay_pos = "(W-w)/2:(H-h)/2"
        elif effect == "vectorscope":
            size = min(width, video_height) // 2
            vis_filter = (
                f"[0:a]avectorscope=s={size}x{size}:"
                f"zoom=1.5:draw=line:scale=log[vis]"
            )
            overlay_pos = "(W-w)/2:(H-h)/2"
        else:
            vis_filter = f"[0:a]anullsink[vis]"
        
        filter_complex = (
            f"{vis_filter};"
            f"color=c={bg_color}:s={width}x{video_height}[bg];"
            f"[bg][vis]overlay={overlay_pos}:shortest=1[out]"
        )
        
        return filter_complex
    
    def _run_ffmpeg(self, cmd: list, output_path: Path) -> bool:
        """运行 ffmpeg 命令"""
        try:
            print(f"⏳ 正在处理...")
            
            # 运行 ffmpeg（隐藏详细输出）
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # 检查输出文件
            if output_path.exists():
                size_mb = output_path.stat().st_size / (1024 * 1024)
                print(f"✅ 视频生成成功: {output_path.name} ({size_mb:.2f} MB)")
                return True
            else:
                print(f"❌ 输出文件未生成: {output_path}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ ffmpeg 执行失败:")
            print(f"   返回码: {e.returncode}")
            if e.stderr:
                # 只显示最后几行错误信息
                error_lines = e.stderr.strip().split("\n")[-5:]
                for line in error_lines:
                    print(f"   {line}")
            return False
        except Exception as e:
            print(f"❌ 生成视频时出错: {e}")
            return False
    
    def batch_generate_from_broadcast(
        self,
        broadcast_dir: Path,
        effect: VisualEffect = "wave",
        color_scheme: str = "tech",
        suffix: str = ""
    ) -> bool:
        """
        从播报目录批量生成视频
        
        Args:
            broadcast_dir: 播报目录（包含 audio_full.mp3 或 broadcast_full.mp3）
            effect: 视觉效果
            color_scheme: 颜色方案
            suffix: 文件名后缀（用于区分不同版本）
        
        Returns:
            bool: 是否成功
        """
        # 查找音频文件（支持两种命名方式）
        audio_file = None
        for filename in [
            "broadcast_full_with_bgm.mp3",  # 新版命名（带BGM）
            "audio_full_with_bgm.mp3",      # 旧版命名（带BGM）
            "broadcast_full.mp3",            # 新版命名（纯人声）
            "audio_full.mp3"                 # 旧版命名（纯人声）
        ]:
            audio_path = broadcast_dir / filename
            if audio_path.exists():
                audio_file = audio_path
                print(f"📢 找到音频文件: {filename}")
                break
        
        if audio_file is None:
            print(f"❌ 未找到音频文件在: {broadcast_dir}")
            print(f"   查找的文件: broadcast_full_with_bgm.mp3, broadcast_full.mp3, audio_full_with_bgm.mp3, audio_full.mp3")
            return False
        
        # 生成视频文件名（添加后缀避免冲突）
        base_name = audio_file.stem.replace("audio_", "video_").replace("broadcast_", "video_")
        if suffix:
            video_name = f"{base_name}_{suffix}.mp4"
        else:
            video_name = f"{base_name}.mp4"
        output_path = broadcast_dir / video_name
        
        # 生成视频
        return self.generate_video(
            audio_path=audio_file,
            output_path=output_path,
            effect=effect,
            color_scheme=color_scheme
        )


def main():
    """主函数 - 处理最新的播报"""
    broadcasts_dir = Path(__file__).parent / "broadcasts"
    
    if not broadcasts_dir.exists():
        print("❌ broadcasts 目录不存在")
        return
    
    # 查找最新的播报目录
    broadcast_dirs = sorted(
        [d for d in broadcasts_dir.iterdir() if d.is_dir()],
        key=lambda d: d.name,
        reverse=True
    )
    
    if not broadcast_dirs:
        print("❌ 未找到任何播报目录")
        return
    
    latest_dir = broadcast_dirs[0]
    print(f"📁 处理最新播报: {latest_dir.name}")
    print()
    
    # 生成视频
    generator = NewsVideoGenerator()
    
    # 生成频谱图效果：1/3宽度，白色，居中
    print("🎨 FFT频谱柱状图（1/3宽度，白色居中）")
    success = generator.batch_generate_from_broadcast(
        latest_dir,
        effect="spectrum",        # 频谱柱状图
        color_scheme="default",   # 白色
        suffix="spectrum"         # 文件名后缀
    )
    
    if success:
        print("\n" + "=" * 50)
        print("✅ 视频生成完成!")
        print(f"📂 输出目录: {latest_dir}")
    else:
        print("\n❌ 视频生成失败")


if __name__ == "__main__":
    main()
