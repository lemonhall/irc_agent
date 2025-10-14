#!/bin/bash
# 新闻播报自动化脚本 (Linux/Debian)
# 完整工作流：抓取新闻 → 生成播报稿 → 生成音频 → 添加背景音乐

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# 默认参数
SKIP_FETCH=false
SKIP_BROADCAST=false
SKIP_AUDIO=false
SKIP_BGM=false
BGM_VOLUME=0.15

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-fetch)
            SKIP_FETCH=true
            shift
            ;;
        --skip-broadcast)
            SKIP_BROADCAST=true
            shift
            ;;
        --skip-audio)
            SKIP_AUDIO=true
            shift
            ;;
        --skip-bgm)
            SKIP_BGM=true
            shift
            ;;
        --bgm-volume)
            BGM_VOLUME="$2"
            shift 2
            ;;
        -h|--help)
            echo "用法: $0 [选项]"
            echo ""
            echo "选项:"
            echo "  --skip-fetch       跳过新闻抓取"
            echo "  --skip-broadcast   跳过播报稿生成"
            echo "  --skip-audio       跳过音频生成"
            echo "  --skip-bgm         跳过背景音乐"
            echo "  --bgm-volume NUM   BGM音量 (0.0-1.0, 默认 0.15)"
            echo "  -h, --help         显示此帮助信息"
            exit 0
            ;;
        *)
            echo "未知参数: $1"
            echo "使用 --help 查看帮助"
            exit 1
            ;;
    esac
done

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}📻 新闻播报自动化工作流${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
NEWS_VIEWER_DIR="$SCRIPT_DIR"

# Python 可执行文件路径
PYTHON="$ROOT_DIR/.venv/bin/python"

# 检查 Python 环境
if [ ! -f "$PYTHON" ]; then
    echo -e "${RED}❌ 错误: 虚拟环境不存在${NC}"
    echo -e "${YELLOW}   请先运行: uv venv${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python 环境: $PYTHON${NC}"
echo ""

# 切换到 news_viewer 目录
cd "$NEWS_VIEWER_DIR"

# 步骤 1: 抓取新闻
if [ "$SKIP_FETCH" = false ]; then
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}📰 步骤 1/4: 抓取新闻${NC}"
    echo -e "${YELLOW}========================================${NC}"
    
    "$PYTHON" fetch_news.py
    
    echo -e "${GREEN}✅ 新闻抓取完成${NC}"
    echo ""
else
    echo -e "${GRAY}⏭️  跳过新闻抓取${NC}"
    echo ""
fi

# 步骤 2: 生成播报稿
if [ "$SKIP_BROADCAST" = false ]; then
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}🎙️  步骤 2/4: 生成播报稿${NC}"
    echo -e "${YELLOW}========================================${NC}"
    
    "$PYTHON" generate_broadcast.py
    
    echo -e "${GREEN}✅ 播报稿生成完成${NC}"
    echo ""
else
    echo -e "${GRAY}⏭️  跳过播报稿生成${NC}"
    echo ""
fi

# 步骤 3: 生成音频
if [ "$SKIP_AUDIO" = false ]; then
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}🎵 步骤 3/4: 生成音频${NC}"
    echo -e "${YELLOW}========================================${NC}"
    
    "$PYTHON" generate_audio.py
    
    echo -e "${GREEN}✅ 音频生成完成${NC}"
    echo ""
else
    echo -e "${GRAY}⏭️  跳过音频生成${NC}"
    echo ""
fi

# 步骤 4: 添加背景音乐
if [ "$SKIP_BGM" = false ]; then
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}🎼 步骤 4/4: 添加背景音乐${NC}"
    echo -e "${YELLOW}========================================${NC}"
    
    # 检查是否有 BGM 文件
    BGM_DIR="$NEWS_VIEWER_DIR/bgm"
    BGM_COUNT=$(find "$BGM_DIR" -maxdepth 1 -name "*.mp3" -o -name "*.wav" -o -name "*.m4a" | wc -l)
    
    if [ "$BGM_COUNT" -eq 0 ]; then
        echo -e "${YELLOW}⚠️  警告: bgm 目录中没有音乐文件，跳过 BGM${NC}"
        echo -e "${GRAY}   请在 bgm/ 目录中放入背景音乐文件${NC}"
    else
        "$PYTHON" add_bgm.py --volume "$BGM_VOLUME"
        
        echo -e "${GREEN}✅ BGM 添加完成${NC}"
    fi
    
    echo ""
else
    echo -e "${GRAY}⏭️  跳过背景音乐${NC}"
    echo ""
fi

# 完成
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 新闻播报生成完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 查找最新的播报目录
BROADCASTS_DIR="$NEWS_VIEWER_DIR/broadcasts"
LATEST_DIR=$(find "$BROADCASTS_DIR" -maxdepth 1 -type d -not -name "broadcasts" | sort -r | head -n 1)

if [ -n "$LATEST_DIR" ]; then
    LATEST_DIR_NAME=$(basename "$LATEST_DIR")
    echo -e "${CYAN}📂 播报目录: $LATEST_DIR_NAME${NC}"
    echo ""
    
    # 列出生成的文件
    if [ -d "$LATEST_DIR" ]; then
        MP3_FILES=$(find "$LATEST_DIR" -maxdepth 1 -name "*.mp3")
        
        if [ -n "$MP3_FILES" ]; then
            echo -e "${CYAN}🎧 生成的音频文件:${NC}"
            
            while IFS= read -r file; do
                FILE_NAME=$(basename "$file")
                FILE_SIZE=$(du -h "$file" | cut -f1)
                echo -e "   📦 $FILE_NAME ($FILE_SIZE)"
            done <<< "$MP3_FILES"
            
            echo ""
            
            # 查找完整版音频
            FULL_AUDIO=$(find "$LATEST_DIR" -maxdepth 1 -name "*_full_with_bgm.mp3" | head -n 1)
            if [ -z "$FULL_AUDIO" ]; then
                FULL_AUDIO=$(find "$LATEST_DIR" -maxdepth 1 -name "*_full.mp3" | head -n 1)
            fi
            
            if [ -n "$FULL_AUDIO" ]; then
                echo -e "${YELLOW}💡 完整版音频路径:${NC}"
                echo -e "${GRAY}   $FULL_AUDIO${NC}"
                echo ""
                
                # 提示播放方法
                echo -e "${YELLOW}💡 播放音频:${NC}"
                echo -e "${GRAY}   # 使用默认播放器${NC}"
                echo -e "${GRAY}   xdg-open \"$FULL_AUDIO\"${NC}"
                echo ""
                echo -e "${GRAY}   # 或使用 VLC${NC}"
                echo -e "${GRAY}   vlc \"$FULL_AUDIO\"${NC}"
                echo ""
                echo -e "${GRAY}   # 或使用 mpv${NC}"
                echo -e "${GRAY}   mpv \"$FULL_AUDIO\"${NC}"
                echo ""
            fi
        fi
    fi
fi

echo -e "${GREEN}✨ 全部完成！${NC}"
