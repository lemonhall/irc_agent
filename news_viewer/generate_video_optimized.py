"""
新闻播报视频生成工具（优化版）
分步骤：
1. 为每个分段音频 + 图片生成简单视频（无特效）
2. 拼接所有片段
3. 添加音频可视化特效
4. 使用 add_bgm.py 添加背景音乐
"""

import json
import subprocess
from pathlib import Path
from typing import Optional, Literal

VisualEffect = Literal["none", "wave", "spectrum", "vectorscope"]


class OptimizedVideoGenerator:
    """优化的视频生成器"""
    
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
        print("🚀 优化版视频生成器初始化完成")
    
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
        根据 broadcast.json 生成视频（优化流程）
        
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
        
        print(f"📊 播报信息")
        print(f"   片段数: {len(scripts)}")
        print(f"   总时长: {data.get('total_duration', 0):.1f}秒")
        print()
        
        # 步骤1: 为每个分段音频生成简单视频（图片+音频，无特效）
        print("=" * 60)
        print("步骤 1/3: 生成分段视频（图片+音频）")
        print("=" * 60)
        temp_videos = self._generate_segments(broadcast_dir, scripts, video_quality)
        
        if not temp_videos:
            print("❌ 没有生成任何视频片段")
            return False
        
        # 步骤2: 拼接所有片段
        print("\n" + "=" * 60)
        print("步骤 2/3: 拼接视频片段")
        print("=" * 60)
        concat_output = broadcast_dir / "video_concat_temp.mp4"
        if not self._concat_videos(temp_videos, concat_output):
            print("❌ 拼接失败")
            return False
        
        # 步骤3: 添加音频可视化特效
        print("\n" + "=" * 60)
        print("步骤 3/3: 添加音频可视化特效")
        print("=" * 60)
        final_output = broadcast_dir / "video_full_timeline.mp4"
        if not self._add_visualization(concat_output, final_output, effect, color_scheme, video_quality):
            print("❌ 添加特效失败")
            return False
        
        # 清理临时文件
        print("\n🧹 清理临时文件...")
        for temp_video in temp_videos:
            try:
                temp_video.unlink()
                print(f"   🗑️ {temp_video.name}")
            except:
                pass
        
        try:
            concat_output.unlink()
            print(f"   🗑️ {concat_output.name}")
        except:
            pass
        
        print(f"\n✅ 视频生成完成: {final_output.name}")
        print(f"📂 位置: {final_output}")
        print("\n💡 提示: 使用 add_bgm.py 可以添加背景音乐")
        
        return True
    
    def _generate_segments(
        self,
        broadcast_dir: Path,
        scripts: list,
        video_quality: int
    ) -> list[Path]:
        """步骤1: 生成分段视频（仅图片+分段音频，无特效）"""
        temp_videos = []
        
        for i, script in enumerate(scripts):
            category_name = script.get("category_name", "Unknown")
            audio_file = script.get("audio_file")
            image_file = script.get("image_file")
            
            if not audio_file:
                print(f"[{i+1}/{len(scripts)}] {category_name} - ⏭️ 跳过（无音频）")
                continue
            
            audio_path = broadcast_dir / audio_file
            if not audio_path.exists():
                print(f"[{i+1}/{len(scripts)}] {category_name} - ⚠️ 音频不存在: {audio_file}")
                continue
            
            print(f"[{i+1}/{len(scripts)}] {category_name}")
            
            # 获取图片
            if image_file:
                image_path = broadcast_dir / image_file
                if not image_path.exists():
                    print(f"   ⚠️ 图片不存在: {image_file}，使用纯色背景")
                    image_path = None
            else:
                image_path = None
            
            # 生成临时视频
            temp_video = broadcast_dir / f"temp_segment_{i:02d}.mp4"
            
            if self._generate_simple_segment(audio_path, image_path, temp_video, video_quality):
                temp_videos.append(temp_video)
                print(f"   ✅ 生成成功")
            else:
                print(f"   ❌ 生成失败，跳过")
        
        return temp_videos
    
    def _generate_simple_segment(
        self,
        audio_path: Path,
        image_path: Optional[Path],
        output_path: Path,
        video_quality: int
    ) -> bool:
        """生成简单的视频片段（图片+音频，无特效）"""
        
        if image_path:
            # 使用图片背景
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
                "-vf", f"scale={self.DEFAULT_WIDTH}:{self.DEFAULT_HEIGHT}:force_original_aspect_ratio=increase,crop={self.DEFAULT_WIDTH}:{self.DEFAULT_HEIGHT}",
                "-shortest",
                str(output_path)
            ]
        else:
            # 使用纯色背景（简化版）
            # 先获取音频时长
            try:
                duration_cmd = [
                    "ffprobe", "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    str(audio_path)
                ]
                duration_result = subprocess.run(duration_cmd, capture_output=True, text=True)
                duration = float(duration_result.stdout.strip())
            except:
                duration = 10  # 默认10秒
            
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", f"color=c={self.DEFAULT_BG_COLOR}:s={self.DEFAULT_WIDTH}x{self.DEFAULT_HEIGHT}:d={duration}",
                "-i", str(audio_path),
                "-c:v", "libx264",
                "-c:a", "aac",
                "-b:a", "192k",
                "-pix_fmt", "yuv420p",
                "-crf", str(video_quality),
                "-shortest",
                str(output_path)
            ]
        
        return self._run_ffmpeg(cmd, silent=True)
    
    def _concat_videos(self, video_files: list[Path], output_path: Path) -> bool:
        """步骤2: 拼接视频文件"""
        print(f"🔗 拼接 {len(video_files)} 个片段...")
        
        # 创建文件列表
        concat_file = output_path.parent / "concat_list.txt"
        with open(concat_file, 'w', encoding='utf-8') as f:
            for video in video_files:
                f.write(f"file '{video.name}'\n")
        
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(output_path)
        ]
        
        success = self._run_ffmpeg(cmd, silent=False)
        
        # 清理
        try:
            concat_file.unlink()
        except:
            pass
        
        if success:
            print(f"✅ 拼接完成")
        
        return success
    
    def _add_visualization(
        self,
        input_video: Path,
        output_video: Path,
        effect: VisualEffect,
        color_scheme: str,
        video_quality: int
    ) -> bool:
        """步骤3: 添加音频可视化特效"""
        
        if effect == "none":
            print("⏭️ 跳过特效，直接复制文件")
            import shutil
            shutil.copy2(input_video, output_video)
            return True
        
        colors = self.COLOR_SCHEMES.get(color_scheme, self.COLOR_SCHEMES["default"])
        
        print(f"🎨 应用特效: {effect}")
        print(f"   颜色方案: {color_scheme}")
        
        # 构建滤镜
        if effect == "wave":
            viz = f"[0:a]showwaves=s={self.DEFAULT_WIDTH}x200:mode=line:rate=25:colors={colors}:scale=lin[viz]"
            overlay = "[0:v][viz]overlay=0:H-h[out]"
        elif effect == "spectrum":
            viz = f"[0:a]showfreqs=s={self.DEFAULT_WIDTH}x200:mode=line:colors={colors}[viz]"
            overlay = "[0:v][viz]overlay=0:H-h[out]"
        elif effect == "vectorscope":
            viz = f"[0:a]avectorscope=s={self.DEFAULT_WIDTH//3}x{self.DEFAULT_HEIGHT//3}:draw=line:scale=lin:rc=40:gc=40:bc=40[viz]"
            overlay = "[0:v][viz]overlay=(W-w)/2:(H-h)/2[out]"
        else:
            return False
        
        filter_complex = f"{viz};{overlay}"
        
        cmd = [
            "ffmpeg", "-y",
            "-i", str(input_video),
            "-filter_complex", filter_complex,
            "-map", "[out]",
            "-map", "0:a",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", str(video_quality),
            "-c:a", "copy",  # 复制音频，不重新编码
            "-pix_fmt", "yuv420p",
            str(output_video)
        ]
        
        success = self._run_ffmpeg(cmd, silent=False)
        
        if success:
            print(f"✅ 特效添加完成")
        
        return success
    
    def _run_ffmpeg(self, cmd: list, silent: bool = False) -> bool:
        """运行 ffmpeg 命令"""
        try:
            if silent:
                # 静默模式（用于批量生成分段）
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
            else:
                # 显示进度模式
                print(f"   ⏳ 处理中...", flush=True)
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"   ✅ 完成")
            
            return True
        except subprocess.CalledProcessError as e:
            if not silent:
                print(f"   ❌ ffmpeg 错误:")
                if e.stderr:
                    error_lines = e.stderr.split('\n')[-10:]
                    for line in error_lines:
                        if line.strip():
                            print(f"      {line}")
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
    
    print("=" * 60)
    print(f"📁 目标目录: {broadcast_dir.name}")
    print("=" * 60)
    print()
    
    # 生成视频
    generator = OptimizedVideoGenerator()
    success = generator.generate_video_from_broadcast(
        broadcast_dir,
        effect="wave",  # wave/vectorscope/spectrum/none
        color_scheme="default"
    )
    
    if not success:
        print("\n❌ 视频生成失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
