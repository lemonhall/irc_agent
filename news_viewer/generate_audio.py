"""
新闻播报文本转语音工具（简化版）
直接读取 JSON 格式的播报文件生成音频
"""

import os
import json
import time
import requests
import wave
from pathlib import Path
import dashscope


class NewsAudioGenerator:
    """新闻音频生成器"""
    
    def __init__(self):
        """初始化生成器"""
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        
        if not self.api_key:
            raise ValueError("❌ 未设置DASHSCOPE_API_KEY环境变量")
        
        self.voice = "Cherry"  # 女声播音员
        print(f"🎤 新闻音频生成器初始化完成 (声音: {self.voice})")
    
    def generate_audio(self, text: str, output_path: Path) -> bool:
        """
        为文本生成音频
        
        Args:
            text: 文本内容
            output_path: 输出路径
            
        Returns:
            是否成功
        """
        try:
            print(f"📝 文本长度: {len(text)} 字符")
            
            # 调用TTS API
            response = dashscope.MultiModalConversation.call(
                model="qwen3-tts-flash",
                api_key=self.api_key,
                text=text,
                voice=self.voice,
                language_type="Chinese",
                stream=False
            )
            
            # 检查响应
            if not hasattr(response, 'output') or not hasattr(response.output, 'audio'):
                print(f"❌ API响应异常: {response}")
                return False
            
            audio_url = response.output.audio.url
            print(f"🌐 下载音频...")
            
            # 下载音频
            audio_response = requests.get(audio_url, timeout=60)
            audio_response.raise_for_status()
            
            # 保存文件
            with open(output_path, 'wb') as f:
                f.write(audio_response.content)
            
            # 获取时长
            duration = self._get_duration(output_path)
            print(f"✅ 保存成功: {output_path.name} ({duration:.1f}秒)")
            
            return True
            
        except Exception as e:
            print(f"❌ 生成失败: {e}")
            return False
    
    def _get_duration(self, audio_path: Path) -> float:
        """获取音频时长"""
        try:
            with wave.open(str(audio_path), 'rb') as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                return frames / float(rate)
        except:
            return 0.0
    
    def generate_from_json(self, json_file: Path) -> list[Path]:
        """
        从JSON文件生成完整新闻播报音频
        
        Args:
            json_file: JSON文件路径
            
        Returns:
            生成的音频文件列表
        """
        # 读取JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        scripts = data.get('scripts', [])
        print(f"\n🎵 共 {len(scripts)} 个新闻段落")
        
        # 输出目录
        output_dir = json_file.parent
        base_name = json_file.stem
        
        audio_files = []
        
        # 1. 生成开场白
        print(f"\n{'='*60}")
        print(f"🎙️  [1/{len(scripts)+2}] 开场白")
        intro_text = "欢迎收听新闻播报。以下是今日的新闻内容。"
        intro_path = output_dir / f"{base_name}_00_intro.wav"
        
        if self.generate_audio(intro_text, intro_path):
            audio_files.append(intro_path)
        
        time.sleep(1)  # API限流
        
        # 2. 生成各个新闻段落
        for i, script_item in enumerate(scripts, 1):
            category_name = script_item['category_name']
            script_text = script_item['script']
            category_id = script_item['category_id']
            
            print(f"\n{'='*60}")
            print(f"🎙️  [{i+1}/{len(scripts)+2}] {category_name}")
            
            output_path = output_dir / f"{base_name}_{i:02d}_{category_id}.wav"
            
            if self.generate_audio(script_text, output_path):
                audio_files.append(output_path)
            
            time.sleep(1)  # API限流
        
        # 3. 生成结束语
        print(f"\n{'='*60}")
        print(f"🎙️  [{len(scripts)+2}/{len(scripts)+2}] 结束语")
        outro_text = "以上就是本次新闻播报的全部内容，感谢收听。"
        outro_path = output_dir / f"{base_name}_{len(scripts)+1:02d}_outro.wav"
        
        if self.generate_audio(outro_text, outro_path):
            audio_files.append(outro_path)
        
        # 4. 合并为完整音频
        if len(audio_files) > 0:
            print(f"\n{'='*60}")
            print(f"🔗 合并音频文件...")
            full_wav_path = output_dir / f"{base_name}_full.wav"
            
            if self._merge_audio(audio_files, full_wav_path):
                audio_files.append(full_wav_path)
                print(f"✅ 完整音频: {full_wav_path.name}")
                
                # 5. 转换为高质量MP3
                print(f"\n{'='*60}")
                print(f"🎵 转换为MP3格式...")
                full_mp3_path = output_dir / f"{base_name}_full.mp3"
                
                if self._convert_to_mp3(full_wav_path, full_mp3_path):
                    audio_files.append(full_mp3_path)
                    print(f"✅ MP3音频: {full_mp3_path.name}")
        
        return audio_files
    
    def _merge_audio(self, audio_files: list[Path], output_path: Path) -> bool:
        """合并多个WAV文件"""
        try:
            # 读取第一个文件的参数
            with wave.open(str(audio_files[0]), 'rb') as first:
                params = first.getparams()
            
            # 写入合并后的文件
            with wave.open(str(output_path), 'wb') as output:
                output.setparams(params)
                
                for audio_file in audio_files:
                    with wave.open(str(audio_file), 'rb') as input_audio:
                        output.writeframes(input_audio.readframes(input_audio.getnframes()))
                    
                    # 添加0.8秒静音间隔
                    silence_frames = int(0.8 * params.framerate)
                    silence = b'\x00' * (silence_frames * params.sampwidth * params.nchannels)
                    output.writeframes(silence)
            
            return True
            
        except Exception as e:
            print(f"❌ 合并失败: {e}")
            return False
    
    def _convert_to_mp3(self, wav_path: Path, mp3_path: Path) -> bool:
        """
        使用ffmpeg将WAV转换为高质量MP3
        
        Args:
            wav_path: WAV文件路径
            mp3_path: MP3输出路径
            
        Returns:
            是否成功
        """
        try:
            import subprocess
            
            # 使用高质量编码: VBR V0 (约245 kbps) 或 CBR 320kbps
            # -q:a 0 表示最高质量的VBR编码
            cmd = [
                'ffmpeg',
                '-i', str(wav_path),
                '-codec:a', 'libmp3lame',
                '-q:a', '0',  # VBR质量等级 0 (最高质量)
                '-y',  # 覆盖已存在的文件
                str(mp3_path)
            ]
            
            print(f"📀 编码参数: VBR V0 (最高质量)")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode == 0:
                # 计算压缩率
                wav_size = wav_path.stat().st_size / 1024 / 1024  # MB
                mp3_size = mp3_path.stat().st_size / 1024 / 1024  # MB
                ratio = (1 - mp3_size / wav_size) * 100
                
                print(f"📊 WAV: {wav_size:.2f} MB → MP3: {mp3_size:.2f} MB (节省 {ratio:.1f}%)")
                return True
            else:
                print(f"❌ ffmpeg错误: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print(f"❌ 未找到ffmpeg，请确保已安装并添加到PATH")
            return False
        except Exception as e:
            print(f"❌ 转换失败: {e}")
            return False


def main():
    """主函数"""
    import sys
    
    # 检查是否是转码模式
    if len(sys.argv) > 1 and sys.argv[1] == '--convert':
        # 转码模式：直接转换已有的WAV文件
        if len(sys.argv) < 3:
            print("❌ 请指定要转换的WAV文件")
            print("   用法: python generate_audio.py --convert <wav_file>")
            sys.exit(1)
        
        wav_file = Path(sys.argv[2])
        if not wav_file.exists():
            print(f"❌ 文件不存在: {wav_file}")
            sys.exit(1)
        
        if wav_file.suffix.lower() != '.wav':
            print(f"❌ 不是WAV文件: {wav_file}")
            sys.exit(1)
        
        # 执行转码
        generator = NewsAudioGenerator()
        mp3_file = wav_file.with_suffix('.mp3')
        
        print(f"🎵 转换 WAV → MP3")
        print(f"📥 输入: {wav_file.name}")
        print(f"📤 输出: {mp3_file.name}\n")
        
        if generator._convert_to_mp3(wav_file, mp3_file):
            print(f"\n✅ 转换成功！")
            print(f"📦 文件: {mp3_file}")
        else:
            print(f"\n❌ 转换失败")
            sys.exit(1)
        
        return
    
    # 正常模式：生成音频
    # 检查API Key
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("❌ 请设置DASHSCOPE_API_KEY环境变量")
        print("   示例: $env:DASHSCOPE_API_KEY='your-api-key'")
        sys.exit(1)
    
    # 获取JSON文件路径
    if len(sys.argv) > 1:
        json_file = Path(sys.argv[1])
    else:
        # 使用最新的JSON文件
        broadcast_dir = Path(__file__).parent / "broadcasts"
        json_files = sorted(broadcast_dir.glob("*.json"), 
                          key=lambda p: p.stat().st_mtime, 
                          reverse=True)
        
        if not json_files:
            print("❌ 未找到任何JSON文件")
            sys.exit(1)
        
        json_file = json_files[0]
        print(f"📄 使用最新的播报文件: {json_file.name}")
    
    if not json_file.exists():
        print(f"❌ 文件不存在: {json_file}")
        sys.exit(1)
    
    # 生成音频
    try:
        generator = NewsAudioGenerator()
        audio_files = generator.generate_from_json(json_file)
        
        print(f"\n{'='*60}")
        print(f"🎉 生成完成！共 {len(audio_files)} 个文件:")
        for audio_file in audio_files:
            file_size = audio_file.stat().st_size / 1024  # KB
            print(f"  📦 {audio_file.name} ({file_size:.1f} KB)")
        
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
