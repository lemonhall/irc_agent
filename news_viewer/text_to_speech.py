"""
新闻播报文本转语音工具
使用通义千问TTS API将新闻播报文本转换为MP3音频
"""

import os
import re
import time
import requests
from pathlib import Path
import dashscope
from typing import List, Tuple


class NewsTextToSpeech:
    """新闻播报TTS转换器"""
    
    def __init__(self):
        """初始化TTS转换器"""
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        
        if not self.api_key:
            raise ValueError("❌ 未设置DASHSCOPE_API_KEY环境变量")
        
        # 使用通义千问TTS支持的声音 Cherry (女声播音员)
        self.default_voice = "Cherry"
        self.language_type = "Chinese"
        
        print(f"🎤 新闻TTS转换器初始化完成")
    
    def parse_broadcast_file(self, file_path: Path) -> List[Tuple[str, str]]:
        """
        解析新闻播报文件，将内容分段
        
        Args:
            file_path: 播报文件路径
            
        Returns:
            [(section_name, content), ...] 列表
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        sections = []
        
        # 分割新闻段落
        # 匹配形如 【🌍 世界新闻】 的标题
        pattern = r'【[^\]]+】\n(.*?)(?=\n-{10,}|\n【|$)'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            title_match = re.search(r'【([^\]]+)】', match.group(0))
            if title_match:
                section_title = title_match.group(1).strip()
                section_content = match.group(1).strip()
                
                if section_content:
                    sections.append((section_title, section_content))
        
        print(f"📝 解析到 {len(sections)} 个新闻段落")
        return sections
    
    def generate_section_audio(self, section_name: str, content: str, 
                              output_path: Path) -> bool:
        """
        为单个新闻段落生成音频
        
        Args:
            section_name: 段落名称
            content: 段落内容
            output_path: 输出音频路径
            
        Returns:
            是否成功
        """
        try:
            print(f"\n🎙️  正在生成: {section_name}")
            print(f"📄 内容长度: {len(content)} 字符")
            
            # 调用通义千问TTS API
            response = dashscope.MultiModalConversation.call(
                model="qwen3-tts-flash",
                api_key=self.api_key,
                text=content,
                voice=self.default_voice,
                language_type=self.language_type,
                stream=False
            )
            
            # 检查响应
            if not hasattr(response, 'output') or not hasattr(response.output, 'audio'):
                print(f"❌ API响应异常: {response}")
                return False
            
            # 获取音频URL
            audio_url = response.output.audio.url
            print(f"🌐 下载音频: {audio_url}")
            
            # 下载音频文件
            try:
                audio_response = requests.get(audio_url, timeout=60)
                audio_response.raise_for_status()
                audio_data = audio_response.content
                
                if audio_data:
                    # 保存为WAV文件
                    with open(output_path, 'wb') as f:
                        f.write(audio_data)
                    
                    print(f"💾 音频已保存: {output_path.name} ({len(audio_data)} 字节)")
                    return True
                else:
                    print("❌ 下载的音频数据为空")
                    return False
                    
            except requests.RequestException as e:
                print(f"❌ 下载音频失败: {e}")
                return False
                
        except Exception as e:
            print(f"❌ 生成音频失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def convert_broadcast_to_audio(self, text_file: Path, 
                                   output_dir: Path = None,
                                   generate_full: bool = True) -> List[Path]:
        """
        将新闻播报文件转换为音频
        
        Args:
            text_file: 播报文本文件路径
            output_dir: 输出目录（默认与文本文件同目录）
            generate_full: 是否合并所有段落为完整音频
            
        Returns:
            生成的音频文件路径列表
        """
        if not text_file.exists():
            raise FileNotFoundError(f"文件不存在: {text_file}")
        
        if output_dir is None:
            output_dir = text_file.parent
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 解析文本文件
        sections = self.parse_broadcast_file(text_file)
        
        if not sections:
            print("❌ 未找到任何新闻段落")
            return []
        
        print(f"\n🎵 开始生成音频，共 {len(sections)} 个段落")
        
        generated_files = []
        
        # 生成开场白
        intro_text = f"欢迎收听新闻播报。以下是今日的新闻内容。"
        intro_path = output_dir / f"{text_file.stem}_00_intro.wav"
        
        if self.generate_section_audio("开场白", intro_text, intro_path):
            generated_files.append(intro_path)
            time.sleep(1)  # API调用间隔
        
        # 为每个段落生成音频
        for i, (section_name, content) in enumerate(sections, 1):
            # 构造输出文件名
            safe_name = re.sub(r'[^\w\s-]', '', section_name).strip()
            output_path = output_dir / f"{text_file.stem}_{i:02d}_{safe_name}.wav"
            
            # 生成音频
            success = self.generate_section_audio(section_name, content, output_path)
            
            if success:
                generated_files.append(output_path)
            
            # API调用间隔
            time.sleep(1)
        
        # 生成结束语
        outro_text = "以上就是本次新闻播报的全部内容，感谢收听。"
        outro_path = output_dir / f"{text_file.stem}_{len(sections)+1:02d}_outro.wav"
        
        if self.generate_section_audio("结束语", outro_text, outro_path):
            generated_files.append(outro_path)
        
        print(f"\n✅ 音频生成完成！共生成 {len(generated_files)} 个文件")
        
        # 如果需要合并为完整音频
        if generate_full and len(generated_files) > 0:
            print("\n🔗 正在合并音频文件...")
            full_audio_path = output_dir / f"{text_file.stem}_full.wav"
            
            if self._merge_audio_files(generated_files, full_audio_path):
                print(f"✅ 完整音频已生成: {full_audio_path}")
                generated_files.append(full_audio_path)
        
        return generated_files
    
    def _merge_audio_files(self, audio_files: List[Path], output_path: Path) -> bool:
        """
        合并多个WAV音频文件
        
        Args:
            audio_files: 音频文件列表
            output_path: 输出文件路径
            
        Returns:
            是否成功
        """
        try:
            import wave
            
            # 读取第一个文件获取参数
            with wave.open(str(audio_files[0]), 'rb') as first_audio:
                params = first_audio.getparams()
            
            # 创建输出文件
            with wave.open(str(output_path), 'wb') as output_audio:
                output_audio.setparams(params)
                
                # 依次写入每个文件的音频数据
                for audio_file in audio_files:
                    with wave.open(str(audio_file), 'rb') as input_audio:
                        output_audio.writeframes(input_audio.readframes(input_audio.getnframes()))
                    
                    # 添加短暂的静音间隔（0.5秒）
                    silence_frames = int(0.5 * params.framerate)
                    silence = b'\x00' * (silence_frames * params.sampwidth * params.nchannels)
                    output_audio.writeframes(silence)
            
            return True
            
        except Exception as e:
            print(f"❌ 合并音频失败: {e}")
            return False


def main():
    """主函数"""
    import sys
    
    # 检查API Key
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("❌ 请设置DASHSCOPE_API_KEY环境变量")
        print("   示例: $env:DASHSCOPE_API_KEY='your-api-key'")
        sys.exit(1)
    
    # 创建TTS转换器
    tts = NewsTextToSpeech()
    
    # 默认处理最新的播报文件
    broadcast_dir = Path(__file__).parent / "broadcasts"
    
    if len(sys.argv) > 1:
        # 使用命令行参数指定的文件
        text_file = Path(sys.argv[1])
    else:
        # 查找最新的txt文件
        txt_files = sorted(broadcast_dir.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        if not txt_files:
            print("❌ 未找到任何播报文件")
            sys.exit(1)
        
        text_file = txt_files[0]
        print(f"📄 将处理最新的播报文件: {text_file.name}")
    
    if not text_file.exists():
        print(f"❌ 文件不存在: {text_file}")
        sys.exit(1)
    
    # 转换为音频
    try:
        audio_files = tts.convert_broadcast_to_audio(text_file, generate_full=True)
        
        if audio_files:
            print("\n🎉 转换完成！生成的音频文件:")
            for audio_file in audio_files:
                print(f"  - {audio_file.name}")
        else:
            print("\n❌ 未生成任何音频文件")
            
    except Exception as e:
        print(f"\n❌ 转换失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
