"""
新闻播报文本转语音工具（简化版）
直接读取 JSON 格式的播报文件生成音频
使用火山引擎 TTS API
"""

import os
import json
import time
import requests
import wave
import base64
import uuid
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class NewsAudioGenerator:
    """新闻音频生成器"""
    
    def __init__(self):
        """初始化生成器"""
        # 火山引擎配置
        self.app_id = os.getenv("VOLCENGINE_APP_ID")
        self.access_token = os.getenv("VOLCENGINE_ACCESS_TOKEN")
        
        if not self.app_id or not self.access_token:
            raise ValueError("❌ 未设置VOLCENGINE_APP_ID或VOLCENGINE_ACCESS_TOKEN环境变量")
        
        # TTS配置
        self.tts_url = "https://openspeech.bytedance.com/api/v1/tts"
        self.cluster = "volcano_tts"
        self.voice = "ICL_zh_female_zhixingwenwan_tob"  # 知性温婉女声
        
        print(f"🎤 新闻音频生成器初始化完成 (声音: {self.voice})")
        print(f"🔑 使用火山引擎 TTS API")
    
    def generate_audio(self, text: str, output_path: Path) -> bool:
        """
        为文本生成音频（使用火山引擎TTS）
        
        Args:
            text: 文本内容
            output_path: 输出路径
            
        Returns:
            是否成功
        """
        try:
            print(f"📝 文本长度: {len(text)} 字符")
            
            # 构造请求
            reqid = str(uuid.uuid4())
            
            headers = {
                "Authorization": f"Bearer;{self.access_token}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "app": {
                    "appid": self.app_id,
                    "token": "token_ignored_but_required",
                    "cluster": self.cluster,
                },
                "user": {
                    "uid": "news_broadcast_user"
                },
                "audio": {
                    "voice_type": self.voice,
                    "encoding": "mp3",
                    "speed_ratio": 1.0,
                    "rate": 24000,
                    "BitRate": 128,
                },
                "request": {
                    "reqid": reqid,
                    "text": text,
                    "operation": "query",
                }
            }
            
            # 调用API
            response = requests.post(self.tts_url, headers=headers, data=json.dumps(payload), timeout=60)
            response.raise_for_status()
            
            result = response.json()
            log_id = response.headers.get("X-Tt-Logid")
            
            if result.get("code") == 3000:
                audio_data_base64 = result.get("data")
                if audio_data_base64:
                    audio_data = base64.b64decode(audio_data_base64)
                    
                    # 保存为MP3文件（改扩展名）
                    output_path = output_path.with_suffix('.mp3')
                    with open(output_path, 'wb') as f:
                        f.write(audio_data)
                    
                    # 获取时长
                    duration_ms = result.get("addition", {}).get("duration", 0)
                    try:
                        # 可能是字符串或数字，统一转换
                        duration_sec = float(duration_ms) / 1000.0
                    except (ValueError, TypeError):
                        duration_sec = 0.0
                    
                    print(f"✅ 保存成功: {output_path.name} ({duration_sec:.1f}秒)")
                    if log_id:
                        print(f"   日志ID: {log_id}")
                    
                    return True
                else:
                    print(f"❌ API响应但无音频数据")
                    return False
            else:
                print(f"❌ API错误: Code={result.get('code')}, Message={result.get('message')}")
                if log_id:
                    print(f"   日志ID: {log_id}")
                return False
                
        except Exception as e:
            print(f"❌ 生成失败: {e}")
            return False
    
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
        intro_path = output_dir / f"{base_name}_00_intro.mp3"
        
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
            
            output_path = output_dir / f"{base_name}_{i:02d}_{category_id}.mp3"
            
            if self.generate_audio(script_text, output_path):
                audio_files.append(output_path)
            
            time.sleep(1)  # API限流
        
        # 3. 生成结束语
        print(f"\n{'='*60}")
        print(f"🎙️  [{len(scripts)+2}/{len(scripts)+2}] 结束语")
        outro_text = "以上就是本次新闻播报的全部内容，感谢收听。"
        outro_path = output_dir / f"{base_name}_{len(scripts)+1:02d}_outro.mp3"
        
        if self.generate_audio(outro_text, outro_path):
            audio_files.append(outro_path)
        
        # 4. 合并为完整音频（MP3格式）
        if len(audio_files) > 0:
            print(f"\n{'='*60}")
            print(f"🔗 合并MP3音频文件...")
            full_mp3_path = output_dir / f"{base_name}_full.mp3"
            
            if self._merge_mp3_files(audio_files, full_mp3_path):
                audio_files.append(full_mp3_path)
                print(f"✅ 完整音频: {full_mp3_path.name}")
        
        return audio_files
    
    def _merge_mp3_files(self, audio_files: list[Path], output_path: Path) -> bool:
        """
        使用ffmpeg合并多个MP3文件
        
        Args:
            audio_files: MP3文件列表
            output_path: 输出文件路径
            
        Returns:
            是否成功
        """
        try:
            import subprocess
            import tempfile
            
            # 创建临时文件列表
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                for audio_file in audio_files:
                    # ffmpeg concat需要相对路径或转义
                    f.write(f"file '{audio_file.absolute()}'\n")
                list_file = f.name
            
            try:
                # 使用ffmpeg concat协议合并MP3
                cmd = [
                    'ffmpeg',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', list_file,
                    '-c', 'copy',  # 直接复制，不重新编码
                    '-y',
                    str(output_path)
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
                
                if result.returncode == 0:
                    file_size = output_path.stat().st_size / 1024 / 1024  # MB
                    print(f"📊 合并完成: {file_size:.2f} MB")
                    return True
                else:
                    print(f"❌ ffmpeg合并错误: {result.stderr}")
                    return False
                    
            finally:
                # 清理临时文件
                try:
                    os.unlink(list_file)
                except:
                    pass
                    
        except FileNotFoundError:
            print(f"❌ 未找到ffmpeg，请确保已安装并添加到PATH")
            return False
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
    # 检查环境变量
    if not os.getenv("VOLCENGINE_APP_ID") or not os.getenv("VOLCENGINE_ACCESS_TOKEN"):
        print("❌ 请设置VOLCENGINE_APP_ID和VOLCENGINE_ACCESS_TOKEN环境变量")
        print("   示例: $env:VOLCENGINE_APP_ID='your-app-id'")
        print("   示例: $env:VOLCENGINE_ACCESS_TOKEN='your-access-token'")
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
