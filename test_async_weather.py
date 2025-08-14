#!/usr/bin/env python3
"""비동기 날씨 API 호출 테스트"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

async def test_openweather_api():
    """OpenWeatherMap API를 비동기로 테스트"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        print("❌ OPENWEATHER_API_KEY가 설정되지 않았습니다.")
        return
    
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": "Tokyo",
        "appid": api_key,
        "units": "metric",
        "lang": "ja"
    }
    
    try:
        print("🌍 Tokyo의 날씨 정보를 가져오는 중...")
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                print(f"📡 응답 상태: {response.status}")
                
                if response.status == 200:
                    weather_data = await response.json()
                    print(f"✅ 성공! 도시: {weather_data['name']}")
                    print(f"🌡️  기온: {weather_data['main']['temp']}°C")
                    print(f"💧 습도: {weather_data['main']['humidity']}%")
                    print(f"🌤️  날씨: {weather_data['weather'][0]['description']}")
                else:
                    print(f"❌ API 오류: {response.status}")
                    error_text = await response.text()
                    print(f"오류 내용: {error_text}")
                    
    except aiohttp.ClientError as e:
        print(f"❌ API 요청 오류: {e}")
    except asyncio.TimeoutError:
        print("❌ 요청 시간 초과")
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")

async def test_langgraph_endpoint():
    """LangGraph 엔드포인트 테스트"""
    try:
        print("\n🔗 LangGraph 엔드포인트 테스트...")
        
        # 간단한 테스트 요청
        test_data = {
            "messages": [{"role": "user", "content": "Tokyo의 날씨는 어떤가요?"}],
            "query": "Tokyo의 날씨는 어떤가요?"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8123/agent",
                json=test_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                print(f"📡 LangGraph 응답 상태: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ LangGraph 성공!")
                    print(f"결과: {result}")
                else:
                    print(f"❌ LangGraph 오류: {response.status}")
                    error_text = await response.text()
                    print(f"오류 내용: {error_text}")
                    
    except aiohttp.ClientError as e:
        print(f"❌ LangGraph 요청 오류: {e}")
    except asyncio.TimeoutError:
        print("❌ LangGraph 요청 시간 초과")
    except Exception as e:
        print(f"❌ LangGraph 예상치 못한 오류: {e}")

async def main():
    """메인 함수"""
    print("🚀 비동기 날씨 API 테스트 시작")
    
    # 1. OpenWeatherMap API 직접 테스트
    await test_openweather_api()
    
    # 2. LangGraph 엔드포인트 테스트
    await test_langgraph_endpoint()
    
    print("\n✨ 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(main()) 