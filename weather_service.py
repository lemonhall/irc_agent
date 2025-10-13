"""天气查询服务模块"""
import requests
import logging
from typing import Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

# 城市代码映射（和风天气城市ID）
CITY_CODES = {
    "北京": "101010100",
    "上海": "101020100", 
    "深圳": "101280601"
}

# 天气图标映射（可选，用于更友好的显示）
WEATHER_ICONS = {
    "晴": "☀️",
    "多云": "⛅",
    "阴": "☁️",
    "小雨": "🌦️",
    "中雨": "🌧️",
    "大雨": "⛈️",
    "雷阵雨": "⚡",
    "雪": "❄️"
}


class WeatherService:
    """天气服务类 - 支持多个免费天气API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化天气服务
        
        Args:
            api_key: 和风天气API密钥（可选，不提供则使用免费接口）
        """
        self.api_key = api_key
        self.cache = {}  # 简单缓存，避免频繁请求
        self.cache_duration = 1800  # 缓存30分钟
        
    def get_weather(self, city: str) -> Optional[str]:
        """
        获取指定城市的天气信息
        
        Args:
            city: 城市名称（北京/上海/深圳）
            
        Returns:
            格式化的天气信息字符串，失败返回 None
        """
        # 检查缓存
        cache_key = city
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if (datetime.now() - cached_time).seconds < self.cache_duration:
                logger.info(f"使用缓存的天气数据: {city}")
                return cached_data
        
        # 尝试多个API
        weather_info = None
        
        # 方案1: 使用和风天气API（需要key）
        if self.api_key:
            weather_info = self._get_weather_qweather(city)
        
        # 方案2: 使用免费的天气API（无需key）
        if not weather_info:
            weather_info = self._get_weather_free_api(city)
        
        # 方案3: 使用另一个备用API
        if not weather_info:
            weather_info = self._get_weather_wttr(city)
        
        # 缓存结果
        if weather_info:
            self.cache[cache_key] = (datetime.now(), weather_info)
        
        return weather_info
    
    def _get_weather_qweather(self, city: str) -> Optional[str]:
        """
        使用和风天气API获取天气
        官网: https://dev.qweather.com/
        """
        if city not in CITY_CODES:
            logger.warning(f"不支持的城市: {city}")
            return None
        
        try:
            city_code = CITY_CODES[city]
            url = f"https://devapi.qweather.com/v7/weather/now"
            params = {
                "location": city_code,
                "key": self.api_key
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") == "200":
                now = data["now"]
                weather_text = now.get("text", "未知")
                temp = now.get("temp", "?")
                feels_like = now.get("feelsLike", temp)
                humidity = now.get("humidity", "?")
                wind_dir = now.get("windDir", "")
                wind_scale = now.get("windScale", "")
                
                # 添加天气图标
                icon = WEATHER_ICONS.get(weather_text, "")
                
                weather_info = (
                    f"{icon}{weather_text}，气温{temp}°C"
                    f"（体感{feels_like}°C），湿度{humidity}%"
                )
                
                if wind_dir and wind_scale:
                    weather_info += f"，{wind_dir}{wind_scale}级"
                
                logger.info(f"和风天气API - {city}: {weather_info}")
                return weather_info
            else:
                logger.warning(f"和风天气API返回错误: {data.get('code')}")
                return None
                
        except Exception as e:
            logger.error(f"和风天气API调用失败: {e}")
            return None
    
    def _get_weather_free_api(self, city: str) -> Optional[str]:
        """
        使用免费天气API（天气API - OpenWeatherMap的中文替代）
        """
        try:
            # 使用 OpenWeatherMap 的免费API（中文城市名拼音）
            city_pinyin = {
                "北京": "Beijing",
                "上海": "Shanghai",
                "深圳": "Shenzhen"
            }.get(city)
            
            if not city_pinyin:
                return None
            
            # 这个API不需要key，但有请求限制
            url = f"https://wttr.in/{city_pinyin}?format=j1&lang=zh"
            
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            current = data["current_condition"][0]
            weather_desc = current.get("lang_zh", [{}])[0].get("value", "未知")
            temp = current.get("temp_C", "?")
            feels_like = current.get("FeelsLikeC", temp)
            humidity = current.get("humidity", "?")
            
            # 匹配图标
            icon = ""
            for key in WEATHER_ICONS:
                if key in weather_desc:
                    icon = WEATHER_ICONS[key]
                    break
            
            weather_info = (
                f"{icon}{weather_desc}，气温{temp}°C"
                f"（体感{feels_like}°C），湿度{humidity}%"
            )
            
            logger.info(f"wttr.in API - {city}: {weather_info}")
            return weather_info
            
        except Exception as e:
            logger.error(f"免费天气API调用失败: {e}")
            return None
    
    def _get_weather_wttr(self, city: str) -> Optional[str]:
        """
        使用 wttr.in 简化格式（最可靠的备用方案）
        """
        try:
            city_pinyin = {
                "北京": "Beijing",
                "上海": "Shanghai",
                "深圳": "Shenzhen"
            }.get(city)
            
            if not city_pinyin:
                return None
            
            # 使用最简单的格式
            url = f"https://wttr.in/{city_pinyin}?format=%C+%t+湿度%h"
            
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            weather_info = response.text.strip()
            logger.info(f"wttr.in 简化格式 - {city}: {weather_info}")
            return weather_info
            
        except Exception as e:
            logger.error(f"wttr.in 备用API调用失败: {e}")
            return None


# 全局单例
_weather_service = None

def get_weather_service(api_key: Optional[str] = None) -> WeatherService:
    """获取天气服务单例"""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService(api_key=api_key)
    return _weather_service


def get_city_weather(city: str) -> str:
    """
    便捷函数：获取城市天气
    
    Args:
        city: 城市名称（北京/上海/深圳）
        
    Returns:
        天气信息字符串，失败返回默认提示
    """
    service = get_weather_service()
    weather = service.get_weather(city)
    
    if weather:
        return weather
    else:
        return f"{city}天气信息暂时无法获取"


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=== 天气服务测试 ===\n")
    
    cities = ["北京", "上海", "深圳"]
    service = WeatherService()
    
    for city in cities:
        print(f"{city}:")
        weather = service.get_weather(city)
        if weather:
            print(f"  {weather}")
        else:
            print(f"  ❌ 获取失败")
        print()
    
    print("\n=== 测试缓存 ===")
    print("再次查询北京（应使用缓存）:")
    weather = service.get_weather("北京")
    print(f"  {weather}")
