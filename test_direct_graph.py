#!/usr/bin/env python3
"""LangGraph를 직접 실행하여 테스트"""

import asyncio
import os
from dotenv import load_dotenv
from src.agent.graph import invoke_graph, InputSchema, Configuration

# 환경변수 로드
load_dotenv()

async def test_direct_graph():
    """LangGraph를 직접 실행하여 테스트"""
    print("🚀 LangGraph 직접 실행 테스트")
    
    # 테스트 케이스 1: city_hint 사용
    print("\n📝 테스트 1: city_hint 사용")
    input1 = InputSchema(
        messages=[{"role": "user", "content": "날씨가 어떤가요?"}],
        city="Tokyo"
    )
    config1 = Configuration(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        api_key=os.getenv("OPENWEATHER_API_KEY", "")
    )
    
    result1 = await invoke_graph(input1, config1)
    print(f"결과 1: {result1}")
    
    # 테스트 케이스 2: 자연어에서 도시명 추출
    print("\n📝 테스트 2: 자연어에서 도시명 추출")
    input2 = InputSchema(
        messages=[{"role": "user", "content": "도쿄의 날씨는 어떤가요?"}]
    )
    config2 = Configuration(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        api_key=os.getenv("OPENWEATHER_API_KEY", "")
    )
    
    result2 = await invoke_graph(input2, config2)
    print(f"결과 2: {result2}")
    
    # 테스트 케이스 3: 에러 케이스 (API 키 없음)
    print("\n📝 테스트 3: 에러 케이스 (API 키 없음)")
    input3 = InputSchema(
        messages=[{"role": "user", "content": "서울의 날씨는 어떤가요?"}],
        city="Seoul"
    )
    
    result3 = await invoke_graph(input3)
    print(f"결과 3: {result3}")

async def main():
    """메인 함수"""
    try:
        await test_direct_graph()
        print("\n✨ 직접 실행 테스트 완료!")
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 